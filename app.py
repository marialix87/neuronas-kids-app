from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'neuronas123'
DB_PATH = os.path.join(os.path.dirname(__file__), 'neuronas.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    clave = request.form['clave']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE usuario = ? AND clave = ?', (usuario, clave)).fetchone()
    conn.close()
    if user:
        session['usuario'] = user['usuario']
        session['rol'] = user['rol']
        return redirect(url_for('dashboard'))
    flash('Usuario o clave incorrectos')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', usuario=session['usuario'], rol=session['rol'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
