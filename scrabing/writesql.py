
import pymysql
import csv
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import DATE, TEXT, create_engine
from sqlalchemy.types import VARCHAR, Float, Integer,Date
#pip install mysqlclient


# sql
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
for x in res:
    # read csv
    df=pd.read_csv(f'{x}.csv')
    df.columns=['Title','Url','Date']
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
    df['Resaturant']=f'{x}'

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

#pie chart
# values=df['Star'].value_counts()
# label=df['Star'].unique().tolist()
# plt.pie(values,labels=label,radius=1,autopct='%.1f%%')
# plt.show()
# print(df)

# # pie chart 2 end


# import matplotlib.pyplot as plt
# labels=df['Season'].unique().tolist()
# values=df['Season'].value_counts()

# # 設置分離的距離，0表示不分離
# explode = (0, 0.1, 0, 0) 
# plt.pie(values, explode=explode, labels=labels, autopct='%1.1f%%',
# shadow=True, startangle=90)
# # Equal aspect ratio 保證畫出的圖是正圓形
# plt.axis('equal') 
# plt.show()

#
# import matplotlib.pyplot as plt
# fig = plt.figure(figsize=(6,6))
# ax = plt.subplot(projection='3d')
# x = [2,4,6,8,10]
# y1 = 11
# y2 = 14
# y3 = 17
# z = 1
# ax.bar3d(x,y1,z,dx=1,dy=1,dz=[5,4,3,2,1])
# ax.bar3d(x,y2,z,dx=1,dy=1,dz=[1,2,3,2,1])
# ax.bar3d(x,y3,z,dx=1,dy=1,dz=[1,4,3,2,4])
# plt.show()





