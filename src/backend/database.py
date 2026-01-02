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

    def obtener_apoderados_completo(self):
        return self.obtener_datos("SELECT id, nombre, telefono, email FROM apoderados")

    def eliminar_apoderado(self, apoderado_id):
        self.ejecutar_query("DELETE FROM apoderados WHERE id = ?", (apoderado_id,))

    def actualizar_apoderado(self, id, nombre, telefono, email):
        self.ejecutar_query("UPDATE apoderados SET nombre=?, telefono=?, email=? WHERE id=?", (nombre, telefono, email, id))

    def verificar_dependencia_apoderado(self, apoderado_id):
        # Retorna True si el apoderado tiene estudiantes asignados
        result = self.obtener_datos("SELECT COUNT(*) FROM estudiantes WHERE apoderado_id = ?", (apoderado_id,))
        return result[0][0] > 0

    def agregar_estudiante(self, nombre, grado, apoderado_id):
        self.ejecutar_query("INSERT INTO estudiantes (nombre, grado, apoderado_id) VALUES (?, ?, ?)", (nombre, grado, apoderado_id))

    def eliminar_estudiante(self, estudiante_id):
        self.ejecutar_query("DELETE FROM estudiantes WHERE id = ?", (estudiante_id,))

    def actualizar_estudiante(self, id, nombre, grado, apoderado_id):
        self.ejecutar_query("UPDATE estudiantes SET nombre=?, grado=?, apoderado_id=? WHERE id=?", (nombre, grado, apoderado_id, id))

    def obtener_estudiante_por_id(self, id):
        return self.obtener_datos("SELECT * FROM estudiantes WHERE id = ?", (id,))

    def obtener_estudiantes_completo(self):
        query = '''
            SELECT e.id, e.nombre, e.grado, a.nombre, a.telefono 
            FROM estudiantes e 
            LEFT JOIN apoderados a ON e.apoderado_id = a.id
        '''
        return self.obtener_datos(query)

    def buscar_estudiantes(self, termino):
        query = '''
            SELECT e.id, e.nombre, e.grado, a.nombre, a.telefono 
            FROM estudiantes e 
            LEFT JOIN apoderados a ON e.apoderado_id = a.id
            WHERE e.nombre LIKE ?
        '''
        return self.obtener_datos(query, ('%' + termino + '%',))

    def registrar_pago(self, estudiante_id, monto, mes):
        self.ejecutar_query("INSERT INTO mensualidades (estudiante_id, monto, mes, pagado) VALUES (?, ?, ?, 1)", (estudiante_id, monto, mes))

    def obtener_estudiantes_simple(self):
        return self.obtener_datos("SELECT id, nombre FROM estudiantes")

    def obtener_historial_pagos(self):
        query = '''
            SELECT m.id, e.nombre, m.monto, m.mes, m.pagado 
            FROM mensualidades m
            JOIN estudiantes e ON m.estudiante_id = e.id
            ORDER BY m.id DESC
        '''
        return self.obtener_datos(query)

    def obtener_morosos(self, mes):
        query = '''
            SELECT e.id, e.nombre, e.grado, a.nombre, a.telefono 
            FROM estudiantes e 
            LEFT JOIN apoderados a ON e.apoderado_id = a.id
            WHERE e.id NOT IN (
                SELECT estudiante_id FROM mensualidades WHERE mes = ?
            )
        '''
        return self.obtener_datos(query, (mes,))

    def obtener_estudiante_detalle(self, id_estudiante):
        query = '''
            SELECT e.nombre, e.grado, a.nombre, a.telefono, a.email
            FROM estudiantes e 
            LEFT JOIN apoderados a ON e.apoderado_id = a.id
            WHERE e.id = ?
        '''
        return self.obtener_datos(query, (id_estudiante,))