from backend.database import SchoolDB
from frontend.interfaz import AppEscolar
from tkinter import messagebox, filedialog
import csv
import re
from datetime import datetime
import threading
import shutil
from typing import List, Optional, Any

class SchoolController:
    MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    def __init__(self):
        self.db = SchoolDB()
        # Pasamos 'self' (el controlador) a la vista
        self.view = AppEscolar(controller=self)
        
        # Cargar configuración
        self.nombre_escuela = self.db.obtener_configuracion("nombre_escuela") or "Escuela Modelo"
        
        # Cargar datos iniciales
        self.actualizar_apoderados()
        self.actualizar_alumnos()
        self.actualizar_pagos_ui()
        self.actualizar_dashboard()
        
        self.view.mainloop()

    def actualizar_dashboard(self):
        mes_actual = self.MESES[datetime.now().month - 1]
        total_alumnos, ingresos = self.db.obtener_estadisticas_dashboard(mes_actual)
        self.view.actualizar_tarjetas_dashboard(total_alumnos, ingresos, mes_actual)

    def guardar_ajustes(self, nombre_escuela):
        if not nombre_escuela:
            messagebox.showerror("Error", "El nombre de la escuela no puede estar vacío")
            return
        self.db.guardar_configuracion("nombre_escuela", nombre_escuela)
        self.nombre_escuela = nombre_escuela
        self.view.mostrar_mensaje_estado("Configuración guardada correctamente")

    def realizar_backup(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db")],
            initialfile=f"backup_escolares_{datetime.now().strftime('%Y%m%d')}.db",
            title="Guardar Copia de Seguridad"
        )
        if file_path:
            try:
                shutil.copy(self.db.db.db_path, file_path)
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
        idx_inicio_clases = 2 
        try:
            mes_actual_idx = self.MESES.index(mes_corte)
        except ValueError:
            mes_actual_idx = datetime.now().month - 1
        
        if mes_actual_idx < idx_inicio_clases:
             messagebox.showinfo("Aviso", "El ciclo escolar comienza en Marzo. No hay reporte de morosidad disponible para Enero/Febrero.")
             return

        # Lista de meses que DEBERÍAN estar pagados a la fecha (ej: Marzo, Abril, Mayo...)
        meses_requeridos = self.MESES[idx_inicio_clases : mes_actual_idx + 1]
        
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
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
        except ImportError:
            messagebox.showerror("Error", "La librería 'reportlab' no está instalada.\nPor favor ejecute: pip install reportlab")
            return

        datos = self.db.obtener_estudiante_detalle(id_alumno)
        if not datos:
            messagebox.showerror("Error", "No se encontraron datos del alumno")
            return
            
        nombre_alu, grado, fecha_reg, nombre_apo, tel_apo, email_apo = datos[0]
        
        # Manejo de valores nulos para evitar que salga "None" en el PDF
        tel_apo = tel_apo if tel_apo else "No registrado"
        email_apo = email_apo if email_apo else "No registrado"
        fecha_reg = fecha_reg if fecha_reg else "No registrada"
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"Ficha_{nombre_alu}.pdf", title="Guardar Ficha de Alumno")
        if not file_path: return

        def worker():
            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                
                c.setFont("Helvetica-Bold", 20)
                c.drawString(50, height - 50, "Ficha del Estudiante")
                
                c.setFont("Helvetica", 12)
                c.drawString(50, height - 100, f"Nombre del Alumno: {nombre_alu}")
                c.drawString(50, height - 120, f"Grado/Curso: {grado}")
                c.drawString(350, height - 120, f"Fecha Registro: {fecha_reg}")
                
                c.line(50, height - 140, width - 50, height - 140)
                
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, height - 170, "Información del Apoderado")
                
                c.setFont("Helvetica", 12)
                c.drawString(50, height - 200, f"Nombre: {nombre_apo}")
                c.drawString(50, height - 220, f"Teléfono: {tel_apo}")
                c.drawString(50, height - 240, f"Email: {email_apo}")
                
                # Tabla de Pagos
                y = height - 280
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, "Historial de Pagos Recientes")
                y -= 25
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, "Mes")
                c.drawString(200, y, "Monto")
                c.drawString(350, y, "Fecha Pago")
                c.line(50, y-5, 500, y-5)
                y -= 20
                c.setFont("Helvetica", 10)
                
                pagos = self.db.obtener_pagos_alumno(id_alumno)
                for p in pagos[:15]: # Mostrar solo los últimos 15 para que quepan
                    mes, monto, fecha = p
                    c.drawString(50, y, str(mes))
                    c.drawString(200, y, f"${monto:,.0f}")
                    c.drawString(350, y, str(fecha))
                    y -= 15

                c.setFont("Helvetica-Oblique", 10)
                c.drawString(50, 50, f"Generado por Sistema de Gestión Escolar - {self.nombre_escuela}")
                
                c.save()
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
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
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
                with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)
                    writer.writerows(datos)
                self.view.after(0, lambda: self.view.mostrar_mensaje_estado("Archivo exportado correctamente"))
            except Exception as e:
                self.view.after(0, lambda: messagebox.showerror("Error", f"No se pudo exportar el archivo: {e}"))

        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    controller = SchoolController()