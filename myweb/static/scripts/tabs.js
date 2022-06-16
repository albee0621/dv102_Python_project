$('.page').each(function(){                   // Find lists of tabs
  var $this = $(this);                            // Store this list
  var $tab = $this.find('.active2');             // Get the active2 list item
  var $link = $tab.find('a');                     // Get link from active2 tab
  var $panel = $($link.attr('href'));             // Get active2 panel

  $this.on('click', '.tab-control', function(e) { // When click on a tab
    e.preventDefault();                           // Prevent link behavior
    var $link = $(this),                          // Store the current link
        id = this.hash;                           // Get href of clicked tab 

    if (id && !$link.is('.active2')) {             // If not currently active2
      $panel.removeClass('active2');               // Make panel inactive2
      $tab.removeClass('active2');                 // Make tab inactive2

      $panel = $(id).addClass('active2');          // Make new panel active2
      $tab = $link.parent().addClass('active2');   // Make new tab active2 
    }
  });
});