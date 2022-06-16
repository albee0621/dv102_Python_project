from flask import Flask, request, render_template, redirect, url_for,abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import configparser, re
import requests
import json
import stars_google as star



app = Flask(__name__)
@app.route('/Home', methods=['GET', 'POST'])
def Home():
    return render_template('index.html')

line_bot_api = LineBotApi('arFOjxE8gCofsnu+fPRsi8QkK2tscViHSsc6D0nlR1FAgFzThd7z+KPMTF0AIiZCgffpKgN/uLMfUgt7l8hQPzSoLcPBAEYnnd59zYx04sfVQLNuRE0opdeHOoGZJuLifI9DmQn6GuxsnJshIZZLWQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('66d58ae72cf2779d33bd850e6d5ea28d')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    if isinstance(event, MessageEvent):
        messages=event.message.text
        # if  messages=="查詢":
        #     flex_message = TextSendMessage(text='請點擊查詢資訊',
        #             quick_reply=QuickReply(items=[
        #                 QuickReplyButton(action=MessageAction(label="王品、瓦城評價查詢",text='查詢評價'))
        #             ]))
        #     line_bot_api.reply_message(event.reply_token,flex_message)
        if re.match('查詢',messages):
            line_bot_api.reply_message(event.reply_token,
            TemplateSendMessage(
                alt_text='ButtonsTemplate',
                template=ButtonsTemplate(
                    thumbnail_image_url='https://hualien.lakeshore.com.tw/wp-content/uploads/sites/14/2019/06/hu_mola_slideshow_1.jpg',
                    title='王品、瓦城集團',
                    text='您想要查詢哪個集團的餐廳呢?',
                    actions=[
                        PostbackTemplateAction(
                            label='王品集團',
                            text='王品集團',
                            data='A&王品集團'
                        ),
                        PostbackTemplateAction(
                            label='瓦城集團',
                            text='瓦城集團',
                            data='A&瓦城集團'            
                        )
                        ]
                        )
                )
            )
        elif event.message.text == "王品集團":
            carousel_template_message = TemplateSendMessage(
            alt_text='餐廳聲量查詢',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTctez7IAM3BQYWJZqwdt2EUoAOYXroM6ZFvg&usqp=CAU',
                        title='王品牛排',
                        text='只款待心中最重要的人',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論:'+str(star.callrating('WangPin','googlemap','Star'))+'      Dcard平均愛心:'+str(star.callrating('WangPin','Dcard','Heart'))
                                # text='QQ'
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://www.wangsteak.com.tw/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUrcgI8yWdfD2yVRqBiNI46k75blMPebx9qffu0iG2ZD9w_EkMAE9JKy9RH5CF0z0WFWY&usqp=CAU',
                        title='石二鍋',
                        text='來點新鮮的Fresh',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論:'+str(star.callrating('ShiErguo','googlemap','Star'))+'      Dcard平均愛心:'+str(star.callrating('ShiErguo','Dcard','Heart'))
                                # text ='QQ'
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://www.12hotpot.com.tw/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRXFut4jRUM9-zI1t74DwwKOovTxjiuCfSdbg&usqp=CAU',
                        title='原燒',
                        text='大滿足!大豐盛!大趣味!',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論:'+str(star.callrating('YakiYan','googlemap','Star'))+'      Dcard平均愛心:'+str(star.callrating('YakiYan','Dcard','Heart'))
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://www.yakiyan.com/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSIEVYVqDpg9iiJesIzUe1GJf0n3F1ppvnAZw&usqp=CAU',
                        title='陶板屋',
                        text='旨味．物語',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論'+str(star.callrating('Tokiya','googlemap','Star'))+'      Dcard平均愛心:'+str(star.callrating('Tokiya','Dcard','Heart'))
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://www.tokiya.com.tw/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKRNHJVSHMwFx0szbdxYu3nHoPLqIaqPHQbA&usqp=CAU',
                        title='夏慕尼',
                        text='先嘗．嘗鮮',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論'+str(star.callrating('ChaMoNix','googlemap','Star'))  +'      Dcard平均愛心:'+str(star.callrating('ChaMoNix','Dcard','Heart'))
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://www.chamonix.com.tw/'
                            )
                        ]
                    )
                    ]))
            line_bot_api.reply_message(event.reply_token, carousel_template_message)
        elif event.message.text == "瓦城集團":
            carousel_template_message = TemplateSendMessage(
            alt_text='餐廳聲量查詢',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTRVdDJdTbYQpRT4h8GpZkevrnoqSlP2A5zGw&usqp=CAU',
                        title='瓦城',
                        text='高品質的泰國道地美味',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論'+str(star.callrating('ThaiTown','googlemap','Star'))+'      Dcard平均愛心:'+str(star.callrating('WangPin','Dcard','Heart'))
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://www.thaitown.com.tw/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://ucarecdn.com/a2c14f9e-01a8-4696-a7b7-9206c2b1856e/',
                        title='時時香',
                        text='跨菜系中式料理',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論'+str(star.callrating('SHANNRICEBAR','googlemap','Star'))+'      Dcard平均愛心:'+str(star.callrating('WangPin','Dcard','Heart'))
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://ricebar.com.tw/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTnKx27Flsej7mxu5AmE7W62WOIOQVrvEiU8A&usqp=CAU',
                        title='非常泰',
                        text='結合美食與時潮的泰美味',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論'+str(star.callrating('VeryThai','googlemap','Star'))+'      Dcard平均愛心:'+str(star.callrating('WangPin','Dcard','Heart'))
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://www.verythai.com.tw/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://www.1010restaurant.com/assets/meta__faf040ada8bcf15af22489819827ff17.jpg',
                        title='1010湘',
                        text='新時代\'食\'尚品味',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論'+str(star.callrating('1010Hunan','googlemap','Star'))  +'      Dcard平均愛心:'+str(star.callrating('WangPin','Dcard','Heart'))
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://www.1010restaurant.com/'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmSdH6P49rl-eCjDDi2q4egy9WRNRN_aWJbg&usqp=CAU',
                        title='大心',
                        text='大大滿足大大開心',
                        actions=[
                            MessageAction(
                                label='評價查詢',
                                text='googlemap平均評論'+str(star.callrating('VeryThaiNoodles','googlemap','Star'))  +'      Dcard平均愛心:'+str(star.callrating('WangPin','Dcard','Heart'))
                             ),
                            URIAction(
                                label='查看主頁',
                                uri='https://bheartnoodles.com/'
                            )
                        ]
                    )
                    ]))
            line_bot_api.reply_message(event.reply_token, carousel_template_message)
        
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',port=5000)