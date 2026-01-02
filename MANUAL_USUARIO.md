# Manual de Usuario - Sistema de Gestión Escolar

## 1. Introducción
Bienvenido al Sistema de Gestión Escolar. Este software permite administrar de manera eficiente la información de alumnos, apoderados y el control de pagos de mensualidades de su institución educativa.

## 2. Instalación y Ejecución

### Requisitos Previos
*   Tener instalado Python 3.8 o superior.
*   Las librerías necesarias (ver `requirements.txt`).

### Pasos para iniciar
1.  Abra una terminal en la carpeta del proyecto.
2.  Ejecute el comando:
    ```bash
    python src/main.py
    ```

## 3. Navegación Principal
La aplicación se divide en 5 pestañas principales ubicadas en la parte superior:
1.  **Inicio**: Panel de control general.
2.  **Inscripción y Alumnos**: Gestión de estudiantes.
3.  **Apoderados**: Gestión de padres o tutores.
4.  **Mensualidades**: Control de pagos y deudas.
5.  **Configuración**: Ajustes del sistema y base de datos.

---

## 4. Módulos del Sistema

### A. Pestaña Inicio (Dashboard)
Aquí encontrará un resumen visual del estado del colegio.
*   **Tarjetas Informativas**: Muestran el total de alumnos inscritos y los ingresos monetarios del mes seleccionado.
*   **Accesos Rápidos**: Botones para ir directamente a inscribir un alumno o registrar un pago.
*   **Selector de Mes**: Permite cambiar el mes para ver los ingresos históricos en el dashboard.
*   **Gráfico**: Visualización de barras con la cantidad de alumnos por grado.

### B. Pestaña Apoderados
**Importante**: Antes de inscribir un alumno, debe existir un apoderado registrado.
1.  **Registrar Nuevo**: Complete Nombre, Teléfono y Email en el formulario izquierdo y presione "Guardar Apoderado".
2.  **Editar**: Haga doble clic sobre un apoderado en la tabla de la derecha para modificar sus datos.
3.  **Eliminar**: Seleccione un apoderado de la lista y presione "Eliminar Seleccionado". *Nota: No puede eliminar un apoderado si tiene alumnos asociados.*

### C. Pestaña Inscripción y Alumnos
1.  **Inscribir Alumno**:
    *   Ingrese el Nombre del Alumno.
    *   Ingrese el Grado o Curso (ej: 1° Básico).
    *   Seleccione el Apoderado de la lista desplegable.
    *   Presione "Inscribir Alumno".
2.  **Buscar**: Use la barra de búsqueda superior derecha para filtrar alumnos por nombre.
3.  **Ficha del Alumno (PDF)**: Seleccione un alumno de la lista y presione "Generar Ficha PDF" para crear un documento con sus datos y últimos pagos.
4.  **Exportar**: El botón "Exportar a CSV" guarda la lista completa en un archivo compatible con Excel.
5.  **Editar/Eliminar**: Doble clic para editar o use el botón "Eliminar Seleccionado".

### D. Pestaña Mensualidades (Pagos)
1.  **Registrar Pago**:
    *   Seleccione al Alumno.
    *   Elija el Mes a pagar.
    *   Ingrese el Monto.
    *   Presione "Registrar Pago".
2.  **Historial**: A la derecha verá todos los pagos realizados. Puede buscar por nombre de alumno.
3.  **Modificar/Eliminar**: Si cometió un error, seleccione el pago en la tabla y use los botones correspondientes en la sección "Administración".
4.  **Reporte de Morosos**:
    *   Seleccione un "Mes de Corte" (ej: Abril).
    *   Presione "Ver Morosos".
    *   El sistema mostrará quiénes deben mensualidades desde Marzo hasta el mes seleccionado.
    *   Puede exportar esta lista a Excel (CSV).

### E. Pestaña Configuración
1.  **Datos de la Escuela**: Cambie el nombre que aparece en los reportes PDF.
2.  **Apariencia**: Cambie entre modo Claro (Light), Oscuro (Dark) o Sistema.
3.  **Gestión Multi-Escuela**:
    *   **Crear Nueva Escuela**: Crea una base de datos vacía para administrar otro colegio por separado.
    *   **Abrir Otra Escuela**: Cambia la base de datos actual por otra existente.
4.  **Respaldo (Backup)**: Crea una copia de seguridad de todos sus datos actuales.
5.  **Zona de Peligro**: Botones para borrar masivamente todos los pagos, alumnos o apoderados. *Úselo con precaución*.

---

## 5. Preguntas Frecuentes

*   **¿Por qué no puedo borrar un apoderado?**
    *   Probablemente tiene alumnos inscritos. Primero elimine o reasigne a los alumnos.
*   **¿Dónde se guardan los archivos PDF o CSV?**
    *   El sistema le preguntará dónde guardarlos cada vez que genere uno.
*   **¿Cómo recupero una copia de seguridad?**
    *   Use la opción "Abrir Otra Escuela" en Configuración y seleccione su archivo de respaldo.