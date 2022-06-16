import jieba
from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import pymysql
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
db=pymysql.connect(host='dv102food.ddns.net', port=3306, user='dv102', passwd='dv102')
cursor=db.cursor()

localtime=datetime.now().strftime("%Y-%m-%d")
one_year_ago=(datetime.now()-relativedelta(years=1)).strftime("%Y-%m-%d")

sql = f'''SELECT * FROM  `googlemap`.`WangPin` WHERE Date > "{one_year_ago}" and Date < "{localtime}";'''
datum = cursor.execute(sql)###
data  = cursor.fetchall(  )
field_names = [i[0] for i in cursor.description]
frame = pd.DataFrame(list(data),columns=field_names)
read = frame.loc[:,'Review'].values.tolist()

stopwords = set()
jiebaword = " ".join(jieba.cut(",".join(read)))

content  = [stopword.strip() for stopword in open("stopwords.txt", "r", encoding="utf-8").readlines()]
stopwords.update(content)

font = 'General_Art.ttf' # 設定字體格式
pngfile = "520.png"
mask1 = np.array(Image.open(pngfile))

wc = WordCloud(background_color="white", margin=2, mask=mask1, font_path=font, max_words=200, stopwords=stopwords).generate(jiebaword)
plt.imshow(wc) 
plt.axis("off")
plt.show()