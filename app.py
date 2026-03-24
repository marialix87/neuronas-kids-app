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
@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    if session['rol'] not in ['admin', 'medico']:
        flash("No tienes permiso para ver esta página.")
        return redirect(url_for('dashboard'))

    conn = get_db_connection()

    filtro = request.form.get('buscar')
    if filtro:
        pacientes = conn.execute("""
            SELECT * FROM pacientes
            WHERE
                nro_historia LIKE ? OR
                nombre LIKE ? OR
                cedula LIKE ?
        """, (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%')).fetchall()
    else:
        pacientes = conn.execute('SELECT * FROM pacientes').fetchall()

    conn.close()
    return render_template('pacientes.html', pacientes=pacientes)



@app.route('/pacientes/agregar', methods=['GET', 'POST'])
def agregar_paciente():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    if session['rol'] not in ['admin', 'medico']:
        flash("No tienes permiso para agregar pacientes.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nro_historia = request.form['nro_historia']
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        observaciones = request.form['observaciones']
        fecha_ingreso = request.form['fecha_ingreso']

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO pacientes (nro_historia, nombre, cedula, fecha_nacimiento, telefono, direccion, observaciones, fecha_ingreso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nro_historia, nombre, cedula, fecha_nacimiento, telefono, direccion, observaciones, fecha_ingreso))
            conn.commit()
            flash("Paciente registrado con éxito.")
        except sqlite3.IntegrityError:
            flash("Ya existe un paciente con ese número de historia.")
        finally:
            conn.close()

        return redirect(url_for('pacientes'))

    return render_template('agregar_paciente.html')
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/pacientes/<int:paciente_id>')
def ver_paciente(paciente_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,)).fetchone()
    historial = conn.execute('''
        SELECT * FROM historial_clinico
        WHERE paciente_id = ?
        ORDER BY fecha DESC
    ''', (paciente_id,)).fetchall()
    conn.close()

    if not paciente:
        flash("Paciente no encontrado.")
        return redirect(url_for('pacientes'))

    return render_template('ver_paciente.html', paciente=paciente, historial=historial)

@app.route('/pacientes/<int:paciente_id>/agregar_entrada', methods=['POST'])
def agregar_entrada(paciente_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    descripcion = request.form['descripcion']
    archivo = request.files['archivo']
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nombre_archivo = None

    if archivo and archivo.filename:
        nombre_archivo = secure_filename(archivo.filename)
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO historial_clinico (paciente_id, fecha, descripcion, archivo)
        VALUES (?, ?, ?, ?)
    """, (paciente_id, fecha, descripcion, nombre_archivo))
    conn.commit()
    conn.close()

    flash("Entrada médica agregada con éxito.")
    return redirect(url_for('ver_paciente', paciente_id=paciente_id))
@app.route('/debug/pacientes')
def debug_pacientes():
    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes').fetchall()
    conn.close()
    return '<br>'.join([f"{p['id']} - {p['nombre']} - {p['nro_historia']}" for p in pacientes])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
