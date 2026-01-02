import sqlite3
import os

class SchoolDB:
    def __init__(self, db_name="escolares.db"):
        # Asegurar que la DB se cree en el directorio correcto
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, "..", db_name)
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla Apoderados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apoderados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT,
                email TEXT
            )
        ''')

        # Tabla Estudiantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                grado TEXT,
                apoderado_id INTEGER,
                FOREIGN KEY (apoderado_id) REFERENCES apoderados (id)
            )
        ''')

        # Tabla Mensualidades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensualidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER,
                monto REAL,
                mes TEXT,
                pagado BOOLEAN DEFAULT 0,
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
            )
        ''')
        conn.commit()
        conn.close()

    def ejecutar_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def obtener_datos(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    # --- Métodos Específicos ---
    
    def agregar_apoderado(self, nombre, telefono, email):
        self.ejecutar_query("INSERT INTO apoderados (nombre, telefono, email) VALUES (?, ?, ?)", (nombre, telefono, email))

    def obtener_apoderados(self):
        return self.obtener_datos("SELECT id, nombre FROM apoderados")

    def agregar_estudiante(self, nombre, grado, apoderado_id):
        self.ejecutar_query("INSERT INTO estudiantes (nombre, grado, apoderado_id) VALUES (?, ?, ?)", (nombre, grado, apoderado_id))

    def eliminar_estudiante(self, estudiante_id):
        self.ejecutar_query("DELETE FROM estudiantes WHERE id = ?", (estudiante_id,))

    def obtener_estudiantes_completo(self):
        query = '''
            SELECT e.id, e.nombre, e.grado, a.nombre, a.telefono 
            FROM estudiantes e 
            LEFT JOIN apoderados a ON e.apoderado_id = a.id
        '''
        return self.obtener_datos(query)

    def registrar_pago(self, estudiante_id, monto, mes):
        self.ejecutar_query("INSERT INTO mensualidades (estudiante_id, monto, mes, pagado) VALUES (?, ?, ?, 1)", (estudiante_id, monto, mes))