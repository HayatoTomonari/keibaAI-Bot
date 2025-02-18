from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
import os
import logging
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

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
    user_id = event.source.user_id  # ✅ ユーザー ID を取得
    logging.info(f"✅ 受信ユーザー ID: {user_id}")  # ✅ ログに記録（Render の Logs で確認）

    line_bot_api.reply_message(
        event.reply_token, TextMessage(text="✅ USER_ID を記録しました！")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
