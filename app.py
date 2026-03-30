Railwayimport sqlite3
import uuid
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
ADMIN_PASSWORD = 'admin123'

def get_db()
    conn = sqlite3.connect('cards.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db()
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS cards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        card_code TEXT UNIQUE,
                        is_active INTEGER DEFAULT 0,
                        bind_machine TEXT,
                        expire_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()
    conn.close()

init_db()

def generate_card()
    return str(uuid.uuid4()).replace('-', '')[16]

@app.route('')
def index()
    if 'logged_in' in session
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('login', methods=['GET', 'POST'])
def login()
    if request.method == 'POST'
        if request.form.get('password') == ADMIN_PASSWORD
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else
            return render_template('login.html', error='密码错误')
    return render_template('login.html')

@app.route('logout')
def logout()
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('admin')
def admin()
    if 'logged_in' not in session
        return redirect(url_for('login'))
    conn = get_db()
    cards = conn.execute('SELECT  FROM cards ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', cards=cards)

@app.route('generate', methods=['POST'])
def generate()
    if 'logged_in' not in session
        return redirect(url_for('login'))
    card_code = generate_card()
    conn = get_db()
    conn.execute('INSERT INTO cards (card_code, is_active) VALUES (, 0)', (card_code,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('toggleintcard_id')
def toggle_card(card_id)
    if 'logged_in' not in session
        return redirect(url_for('login'))
    conn = get_db()
    card = conn.execute('SELECT is_active FROM cards WHERE id=', (card_id,)).fetchone()
    if card
        new_status = 0 if card['is_active'] else 1
        conn.execute('UPDATE cards SET is_active= WHERE id=', (new_status, card_id))
        conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('deleteintcard_id')
def delete_card(card_id)
    if 'logged_in' not in session
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM cards WHERE id=', (card_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('verify', methods=['POST'])
def verify()
    data = request.get_json()
    if not data
        return jsonify({'code' 1, 'msg' '请求格式错误'})
    card_code = data.get('card_code')
    machine_id = data.get('machine_id')
    if not card_code
        return jsonify({'code' 1, 'msg' '卡密不能为空'})
    conn = get_db()
    row = conn.execute('SELECT is_active, bind_machine, expire_date FROM cards WHERE card_code=', (card_code,)).fetchone()
    conn.close()
    if not row
        return jsonify({'code' 2, 'msg' '卡密不存在'})
    is_active, bind_machine, expire_date = row
    if expire_date
        if datetime.now()  datetime.strptime(expire_date, '%Y-%m-%d')
            return jsonify({'code' 3, 'msg' '卡密已过期'})
    if is_active
        if bind_machine and bind_machine != machine_id
            return jsonify({'code' 4, 'msg' '卡密已被其他设备绑定'})
        return jsonify({'code' 0, 'msg' '验证成功'})
    else
        conn = get_db()
        conn.execute('UPDATE cards SET is_active=1, bind_machine= WHERE card_code=', (machine_id, card_code))
        conn.commit()
        conn.close()
        return jsonify({'code' 0, 'msg' '激活成功'})

if __name__ == '__main__'
    app.run(host='0.0.0.0', port=5000)