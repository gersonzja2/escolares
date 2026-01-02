import shutil
import os
import glob

def limpiar():
    # Solo borramos 'build' y caché. 
    # NO borramos 'dist' porque ahí está el ejecutable final (.exe).
    carpetas = ['build', '__pycache__']
    
    print("Limpiando carpetas temporales...")
    
    for carpeta in carpetas:
        if os.path.exists(carpeta):
            try:
                shutil.rmtree(carpeta)
                print(f"Eliminado: {carpeta}/")
            except Exception as e:
                print(f"Error eliminando {carpeta}: {e}")

    print("Limpiando archivos de especificación...")
    for archivo in glob.glob("*.spec"):
        try:
            os.remove(archivo)
            print(f"Eliminado: {archivo}")
        except Exception as e:
            print(f"Error eliminando {archivo}: {e}")
                
    print("Limpieza completada.")

if __name__ == "__main__":
    limpiar()