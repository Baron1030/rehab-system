from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# 建立資料庫
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
         CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            account TEXT UNIQUE,
            password TEXT,
            idNo TEXT,
            phone TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('test.html')

# 登入
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    account = data['account']
    password = data['password']
    role = data['role']

    # 醫護登入先寫死，之後再改資料庫版
    if role == 'staff':
        staff_code = data.get('staffCode', '')
        if account == 'nurse' and password == '1234' and staff_code == 'CARE2026':
            return jsonify({"status": "success", "role": "staff"})
        return jsonify({"status": "fail", "message": "醫護帳號、密碼或驗證碼錯誤"})

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name, account, idNo, phone, status FROM users WHERE account=? AND password=?",
              (account, password))
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({"status": "fail", "message": "使用者帳號或密碼錯誤"})

    if user[4] == "pending":
        return jsonify({"status": "fail", "message": "帳號尚未啟用，請等待醫護端審核"})

    if user[4] == "disabled":
        return jsonify({"status": "fail", "message": "帳號已停用，請聯絡醫護人員"})

    return jsonify({
        "status": "success",
        "role": "user",
        "user": {
            "name": user[0],
            "account": user[1],
            "idNo": user[2],
            "phone": user[3],
            "status": user[4]
        }
    })

# 註冊（使用者啟用帳號）
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data['name']
    account = data['account']
    idNo = data['idNo']
    phone = data['phone']
    password = data['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE account=? OR idNo=? OR phone=?",
              (account, idNo, phone))
    duplicate = c.fetchone()

    if duplicate:
        conn.close()
        return jsonify({"status": "fail", "message": "帳號、身分證字號或手機號碼已存在"})

    c.execute("""
        INSERT INTO users (name, account, password, idNo, phone, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, account, password, idNo, phone, "pending"))

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "註冊成功，請等待醫護端啟用"})

# 醫護新增病人
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name, account, idNo, phone, status FROM users")
    users = c.fetchall()
    conn.close()

    result = []
    for u in users:
        result.append({
            "name": u[0],
            "account": u[1],
            "idNo": u[2],
            "phone": u[3],
            "status": u[4]
        })
    return jsonify(result)


@app.route('/api/activate_user', methods=['POST'])
def activate_user():
    data = request.json
    account = data['account']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET status='active' WHERE account=?", (account,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


@app.route('/api/disable_user', methods=['POST'])
def disable_user():
    data = request.json
    account = data['account']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET status='disabled' WHERE account=?", (account,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


@app.route('/api/delete_user', methods=['POST'])
def delete_user():
    data = request.json
    account = data['account']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE account=?", (account,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


@app.route('/api/search_user', methods=['POST'])
def search_user():
    data = request.json
    keyword = data['keyword']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT name, account, idNo, phone, status
        FROM users
        WHERE account=? OR idNo=? OR phone=?
    """, (keyword, keyword, keyword))
    u = c.fetchone()
    conn.close()

    if not u:
        return jsonify({"status": "fail", "message": "查無資料"})

    return jsonify({
        "status": "success",
        "user": {
            "name": u[0],
            "account": u[1],
            "idNo": u[2],
            "phone": u[3],
            "status": u[4]
        }
    })

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
