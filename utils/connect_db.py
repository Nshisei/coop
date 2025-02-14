import mysql.connector
from mysql.connector import Error
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
abs_dirpath = os.path.dirname(os.path.abspath(__file__))  # 絶対パスを取得
sql_dir = os.path.join(abs_dirpath, 'sqls')

def exec_sql_cmd(path_to_sql, replace_dict={}):
    """
    output: dict(output_type: result)
    output_type: 成功したかどうか, success / error 
    result: successならlist(tupple), errorならエラーメッセージ(str)
    """
    result = {"result":None, "output": None}
    try:
        with mysql.connector.connect(autocommit=True, **db_config) as conn:
            with conn.cursor(dictionary=True) as cur:
                with open(path_to_sql, 'r') as f:
                    sql = f.read()
                    for key, val in replace_dict.items():
                        sql = sql.replace(key, val)
                    cur.execute(sql)
                rows = cur.fetchall()
        result["result"] = "success"
        result["output"] = rows
        return result
    except Error as err:
        result["result"] = "error"
        result["output"] = err
        return result

def get_items(barcode_data):
    """取得したバーコードのid, name, priceを取得
    barcodeがDBに登録済み
        → id, name, price を返す
    barcodeが未登録
        → 空の配列を返す
    barcodeに登録された商品が複数
        → error
    """
    sql_path = os.path.join(sql_dir, 'get_items.sql')
    result = exec_sql_cmd(sql_path, replace_dict={'BARCODE': str(barcode_data)})
    if result["result"] == "success":
        # DBに問い合わせが成功
        if len(result["output"]) == 0:
            # barcodeがDBに登録されていなければbarcodeを返す
            return barcode_data
        else:
            # 登録されていればその結果を返す
            return result["output"][0]
    else:
        # エラーが出たら出力
        print('error')

def get_user(nfc_id):
    """取得したユーザーのid, name, nfc_id, grade, balanceを取得
    userがDBに登録済み
        → id, name, nfc_id, grade, balance を返す
    usereが未登録
        → 
    barcodeに登録された商品が複数
        → error
    """
    sql_path = os.path.join(sql_dir, 'get_user.sql')
    result = exec_sql_cmd(sql_path, replace_dict={'NFC_ID': str(nfc_id)})
    if result["result"] == "success":
        # DBに問い合わせが成功
        if len(result["output"]) == 0:
            # barcodeがDBに登録されていなければbarcodeを返す
            return nfc_id 
        else:
            # 登録されていればその結果を返す
            return result["output"][0]
    else:
        # エラーが出たら出力
        print('error')

def insert_order(data):
    """user_idと購入した商品をもとに購入記録を追記、在庫数を更新
    """
    user_id = data['user_id']
    item_ids = data['item_id']
    prices = data['price']
    print(item_ids, prices)
    sql_path = os.path.join(sql_dir, 'insert_order.sql')
    sql_path2 = os.path.join(sql_dir, 'update_stock_num.sql')
    for item_id, price in zip(item_ids, prices):
        replace_ditc = {
            'USER_ID': str(user_id),
            'ITEM_ID': str(item_id),
            'ITEM_PRICE': str(price),
        }
        result = exec_sql_cmd(sql_path, replace_dict=replace_ditc)
        result += exec_sql_cmd(sql_path2, replace_dict=replace_ditc)
    print("inter_order")
    print(result)

def update_balance(data):
    """user_idと購入合計金額をもとに収支を更新
    """
    user_id = data['user_id']
    total = data['total']
    sql_path = os.path.join(sql_dir, 'update_balance.sql')
    replace_ditc = {
        'TOTAL': str(total),
        'USER_ID': str(user_id),
    }
    result = exec_sql_cmd(sql_path, replace_dict=replace_ditc)
    print("update_balance")
    print(result)


def new_user_or_update_user(data):
    """取得したバーコードのid, name, priceを取得
    barcodeがDBに登録済み
        → id, name, price を返す
    barcodeが未登録
        → 空の配列を返す
    barcodeに登録された商品が複数
        → error
    """
    nfc_id = data["nfcId"]
    name = data["userName"]
    year = data["userYear"]
    balance = data["balance"]
    charge = data["charge"]
    replace_ditc = {
        'NFC_ID': str(nfc_id),
        'NAME': str(name),
        'GRADE': str(year),
        'CHARGE': str(charge),
    }
    if isinstance(get_user(nfc_id), tuple):
        # 既に商品が存在する
        sql_path = os.path.join(sql_dir, 'update_user.sql')
        result = exec_sql_cmd(sql_path, replace_dict=replace_ditc)
    else:
        sql_path = os.path.join(sql_dir, 'insert_new_user.sql')
        result = exec_sql_cmd(sql_path, replace_dict=replace_ditc)
    return result

def new_items_or_update_items(data):
    """取得したバーコードのid, name, priceを取得
    barcodeがDBに登録済み
        → id, name, price を返す
    barcodeが未登録
        → 空の配列を返す
    barcodeに登録された商品が複数
        → error
    """
    barcode = data['barcode']
    productName = data['productName']
    productPrice = data['productPrice']
    stockQuantity = data['stockQuantity']
    stockAdd = data['stockAdd']
    productCategory = data['productCategory']
    replace_ditc = {
        'NAME': str(productName),
        'ADD_NUM': str(stockAdd),
        'BARCODE': str(barcode),
        'PRICE': str(productPrice),
        'CLASS': str(productCategory),
    }
    if isinstance(get_items(barcode), tuple):
        # 既に商品が存在する
        sql_path = os.path.join(sql_dir, 'update_item.sql')
        result = exec_sql_cmd(sql_path, replace_dict=replace_ditc)
    else:
        sql_path = os.path.join(sql_dir, 'insert_new_item.sql')
        result = exec_sql_cmd(sql_path, replace_dict=replace_ditc)
    return result
    
