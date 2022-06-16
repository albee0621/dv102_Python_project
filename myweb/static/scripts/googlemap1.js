
      'use strict';

      /**
       * Defines an instance of the Locator+ solution, to be instantiated
       * when the Maps library is loaded.
       */
      function LocatorPlus(configuration) {
        const locator = this;

        locator.each_locations = configuration.each_locations || [];
        locator.capabilities = configuration.capabilities || {};

        const mapEl = document.getElementById('gmp-map');
        const panelEl = document.getElementById('locations-panel');
        locator.panelListEl = document.getElementById('locations-panel-list');
        const sectionNameEl =
            document.getElementById('location-results-section-name');
        const resultsContainerEl = document.getElementById('location-results-list');

        const itemsTemplate = Handlebars.compile(
            document.getElementById('locator-result-items-tmpl').innerHTML);

        locator.searchLocation = null;
        locator.searchLocationMarker = null;
        locator.selectedLocationIdx = null;
        locator.userCountry = null;

        // Initialize the map -------------------------------------------------------
        locator.map = new google.maps.Map(mapEl, configuration.mapOptions);

        // Store selection.
        const selectResultItem = function(locationIdx, panToMarker, scrollToResult) {
          locator.selectedLocationIdx = locationIdx;
          for (let locationElem of resultsContainerEl.children) {
            locationElem.classList.remove('selected');
            if (getResultIndex(locationElem) === locator.selectedLocationIdx) {
              locationElem.classList.add('selected');
              if (scrollToResult) {
                panelEl.scrollTop = locationElem.offsetTop;
              }
            }
          }
          if (panToMarker && (locationIdx != null)) {
            locator.map.panTo(locator.each_locations[locationIdx].coords);
          }
        };

        // Create a marker for each location.
        const markers = locator.each_locations.map(function(location, index) {
          const marker = new google.maps.Marker({
            position: location.coords,
            map: locator.map,
            title: location.title,
          });
          marker.addListener('click', function() {
            selectResultItem(index, false, true);
          });
          return marker;
        });

        // Fit map to marker bounds.
        locator.updateBounds = function() {
          const bounds = new google.maps.LatLngBounds();
          if (locator.searchLocationMarker) {
            bounds.extend(locator.searchLocationMarker.getPosition());
          }
          for (let i = 0; i < markers.length; i++) {
            bounds.extend(markers[i].getPosition());
          }
          locator.map.fitBounds(bounds);
        };
        if (locator.each_locations.length) {
          locator.updateBounds();
        }

        // Get the distance of a store location to the user's location,
        // used in sorting the list.
        const getLocationDistance = function(location) {
          if (!locator.searchLocation) return null;

          // Fall back to straight-line distance.
          return google.maps.geometry.spherical.computeDistanceBetween(
              new google.maps.LatLng(location.coords),
              locator.searchLocation.location);
        };

        // Render the results list --------------------------------------------------
        const getResultIndex = function(elem) {
          return parseInt(elem.getAttribute('data-location-index'));
        };

        locator.renderResultsList = function() {
          let each_locations = locator.each_locations.slice();
          for (let i = 0; i < each_locations.length; i++) {
            each_locations[i].index = i;
          }
          if (locator.searchLocation) {
            sectionNameEl.textContent =
                'Nearest locations (' + each_locations.length + ')';
            each_locations.sort(function(a, b) {
              return getLocationDistance(a) - getLocationDistance(b);
            });
          } else {
            sectionNameEl.textContent = `All locations (${each_locations.length})`;
          }
          const resultItemContext = { each_locations: each_locations };
          resultsContainerEl.innerHTML = itemsTemplate(resultItemContext);
          for (let item of resultsContainerEl.children) {
            const resultIndex = getResultIndex(item);
            if (resultIndex === locator.selectedLocationIdx) {
              item.classList.add('selected');
            }

            const resultSelectionHandler = function() {
              selectResultItem(resultIndex, true, false);
            };

            // Clicking anywhere on the item selects this location.
            // Additionally, create a button element to make this behavior
            // accessible under tab navigation.
            item.addEventListener('click', resultSelectionHandler);
            item.querySelector('.select-location')
                .addEventListener('click', function(e) {
                  resultSelectionHandler();
                  e.stopPropagation();
                });
          }
        };

        // Optional capability initialization --------------------------------------
        initializeSearchInput(locator);

        // Initial render of results -----------------------------------------------
        locator.renderResultsList();
      }

      /** When the search input capability is enabled, initialize it. */
      function initializeSearchInput(locator) {
        const geocodeCache = new Map();
        const geocoder = new google.maps.Geocoder();

        const searchInputEl = document.getElementById('location-search-input');
        const searchButtonEl = document.getElementById('location-search-button');

        const updateSearchLocation = function(address, location) {
          if (locator.searchLocationMarker) {
            locator.searchLocationMarker.setMap(null);
          }
          if (!location) {
            locator.searchLocation = null;
            return;
          }
          locator.searchLocation = {'address': address, 'location': location};
          locator.searchLocationMarker = new google.maps.Marker({
            position: location,
            map: locator.map,
            title: 'My location',
            icon: {
              path: google.maps.SymbolPath.CIRCLE,
              scale: 12,
              fillColor: '#3367D6',
              fillOpacity: 0.5,
              strokeOpacity: 0,
            }
          });

          // Update the locator's idea of the user's country, used for units. Use
          // `formatted_address` instead of the more structured `address_components`
          // to avoid an additional billed call.
          const addressParts = address.split(' ');
          locator.userCountry = addressParts[addressParts.length - 1];

          // Update map bounds to include the new location marker.
          locator.updateBounds();

          // Update the result list so we can sort it by proximity.
          locator.renderResultsList();
        };

        const geocodeSearch = function(query) {
          if (!query) {
            return;
          }

          const handleResult = function(geocodeResult) {
            searchInputEl.value = geocodeResult.formatted_address;
            updateSearchLocation(
                geocodeResult.formatted_address, geocodeResult.geometry.location);
          };

          if (geocodeCache.has(query)) {
            handleResult(geocodeCache.get(query));
            return;
          }
          const request = {address: query, bounds: locator.map.getBounds()};
          geocoder.geocode(request, function(results, status) {
            if (status === 'OK') {
              if (results.length > 0) {
                const result = results[0];
                geocodeCache.set(query, result);
                handleResult(result);
              }
            }
          });
        };

        // Set up geocoding on the search input.
        searchButtonEl.addEventListener('click', function() {
          geocodeSearch(searchInputEl.value.trim());
        });

        // Add in an event listener for the Enter key.
        searchInputEl.addEventListener('keypress', function(evt) {
          if (evt.key === 'Enter') {
            geocodeSearch(searchInputEl.value);
          }
        });
      }

      const CONFIGURATION = {
        "each_locations": [
          {"title":"王品牛排 台北羅斯福店","address1":"100台灣台北市中正區羅斯福路二段9號","coords":{"lat":25.028953476588693,"lng":121.52136346256563},"placeId":"EkxOby4gOSwgU2VjdGlvbiAyLCBSb29zZXZlbHQgUmQsIFpob25nemhlbmcgRGlzdHJpY3QsIFRhaXBlaSBDaXR5LCBUYWl3YW4gMTAwIlASTgo0CjIJC8o6yZupQjQRrezskaQKbLAaHgsQ7sHuoQEaFAoSCce8rdGbqUI0EUQZXYaO48AnDBAJKhQKEgkJaT5cmqlCNBE1VoSRXrF_ag"},
          {"title":"王品牛排 台北中山北店","address1":"10491台灣台北市中山區中山北路二段33號2 樓","coords":{"lat":25.05339107611054,"lng":121.52284733558197},"placeId":"ElcyIOaokywgTm8uIDMzLCBTZWN0aW9uIDIsIFpob25nc2hhbiBOIFJkLCBaaG9uZ3NoYW4gRGlzdHJpY3QsIFRhaXBlaSBDaXR5LCBUYWl3YW4gMTA0OTEiWxpZClASTgo0CjIJcxjb4WipQjQRHZRmClmXvWMaHgsQ7sHuoQEaFAoSCZtsLV75q0I0EXXHnHuH-hrODBAhKhQKEgmti0aUT6lCNBFUnZRClRugSBIFMiDmqJM"},
          {"title":"王品牛排 台北南京東店","address1":"105台灣台北市松山區南京東路四段169號","coords":{"lat":25.051749376743636,"lng":121.55631479755324},"placeId":"ChIJMc7_UeqrQjQRXsCgAem_XTY"},
          {"title":"王品牛排 板橋縣民大道店","address1":"220台灣新北市板橋區縣民大道一段189號2 樓","coords":{"lat":25.01059562454075,"lng":121.461097617791},"placeId":"ElYyIOaokywgTm8uIDE4OSwgU2VjdGlvbiAxLCBYaWFubWluIEJsdmQsIEJhbnFpYW8gRGlzdHJpY3QsIE5ldyBUYWlwZWkgQ2l0eSwgVGFpd2FuIDIyMCJcGloKURJPCjQKMgml9AW0HahCNBGbdL3-D3FrgRoeCxDuwe6hARoUChIJ28E-m6gCaDQR-3HEyUH727kMEL0BKhQKEgkTZ5LepwJoNBGwb0oKq3AOcBIFMiDmqJM"},
          {"title":"王品牛排 桃園同德店","address1":"330台灣桃園市桃園區同德五街69號3 樓","coords":{"lat":25.014301331913025,"lng":121.30003364540367},"placeId":"EkgzIOaokywgTm8uIDY5LCBUb25nZGUgNXRoIFN0LCBUYW95dWFuIERpc3RyaWN0LCBUYW95dWFuIENpdHksIFRhaXdhbiAzMzAiWxpZClASTgo0CjIJPTNY0rEfaDQRZASbGWf-XNoaHgsQ7sHuoQEaFAoSCR35Wm4PH2g0EdSNb_zTIbq5DBBFKhQKEgl_YRDdrx9oNBE7eLh-o1y0qxIFMyDmqJM"},
          {"title":"王品牛排 中壢延平店","address1":"320台灣桃園市中壢區延平路552號2 樓","coords":{"lat":24.955590514360363,"lng":121.22272751779099},"placeId":"EkYyIOaokywgTm8uIDU1MiwgWWFucGluZyBSZCwgWmhvbmdsaSBEaXN0cmljdCwgVGFveXVhbiBDaXR5LCBUYWl3YW4gMzIwIlwaWgpREk8KNAoyCQGB5oZJImg0EYkTlNuSRF7RGh4LEO7B7qEBGhQKEgmbjeHM1iNoNBFBcSKBDUMP9QwQqAQqFAoSCTkewI83Img0EekfLEA1fWATEgUyIOaokw"},
          {"title":"王品牛排 竹北光明店","address1":"302台灣新竹縣竹北市光明一路181號","coords":{"lat":24.83040112735319,"lng":121.01429819999998},"placeId":"ChIJ08PJj-s2aDQRvGXc45Vj_5Y"},
          {"title":"王品牛排 台中文心店","address1":"407台灣台中市西屯區寧夏路233號","coords":{"lat":24.170518218826295,"lng":120.65915034110449},"placeId":"ChIJLfF9nikWaTQR5tcAWBBLBVo"},
          {"title":"王品牛排 台南健康店","address1":"700台灣台南市中西區健康路一段24號","coords":{"lat":22.981367280473012,"lng":120.2110756588955},"placeId":"ChIJ_e6c1oN2bjQRrXbUPEvp04A"},
          {"title":"王品牛排 高雄中正店","address1":"800台灣高雄市新興區中正三路88號","coords":{"lat":22.63125557328444,"lng":120.30717458220899},"placeId":"ChIJEyQF3I0EbjQRzkxjFRre7so"},
          {"title":"王品牛排 高雄博愛店","address1":"813台灣高雄市左營區博愛二路360-2號","coords":{"lat":22.66491061728572,"lng":120.30363775826648},"placeId":"ChIJdXmAGQQFbjQRZGCMBafjaOY"},
          {"title":"石二鍋 台北士林中正店(旗艦店)","address1":"111台灣台北市士林區中正路183-185號","coords":{"lat":25.095538575933652,"lng":121.52743660674594},"placeId":"ChIJb8ddYa2vQjQRGNl6vrhujqQ"},
          {"title":"石二鍋 台北延平南店","address1":"100台灣台北市中正區延平南路183號","coords":{"lat":25.034259405686026,"lng":121.50761986441805},"placeId":"ChIJnc58aTKpQjQRSvXe66981sg"},
          {"title":"石二鍋_中崙大潤發店","address1":"104台灣台北市中山區八德路二段306號B1","coords":{"lat":25.046944520093003,"lng":121.54253880674594},"placeId":"ChIJyQ4Iw0CrQjQR2Rr7kK5N8z0"},
          {"title":"石二鍋 捷運新北投店","address1":"112台灣台北市北投區泉源路12號2樓","coords":{"lat":25.13712696231766,"lng":121.50434126441803},"placeId":"ChIJ0UPoLQivQjQRyPJVGbA4xR0"},
          {"title":"石二鍋基隆愛買店","address1":"201台灣基隆市信義區深溪路53號B1","coords":{"lat":25.133041030732457,"lng":121.78218583558197},"placeId":"ChIJceTDDaNPXTQRJYGp-YYddCI"},
          {"title":"石二鍋_基隆仁二店","address1":"200台灣基隆市仁愛區仁二路236號","coords":{"lat":25.13033999651585,"lng":121.74355576441805},"placeId":"ChIJVymQLxtPXTQRIcZTpsDZYS0"},
          {"title":"石二鍋_中和德光店","address1":"235台灣新北市中和區德光路32號","coords":{"lat":25.00442629682213,"lng":121.4705151067459},"placeId":"ChIJKVRZt58CaDQRFlKn4afuxIM"},
          {"title":"石二鍋 新莊輔大店","address1":"242台灣新北市新莊區建國一路61號","coords":{"lat":25.03004568999566,"lng":121.43469537790982},"placeId":"ChIJU3Gwmd4XaTQR9PLvz9a7aOY"},
          {"title":"石二鍋＿三重龍門店","address1":"241台灣新北市三重區龍門路6號3F","coords":{"lat":25.071454147370357,"lng":121.49476072023772},"placeId":"ChIJL8vC-iapQjQR5eWNtNot6EM"},
          {"title":"石二鍋重新家樂福店","address1":"241台灣新北市三重區重新路五段654號","coords":{"lat":25.043338268389697,"lng":121.46750140674591},"placeId":"ChIJ0QMaT2eoQjQRhIJfzQSrREA"},
          {"title":"家樂福 蘆洲店","address1":"241台灣新北市三重區五華街282號","coords":{"lat":25.087980417615245,"lng":121.48677136441805},"placeId":"ChIJW3xeRiuvQjQRM92HBVStYpk"},
          {"title":"石二鍋＿板橋捷運新埔店","address1":"220台灣新北市板橋區文化路一段360號","coords":{"lat":25.02368943320089,"lng":121.46879453558196},"placeId":"ChIJE-39IT6oQjQRl6cDScIRop4"},
          {"title":"石二鍋_林口家樂福店","address1":"244台灣新北市林口區文化二路一段559號","coords":{"lat":25.07763473834139,"lng":121.37412200674592},"placeId":"ChIJl2oFStymQjQRRWJogAi2hOc"},
          {"title":"石二鍋_樹林家樂福店","address1":"238台灣新北市樹林區大安路118號","coords":{"lat":24.996689001858755,"lng":121.42100890674591},"placeId":"ChIJXVlXyWodaDQR71yqJPvICsI"},
          {"title":"石二鍋_捷運七張店","address1":"231台灣新北市新店區北新路二段128號","coords":{"lat":24.974843424272855,"lng":121.5431669932541},"placeId":"ChIJaRIXXPkBaDQRvJMijgmcOCw"},
          {"title":"石二鍋_三峽大學店","address1":"237台灣新北市三峽區大學路123號2樓","coords":{"lat":24.94319084941297,"lng":121.37486426441805},"placeId":"ChIJEywjffUbaDQRs333vmoP9n8"},
          {"title":"石二鍋 淡水中山店","address1":"251台灣新北市淡水區中山路8號3樓","coords":{"lat":25.16915080719822,"lng":121.44502980674591},"placeId":"ChIJdfqYelilQjQRduRXLLJ6afo"},
          {"title":"石二鍋_板橋愛買南雅店","address1":"220台灣新北市板橋區貴興路101號1","coords":{"lat":25.001825403112523,"lng":121.45658076441804},"placeId":"ChIJnXiJ230DaDQRpMugsoWfg2E"},
          {"title":"石二鍋_土城青雲","address1":"236台灣新北市土城區青雲路152號1樓","coords":{"lat":24.98339584715139,"lng":121.45889637790982},"placeId":"ChIJn-dYiS8DaDQRXDLCV3HAmTk"},
          {"title":"石二鍋 台北民權龍江店","address1":"10491台灣台北市中山區民權東路三段19號","coords":{"lat":25.062695729197365,"lng":121.541574635582},"placeId":"ChIJZ3oFROOrQjQRLj8dOKmNcv4"},
          {"title":"石二鍋 台北天母店","address1":"111台灣台北市士林區天母西路40號","coords":{"lat":25.118338835598234,"lng":121.5259059067459},"placeId":"ChIJ1_262YeuQjQRS74MTR0E40w"},
          {"title":"石二鍋 台北興隆店","address1":"116台灣台北市文山區興隆路四段149號","coords":{"lat":24.984865603959268,"lng":121.56177752209015},"placeId":"ChIJQwmQY3WqQjQR__dW7rWHmQk"},
          {"title":"石二鍋 台北信義店","address1":"106台灣台北市大安區信義路二段72號","coords":{"lat":25.03430841801476,"lng":121.52631337790983},"placeId":"ChIJwVCWXMqrQjQRg85iIjoKkjc"},
          {"title":"石二鍋_台北安居店","address1":"106台灣台北市大安區安居街50號","coords":{"lat":25.020302571599355,"lng":121.55394633558197},"placeId":"ChIJ9-Hu0jCqQjQR4A95UtrPWzI"},
          {"title":"石二鍋 台北捷運後山埤店","address1":"110台灣台北市信義區忠孝東路五段789號","coords":{"lat":25.0441250067157,"lng":121.58156730674591},"placeId":"ChIJP_G0b6OrQjQRNM3E-RPDb7Q"},
          {"title":"石二鍋 桂林家樂福店","address1":"108台灣台北市萬華區桂林路1號4F","coords":{"lat":25.037733377002073,"lng":121.5061659067459},"placeId":"ChIJX3hlt4KpQjQRE-7Hyp1pmT0"},
          {"title":"石二鍋 新竹林森店","address1":"300台灣新竹市東區林森路2巷9號3樓","coords":{"lat":24.802396295735676,"lng":120.97096427790984},"placeId":"ChIJD-Nu_Ok1aDQRlEaHs0rjUmQ"},
          {"title":"石二鍋_新竹大魯閣店","address1":"300台灣新竹市北區湳雅街91-2號B1","coords":{"lat":24.819529292714975,"lng":120.97017196441803},"placeId":"ChIJqSkIkUo1aDQRgNR-_u6ZX3Q"},
          {"title":"石二鍋_新竹忠孝店","address1":"300台灣新竹市東區忠孝路279-7號","coords":{"lat":24.80458288640215,"lng":120.98550944907379},"placeId":"ChIJJfegw9Y1aDQR-tI0qA1iKb8"},
          {"title":"石二鍋_中壢中美店","address1":"320台灣桃园市中坜市中美路一段12號3樓","coords":{"lat":24.959776080714875,"lng":121.2239383067459},"placeId":"ChIJJ9o3ZzYiaDQR58dtJwSqpV4"},
          {"title":"石二鍋 中壢家樂福中山東店","address1":"320台灣桃園市中壢區中山東路二段510號1F","coords":{"lat":24.946894862436064,"lng":121.244466735582},"placeId":"ChIJc3MvWGkiaDQRmggAkDnWSBg"},
          {"title":"石二鍋 八德家樂福店","address1":"334台灣桃園市八德區介壽路一段728號","coords":{"lat":24.965063541761175,"lng":121.29873017790986},"placeId":"ChIJryV-TCwfaDQRMzBdSI7s-po"},
          {"title":"石二鍋 桃園愛買店","address1":"330台灣桃園市桃園區中山路939號1樓","coords":{"lat":24.985850678319977,"lng":121.28541889325408},"placeId":"ChIJxR1ltDUfaDQRCGBL1TD4tVg"},
          {"title":"石二鍋 春日家樂福店","address1":"330台灣桃園市桃園區春日路1593號","coords":{"lat":25.02440382900827,"lng":121.30568063558194},"placeId":"ChIJyRtnj5gfaDQRhmUPdWLw4as"},
          {"title":"石二鍋_苗栗家樂福店","address1":"360台灣苗栗縣苗栗市國華路599號","coords":{"lat":24.57364229575264,"lng":120.81784700674591},"placeId":"ChIJxY5g-SqtaTQRKcCTwTUz9dI"},
          {"title":"石二鍋_頭份大潤發店","address1":"351台灣苗栗縣頭份市自強路230號B1","coords":{"lat":24.686788680375848,"lng":120.90342473558195},"placeId":"ChIJDzikg0pNaDQRdBLbCILr_j8"},
          {"title":"石二鍋_彰化中山店","address1":"500台灣彰化縣彰化市中山路二段227號","coords":{"lat":24.071368981032503,"lng":120.54237836441804},"placeId":"ChIJN60v4Kw5aTQRpsyzQ98VvL8"},
          {"title":"石二鍋_台中文心崇德店(旗艦店)","address1":"406台灣台中市北屯區文心路四段595號1樓","coords":{"lat":24.172541844047885,"lng":120.6846309067459},"placeId":"ChIJMy8Y_DEXaTQRSf_qfQPIiPo"},
          {"title":"石二鍋 太平中山店","address1":"411台灣台中市太平區中山路四段169號","coords":{"lat":24.148054333571345,"lng":120.70233266441802},"placeId":"ChIJr_ORJlA9aTQRujxlqWycJgo"},
          {"title":"石二鍋_台中黎明店","address1":"408台灣台中市南屯區黎明路二段216號","coords":{"lat":24.14717808943315,"lng":120.63626010674588},"placeId":"ChIJl0Jz7sM9aTQRyeZuWXCgLHQ"},
          {"title":"石二鍋 台中中華店","address1":"404台灣台中市北區中華路二段199-6號","coords":{"lat":24.152686759466594,"lng":120.6821886067459},"placeId":"ChIJm8eW9mU9aTQRwa7eCk663CI"},
          {"title":"石二鍋 豐原源豐店","address1":"420台灣台中市豐原區源豐路36號","coords":{"lat":24.25209950193052,"lng":120.71555757790986},"placeId":"ChIJqU1TmwgaaTQRB0DmWPuEGgo"},
          {"title":"石二鍋 台中美村南店","address1":"40253台灣台中市南區美村南路126號1樓","coords":{"lat":24.114825316142806,"lng":120.66688960674588},"placeId":"ChIJy17JZfg8aTQReDpi8t1A0G8"},
          {"title":"石二鍋_清水中山店","address1":"436台灣台中市清水區中山路177號","coords":{"lat":24.26670782082282,"lng":120.57427260674591},"placeId":"ChIJ8_tD-X0UaTQRItGMw9F6MqA"},
          {"title":"石二鍋＿台中文心家樂福店","address1":"408台灣台中市南屯區文心路一段521號","coords":{"lat":24.15414802264438,"lng":120.64633946441806},"placeId":"ChIJKxtTZJQ9aTQRDxgc4oau354"},
          {"title":"石二鍋 大里大買家店","address1":"412台灣台中市大里區國光路二段710號2F","coords":{"lat":24.115517015710207,"lng":120.67967900674589},"placeId":"ChIJUVsce-M8aTQR_GM7lQZmooU"},
          {"title":"石二鍋_台中大魯閣店","address1":"401台灣台中市東區復興路四段186號B1","coords":{"lat":24.136236396689643,"lng":120.68773447790984},"placeId":"ChIJRQz8M5A9aTQRXl_I406HrFQ"},
          {"title":"石二鍋青海家樂福店","address1":"407台灣台中市西屯區青海路二段207-18號","coords":{"lat":24.170514244750574,"lng":120.64479990674592},"placeId":"ChIJX7MsLlU9aTQRrX1qofnJynM"},
          {"title":"石二鍋_台中東海Jmall店","address1":"407台灣台中市西屯區台灣大道四段1038號1F","coords":{"lat":24.183298358521537,"lng":120.61550483558197},"placeId":"ChIJefqwcvMVaTQRBCF5nA0XqLg"},
          {"title":"石二鍋-員林大潤發店","address1":"513台灣彰化縣埔心鄉中山路一段319號1樓","coords":{"lat":23.94730764946729,"lng":120.56370656441803},"placeId":"ChIJg4i67mU2aTQRiHnS0zjg7D8"},
          {"title":"石二鍋_彰化家樂福店","address1":"500台灣彰化縣彰化市金馬路二段321號1F","coords":{"lat":24.09454737014178,"lng":120.54245346441802},"placeId":"ChIJfzKNjtE5aTQRblUQrduBSv0"},
          {"title":"石二鍋_南投家樂福店","address1":"540台灣南投縣南投市三和三路21號2F","coords":{"lat":23.905865583860148,"lng":120.6891286067459},"placeId":"ChIJG9tdSvUxaTQRMLA3_eNgd_Y"},
          {"title":"石二鍋_埔里家樂福店","address1":"545台灣南投縣埔里鎮信義路1029號","address2":"2F","coords":{"lat":23.970918189264214,"lng":120.95709250674591},"placeId":"ChIJhz7qEi3ZaDQR74rCB0dq89w"},
          {"title":"石二鍋_水湳家樂福店","address1":"406台灣台中市北屯區中清路二段165號","coords":{"lat":24.176664712591382,"lng":120.66962520674593},"placeId":"ChIJsWirN58XaTQRkxYRhwmkVMs"},
          {"title":"石二鍋 嘉義大潤發店","address1":"600台灣嘉義市西區博愛路二段281號","coords":{"lat":23.478509862471903,"lng":120.43785143558199},"placeId":"ChIJBWGzaCiUbjQRaMH_lz6x9tY"},
          {"title":"石二鍋_嘉義北門家樂福店","address1":"600台灣嘉義市東區忠孝路346巷21號1F","coords":{"lat":23.49006107878865,"lng":120.455387664418},"placeId":"ChIJ33tajgCVbjQRqk5W_UHU9Xc"},
          {"title":"石二鍋_斗六家樂福店","address1":"640台灣雲林縣斗六市雲林路二段297號","coords":{"lat":23.701783395574953,"lng":120.53075683558197},"placeId":"ChIJ35wzlC_JbjQR4f_L4Vor-Bs"},
          {"title":"石二鍋＿台南中華東店","address1":"701台灣台南市東區中華東路三段341號","coords":{"lat":22.974010175051063,"lng":120.2228681067459},"placeId":"ChIJS2ZdziB0bjQR78IIgHnpcPU"},
          {"title":"石二鍋＿仁德中山店","address1":"717台灣台南市仁德區中山路777號","coords":{"lat":22.972886676623983,"lng":120.2460458067459},"placeId":"ChIJh0IAN6p2bjQR-S9FcN5R0hE"},
          {"title":"石二鍋_安平家樂福店","address1":"700台灣台南市中西區中華西路二段16號","address2":"號2樓","coords":{"lat":22.98845486117573,"lng":120.1871494932541},"placeId":"ChIJQXjqcF13bjQR1ST8OouZ7UA"},
          {"title":"石二鍋_永康中正家樂福店","address1":"710台灣台南市永康區中正南路358號1樓","coords":{"lat":23.032817164183886,"lng":120.22860653558199},"placeId":"ChIJJfS8SkJ3bjQROzs_J6qBKi0"},
          {"title":"石二鍋_新仁家樂福店","address1":"717台灣台南市仁德區大同路三段755號1F","coords":{"lat":22.947481431783046,"lng":120.22007303558195},"placeId":"ChIJxxQ7bN91bjQRHJrRseyBF60"},
          {"title":"石二鍋_宜蘭家樂福店","address1":"260台灣宜蘭縣宜蘭市民權路二段38巷2號b2","coords":{"lat":24.753935333065495,"lng":121.75072846441803},"placeId":"ChIJxYu5NUDlZzQRg-xS_HFsx7g"},
          {"title":"石二鍋_高雄華夏店","address1":"813台灣高雄市左營區華夏路685號","coords":{"lat":22.67796879483258,"lng":120.30186540674589},"placeId":"ChIJc3ikcwsFbjQRxq8ncgJyVJY"},
          {"title":"石二鍋_高雄鳳山店","address1":"830台灣高雄市鳳山區青年路二段259號","coords":{"lat":22.638640007577592,"lng":120.3504569067459},"placeId":"ChIJvYE_5zEbbjQRnCfPSLYRyrc"},
          {"title":"石二鍋＿鳳山五甲店","address1":"830台灣高雄市鳳山區五甲一路261號","coords":{"lat":22.616529647326818,"lng":120.35405640674588},"placeId":"ChIJmah1jU8bbjQRhU-6xsi4hsg"},
          {"title":"石二鍋_高雄鼎山家樂福店","address1":"807台灣高雄市三民區大順二路849號1 樓","coords":{"lat":22.652749568571206,"lng":120.31894400674591},"placeId":"ChIJgfgz-yoFbjQRTMEKbJwwI9A"},
          {"title":"石二鍋_高雄三多三店","address1":"806台灣高雄市前鎮區三多三路137號","coords":{"lat":22.6159809874311,"lng":120.31082840674593},"placeId":"ChIJ-7z3lKAFbjQR7wLJgLvF5-I"},
          {"title":"石二鍋_新楠家樂福店","address1":"811台灣高雄市楠梓區土庫一路60號","coords":{"lat":22.7362326403056,"lng":120.33105630674588},"placeId":"ChIJfeHyMjQPbjQRdkT16YD9muI"},
          {"title":"石二鍋 (高雄美術南三店)","address1":"804台灣高雄市鼓山區美術南三路132號","coords":{"lat":22.653385386820936,"lng":120.28742020674589},"placeId":"ChIJbRNduH8FbjQRaBWVW5CtXZg"},
          {"title":"石二鍋_楠梓家樂福店","address1":"811台灣高雄市楠梓區藍田路288號1樓","coords":{"lat":22.727773692463785,"lng":120.29042610674591},"placeId":"ChIJb6VyYSYPbjQRgrLbbidi0Gk"},
          {"title":"石二鍋_高雄成功家樂福店","address1":"806台灣高雄市前鎮區中華五路1111號1樓","coords":{"lat":22.605069732308746,"lng":120.30419034907378},"placeId":"ChIJ7a7YSSsDbjQROqpMslIMlCk"},
          {"title":"石二鍋＿屏東家樂福店","address1":"900台灣屏東縣屏東市仁愛路188號","coords":{"lat":22.682493418018698,"lng":120.49763379325407},"placeId":"ChIJo3h8eIUXbjQRv0IOcG5cgpY"},
          {"title":"石二鍋_五甲家樂福","address1":"830台灣高雄市鳳山區林森路291號2樓","coords":{"lat":22.596577650634753,"lng":120.3364889067459},"placeId":"ChIJlYFpECIDbjQRoxI6g9mPgbw"}
        ],
        "mapOptions": {"center":{"lat":38.0,"lng":-100.0},"fullscreenControl":true,"mapTypeControl":false,"streetViewControl":false,"zoom":4,"zoomControl":true,"maxZoom":17},
        "mapsApiKey": "AIzaSyBxfQwB_YpxBAfnpkRhIPvrRd4gHEA5Xa8",
        "capabilities": {"input":true,"autocomplete":false,"directions":false,"distanceMatrix":false,"details":false}
      };

      function initMap() {
        new LocatorPlus(CONFIGURATION);
      }