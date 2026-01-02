import unittest
import os
import sys

# Ajustar el path para que encuentre el módulo 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from backend.database import SchoolDB

class TestSchoolDB(unittest.TestCase):
    def setUp(self):
        # Usar una base de datos de prueba para no ensuciar la real
        self.db_name = "test_escolares.db"
        self.db = SchoolDB(self.db_name)
        
    def tearDown(self):
        # Eliminar la base de datos de prueba al finalizar
        if os.path.exists(self.db.db_path):
            try:
                os.remove(self.db.db_path)
            except PermissionError:
                pass # A veces el archivo queda tomado brevemente por el sistema

    def test_flujo_completo(self):
        """Prueba el ciclo de vida: Crear Apoderado -> Crear Alumno -> Pagar -> Verificar"""
        
        # 1. Agregar Apoderado
        self.db.agregar_apoderado("Test Apoderado", "123456", "test@mail.com")
        apoderados = self.db.obtener_apoderados()
        self.assertEqual(len(apoderados), 1)
        id_apo = apoderados[0][0]

        # 2. Agregar Alumno
        self.db.agregar_estudiante("Test Alumno", "1° Basico", id_apo)
        alumnos = self.db.obtener_estudiantes_simple()
        self.assertEqual(len(alumnos), 1)
        id_alu = alumnos[0][0]

        # 3. Registrar Pago
        self.db.registrar_pago(id_alu, 50000, "Marzo")
        
        # 4. Verificar Pago
        pagos = self.db.obtener_historial_pagos()
        self.assertEqual(len(pagos), 1)
        self.assertEqual(pagos[0][3], 50000) # Monto
        self.assertEqual(pagos[0][4], "Marzo") # Mes

        # 5. Verificar Morosidad (Si pagó Marzo, no debería salir en morosos de Marzo)
        morosos_marzo = self.db.obtener_morosos("Marzo")
        # La consulta de morosos devuelve alumnos que NO han pagado.
        # Como acabamos de pagar, la lista debe estar vacía para este alumno.
        ids_morosos = [m[0] for m in morosos_marzo]
        self.assertNotIn(id_alu, ids_morosos)

        # 6. Verificar Morosidad Abril (No pagado)
        morosos_abril = self.db.obtener_morosos("Abril")
        ids_morosos_abril = [m[0] for m in morosos_abril]
        self.assertIn(id_alu, ids_morosos_abril)

    def test_validacion_pago_duplicado(self):
        self.db.agregar_apoderado("Apo", "1", "a@a.com")
        self.db.agregar_estudiante("Alu", "1", 1)
        
        self.db.registrar_pago(1, 100, "Marzo")
        existe = self.db.verificar_pago_existente(1, "Marzo")
        self.assertTrue(existe)

if __name__ == '__main__':
    unittest.main()