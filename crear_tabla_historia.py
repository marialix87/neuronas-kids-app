import sqlite3

conn = sqlite3.connect('neuronas.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS historial_clinico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    fecha TEXT,
    descripcion TEXT,
    archivo TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
)
''')

conn.commit()
conn.close()

print("✅ Tabla 'historial_clinico' creada.")
