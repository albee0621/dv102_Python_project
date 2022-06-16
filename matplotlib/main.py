import numpy as np
import pandas as pd
import matplot_draw as mat
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
import os
import re
import mpld3
import pymysql
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from distutils.command.config import config
import tkinter as tk
import tkinter.ttk as ttk
import jieba
from wordcloud import WordCloud
from PIL import Image
from collections import Counter
localtime=datetime.now().strftime("%Y-%m-%d")
one_year_ago=(datetime.now()-relativedelta(years=1)).strftime("%Y-%m-%d")
####資料庫連線
db=pymysql.connect(host='dv102food.ddns.net', port=3306, user='dv102', passwd='dv102')
cursor=db.cursor()
####各資料源的所有品牌資料表加起來
def data_allsource(restaurant_brand):
	restdatadict = {}
	for source in restaurant_brand:
		for name in restaurant_brand[source]:
			sql = f'''SELECT * FROM  `{source}`.`{name}` WHERE Date > "{one_year_ago}" and Date < "{localtime}";'''
			datum = cursor.execute(sql)###
			data  = cursor.fetchall(  )
			field_names = [i[0] for i in cursor.description]
			frame = pd.DataFrame(list(data),columns=field_names)
			restdatadict[source+name]=frame

	all_dataframe = []
	for source in restaurant_brand:
		for name in restaurant_brand[source]:
			newdataframe = restdatadict[source+name].loc[:,['Month','Season','Brand']]
			all_dataframe.append(newdataframe)
	all_data = pd.concat(all_dataframe)#把所有dataframe合併起起來
	# pd.set_option('display.max_rows',None)
	all_data.reset_index(drop=True, inplace=True)
	return(all_data)

####所有資料源的所有品牌資料表加起來
def data(restaurant,resource):
	restdatadict = {}
	for name in restaurant:
		sql = f'''SELECT * FROM  `{resource}`.`{name}` WHERE Date > "{one_year_ago}" and Date < "{localtime}";'''
		datum = cursor.execute(sql)###
		data  = cursor.fetchall(  )
		field_names = [i[0] for i in cursor.description]
		frame = pd.DataFrame(list(data),columns=field_names)
		restdatadict[name]=frame
	all_dataframe = []
	for rest in restdatadict:
		all_dataframe.append(restdatadict[rest])
	all_data = pd.concat(all_dataframe)#把所有dataframe合併起起來
	# pd.set_option('display.max_rows',None)
	all_data.reset_index(drop=True, inplace=True)
	return(all_data)

####單一資料源單一餐廳
def cloud(res,sourc2,colname):
	sql = f'''SELECT * FROM  `{sourc2}`.`{res}` WHERE Date > "{one_year_ago}" and Date < "{localtime}";'''
	datum = cursor.execute(sql)###
	data  = cursor.fetchall(  )
	field_names = [i[0] for i in cursor.description]
	frame = pd.DataFrame(list(data),columns=field_names)
	read = frame.loc[:,colname].values.tolist()
	stopwords = set()
	jiebaword = " ".join(jieba.cut(",".join(read)))

	content  = [stopword.strip() for stopword in open("textcloud/stopwords.txt", "r", encoding="utf-8").readlines()]
	stopwords.update(content)

	font = 'textcloud/General_Art.ttf' # 設定字體格式
	pngfile = "textcloud/520.png"
	mask1 = np.array(Image.open(pngfile))

	wc = WordCloud(background_color="white", margin=2, mask=mask1, font_path=font, max_words=200, stopwords=stopwords).generate(jiebaword)
	plt.imshow(wc) 
	plt.axis("off")
	plt.show()
####所有資料源單一餐廳
def cloud_allsource(name,restaurant_brand2,colname):
	readall = []
	for src in restaurant_brand2:
		sql = f'''SELECT * FROM  `{src}`.`{name}` WHERE Date > "{one_year_ago}" and Date < "{localtime}";'''
		datum = cursor.execute(sql)###
		data  = cursor.fetchall(  )
		field_names = [i[0] for i in cursor.description]
		frame = pd.DataFrame(list(data),columns=field_names)
		trans = {'Content':"Review"}
		if 'Content' in frame.columns:
			frame.rename(columns = trans,inplace=True)
		read = frame.loc[:,colname].values.tolist()	
		readall = readall+read
	stopwords = set()
	jiebaword = " ".join(jieba.cut(",".join(readall)))

	content  = [stopword.strip() for stopword in open("textcloud/stopwords.txt", "r", encoding="utf-8").readlines()]
	stopwords.update(content)

	font = 'textcloud/General_Art.ttf' # 設定字體格式
	pngfile = "textcloud/520.png"
	mask1 = np.array(Image.open(pngfile))

	wc = WordCloud(background_color="white", margin=2, mask=mask1, font_path=font, max_words=200, stopwords=stopwords).generate(jiebaword)
	plt.imshow(wc) 
	plt.axis("off")
	plt.show()
####讀檔資料表名&建立畫圖物件
brand = ['WangPin_Group','ThaiTown_Group']
restaurant=['WangPin','ShiErguo','YakiYan','ChaMoNix','Tokiya','ThaiTown','VeryThai','1010Hunan','VeryThaiNoodles','SHANNRICEBAR']		
restaurant_brand = {'Dcard':brand,'ETTODAY':brand,'googlemap':brand}
season_object = mat.matplotdraw_season_3d()
month_object = mat.matplotdraw_month()
####讀檔資料表名
restaurant_C = ['王品牛排','石二鍋','夏慕尼','原燒','陶板屋','瓦城','非常泰','1010湘','大心','時時香']
restdict = dict(zip(restaurant_C,restaurant))
restaurant_brand2 = ['googlemap','Dcard']

def getfunc(a):
	global way
	way = comboExample.get()
	print(way)
	return way
def getfunc2(a):
	global sourc
	sourc = comboExample2.get()
	print(sourc)
	return sourc
def getfunc3(a):
	global res
	res = comboExample3.get()
	print(res)
	return res
def getfunc4(a):
	global sourc2
	sourc2 = comboExample4.get()
	print(sourc2)
	return sourc2
def button_event():
	if way == '季節聲量變化' and sourc == 'Dcard':
		# os.system("python count_by_season_3d_Dcard.py")
		season_count = season_object.count_by_season_3d(data(restaurant,sourc))
	elif way == '季節聲量變化' and sourc == 'ETTODAY':
		# os.system("python count_by_season_3d_ETTODAY.py")
		season_count = season_object.count_by_season_3d(data(restaurant,sourc))
	elif way == '季節聲量變化' and sourc == 'googlemap':
		# os.system("python count_by_season_3d_Googlemap.py")
		season_count = season_object.count_by_season_3d(data(restaurant,sourc))
	elif way == '季節聲量變化' and sourc == '所有資料源':
		# os.system("python count_by_season_3d_allsource.py")
		season_count = season_object.count_by_season_3d(data_allsource(restaurant_brand))
	elif way == '月份聲量變化' and sourc == 'Dcard':
		# os.system("python count_by_month_Dcard.py")
		season_count = month_object.count_by_month(data(restaurant,sourc))
	elif way == '月份聲量變化' and sourc == 'ETTODAY':
		# os.system("python count_by_month_ETTODAY.py")
		season_count = month_object.count_by_month(data(restaurant,sourc))		
	elif way == '月份聲量變化' and sourc == 'googlemap':
		# os.system("python count_by_month_Googlemap.py")
		season_count = month_object.count_by_month(data(restaurant,sourc))	
	elif way == '月份聲量變化' and sourc == '所有資料源':
		# os.system("python count_by_month_allsource.py")
		season_count = month_object.count_by_month(data_allsource(restaurant_brand))
def button_event2():
	rest_ava = restdict[res]
	colname_D = 'Content'
	colname_G = 'Review'
	if res == '王品牛排' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '石二鍋' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '夏慕尼' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '原燒' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '陶板屋' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '瓦城' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '時時香' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '非常泰' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '1010湘' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '大心' and sourc2 == 'Dcard':
		cloud(rest_ava,sourc2,colname_D)
	elif res == '王品牛排' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '石二鍋' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '夏慕尼' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '原燒' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '陶板屋' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '瓦城' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '時時香' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '非常泰' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '1010湘' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '大心' and sourc2 == 'googlemap':
		cloud(rest_ava,sourc2,colname_G)
	elif res == '王品牛排' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '石二鍋' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '夏慕尼' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '原燒' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '陶板屋' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '瓦城' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '時時香' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '非常泰' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '1010湘' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)
	elif res == '大心' and sourc2 == '所有資料源':
		cloud_allsource(rest_ava,restaurant_brand2,colname_G)

app = tk.Tk() 
app.geometry('220x220')
comboboxText = tk.StringVar()
label1 = tk.Label(app,
                    text = "請選擇欲查詢各集團聲量")
label1.place(x=25, y=0)

label2 = tk.Label(app,
                    text = "請選擇欲查詢各餐廳評價")
label2.place(x=25, y=100)

comboExample = ttk.Combobox(app, 
                            values=[
                                    "季節聲量變化", 
                                    "月份聲量變化",
                                    ])
comboExample2 = ttk.Combobox(app, 
                            values=[
                                    "Dcard", 
                                    "ETTODAY",
									"googlemap",
									"所有資料源",
                                    ])
comboExample3 = ttk.Combobox(app, 
                            values=[
                                    "王品牛排", 
                                    "石二鍋",
									"夏慕尼",
									"原燒",
									"陶板屋",
									"瓦城",
									"時時香",
									"非常泰",
									"1010湘",
									"大心",
                                    ])
comboExample4 = ttk.Combobox(app, 
                            values=[
                                    "Dcard", 
									"googlemap",
									"所有資料源",
                                    ])
mybutton = ttk.Button(app, text="提交",command=button_event)
mybutton2 = ttk.Button(app, text="提交",command=button_event2)
comboExample.place(x=25, y=25)
comboExample.current(None)
comboExample.bind("<<ComboboxSelected>>", getfunc)

comboExample2.place(x=25, y=50)
comboExample2.current(None)
comboExample2.bind("<<ComboboxSelected>>", getfunc2)

mybutton.place(x=100,y=75)

comboExample3.place(x=25, y=125)
comboExample3.current(None)
comboExample3.bind("<<ComboboxSelected>>", getfunc3)

comboExample4.place(x=25, y=150)
comboExample4.current(None)
comboExample4.bind("<<ComboboxSelected>>", getfunc4)

mybutton2.place(x=100,y=175)


# if comboboxText.get() == 
app.mainloop()
