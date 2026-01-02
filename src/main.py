from backend.database import SchoolDB
from frontend.interfaz import AppEscolar
from tkinter import messagebox, filedialog
import csv
import re
from datetime import datetime

class SchoolController:
    def __init__(self):
        self.db = SchoolDB()
        # Pasamos 'self' (el controlador) a la vista
        self.view = AppEscolar(controller=self)
        
        # Cargar datos iniciales
        self.actualizar_apoderados()
        self.actualizar_alumnos()
        self.actualizar_pagos_ui()
        
        self.view.mainloop()

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

    def buscar_alumnos(self, termino):
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

    def guardar_apoderado(self, nombre, tel, email):
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        # Validación de formato de email
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "El formato del email es inválido (ej: correo@dominio.com)")
            return
        
        self.db.agregar_apoderado(nombre, tel, email)
        messagebox.showinfo("Éxito", "Apoderado guardado correctamente")
        self.view.limpiar_form_apoderado()
        self.actualizar_apoderados() # Actualizar lista en pestaña inscripción

    def editar_apoderado(self, id, nombre, tel, email, window):
        if not nombre:
             messagebox.showerror("Error", "El nombre es obligatorio")
             return
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "El formato del email es inválido")
            return
            
        self.db.actualizar_apoderado(id, nombre, tel, email)
        messagebox.showinfo("Éxito", "Apoderado actualizado correctamente")
        window.destroy()
        self.actualizar_apoderados()

    def eliminar_apoderado(self, id_apoderado):
        if self.db.verificar_dependencia_apoderado(id_apoderado):
            messagebox.showerror("Error", "No se puede eliminar el apoderado porque tiene alumnos inscritos. Elimine o reasigne a los alumnos primero.")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este apoderado?"):
            self.db.eliminar_apoderado(id_apoderado)
            self.actualizar_apoderados()

    def inscribir_alumno(self, nombre, grado, apo_id):
        if not nombre:
            messagebox.showerror("Error", "El nombre del alumno es obligatorio")
            return
            
        if not apo_id:
            messagebox.showerror("Error", "Debe seleccionar un apoderado para inscribir al alumno")
            return
            
        self.db.agregar_estudiante(nombre, grado, apo_id)
        messagebox.showinfo("Éxito", "Alumno inscrito correctamente")
        self.view.limpiar_form_inscripcion()
        self.actualizar_alumnos()
        self.actualizar_pagos_ui() # Actualizar lista en pagos también

    def preparar_edicion_alumno(self, id_alumno):
        estudiante = self.db.obtener_estudiante_por_id(id_alumno)
        if estudiante:
            self.view.abrir_ventana_edicion_alumno(estudiante[0])

    def editar_alumno(self, id, nombre, grado, apo_id, window):
        if not nombre or not apo_id:
             messagebox.showerror("Error", "Faltan datos o apoderado inválido")
             return
        self.db.actualizar_estudiante(id, nombre, grado, apo_id)
        messagebox.showinfo("Éxito", "Alumno actualizado correctamente")
        window.destroy()
        self.actualizar_alumnos()

    def eliminar_alumno(self, id_alumno):
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este alumno?"):
            self.db.eliminar_estudiante(id_alumno)
            self.actualizar_alumnos()
            self.actualizar_pagos_ui()

    def registrar_pago(self, estudiante_id, monto, mes):
        if not estudiante_id or not monto or not mes:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                messagebox.showerror("Error", "El monto debe ser un número positivo mayor a 0")
                return
            self.db.registrar_pago(estudiante_id, monto_float, mes)
            messagebox.showinfo("Éxito", "Pago registrado correctamente")
            self.actualizar_pagos_ui()
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")

    def mostrar_reporte_morosos(self):
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_actual = meses[datetime.now().month - 1]
        
        datos = self.db.obtener_morosos(mes_actual)
        self.view.mostrar_ventana_morosos(datos, mes_actual)

    def exportar_alumnos_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Guardar lista de alumnos")
        if not file_path: return
        
        datos = self.db.obtener_estudiantes_completo()
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Nombre Alumno", "Grado", "Nombre Apoderado", "Teléfono"])
                writer.writerows(datos)
            messagebox.showinfo("Éxito", "Lista de alumnos exportada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el archivo: {e}")

    def generar_ficha_alumno_pdf(self, id_alumno):
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
            
        nombre_alu, grado, nombre_apo, tel_apo, email_apo = datos[0]
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"Ficha_{nombre_alu}.pdf", title="Guardar Ficha de Alumno")
        if not file_path: return

        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, height - 50, "Ficha del Estudiante")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 100, f"Nombre del Alumno: {nombre_alu}")
            c.drawString(50, height - 120, f"Grado/Curso: {grado}")
            
            c.line(50, height - 140, width - 50, height - 140)
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 170, "Información del Apoderado")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 200, f"Nombre: {nombre_apo}")
            c.drawString(50, height - 220, f"Teléfono: {tel_apo}")
            c.drawString(50, height - 240, f"Email: {email_apo}")
            
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(50, 50, "Generado por Sistema de Gestión Escolar")
            
            c.save()
            messagebox.showinfo("Éxito", "Ficha PDF generada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")

    def exportar_pagos_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Guardar historial de pagos")
        if not file_path: return
        
        datos = self.db.obtener_historial_pagos()
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID Pago", "Alumno", "Monto", "Mes", "Pagado (1=Sí, 0=No)"])
                writer.writerows(datos)
            messagebox.showinfo("Éxito", "Historial de pagos exportado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el archivo: {e}")

    def exportar_morosos_csv(self, datos, mes):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile=f"Morosos_{mes}.csv", title="Guardar reporte de morosos")
        if not file_path: return
        
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID Alumno", "Nombre", "Grado", "Apoderado", "Teléfono"])
                writer.writerows(datos)
            messagebox.showinfo("Éxito", "Reporte de morosos exportado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el archivo: {e}")

if __name__ == "__main__":
    controller = SchoolController()