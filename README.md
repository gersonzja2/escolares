# Sistema de Gestión Escolar

Aplicación de escritorio desarrollada en Python para la administración de escuelas, academias o talleres. Permite gestionar alumnos, apoderados, mensualidades y enviar recordatorios de cobranza automatizados vía WhatsApp.

## 🚀 Características Principales

*   **Gestión de Alumnos:** Inscripción, edición y bajas.
*   **Base de Datos:** Almacenamiento local seguro usando SQLite.
*   **Control de Pagos:** Registro de mensualidades, generación de recibos PDF y reporte de morosos.
*   **Dashboard:** Visualización gráfica de alumnos por grado e ingresos mensuales.
*   **Automatización de WhatsApp:**
    *   Envío de recordatorios de pago individuales.
    *   Anuncios generales a todos los apoderados.
    *   **Configuración de espera ajustable** para conexiones lentas.
*   **Seguridad:** Copias de seguridad (backup) automáticas al iniciar.

## 📋 Requisitos Previos

*   Python 3.8 o superior.
*   Navegador Google Chrome o Microsoft Edge (para WhatsApp Web).
*   Cuenta de WhatsApp activa vinculada en el navegador.

## 🛠️ Instalación

1.  Clonar o descargar este repositorio.
2.  Abrir una terminal en la carpeta del proyecto.
3.  (Opcional) Crear y activar un entorno virtual:

```bash
python -m venv env
# En Windows:
.\env\Scripts\activate
```

4.  Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

Para iniciar la aplicación, ejecuta el archivo principal:

```bash
python src/main.py
```

## ⚙️ Configuración de WhatsApp

La aplicación utiliza WhatsApp Web para enviar mensajes. Debido a que la velocidad de carga depende de tu PC e Internet, puedes ajustar el tiempo de espera para evitar errores.

1.  Ve a la pestaña **Configuración** dentro de la aplicación.
2.  Busca el control deslizante **"Tiempo de Espera WhatsApp"**.
3.  Ajusta el valor (por defecto 20s).
    *   Si tienes una PC rápida y buen internet: **10s - 15s**.
    *   Si tu PC es lenta o el internet inestable: **30s - 40s**.
4.  Presiona **"Guardar Configuración"**.
5.  Usa el botón **"📲 Probar WhatsApp"** para verificar que funcione correctamente.

> **Nota:** No utilices el mouse ni el teclado mientras se realiza el envío automático de mensajes.

## 📦 Generar Ejecutable (.exe)

Si deseas convertir la aplicación en un archivo ejecutable para Windows, utiliza PyInstaller:

```bash
pyinstaller --noconfirm --onefile --windowed --name "SistemaEscolar" --add-data "src;src" --icon "icono.ico" src/main.py
```
*(Asegúrate de tener un archivo `icono.ico` o elimina la opción `--icon`)*.

## 📂 Estructura del Proyecto

*   `src/main.py`: Controlador principal de la aplicación.
*   `src/frontend/`: Interfaz gráfica (CustomTkinter).
*   `src/backend/`: Lógica de base de datos y servicios (PDF, WhatsApp).
*   `backups/`: Carpeta donde se guardan automáticamente las copias de seguridad de la base de datos.
*   `config.json`: Archivo de configuración local (se genera automáticamente).

## 📄 Licencia

Este proyecto es de uso libre para fines educativos y de gestión interna.

---
Desarrollado con Python y CustomTkinter.