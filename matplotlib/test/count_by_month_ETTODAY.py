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
# restaurant = ['王品牛排','石二鍋','夏慕尼','原燒','陶板屋','瓦城','非常泰','1010湘','大心新泰式麵食','時時香']
# path = r'D:/my_project_v3/Myproject_v3/PTT_CSV/'
localtime=datetime.now().strftime("%Y-%m-%d")
# print(localtime)
one_year_ago=(datetime.now()-relativedelta(years=1)).strftime("%Y-%m-%d")
# print(one_year_ago.strftime("%Y-%m-%d"))
restaurant=['WangPin','ShiErguo','YakiYan','ChaMoNix','Tokiya','ThaiTown','VeryThai','1010Hunan','VeryThaiNoodles','SHANNRICEBAR']
db=pymysql.connect(host='dv102food.ddns.net', port=3306, user='dv102', passwd='dv102')
cursor=db.cursor()
restdatadict = {}
for name in restaurant:
    sql = f'''SELECT * FROM  `ETTODAY`.`{name}` WHERE Date > "{one_year_ago}" and Date < "{localtime}";'''
    datum = cursor.execute(sql)###
    data  = cursor.fetchall(  )
    field_names = [i[0] for i in cursor.description]
    frame = pd.DataFrame(list(data),columns=field_names)
    restdatadict[name]=frame
# matplot_object = mat.preprocess()
# mydataframe = matplot_object.final_dataframe(restdatadict)
all_dataframe = []
for rest in restdatadict:
    all_dataframe.append(restdatadict[rest])
all_data = pd.concat(all_dataframe)#把所有dataframe合併起起來
# pd.set_option('display.max_rows',None)
all_data.reset_index(drop=True, inplace=True)
# print(all_data)
month_object = mat.matplotdraw_month()
season_count = month_object.count_by_month(all_data)