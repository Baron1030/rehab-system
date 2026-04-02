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
            username TEXT,
            password TEXT,
            role TEXT,
            active INTEGER
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
    username = data['username']
    password = data['password']
    role = data['role']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=? AND active=1",
              (username, password, role))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"})

# 註冊（使用者啟用帳號）
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password=?, active=1 WHERE username=?",
              (password, username))
    conn.commit()
    conn.close()

    return jsonify({"status": "registered"})

# 醫護新增病人
@app.route('/api/add_patient', methods=['POST'])
def add_patient():
    data = request.json
    username = data['username']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role, active) VALUES (?, '', 'user', 0)",
              (username,))
    conn.commit()
    conn.close()

    return jsonify({"status": "added"})

app.run(debug=True)
