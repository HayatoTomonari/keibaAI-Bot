from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

# Webhook エンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# メッセージを受け取ったときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.lower()

    if user_message == "予測":
        # LINE に送信
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="テストでござんす"))

    else:
        reply_text = "「予測」と送ると最新のデータを取得できます！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

# サーバー起動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
