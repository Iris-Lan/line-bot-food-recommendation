from email.policy import default
import json
from pprint import pprint
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, LocationSendMessage, LocationMessage
import google_map_method as googleMethods
import re
import random


with open('keys_path') as f:
    data = json.load(f)

app = Flask(__name__)

line_bot_api = LineBotApi(data['accessToken'])
handler = WebhookHandler(data['channelSecret'])

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
    message = event.message.text
    pattern_correct = "(?i).*(中午|午餐|lunch|昼ご飯|昼ごはん|ひるごはん).*"
    pattern_wrong = "(?i).*(晚餐|dinner|晩御飯|晩ご飯|晩ごはん|ばんごはん).*"
    pattern_address = "(.*(市|縣|TAIPEI).*(區|路|街)?.*)"
    pattern_station = "(.*站.*)"
    pattern_anything = ".+"
    # user asks for recommendation
    if re.match(pattern_correct, message):
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="問我吃的就對了ˇuˇ \n\rPlease enter city and district or send your location to randomly get one of the Top5 restaurants nearby! \n輸入縣市區或傳送位置，讓我隨機幫你挑一家附近的Top5美食啦!:p")
        )
    # user asks for dinner!??
    elif re.match(pattern_wrong, message):
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="Dinner? lol     LUNCH! \n晚餐?? 阿午餐勒@@")
        )
    # user gives address
    elif re.match(pattern_address, message) or re.match(pattern_station, message) or re.match(pattern_anything, message):
        lat, lng = googleMethods.get_latitude_longtitude(address=message)
        # a radius distance around the given address. Unit is meter. 
        radius = 2500
        # what kind of store does user want to find 
        # restaurant = ['restaurant', 'food']
        restaurant = ['restaurant']
        # get the Top5 restaurant details
        results = googleMethods.get_Top5(lat, lng, radius, restaurant)
        # random get one or return no result
        if len(results) == 0:
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(text="沒找到QQ No Found.... :(\nTry the next address!")
            )
        else:
            pick_one = random.randint(0, len(results) - 1)
            location_message = LocationSendMessage(
                title = results[pick_one]['name'],
                address = results[pick_one]['vicinity'],
                latitude = results[pick_one]['geometry']['location']['lat'],
                longitude = results[pick_one]['geometry']['location']['lng']
            )
            line_bot_api.reply_message(
                event.reply_token, 
                location_message
            )
    # user types wrong content
    else:
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="要打對餒:p \n\r輸入縣市區或傳送位置，讓我隨機幫你挑一家附近的Top5美食啦! \nPlease enter city and district or send your location to randomly get one of the Top5 restaurants nearby!")
        )

@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    title = event.message.title
    address = event.message.address
    latitude = event.message.latitude
    longitude = event.message.longitude

    # a radius distance around the given address. Unit is meter. 
    radius = 2500
    # what kind of store does user want to find 
    # restaurant = ['restaurant', 'food']
    restaurant = ['restaurant']
    # get the Top5 restaurant details
    results = googleMethods.get_Top5(latitude, longitude, radius, restaurant)
    # random get one or return no result
    if len(results) == 0:
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="沒找到QQ No Found.... :(\nTry the next address!")
        )
    else:
        pick_one = random.randint(0, len(results) - 1)
        location_message = LocationSendMessage(
            title = results[pick_one]['name'],
            address = results[pick_one]['vicinity'],
            latitude = results[pick_one]['geometry']['location']['lat'],
            longitude = results[pick_one]['geometry']['location']['lng']
        )
        line_bot_api.reply_message(
            event.reply_token, 
            location_message
        )


if __name__ == "__main__":
    app.run()