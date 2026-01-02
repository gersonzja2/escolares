import unittest
import os
import sys

# Asegurar que podemos importar los módulos de src
# Esto agrega la carpeta 'src' al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SchoolDB

class TestSchoolDB(unittest.TestCase):
    def setUp(self):
        """Se ejecuta antes de cada prueba: Crea una DB temporal."""
        self.db_name = "test_escolares.db"
        # Inicializamos la DB. Al ser test, se creará en la estructura definida en database.py
        self.db = SchoolDB(self.db_name)
        
        # Limpiamos tablas para empezar desde cero
        self.db.eliminar_todos_estudiantes()
        self.db.eliminar_todos_apoderados()
        self.db.eliminar_todos_pagos()

    def tearDown(self):
        """Se ejecuta después de cada prueba: Borra la DB temporal."""
        if os.path.exists(self.db.db_path):
            try:
                # Cerramos conexión forzosamente si quedó abierta (aunque SchoolDB cierra en cada query)
                os.remove(self.db.db_path)
            except PermissionError:
                pass # Windows a veces retiene el archivo unos milisegundos

    def test_flujo_apoderado(self):
        """Prueba crear, leer y actualizar un apoderado."""
        # 1. Crear
        self.db.agregar_apoderado("Juan Perez", "+56912345678", "juan@test.com")
        apoderados = self.db.obtener_apoderados_completo()
        self.assertEqual(len(apoderados), 1)
        self.assertEqual(apoderados[0][1], "Juan Perez")
        
        # 2. Actualizar
        id_apo = apoderados[0][0]
        self.db.actualizar_apoderado(id_apo, "Juan P.", "+56911111111", "juan@test.com")
        apoderados_upd = self.db.obtener_apoderados_completo()
        self.assertEqual(apoderados_upd[0][1], "Juan P.")

    def test_flujo_estudiante_y_pagos(self):
        """Prueba inscribir alumno y registrar pagos."""
        # Setup: Crear apoderado
        self.db.agregar_apoderado("Maria Lopez", "+56987654321", "maria@test.com")
        id_apo = self.db.obtener_apoderados()[0][0]

        # 1. Inscribir Alumno
        self.db.agregar_estudiante("Pedrito", "1ro Basico", id_apo)
        estudiantes = self.db.obtener_estudiantes_completo()
        self.assertEqual(len(estudiantes), 1)
        self.assertEqual(estudiantes[0][1], "Pedrito")
        
        id_alu = estudiantes[0][0]

        # 2. Registrar Pago
        self.db.registrar_pago(id_alu, 50000, "Marzo")
        pagos = self.db.obtener_pagos_alumno(id_alu)
        
        self.assertEqual(len(pagos), 1)
        self.assertEqual(pagos[0][0], "Marzo")
        self.assertEqual(pagos[0][1], 50000.0)

    def test_validacion_duplicados(self):
        """Verifica que detecte alumnos duplicados."""
        self.db.agregar_apoderado("Apo Test", "+1", "a@a.com")
        id_apo = self.db.obtener_apoderados()[0][0]
        
        self.db.agregar_estudiante("Duplicado", "1A", id_apo)
        
        self.assertTrue(self.db.verificar_estudiante_existente("Duplicado", "1A"))
        self.assertFalse(self.db.verificar_estudiante_existente("Otro", "1A"))

if __name__ == '__main__':
    unittest.main()