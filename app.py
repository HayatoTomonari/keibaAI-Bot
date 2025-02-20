import os
from flask import Flask
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# Flaskサーバー起動
app = Flask(__name__)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))