from flask import Flask, request, jsonify, render_template
import sqlite3
import re
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

# 🔹 Create DB if not exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS car_num (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_num TEXT UNIQUE
        );
    """)
    conn.commit()
    conn.close()

init_db()

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO car_num (car_num) VALUES ('GJ02AB1234')")
    c.execute("INSERT OR IGNORE INTO car_num (car_num) VALUES ('GJ01AB1234')")
    c.execute("INSERT OR IGNORE INTO car_num (car_num) VALUES ('MH14XY9876')")
    conn.commit()
    conn.close()

seed_data()

# 🔹 Normalizing car number function
def normalize_plate(s):
    if not s:
        return ''
    s = s.strip().upper()
    s = re.sub(r'[^A-Z0-9]', '', s)
    word_to_digit = {
        'ZERO': '0', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4',
        'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9'
    }
    for w, d in word_to_digit.items():
        s = s.replace(w, d)
    return s


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_car', methods=['POST'])
def check_car():
    data = request.get_json() or {}
    raw = data.get('car_number', '').strip()
    car = normalize_plate(raw)
    print("Car searched:", car)

    if not car:
        return jsonify({"message": "Mujhe car number samajh nahi aaya, kripya dubara batayein."}), 200

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = """
            SELECT car_num FROM car_num
            WHERE REPLACE(UPPER(car_num), ' ', '') = ?
            LIMIT 1;
        """
        cursor.execute(sql, (car,))
        res = cursor.fetchone()

        cursor.close()
        conn.close()

        if res:
            msg = f"Yes, your car with registration number {res['car_num']} has been towed by us. You can come and collect it between 10 a.m. to 5 p.m. tomorrow."
            return jsonify({"message": msg, "found": True})
        else:
            msg = f"We’re sorry, but your car number could not be found in our records."
            return jsonify({"message": msg, "found": False})

    except Exception as e:
        print("DB error:", e)
        return jsonify({"message": "We are experiencing some technical difficulties. Please try again after some time."}), 500


if __name__ == '__main__':
     app.run(debug=True, use_reloader=False)
