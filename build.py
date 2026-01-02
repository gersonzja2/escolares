import PyInstaller.__main__
import os

# Asegurarse de ejecutar desde la raíz del proyecto
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)

print("Iniciando compilación del Sistema Escolar...")

PyInstaller.__main__.run([
    'src/main.py',                      # Script principal
    '--name=SistemaEscolar',            # Nombre del ejecutable
    '--windowed',                       # No mostrar consola negra (GUI mode)
    '--onedir',                         # Generar carpeta (más rápido y fácil de depurar que --onefile)
    '--noconfirm',                      # Sobrescribir carpeta dist sin preguntar
    '--clean',                          # Limpiar caché de compilación
    
    # Si tienes un icono, descomenta la siguiente línea y pon el nombre de tu archivo .ico
    # '--icon=src/icono.ico',
    
    # Recolectar recursos de librerías complejas
    '--collect-all=customtkinter',
    '--collect-all=reportlab',
    '--collect-all=matplotlib',
    '--collect-all=pywhatkit',
    '--hidden-import=PIL',
    
    # Incluir documentación en la carpeta del ejecutable (formato Windows: origen;destino)
    '--add-data=README.md;.',
    '--add-data=MANUAL_USUARIO.md;.',
    
    # Agregar ruta src para que encuentre los módulos backend/frontend
    '--paths=src',
])

print("¡Compilación finalizada! Revisa la carpeta 'dist/SistemaEscolar'")