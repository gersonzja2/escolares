import sqlite3
import os
from datetime import datetime

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
                email TEXT,
                fecha_registro TEXT
            )
        ''')

        # Tabla Estudiantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                grado TEXT,
                apoderado_id INTEGER,
                fecha_registro TEXT,
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
                fecha_pago TEXT,
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
            )
        ''')

        # Tabla Configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')
        conn.commit()
        
        # Migraciones: Agregar columnas a tablas existentes si no existen
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE apoderados ADD COLUMN fecha_registro TEXT")
        except sqlite3.OperationalError: pass
        try:
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN fecha_registro TEXT")
        except sqlite3.OperationalError: pass
        try:
            cursor.execute("ALTER TABLE mensualidades ADD COLUMN fecha_pago TEXT")
        except sqlite3.OperationalError: pass
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
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ejecutar_query("INSERT INTO apoderados (nombre, telefono, email, fecha_registro) VALUES (?, ?, ?, ?)", (nombre, telefono, email, fecha))

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
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ejecutar_query("INSERT INTO estudiantes (nombre, grado, apoderado_id, fecha_registro) VALUES (?, ?, ?, ?)", (nombre, grado, apoderado_id, fecha))

    def eliminar_estudiante(self, estudiante_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mensualidades WHERE estudiante_id = ?", (estudiante_id,))
        cursor.execute("DELETE FROM estudiantes WHERE id = ?", (estudiante_id,))
        conn.commit()
        conn.close()

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
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ejecutar_query("INSERT INTO mensualidades (estudiante_id, monto, mes, pagado, fecha_pago) VALUES (?, ?, ?, 1, ?)", (estudiante_id, monto, mes, fecha))

    def eliminar_pago(self, id_pago):
        self.ejecutar_query("DELETE FROM mensualidades WHERE id = ?", (id_pago,))

    def actualizar_pago(self, id_pago, monto, mes):
        self.ejecutar_query("UPDATE mensualidades SET monto=?, mes=? WHERE id=?", (monto, mes, id_pago))

    def obtener_estudiantes_simple(self):
        return self.obtener_datos("SELECT id, nombre FROM estudiantes")

    def obtener_historial_pagos(self):
        query = '''
            SELECT m.id, e.nombre, m.monto, m.mes, m.pagado, m.fecha_pago 
            FROM mensualidades m
            JOIN estudiantes e ON m.estudiante_id = e.id
            ORDER BY m.id DESC
        '''
        return self.obtener_datos(query)

    def buscar_pagos(self, termino):
        query = '''
            SELECT m.id, e.nombre, m.monto, m.mes, m.pagado, m.fecha_pago 
            FROM mensualidades m
            JOIN estudiantes e ON m.estudiante_id = e.id
            WHERE e.nombre LIKE ?
            ORDER BY m.id DESC
        '''
        return self.obtener_datos(query, ('%' + termino + '%',))

    def verificar_pago_existente(self, estudiante_id, mes):
        query = "SELECT COUNT(*) FROM mensualidades WHERE estudiante_id = ? AND mes = ?"
        result = self.obtener_datos(query, (estudiante_id, mes))
        return result[0][0] > 0

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

    def obtener_pagos_todos(self):
        return self.obtener_datos("SELECT estudiante_id, mes FROM mensualidades")

    def obtener_estudiante_detalle(self, id_estudiante):
        query = '''
            SELECT e.nombre, e.grado, a.nombre, a.telefono, a.email
            FROM estudiantes e 
            LEFT JOIN apoderados a ON e.apoderado_id = a.id
            WHERE e.id = ?
        '''
        return self.obtener_datos(query, (id_estudiante,))

    def obtener_configuracion(self, clave):
        res = self.obtener_datos("SELECT valor FROM configuracion WHERE clave = ?", (clave,))
        return res[0][0] if res else None

    def guardar_configuracion(self, clave, valor):
        self.ejecutar_query("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, valor))

    def obtener_estadisticas_dashboard(self, mes_actual):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM estudiantes")
        total_alumnos = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(monto) FROM mensualidades WHERE mes = ?", (mes_actual,))
        ingresos = cursor.fetchone()[0]
        conn.close()
        
        return total_alumnos, (ingresos if ingresos else 0.0)