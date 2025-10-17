from flask import Flask, request, jsonify, render_template
import mysql.connector
import re

app = Flask(__name__)

import pymysql
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "car",
    "cursorclass": pymysql.cursors.DictCursor  # <-- यह important है dictionary result के लिए
}

def normalize_plate(s):
    if not s:
        return ''
    s = s.strip().upper()
    # remove spaces and non-alphanum
    s = re.sub(r'[^A-Z0-9]', '', s)
    # optionally convert words like 'ZERO' -> '0' if speech engine gives words (rare)
    word_to_digit = {
        'ZERO':'0','ONE':'1','TWO':'2','THREE':'3','FOUR':'4','FIVE':'5',
        'SIX':'6','SEVEN':'7','EIGHT':'8','NINE':'9'
    }
    # replace words
    for w,d in word_to_digit.items():
        s = s.replace(w,d)
    return s

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/check_car', methods=['POST'])
def check_car():
    data = request.get_json() or {}
    raw = data.get('car_number', '').strip()
    car = normalize_plate(raw)
    print(car)

    if not car:
        return jsonify({"message":"Mujhe car number samajh nahi aaya, kripya dubara batayein."}), 200

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # SQL Query
        sql = """
        SELECT car_num
        FROM car_num
        WHERE REPLACE(UPPER(car_num), ' ', '') = %s
        LIMIT 1;
        """

        # Execute and fetch
        cursor.execute(sql, (car,))
        res = cursor.fetchone()

        # Close connections
        cursor.close()
        conn.close()

        if res:
            msg = f"Yes, your car with registration number {res['car_num']} has been towed by us. You can come and collect it between 10 a.m. to 5 p.m. tomorrow."
            return jsonify({"message": msg, "found": True})
        else:
            msg=f"We’re sorry, but your car number {res['car_num']} could not be found in our records."
            return jsonify({"message":msg,"found": False})

    except Exception as e:
        print("DB error:", e)
        return jsonify({"message":"We are experiencing some technical difficulties. Please try again after some time."}), 500

if __name__ == '__main__':
    app.run()
