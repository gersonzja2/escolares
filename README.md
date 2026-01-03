# Sistema de Gestión Escolar

Aplicación de escritorio desarrollada en Python para la administración de escuelas, gestión de alumnos, control de mensualidades y comunicación con apoderados vía WhatsApp.

## Características Principales

### 1. Gestión Académica
- **Registro de Alumnos:** Inscripción de estudiantes con asignación de grado y apoderado.
- **Base de Datos de Apoderados:** Gestión de contactos (teléfono, email) para comunicación.
- **Búsqueda:** Filtrado rápido de alumnos y apoderados.

### 2. Control Financiero
- **Registro de Pagos:** Control de mensualidades por alumno.
- **Historial:** Visualización completa del historial de pagos.
- **Recibos:** Generación automática de recibos en formato PDF.
- **Reporte de Morosidad:** Detección automática de alumnos con deudas basado en el ciclo escolar configurado.

### 3. Comunicación y Notificaciones
- **Integración con WhatsApp:**
  - Envío de recordatorios de pago individuales.
  - Cobranza masiva a todos los morosos con un solo clic.
  - Anuncios generales a todos los apoderados.
- **Validación de Contactos:** Limpieza y validación automática de números telefónicos.

### 4. Seguridad y Mantenimiento
- **Base de Datos:** SQLite local (`escolares.db`).
- **Backups Automáticos:** El sistema crea copias de seguridad automáticas en la carpeta `backups/` al iniciar, manteniendo un historial rotativo de las últimas 10 versiones.
- **Migraciones:** Sistema de actualización automática de la estructura de la base de datos.

## Requisitos del Sistema

- Python 3.8 o superior.
- Librerías necesarias (instalar vía `pip` si no se usa el ejecutable):
  - `tkinter` (incluido en Python)
  - `sqlite3` (incluido en Python)
  - `reportlab` (para generación de PDFs)
  - `pywhatkit` o similar (según implementación de `WhatsAppService`)

## Estructura del Proyecto

```
escolares/
├── backups/            # Copias de seguridad automáticas
├── src/
│   ├── main.py         # Punto de entrada de la aplicación (Controlador)
│   ├── backend/
│   │   ├── database.py # Lógica de base de datos y migraciones
│   │   ├── services.py # Generación de reportes PDF/CSV
│   │   └── whatsapp_service.py
│   └── frontend/
│       └── interfaz.py # Interfaz gráfica (Tkinter)
├── config.json         # Configuración de usuario (se genera automáticamente)
└── escolares.db        # Base de datos principal
```

## Configuración

Al iniciar la aplicación por primera vez, se pueden configurar los siguientes parámetros desde la interfaz:
- **Nombre de la Escuela.**
- **Día de Cobranza:** Día del mes límite para los pagos.
- **Inicio de Clases:** Mes en el que inicia el ciclo escolar (para cálculo de morosidad).
- **Teléfono Administrador:** Para pruebas de envío de mensajes.

## Notas de Desarrollo

- El sistema detecta automáticamente si se está ejecutando como script (`.py`) o como ejecutable congelado (PyInstaller), ajustando las rutas de recursos y base de datos automáticamente.
- Los procesos pesados (generación de PDF, envíos masivos de WhatsApp) se ejecutan en hilos secundarios para no congelar la interfaz.