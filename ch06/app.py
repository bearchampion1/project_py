import stock_crawler_plot
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv
import all_function
import os

load_dotenv("detail.env")#要加上檔名在load_dotenv("這邊加")

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))#自動抓取(load_dotenv已設置完成)
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback")
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    all_function.linebot(user_text)
   
    reply_text = f"你說了：{user_text}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
if __name__ == "__main__":
    app.run()