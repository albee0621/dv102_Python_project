import pymysql
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
localtime=datetime.now().strftime("%Y-%m-%d")
one_year_ago=(datetime.now()-relativedelta(years=1)).strftime("%Y-%m-%d")
####資料庫連線
db=pymysql.connect(host='dv102food.ddns.net', port=3306, user='dv102', passwd='dv102')
cursor=db.cursor()
def callrating(restaurantname,source,col):
    sql = f'''SELECT * FROM  `{source}`.`{restaurantname}` WHERE Date > "{one_year_ago}" and Date < "{localtime}";'''
    datum = cursor.execute(sql)###
    data  = cursor.fetchall(  )
    field_names = [i[0] for i in cursor.description]
    frame = pd.DataFrame(list(data),columns=field_names)
    starlist  = frame.loc[:,col].to_list()
    count = frame.shape[0]
    totalstar = 0
    for star in starlist:
        totalstar = totalstar + int(star)
    averagestar = round(totalstar/count,2)
    return averagestar