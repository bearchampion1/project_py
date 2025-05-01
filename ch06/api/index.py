from flask import Flask, request
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 載入 json 標準函式庫，處理回傳的資料格式
import json
import os
# 載入 LINE Message API 相關函式庫
from linebot.v3 import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service



options = Options()
options.add_argument('--headless')  # 如果你需要無頭模式（可選）
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
service = Service('./chromedriver-win64/chromedriver.exe')
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://www.twse.com.tw/zh/listed/profile/company.html")

wait = WebDriverWait(browser, 10)
#input_tag = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "input")))
load_dotenv("detail.env")
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))#自動抓取(load_dotenv已設置完成)
webhook_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
        
@app.route("/callback", methods=['POST'])#@app.route("網址最後內容",methods=['POST'])
def linebot():
    body = request.get_data(as_text=True) 
    
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        access_token = 'YsYMRBHXws+LOIDe1EmNizRNyjA9Y0Rz/+DLKs0XXL5j3rbKyzPou56BHYB6p97c2bCb5Wp4gYTYCqOOEeProv54/e6RBczMXm62qKoA+ErewGWsQZuXMPjVTkWuEJ5YZfnBzBwjiHPmzTOVAG2EIgdB04t89/1O/w1cDnyilFU='
        secret = '5fcd4f4e01583c44f9bad74a835b3aed'
        line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
        webhook_handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        webhook_handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型
        if type=='text':
            msg = json_data['events'][0]['message']['text']# 取得 LINE 收到的文字訊息
            #text = reply_msg(msg)
            #line_bot_api.reply_message(tk, TextSendMessage(text=text))
            #print(text)
            if msg == '101':
            # 如果有地點資訊，回傳地點
                location_message = LocationSendMessage(title='台北 101',
                                                    address='110台北市信義區信義路五段7號',
                                                    latitude='25.034095712145003',
                                                    longitude='121.56489941996108')
                line_bot_api.reply_message(tk,location_message)
            elif msg == '股票資訊':
                line_bot_api.reply_message(tk, TextSendMessage(text="請輸入股票代碼，例如：2330"))

            # 處理股票代碼輸入（第二階段：回傳資料）
            elif msg.isdigit() and len(msg) in [4, 5]:
                try:
        # 打開 selenium 頁面並輸入股票代碼
                    browser.get("https://www.twse.com.tw/zh/listed/profile/company.html")
                    input_tag = browser.find_element("tag name", "input")  # 這裡用新版 selenium 語法
                    try:
                        input_tag = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "input")))
                        print("找到欄位：", input_tag.get_attribute('outerHTML'))
                        input_tag.clear()
                        input_tag.send_keys("2330")
                    except Exception as e:
                        print("發生錯誤：", e)
                    input_tag.clear()
                    input_tag.send_keys(msg)
                                        # TODO：根據網站結構抓取資料（這裡先模擬）
                    stock_info = f"你查詢的股票代碼是：{msg}（這裡是模擬資料）"
                    line_bot_api.reply_message(tk, TextSendMessage(text=stock_info))
                except Exception as e:
                    line_bot_api.reply_message(tk, TextSendMessage(text=f"查詢錯誤：{str(e)}"))
        elif type =='sticker':
            stickerId = json_data['events'][0]['message']['stickerId'] # 取得 stickerId
            packageId = json_data['events'][0]['message']['packageId'] # 取得 packageId
            # 使用 StickerSendMessage 方法回傳同樣的表情貼圖
            line_bot_api.reply_message(tk,StickerSendMessage(sticker_id=stickerId, package_id=packageId))
        else:
            reply = 'error'
        print(reply)
    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略

