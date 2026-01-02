# Sistema de Gestión Escolar

Aplicación de escritorio desarrollada en Python para la administración eficiente de instituciones educativas. Permite gestionar alumnos, apoderados, mensualidades y generar reportes financieros y académicos de manera sencilla y moderna.

## Características Principales

*   **Gestión Integral:** Registro y administración de Alumnos y Apoderados.
*   **Control de Pagos:** Seguimiento de mensualidades, historial de pagos y detección automática de morosos.
*   **Soporte Multi-Escuela:** Capacidad para gestionar múltiples colegios utilizando bases de datos independientes.
*   **Dashboard Interactivo:** Visualización de estadísticas clave (total alumnos, ingresos mensuales) y gráficos de distribución.
*   **Reportes y Exportación:**
    *   Generación de fichas de alumno en formato **PDF**.
    *   Exportación de listas de alumnos, historiales de pago y reportes de morosidad a **CSV** (Excel).
*   **Seguridad y Mantenimiento:**
    *   **Respaldo Automático:** El sistema crea copias de seguridad automáticas (rotación de las últimas 10) en la carpeta `backups/` cada vez que se inicia el programa.
    *   **Zona de Peligro:** Funcionalidades para el borrado masivo de datos (pagos, alumnos, apoderados) protegidas con confirmación.

## Requisitos del Sistema

*   Python 3.8 o superior.
*   Librerías listadas en `requirements.txt`.

## Instalación

1.  **Clonar el repositorio o descargar el código:**
    ```bash
    git clone <url-del-repositorio>
    cd escolares
    ```

2.  **Crear un entorno virtual (Recomendado):**
    ```bash
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Linux/Mac:
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

**Opción A: Ejecutar desde código fuente (Python)**
Ejecute el archivo principal desde la carpeta raíz:

```bash
python src/main.py
```

*   **Datos de Prueba:** Puede poblar el sistema con datos ficticios ejecutando `python src/datos_prueba.py`.
*   **Configuración:** Desde la pestaña de configuración puede cambiar el nombre de la escuela, el tema visual y gestionar los archivos de base de datos.

## Estructura del Proyecto

*   `src/main.py`: Controlador principal y punto de entrada.
*   `src/frontend/`: Interfaz gráfica (UI) construida con CustomTkinter.
*   `src/backend/`: Lógica de base de datos (SQLite) y servicios de generación de archivos.

## Generar Ejecutable Portable (.exe)

Para crear una versión que funcione en cualquier computador con Windows (sin necesidad de instalar Python):

1.  Ejecute el script de construcción:
    ```bash
    python build.py
    ```
2.  Se generará una carpeta `dist/SistemaEscolar`.
3.  **Esa carpeta es su aplicación portable.** Puede copiarla completa a una memoria USB o a otro computador.
4.  Para usar el programa, abra el archivo `SistemaEscolar.exe` que está dentro de esa carpeta.
    *   *Importante: La carpeta contiene su base de datos (`escolares.db`). Si la mueve a otro PC, sus datos viajarán con ella.*