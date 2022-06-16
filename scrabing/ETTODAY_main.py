import requests
import selenium
from selenium import webdriver
import chromedriver_autoinstaller
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup as bs
import re
import json
from lxml import html
from lxml import cssselect
import pandas as pd
import pymysql
import csv
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import DATE, TEXT, create_engine
from sqlalchemy.types import VARCHAR, Float, Integer,Date

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()
driver.get("https://www.ettoday.net/")
driver.implicitly_wait(10)
keyword = '王品牛排'
search = driver.find_element_by_xpath("/html/body/div[4]/div/div[4]/div/div[1]/div[2]/div[1]/form/input")
search.send_keys(keyword)
search.send_keys(Keys.RETURN)
restaurant = [keyword,'石二鍋','夏慕尼','原燒','陶板屋','瓦城','非常泰','1010湘','大心','時時香']
result = {}
for key in restaurant:
    search2 = driver.find_element_by_xpath('//*[@id="header"]/div[3]/form/p[1]/input')
    for word in range(10):
        search2.send_keys(Keys.BACK_SPACE)
    search2.send_keys(key)
    search2.send_keys(Keys.RETURN)
    pagesize = driver.find_element_by_xpath('//*[@id="result-list"]/div[12]/div/p').text.split("|")[1]
    page = re.findall(r'\d+',pagesize)
    pages = int(page[0])
    condic = {}
    for x in range(1,pages+1):#
        try:
            titles = []
            link = []
            driver.get(f'https://www.ettoday.net/news_search/doSearch.php?keywords={key}&idx=1&page={x}')
            title = driver.find_elements_by_xpath('//*[@id="result-list"]/div/div[2]/h2/a')
            for cont in title:  
                condic[cont.text]=cont.get_attribute("href")
            time.sleep(1)
        except:
            result[key] = condic
            break
        result[key] = condic
# with open('news.json','w',encoding='UTF-8') as file:
#     file.write(json.dumps(result,ensure_ascii=False))
# with open('news.json','r',encoding="utf-8") as file:
#     news = json.loads(file.read())
alltime = []
allarticle = []
for title in result:
    times = []
    articles = []
    new_tit = (result[title].keys())
    for tit in new_tit:
        respon = requests.get(result[title][tit])
        # tree = html.fromstring(respon.text)
        soup = bs(respon.text,'lxml')
        try:
            cont = soup.find_all('div','story')[0]
            content = cont.find_all('p')
            article = []
            for para in content:
                if '圖' in para.text:
                    continue
                else:
                    article.append(para.text)
            art = "".join(article)
            articles.append(art)
        except:
            articles.append("")
        try:
            time = soup.find_all('time','date')[0]
            spltime = time.text.strip().split(" ")[0].replace("年","-").replace("月","-").replace("日","")
            spltimes = spltime.split("-")
            if len(spltimes[2]) == 1:
                spltimes[2] = "0"+spltimes[2]
            finaltime = "-".join(spltimes)
            times.append(finaltime)
        except:
            # times.append("")
            try:
                time2 = soup.find_all('time','news-time')[0]
                spltime2 = time2.text.strip().split(" ")[0].replace("年","-").replace("月","-").replace("日","")
                spltimes2 = spltime2.split("-")
                if len(spltimes2[2]) == 1:
                    spltimes2[2] = "0"+spltimes2[2]
                finaltime2 = "-".join(spltimes2)
                times.append(finaltime2)
            except:
                time3 = soup.find_all('div','date')[0]
                spltime3 = time3.text.strip().split(" ")[0].replace("年","-").replace("月","-").replace("日","")
                spltimes3 = spltime3.split("-")
                if len(spltimes3[2]) == 1:
                    spltimes3[2] = "0"+spltimes3[2]
                finaltime3 = "-".join(spltimes3)
                times.append(finaltime3)
    alltime.append(times)
    allarticle.append(articles)
# with open('time.json','w',encoding='UTF-8') as file:
#     file.write(json.dumps(alltime,ensure_ascii=False))
# with open('article.json','w',encoding='UTF-8') as file:
#     file.write(json.dumps(allarticle,ensure_ascii=False))
newsresult = {}
for index1,title in enumerate(result):
    ll = []
    new_tit = (result[title].keys())
    for index2,tit in enumerate(new_tit):
        allnews = {}
        allnews['title'] = tit
        allnews['url'] = result[title][tit]
        allnews['time'] = alltime[index1][index2]
        allnews['content'] = allarticle[index1][index2]
        ll.append(allnews)
    newsresult[title] = ll

finaldataframe = {}
for rest in newsresult:
    titles = []
    url = []
    tim = []
    contents = []
    for i in newsresult[rest]:
        titles.append(i["title"])
        url.append(i["url"])
        tim.append(i["time"])
        contents.append(i["content"])
    df = pd.DataFrame({"title":titles,"url":url,"time":tim,"Content":contents})
    finaldataframe[rest] = df
##writesql
db=pymysql.connect(host='dv102food.ddns.net', port=3306, user='dv102', passwd='dv102')
cursor=db.cursor()

create_database='''CREATE DATABASE IF NOT EXISTS ETTODAY
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;'''

cursor.execute(create_database)
db.commit()

db.close()


res=['WangPin','ShiErguo','YakiYan','ChaMoNix','Tokiya','ThaiTown','VeryThai','1010Hunan','VeryThaiNoodles','SHANNRICEBAR']


df_list={}
for i,x in enumerate(finaldataframe):
    # read csv
    df = finaldataframe[x]
    df.columns=['Title','Url','Date','Content']
    # print(df)
    #整理出月份column
    month=[]
    change=df['Date'].values.tolist()
    for new in change:
        month.append(new.split('-')[1])
    df['Month']=month

    # 將月份轉換成新column
    season={'01':'spring',
    '02':'spring',
    '03':'spring',
    '04':'summer',
    '05':'summer',
    '06':'summer',
    '07':'autumn',
    '08':'autumn',
    '09':'autumn',
    '10':'winter',
    '11':'winter',
    '12':'winter'}

    # 月份轉季節column
    df['Season']=df['Month'].map(season)
    df['Resaturant']=f'{res[i]}'

    if x in res[0:5]:
        df['Brand']='WangPin'
    else:
        df['Brand']='ThaiTown'
    df['Source']='ETTODAY'
    df_list[f'{x}']=df



    engine = create_engine("mysql://dv102:dv102@dv102food.ddns.net:3306/ETTODAY")
    dtypedict = {
    'Title': TEXT(),
    'Url': TEXT(),
    'Date ':DATE(),
    'Season  ':TEXT(),
    'Month  ':TEXT(),
    'Brand    ':TEXT(),
    'Source ':TEXT(),

    }
    df.to_sql(name=f'{x}',con=engine,if_exists='replace',dtype=dtypedict)
    # print(df)

c_data=pd.concat([df_list['WangPin'],df_list['ShiErguo'],df_list['ChaMoNix'],df_list['YakiYan'],df_list['Tokiya']])
c_data2=pd.concat([df_list['ThaiTown'],df_list['VeryThai'],df_list['VeryThaiNoodles'],df_list['SHANNRICEBAR'],df_list['1010Hunan']])

c_data.to_sql(name='WangPin_Group',con=engine,if_exists='replace',dtype=dtypedict)
c_data2.to_sql(name='ThaiTown_Group',con=engine,if_exists='replace',dtype=dtypedict)