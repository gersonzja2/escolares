from backend.database import SchoolDB
from backend.services import ReportService
from frontend.interfaz import AppEscolar
from tkinter import messagebox, filedialog
import re
from datetime import datetime
import threading
import shutil
from typing import List, Optional, Any

class SchoolController:
    MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    INICIO_CLASES_IDX = 2  # Marzo es el índice 2

    def __init__(self):
        self.db = SchoolDB()
        # Cargar configuración
        self.nombre_escuela = self.db.obtener_configuracion("nombre_escuela") or "Escuela Modelo"
        self.mostrar_grafico = (self.db.obtener_configuracion("mostrar_grafico") or "1") == "1"
        
        # Pasamos 'self' (el controlador) a la vista
        self.view = AppEscolar(controller=self)
        self.view.title(f"Sistema de Gestión Escolar - {self.nombre_escuela}")
        
        # Cargar datos iniciales
        self.actualizar_apoderados()
        self.actualizar_alumnos()
        self.actualizar_pagos_ui()
        self.actualizar_dashboard()
        
    def iniciar(self):
        """Inicia el bucle principal de la interfaz gráfica."""
        self.view.mainloop()

    def actualizar_dashboard(self, mes_seleccionado: Optional[str] = None):
        if mes_seleccionado:
            mes_actual = mes_seleccionado
        else:
            mes_actual = self.MESES[datetime.now().month - 1]
        total_alumnos, ingresos = self.db.obtener_estadisticas_dashboard(mes_actual)
        self.view.actualizar_tarjetas_dashboard(total_alumnos, ingresos, mes_actual)
        # Actualizar gráfico si existe
        if hasattr(self.view, 'actualizar_grafico_alumnos'):
            self.view.actualizar_grafico_alumnos()

    def guardar_ajustes(self, nombre_escuela, mostrar_grafico):
        if not nombre_escuela:
            messagebox.showerror("Error", "El nombre de la escuela no puede estar vacío")
            return
        self.db.guardar_configuracion("nombre_escuela", nombre_escuela)
        self.db.guardar_configuracion("mostrar_grafico", "1" if mostrar_grafico else "0")
        self.nombre_escuela = nombre_escuela
        self.mostrar_grafico = mostrar_grafico
        self.view.mostrar_mensaje_estado("Configuración guardada correctamente")
        self.actualizar_dashboard()

    def obtener_estadisticas_grado(self):
        return self.db.obtener_alumnos_por_grado()

    def cargar_escuela(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("SQLite DB", "*.db")],
            title="Seleccionar Base de Datos de Escuela"
        )
        if file_path:
            self.cambiar_db(file_path)

    def nueva_escuela(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db")],
            title="Crear Nueva Base de Datos para Escuela"
        )
        if file_path:
            self.cambiar_db(file_path)

    def cambiar_db(self, db_path: str):
        try:
            # 1. Conectar a la nueva DB
            self.db = SchoolDB(db_path)
            
            # 2. Recargar configuración
            self.nombre_escuela = self.db.obtener_configuracion("nombre_escuela") or "Nueva Escuela"
            self.mostrar_grafico = (self.db.obtener_configuracion("mostrar_grafico") or "1") == "1"
            
            # 3. Actualizar UI (Título y Configuración)
            self.view.title(f"Sistema de Gestión Escolar - {self.nombre_escuela}")
            self.view.actualizar_ui_configuracion(self.nombre_escuela, self.mostrar_grafico)

            # 4. Refrescar datos de las tablas y dashboard
            self.actualizar_apoderados()
            self.actualizar_alumnos()
            self.actualizar_pagos_ui()
            self.actualizar_dashboard()
            self.view.mostrar_mensaje_estado(f"Escuela cargada: {self.nombre_escuela}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar de escuela: {e}")

    def realizar_backup(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db")],
            initialfile=f"backup_escolares_{datetime.now().strftime('%Y%m%d')}.db",
            title="Guardar Copia de Seguridad"
        )
        if file_path:
            try:
                shutil.copy(self.db.db_path, file_path)
                self.view.mostrar_mensaje_estado("Copia de seguridad creada con éxito")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el backup: {e}")

    def actualizar_apoderados(self):
        # Actualizar combo en inscripción (lista simple)
        apoderados_simple = self.db.obtener_apoderados()
        self.view.actualizar_combo_apoderados(apoderados_simple)
        
        # Actualizar tabla en pestaña apoderados (lista completa)
        apoderados_completo = self.db.obtener_apoderados_completo()
        self.view.actualizar_tabla_apoderados(apoderados_completo)

    def actualizar_alumnos(self):
        datos = self.db.obtener_estudiantes_completo()
        self.view.actualizar_tabla_alumnos(datos)

    def buscar_alumnos(self, termino: str):
        if not termino:
            self.actualizar_alumnos()
            return
        datos = self.db.buscar_estudiantes(termino)
        self.view.actualizar_tabla_alumnos(datos)

    def actualizar_pagos_ui(self):
        estudiantes = self.db.obtener_estudiantes_simple()
        self.view.actualizar_combo_estudiantes_pago(estudiantes)
        pagos = self.db.obtener_historial_pagos()
        self.view.actualizar_tabla_pagos(pagos)

    def buscar_pagos(self, termino: str):
        if not termino:
            self.actualizar_pagos_ui()
            return
        pagos = self.db.buscar_pagos(termino)
        self.view.actualizar_tabla_pagos(pagos)

    def guardar_apoderado(self, nombre: str, tel: str, email: str):
        nombre = nombre.strip() if nombre else ""
        tel = tel.strip() if tel else ""
        email = email.strip() if email else ""

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        if tel and not re.match(r"^\+?[\d\s-]+$", tel):
            messagebox.showerror("Error", "El teléfono contiene caracteres inválidos")
            return

        # Validación de formato de email
        if not self._validar_email(email):
            messagebox.showerror("Error", "El formato del email es inválido (ej: correo@dominio.com)")
            return
        
        self.db.agregar_apoderado(nombre, tel, email)
        self.view.mostrar_mensaje_estado("Apoderado guardado correctamente")
        self.view.limpiar_form_apoderado()
        self.actualizar_apoderados() # Actualizar lista en pestaña inscripción

    def editar_apoderado(self, id: int, nombre: str, tel: str, email: str, window: Any):
        nombre = nombre.strip() if nombre else ""
        tel = tel.strip() if tel else ""
        email = email.strip() if email else ""

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        if tel and not re.match(r"^\+?[\d\s-]+$", tel):
            messagebox.showerror("Error", "El teléfono contiene caracteres inválidos")
            return
        if not self._validar_email(email):
            messagebox.showerror("Error", "El formato del email es inválido")
            return
            
        self.db.actualizar_apoderado(id, nombre, tel, email)
        self.view.mostrar_mensaje_estado("Apoderado actualizado correctamente")
        window.destroy()
        self.actualizar_apoderados()

    def eliminar_apoderado(self, id_apoderado: int):
        if self.db.verificar_dependencia_apoderado(id_apoderado):
            messagebox.showerror("Error", "No se puede eliminar el apoderado porque tiene alumnos inscritos. Elimine o reasigne a los alumnos primero.")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este apoderado?"):
            self.db.eliminar_apoderado(id_apoderado)
            self.actualizar_apoderados()

    def inscribir_alumno(self, nombre: str, grado: str, apo_id: int):
        nombre = nombre.strip() if nombre else ""
        grado = grado.strip() if grado else ""

        if not nombre:
            messagebox.showerror("Error", "El nombre del alumno es obligatorio")
            return
            
        if not apo_id:
            messagebox.showerror("Error", "Debe seleccionar un apoderado para inscribir al alumno")
            return
            
        self.db.agregar_estudiante(nombre, grado, apo_id)
        self.view.mostrar_mensaje_estado("Alumno inscrito correctamente")
        self.view.limpiar_form_inscripcion()
        self.actualizar_alumnos()
        self.actualizar_pagos_ui() # Actualizar lista en pagos también
        self.actualizar_dashboard()

    def preparar_edicion_alumno(self, id_alumno: int):
        estudiante = self.db.obtener_estudiante_por_id(id_alumno)
        if estudiante:
            self.view.abrir_ventana_edicion_alumno(estudiante[0])

    def editar_alumno(self, id: int, nombre: str, grado: str, apo_id: int, window: Any):
        nombre = nombre.strip() if nombre else ""
        grado = grado.strip() if grado else ""

        if not nombre or not apo_id:
            messagebox.showerror("Error", "Faltan datos o apoderado inválido")
            return
        self.db.actualizar_estudiante(id, nombre, grado, apo_id)
        self.view.mostrar_mensaje_estado("Alumno actualizado correctamente")
        window.destroy()
        self.actualizar_alumnos()

    def eliminar_alumno(self, id_alumno: int):
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este alumno?"):
            self.db.eliminar_estudiante(id_alumno)
            self.actualizar_alumnos()
            self.actualizar_pagos_ui()
            self.actualizar_dashboard()

    def registrar_pago(self, estudiante_id: int, monto: str, mes: str):
        if not estudiante_id or not monto or not mes:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                messagebox.showerror("Error", "El monto debe ser un número positivo mayor a 0")
                return
            
            if self.db.verificar_pago_existente(estudiante_id, mes):
                messagebox.showwarning("Aviso", f"El pago de {mes} ya está registrado para este alumno.")
                return

            self.db.registrar_pago(estudiante_id, monto_float, mes)
            self.view.mostrar_mensaje_estado("Pago registrado correctamente")
            self.actualizar_pagos_ui()
            self.actualizar_dashboard()
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")

    def eliminar_pago(self, id_pago: int):
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este registro de pago?"):
            self.db.eliminar_pago(id_pago)
            self.view.mostrar_mensaje_estado("Pago eliminado correctamente")
            self.actualizar_pagos_ui()
            self.actualizar_dashboard()

    def modificar_pago(self, id_pago: int, monto: str, mes: str, window: Any):
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                messagebox.showerror("Error", "El monto debe ser positivo")
                return
            
            self.db.actualizar_pago(id_pago, monto_float, mes)
            self.view.mostrar_mensaje_estado("Pago actualizado correctamente")
            window.destroy()
            self.actualizar_pagos_ui()
            self.actualizar_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")

    def mostrar_reporte_morosos(self, mes_corte: str):
        # Lógica de ciclo escolar: Marzo (índice 2) a Diciembre
        try:
            mes_actual_idx = self.MESES.index(mes_corte)
        except ValueError:
            mes_actual_idx = datetime.now().month - 1
        
        if mes_actual_idx < self.INICIO_CLASES_IDX:
            messagebox.showinfo("Aviso", "El ciclo escolar comienza en Marzo. No hay reporte de morosidad disponible para Enero/Febrero.")
            return

        # Lista de meses que DEBERÍAN estar pagados a la fecha (ej: Marzo, Abril, Mayo...)
        meses_requeridos = self.MESES[self.INICIO_CLASES_IDX : mes_actual_idx + 1]
        
        estudiantes = self.db.obtener_estudiantes_completo()
        pagos_raw = self.db.obtener_pagos_todos()
        
        # Crear mapa de pagos: { id_estudiante: {'Marzo', 'Abril'} }
        pagos_map = {}
        for pid, mes in pagos_raw:
            if pid not in pagos_map:
                pagos_map[pid] = set()
            pagos_map[pid].add(mes)
            
        lista_morosos = []
        for est in estudiantes:
            # Se ajusta el desempaquetado para los 7 valores que retorna la consulta (ignoramos fecha y email)
            eid, nombre, grado, _, apo, tel, _ = est
            pagados = pagos_map.get(eid, set())
            
            # Calcular meses faltantes
            deuda = [m for m in meses_requeridos if m not in pagados]
            
            if deuda:
                deuda_str = ", ".join(deuda)
                # Agregamos la columna de meses adeudados al final
                lista_morosos.append((eid, nombre, grado, apo, tel, deuda_str))

        titulo = f"Morosidad Acumulada (Marzo - {mes_corte})"
        self.view.mostrar_ventana_morosos(lista_morosos, titulo)

    def exportar_alumnos_csv(self):
        datos = self.db.obtener_estudiantes_completo()
        headers = ["ID", "Nombre Alumno", "Grado", "Fecha Registro", "Nombre Apoderado", "Teléfono", "Email Apoderado"]
        self._exportar_csv(datos, headers, "Lista_Alumnos.csv", "Guardar lista de alumnos")

    def generar_ficha_alumno_pdf(self, id_alumno: int):
        datos = self.db.obtener_estudiante_detalle(id_alumno)
        if not datos:
            messagebox.showerror("Error", "No se encontraron datos del alumno")
            return
            
        datos_alumno = datos[0]
        nombre_alu = datos_alumno[0]
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"Ficha_{nombre_alu}.pdf", title="Guardar Ficha de Alumno")
        if not file_path: return

        def worker():
            try:
                pagos = self.db.obtener_pagos_alumno(id_alumno)
                ReportService.generar_ficha_alumno_pdf(file_path, datos_alumno, pagos, self.nombre_escuela)
                self.view.after(0, lambda: self.view.mostrar_mensaje_estado("Ficha PDF generada correctamente"))
            except Exception as e:
                self.view.after(0, lambda: messagebox.showerror("Error", f"No se pudo generar el PDF: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def exportar_pagos_csv(self):
        datos = self.db.obtener_historial_pagos()
        headers = ["ID Pago", "Alumno", "Grado", "Monto", "Mes", "Pagado (1=Sí, 0=No)", "Fecha Pago"]
        self._exportar_csv(datos, headers, "Historial_Pagos.csv", "Guardar historial de pagos")

    def exportar_morosos_csv(self, datos: List[Any], titulo_reporte: str):
        headers = ["ID Alumno", "Nombre", "Grado", "Apoderado", "Teléfono", "Meses Adeudados"]
        # Limpiamos el título para usarlo de nombre de archivo
        nombre_archivo = f"Reporte_{titulo_reporte.replace(' ', '_').replace('(', '').replace(')', '')}.csv"
        self._exportar_csv(datos, headers, nombre_archivo, "Guardar reporte de morosos")

    # --- Métodos Auxiliares ---

    def _validar_email(self, email: str) -> bool:
        # Regex mejorado para validación de email
        if email and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return False
        return True

    def _exportar_csv(self, datos: List[Any], headers: List[str], default_name: str, title: str):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv")], 
            initialfile=default_name, 
            title=title
        )
        if not file_path: 
            return

        def worker():
            try:
                ReportService.exportar_csv(file_path, headers, datos)
                self.view.after(0, lambda: self.view.mostrar_mensaje_estado("Archivo exportado correctamente"))
            except Exception as e:
                self.view.after(0, lambda: messagebox.showerror("Error", f"No se pudo exportar el archivo: {e}"))

        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    controller = SchoolController()
    controller.iniciar()