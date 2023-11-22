import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
# データベースの設定
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PW'),
    'database': os.getenv('DB_NAME')
}

# データベースへの接続
conn = mysql.connector.connect(**db_config)

# カーソルの作成
cursor = conn.cursor()

# SQLクエリの実行
query = "SELECT * FROM cards" # your_tableは対象のテーブル名に置き換えてください
cursor.execute(query)

# データの取得
for row in cursor.fetchall():
    print(row)

# カーソルと接続のクローズ
cursor.close()
conn.close()
