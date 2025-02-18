import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import pandas as pd
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
USER_ID = os.getenv("USER_ID")  # 送信先のユーザーID（環境変数で管理）

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

PREDICTION_DIR = "prediction"
os.makedirs(PREDICTION_DIR, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)


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
    user_id = event.source.user_id

    logging.info(f"📩 受信メッセージ: {user_message}, ユーザーID: {user_id}")  # ユーザーIDをログに記録

    if user_message == "予測":
        send_saved_csv(user_id)
    else:
        reply_text = "「予測」と送ると最新のデータを取得できます！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))


def send_saved_csv(user_id):
    """
    保存されたCSVを読み込み、LINEに送信する
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "prediction", "result.csv")

    if not os.path.exists(csv_path):
        logging.warning(f"⚠️ CSV ファイルが見つかりません: {csv_path}")
        line_bot_api.push_message(user_id, TextSendMessage(text="予測データがありません。"))
        return

    # CSV を読み込んでテキストに変換
    df = pd.read_csv(csv_path)
    csv_text = df.head(10).to_string(index=False)[:4000]  # 上位10行、4000文字制限

    # LINE に送信
    line_bot_api.push_message(user_id, TextSendMessage(text=f"予測結果:\n{csv_text}"))


def send_scheduled_message():
    """
    特定の時間に LINE へメッセージを送信する（Render の Job で実行）
    """
    if not USER_ID:
        logging.error("❌ USER_ID が設定されていません！")
        return

    send_saved_csv(USER_ID)
    logging.info("✅ 定期メッセージを送信しました！")


# Flask サーバー起動 or Scheduled Job 実行
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "send_message":
        send_scheduled_message()
    else:
        app.run(host="0.0.0.0", port=5000)
