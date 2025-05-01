import os
import json
import requests
from io import StringIO
import pandas as pd
import datetime
from time import sleep
from flask import Flask, request
from dotenv import load_dotenv
from linebot.v3 import WebhookHandler
from linebot import LineBotApi
from linebot.models import TextSendMessage, LocationSendMessage

load_dotenv("detail.env")
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
webhook_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 狀態儲存字典
user_states = {}

# 更新 stock.txt 檔案
def fix_file(stock_code, start_date, end_date):
    with open('stock.txt', "w") as f:
        f.write(f"{stock_code},{start_date},{end_date}")

def get_setting():
    try:
        with open('stock.txt') as f:
            a, b, c = f.readline().split(',')
            return [a, b, c]
    except Exception as e:
        print(f"stock.txt 讀取錯誤: {e}")
        return []

def get_data():
    data = get_setting()
    dates = []
    start_date = datetime.datetime.strptime(data[1], '%Y%m%d')
    end_date = datetime.datetime.strptime(data[2], '%Y%m%d')
    for day in range((end_date - start_date).days + 1):
        date = (start_date + datetime.timedelta(days=day))
        if date.weekday() < 5:  # 只要週一到週五
            dates.append(date.strftime('%Y%m%d'))
    return data[0], dates

def crawl_data(date, symbol):
    r = requests.get(f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={date}&type=ALL')
    if r.status_code != 200:
        return [], []

    r_text = [i for i in r.text.split('\n') if len(i.split('",')) == 17 and i[0] != '=']
    if not r_text:
        return [], []

    try:
        df = pd.read_csv(StringIO("\n".join(r_text)))
        df = df.drop(columns=['Unnamed: 16'])
        filtered = df[df["證券代號"] == symbol]
        if filtered.empty:
            return [], []
        filtered.insert(0, "日期", date)
        return list(filtered.iloc[0]), filtered.columns
    except Exception as e:
        print(f"資料處理錯誤: {e}")
        return [], []

# LINE Bot 入口點
@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    json_data = json.loads(body)
    webhook_handler.handle(body, signature)

    event = json_data['events'][0]
    reply_token = event['replyToken']
    user_id = event['source']['userId']
    message = event['message']['text']

    state = user_states.get(user_id, {"stage": None})

    if message == "股票資訊":
        user_states[user_id] = {"stage": "awaiting_code"}
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入股票代碼（如 2330）："))

    elif state["stage"] == "awaiting_code" and message.isdigit():
        user_states[user_id]["stock_code"] = message
        user_states[user_id]["stage"] = "awaiting_start"
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入開始日期 (YYYYMMDD)："))

    elif state["stage"] == "awaiting_start" and message.isdigit() and len(message) == 8:
        user_states[user_id]["start_date"] = message
        user_states[user_id]["stage"] = "awaiting_end"
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入結束日期 (YYYYMMDD)："))

    elif state["stage"] == "awaiting_end" and message.isdigit() and len(message) == 8:
        user_states[user_id]["end_date"] = message
        stock_code = state["stock_code"]
        start_date = state["start_date"]
        end_date = message
        fix_file(stock_code, start_date, end_date)

        stock_symbol, dates = get_data()
        all_list = []
        df_columns = []

        for date in dates:
            sleep(1)
            row, columns = crawl_data(date, stock_symbol)
            if row:
                all_list.append(row)
                df_columns = columns

        if not all_list:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="找不到相關資料，請檢查代碼或日期"))
        else:
            df = pd.DataFrame(all_list, columns=df_columns)
            info = f"查詢 {stock_symbol} 結果如下：\n\n{df.to_string(index=False)}"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=info))

        # 清除使用者狀態
        user_states.pop(user_id)

    elif message == "101":
        location_message = LocationSendMessage(
            title='台北 101',
            address='110台北市信義區信義路五段7號',
            latitude='25.034095712145003',
            longitude='121.56489941996108'
        )
        line_bot_api.reply_message(reply_token, location_message)

    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入有效的指令或開始輸入『股票資訊』"))

    return 'OK'

if __name__ == "__main__":
    app.run(port=5000)
