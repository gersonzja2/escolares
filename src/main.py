from backend.database import SchoolDB
from frontend.interfaz import AppEscolar
from tkinter import messagebox

class SchoolController:
    def __init__(self):
        self.db = SchoolDB()
        # Pasamos 'self' (el controlador) a la vista
        self.view = AppEscolar(controller=self)
        
        # Cargar datos iniciales
        self.actualizar_apoderados()
        self.actualizar_alumnos()
        
        self.view.mainloop()

    def actualizar_apoderados(self):
        apoderados = self.db.obtener_apoderados()
        self.view.actualizar_combo_apoderados(apoderados)

    def actualizar_alumnos(self):
        datos = self.db.obtener_estudiantes_completo()
        self.view.actualizar_tabla_alumnos(datos)

    def guardar_apoderado(self, nombre, tel, email):
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        self.db.agregar_apoderado(nombre, tel, email)
        messagebox.showinfo("Éxito", "Apoderado guardado correctamente")
        self.view.limpiar_form_apoderado()
        self.actualizar_apoderados() # Actualizar lista en pestaña inscripción

    def inscribir_alumno(self, nombre, grado, apo_id):
        if not nombre or not apo_id:
            messagebox.showerror("Error", "Faltan datos o apoderado inválido")
            return
            
        self.db.agregar_estudiante(nombre, grado, apo_id)
        messagebox.showinfo("Éxito", "Alumno inscrito correctamente")
        self.view.limpiar_form_inscripcion()
        self.actualizar_alumnos()

    def eliminar_alumno(self, id_alumno):
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este alumno?"):
            self.db.eliminar_estudiante(id_alumno)
            self.actualizar_alumnos()

if __name__ == "__main__":
    controller = SchoolController()