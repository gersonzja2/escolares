import customtkinter as ctk
from tkinter import ttk, messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AppEscolar(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.title("Sistema de Gestión Escolar")
        self.geometry("900x600")

        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_inscripcion = self.tab_view.add("Inscripción y Alumnos")
        self.tab_apoderados = self.tab_view.add("Apoderados")
        self.tab_pagos = self.tab_view.add("Mensualidades")

        self.mapa_apoderados = {}

        self.setup_ui_apoderados()
        self.setup_ui_inscripcion()
        self.setup_ui_pagos()

    def setup_ui_apoderados(self):
        frame = self.tab_apoderados
        
        ctk.CTkLabel(frame, text="Nombre Apoderado:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_apo_nombre = ctk.CTkEntry(frame)
        self.entry_apo_nombre.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Teléfono:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_apo_tel = ctk.CTkEntry(frame)
        self.entry_apo_tel.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Email:").grid(row=2, column=0, padx=10, pady=10)
        self.entry_apo_email = ctk.CTkEntry(frame)
        self.entry_apo_email.grid(row=2, column=1, padx=10, pady=10)

        btn_add = ctk.CTkButton(frame, text="Guardar Apoderado", command=self.solicitar_guardar_apoderado)
        btn_add.grid(row=3, column=0, columnspan=2, pady=20)

    def solicitar_guardar_apoderado(self):
        nombre = self.entry_apo_nombre.get()
        tel = self.entry_apo_tel.get()
        email = self.entry_apo_email.get()
        self.controller.guardar_apoderado(nombre, tel, email)

    def limpiar_form_apoderado(self):
        self.entry_apo_nombre.delete(0, 'end')
        self.entry_apo_tel.delete(0, 'end')
        self.entry_apo_email.delete(0, 'end')

    def setup_ui_inscripcion(self):
        frame = self.tab_inscripcion
        frame.grid_columnconfigure(1, weight=1)

        # Formulario
        panel_form = ctk.CTkFrame(frame)
        panel_form.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ctk.CTkLabel(panel_form, text="Nombre Alumno:").pack(pady=5)
        self.entry_alu_nombre = ctk.CTkEntry(panel_form)
        self.entry_alu_nombre.pack(pady=5)

        ctk.CTkLabel(panel_form, text="Grado/Curso:").pack(pady=5)
        self.entry_alu_grado = ctk.CTkEntry(panel_form)
        self.entry_alu_grado.pack(pady=5)

        ctk.CTkLabel(panel_form, text="Seleccionar Apoderado:").pack(pady=5)
        self.combo_apoderados = ctk.CTkComboBox(panel_form, values=[])
        self.combo_apoderados.pack(pady=5)
        
        ctk.CTkButton(panel_form, text="Inscribir Alumno", command=self.solicitar_inscripcion).pack(pady=20)
        ctk.CTkButton(panel_form, text="Eliminar Seleccionado", fg_color="red", command=self.solicitar_eliminacion).pack(pady=5)
        ctk.CTkButton(panel_form, text="Actualizar Lista", command=lambda: self.controller.actualizar_alumnos()).pack(pady=5)

        # Tabla de visualización
        style = ttk.Style()
        style.theme_use("clam")
        
        columns = ("ID", "Nombre", "Grado", "Apoderado", "Contacto")
        self.tree_alumnos = ttk.Treeview(frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree_alumnos.heading(col, text=col)
            self.tree_alumnos.column(col, width=100)
        
        self.tree_alumnos.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def actualizar_combo_apoderados(self, lista_apoderados):
        # Recibe lista de tuplas (id, nombre)
        self.mapa_apoderados = {f"{id} - {nombre}": id for id, nombre in lista_apoderados}
        values = list(self.mapa_apoderados.keys())
        self.combo_apoderados.configure(values=values)
        if values:
            self.combo_apoderados.set(values[0])
        else:
            self.combo_apoderados.set("")

    def solicitar_inscripcion(self):
        nombre = self.entry_alu_nombre.get()
        grado = self.entry_alu_grado.get()
        apo_str = self.combo_apoderados.get()
        apo_id = self.mapa_apoderados.get(apo_str)
        self.controller.inscribir_alumno(nombre, grado, apo_id)

    def limpiar_form_inscripcion(self):
        self.entry_alu_nombre.delete(0, 'end')

    def actualizar_tabla_alumnos(self, datos):
        for item in self.tree_alumnos.get_children():
            self.tree_alumnos.delete(item)
        for fila in datos:
            self.tree_alumnos.insert("", "end", values=fila)

    def solicitar_eliminacion(self):
        selected = self.tree_alumnos.selection()
        if selected:
            item = self.tree_alumnos.item(selected[0])
            id_alumno = item['values'][0]
            self.controller.eliminar_alumno(id_alumno)

    def setup_ui_pagos(self):
        frame = self.tab_pagos
        ctk.CTkLabel(frame, text="Módulo de Pagos (En desarrollo)").pack(pady=20)
        
        # Aquí iría la lógica similar: Seleccionar alumno de un dropdown, 
        # ingresar monto, mes y guardar en la tabla 'mensualidades'.
        
        ctk.CTkLabel(frame, text="ID Estudiante:").pack()
        self.entry_pago_id = ctk.CTkEntry(frame)
        self.entry_pago_id.pack()
        
        ctk.CTkLabel(frame, text="Monto:").pack()
        self.entry_pago_monto = ctk.CTkEntry(frame)
        self.entry_pago_monto.pack()
        
        ctk.CTkButton(frame, text="Registrar Pago", command=lambda: messagebox.showinfo("Info", "Función a implementar conectando con DB")).pack(pady=20)
