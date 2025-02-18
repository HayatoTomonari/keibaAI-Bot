import logging
import os
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
USER_ID = os.getenv("USER_ID")  # 送信先のユーザーID（環境変数で管理）

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

PREDICTION_DIR = "prediction"
os.makedirs(PREDICTION_DIR, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)

def send_scheduled_message():
    """
    Job で実行され、LINE に `result.csv` の内容を送信する。
    """

    print("Current Working Directory:", os.getcwd())

    if not USER_ID or not USER_ID.startswith("U"):
        logging.error(f"❌ USER_ID が無効です: {USER_ID}")
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "prediction", "result.csv")

    logging.info(f"📂 CSV ファイルの検索パス: {csv_path}")  # ✅ 確認用ログ

    if not os.path.exists(csv_path):
        logging.warning(f"⚠️ CSV ファイルが見つかりません: {csv_path}")
        line_bot_api.push_message(USER_ID, TextSendMessage(text="予測データがありません。"))
        return

    logging.info(f"✅ CSV ファイルが見つかりました: {csv_path}")  # ✅ ログで確認

    df = pd.read_csv(csv_path)
    csv_text = df.head(10).to_string(index=False)[:4000]  # 文字数制限対応

    # LINE に送信
    line_bot_api.push_message(USER_ID, TextSendMessage(text=f"📊 予測結果:\n{csv_text}"))

from flask import Flask

app = Flask(__name__)

PORT = int(os.getenv("PORT", 5000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
