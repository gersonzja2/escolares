import random
from datetime import datetime
from backend.database import SchoolDB

# Listas de datos ficticios
NOMBRES = ["Juan", "Maria", "Pedro", "Ana", "Luis", "Sofia", "Carlos", "Lucia", "Diego", "Valentina"]
APELLIDOS = ["Perez", "Gomez", "Rodriguez", "Fernandez", "Lopez", "Martinez", "Gonzalez", "Sanchez"]
GRADOS = ["1° Básico", "2° Básico", "3° Básico", "4° Básico", "5° Básico", "1° Medio", "2° Medio"]
MESES = ["Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def generar_nombre():
    return f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"

def poblar_sistema():
    print("Iniciando generación de datos de prueba...")
    db = SchoolDB()
    
    # 1. Crear Apoderados
    ids_apoderados = []
    for _ in range(5):
        nombre = generar_nombre()
        tel = f"+569{random.randint(10000000, 99999999)}"
        email = f"{nombre.lower().replace(' ', '.')}@example.com"
        db.agregar_apoderado(nombre, tel, email)
        print(f"Apoderado creado: {nombre}")
    
    # Obtener IDs reales de la base de datos
    apoderados = db.obtener_apoderados() # devuelve [(id, nombre), ...]
    ids_apoderados = [a[0] for a in apoderados]

    # 2. Crear Alumnos
    ids_alumnos = []
    for _ in range(15):
        nombre = generar_nombre()
        grado = random.choice(GRADOS)
        apo_id = random.choice(ids_apoderados)
        db.agregar_estudiante(nombre, grado, apo_id)
        print(f"Alumno inscrito: {nombre} ({grado})")

    # Obtener IDs de alumnos
    estudiantes = db.obtener_estudiantes_simple()
    ids_alumnos = [e[0] for e in estudiantes]

    # 3. Registrar Pagos (Aleatorios)
    for alu_id in ids_alumnos:
        # Pagar entre 0 y 5 meses aleatorios
        meses_a_pagar = random.sample(MESES, k=random.randint(0, 6))
        for mes in meses_a_pagar:
            if not db.verificar_pago_existente(alu_id, mes):
                monto = random.choice([50000, 60000, 75000])
                db.registrar_pago(alu_id, monto, mes)
                print(f"Pago registrado: Alumno ID {alu_id} - {mes}")

    print("\n¡Datos cargados exitosamente!")
    print("Ahora puedes ejecutar 'src/main.py' y ver el sistema con datos.")

if __name__ == "__main__":
    poblar_sistema()