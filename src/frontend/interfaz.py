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
        self.mapa_estudiantes_pago = {}

        self.setup_ui_apoderados()
        self.setup_ui_inscripcion()
        self.setup_ui_pagos()

    def setup_ui_apoderados(self):
        frame = self.tab_apoderados
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Panel Izquierdo: Formulario
        panel_form = ctk.CTkFrame(frame)
        panel_form.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ctk.CTkLabel(panel_form, text="Nombre Apoderado:").pack(pady=5)
        self.entry_apo_nombre = ctk.CTkEntry(panel_form)
        self.entry_apo_nombre.pack(pady=5)

        ctk.CTkLabel(panel_form, text="Teléfono:").pack(pady=5)
        self.entry_apo_tel = ctk.CTkEntry(panel_form)
        self.entry_apo_tel.pack(pady=5)

        ctk.CTkLabel(panel_form, text="Email:").pack(pady=5)
        self.entry_apo_email = ctk.CTkEntry(panel_form)
        self.entry_apo_email.pack(pady=5)

        ctk.CTkButton(panel_form, text="Guardar Apoderado", command=self.solicitar_guardar_apoderado).pack(pady=20)
        ctk.CTkButton(panel_form, text="Eliminar Seleccionado", fg_color="red", command=self.solicitar_eliminar_apoderado).pack(pady=5)

        # Panel Derecho: Tabla
        style = ttk.Style()
        columns = ("ID", "Nombre", "Teléfono", "Email")
        self.tree_apoderados = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_apoderados.heading(col, text=col)
            self.tree_apoderados.column(col, width=120)
        
        self.tree_apoderados.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.tree_apoderados.bind("<Double-1>", self.on_double_click_apoderado)

    def on_double_click_apoderado(self, event):
        item = self.tree_apoderados.selection()
        if not item: return
        values = self.tree_apoderados.item(item, "values")
        self.abrir_ventana_edicion_apoderado(values)

    def abrir_ventana_edicion_apoderado(self, values):
        id_apo, nombre, tel, email = values
        
        top = ctk.CTkToplevel(self)
        top.title("Editar Apoderado")
        top.geometry("400x300")
        top.grab_set() # Hace la ventana modal
        
        ctk.CTkLabel(top, text="Nombre:").pack(pady=5)
        entry_nombre = ctk.CTkEntry(top)
        entry_nombre.pack(pady=5)
        entry_nombre.insert(0, nombre)
        
        ctk.CTkLabel(top, text="Teléfono:").pack(pady=5)
        entry_tel = ctk.CTkEntry(top)
        entry_tel.pack(pady=5)
        entry_tel.insert(0, tel)
        
        ctk.CTkLabel(top, text="Email:").pack(pady=5)
        entry_email = ctk.CTkEntry(top)
        entry_email.pack(pady=5)
        entry_email.insert(0, email)
        
        def guardar():
            self.controller.editar_apoderado(id_apo, entry_nombre.get(), entry_tel.get(), entry_email.get(), top)
            
        ctk.CTkButton(top, text="Actualizar", command=guardar).pack(pady=20)

    def actualizar_tabla_apoderados(self, datos):
        for item in self.tree_apoderados.get_children():
            self.tree_apoderados.delete(item)
        for fila in datos:
            self.tree_apoderados.insert("", "end", values=fila)

    def solicitar_eliminar_apoderado(self):
        selected = self.tree_apoderados.selection()
        if selected:
            item = self.tree_apoderados.item(selected[0])
            id_apo = item['values'][0]
            self.controller.eliminar_apoderado(id_apo)

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
        frame.grid_rowconfigure(0, weight=1)

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
        ctk.CTkButton(panel_form, text="Exportar a CSV", fg_color="green", command=self.solicitar_exportar_csv).pack(pady=20)
        ctk.CTkButton(panel_form, text="Generar Ficha PDF", fg_color="#E0A800", text_color="black", command=self.solicitar_ficha_pdf).pack(pady=5)

        # Panel Derecho (Buscador + Tabla)
        panel_derecho = ctk.CTkFrame(frame, fg_color="transparent")
        panel_derecho.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        panel_derecho.grid_rowconfigure(1, weight=1)
        panel_derecho.grid_columnconfigure(0, weight=1)

        # Buscador
        frame_busqueda = ctk.CTkFrame(panel_derecho, fg_color="transparent")
        frame_busqueda.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.entry_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Buscar alumno...")
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_busqueda.bind("<Return>", lambda event: self.solicitar_busqueda())
        
        ctk.CTkButton(frame_busqueda, text="Buscar", width=100, command=self.solicitar_busqueda).pack(side="right")

        # Tabla de visualización
        style = ttk.Style()
        style.theme_use("clam")
        
        columns = ("ID", "Nombre", "Grado", "Apoderado", "Contacto")
        self.tree_alumnos = ttk.Treeview(panel_derecho, columns=columns, show="headings")
        
        for col in columns:
            self.tree_alumnos.heading(col, text=col)
            self.tree_alumnos.column(col, width=100)
        
        self.tree_alumnos.grid(row=1, column=0, sticky="nsew")
        self.tree_alumnos.bind("<Double-1>", self.on_double_click_alumno)

    def on_double_click_alumno(self, event):
        item = self.tree_alumnos.selection()
        if not item: return
        # Obtenemos solo el ID del treeview, el resto lo pedimos a la DB para tener el ID del apoderado correcto
        id_alumno = self.tree_alumnos.item(item, "values")[0]
        self.controller.preparar_edicion_alumno(id_alumno)

    def abrir_ventana_edicion_alumno(self, datos_alumno):
        # datos_alumno viene de la DB: (id, nombre, grado, apoderado_id)
        id_alu, nombre, grado, apo_id = datos_alumno
        
        top = ctk.CTkToplevel(self)
        top.title("Editar Alumno")
        top.geometry("400x350")
        top.grab_set()
        
        ctk.CTkLabel(top, text="Nombre:").pack(pady=5)
        entry_nombre = ctk.CTkEntry(top)
        entry_nombre.pack(pady=5)
        entry_nombre.insert(0, nombre)
        
        ctk.CTkLabel(top, text="Grado:").pack(pady=5)
        entry_grado = ctk.CTkEntry(top)
        entry_grado.pack(pady=5)
        entry_grado.insert(0, grado)
        
        ctk.CTkLabel(top, text="Apoderado:").pack(pady=5)
        combo_apo = ctk.CTkComboBox(top, values=list(self.mapa_apoderados.keys()))
        combo_apo.pack(pady=5)
        
        # Pre-seleccionar el apoderado actual en el combobox
        for key, val in self.mapa_apoderados.items():
            if val == apo_id:
                combo_apo.set(key)
                break
        
        def guardar():
            apo_str = combo_apo.get()
            new_apo_id = self.mapa_apoderados.get(apo_str)
            self.controller.editar_alumno(id_alu, entry_nombre.get(), entry_grado.get(), new_apo_id, top)
            
        ctk.CTkButton(top, text="Actualizar", command=guardar).pack(pady=20)

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

    def solicitar_busqueda(self):
        termino = self.entry_busqueda.get()
        self.controller.buscar_alumnos(termino)

    def limpiar_form_inscripcion(self):
        self.entry_alu_nombre.delete(0, 'end')

    def solicitar_exportar_csv(self):
        self.controller.exportar_alumnos_csv()

    def solicitar_ficha_pdf(self):
        selected = self.tree_alumnos.selection()
        if selected:
            item = self.tree_alumnos.item(selected[0])
            id_alumno = item['values'][0]
            self.controller.generar_ficha_alumno_pdf(id_alumno)
        else:
            messagebox.showwarning("Aviso", "Seleccione un alumno para generar la ficha.")

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
        frame.grid_columnconfigure(1, weight=1)
        
        # Panel Izquierdo: Formulario de Pago
        panel_pago = ctk.CTkFrame(frame)
        panel_pago.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ctk.CTkLabel(panel_pago, text="Seleccionar Alumno:").pack(pady=5)
        self.combo_alu_pago = ctk.CTkComboBox(panel_pago, values=[])
        self.combo_alu_pago.pack(pady=5)

        ctk.CTkLabel(panel_pago, text="Mes a Pagar:").pack(pady=5)
        self.combo_mes = ctk.CTkComboBox(panel_pago, values=["Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        self.combo_mes.pack(pady=5)
        
        ctk.CTkLabel(panel_pago, text="Monto:").pack(pady=5)
        self.entry_pago_monto = ctk.CTkEntry(panel_pago)
        self.entry_pago_monto.pack()
        
        ctk.CTkButton(panel_pago, text="Registrar Pago", command=self.solicitar_pago).pack(pady=20)
        ctk.CTkButton(panel_pago, text="Ver Morosos (Mes Actual)", fg_color="#D35B58", hover_color="#C72C41", command=self.solicitar_morosos).pack(pady=5)
        ctk.CTkButton(panel_pago, text="Exportar Historial CSV", fg_color="green", command=self.solicitar_exportar_pagos).pack(pady=20)

        # Panel Derecho: Historial
        style = ttk.Style()
        columns = ("ID", "Alumno", "Monto", "Mes", "Estado")
        self.tree_pagos = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_pagos.heading(col, text=col)
            self.tree_pagos.column(col, width=90)
        self.tree_pagos.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def actualizar_combo_estudiantes_pago(self, lista_estudiantes):
        self.mapa_estudiantes_pago = {f"{id} - {nombre}": id for id, nombre in lista_estudiantes}
        values = list(self.mapa_estudiantes_pago.keys())
        self.combo_alu_pago.configure(values=values)
        if values: self.combo_alu_pago.set(values[0])

    def actualizar_tabla_pagos(self, datos):
        for item in self.tree_pagos.get_children():
            self.tree_pagos.delete(item)
        for fila in datos:
            # Convertir el booleano 1/0 a texto
            fila_lista = list(fila)
            fila_lista[4] = "Pagado" if fila_lista[4] else "Pendiente"
            self.tree_pagos.insert("", "end", values=fila_lista)

    def solicitar_pago(self):
        alu_str = self.combo_alu_pago.get()
        alu_id = self.mapa_estudiantes_pago.get(alu_str)
        monto = self.entry_pago_monto.get()
        mes = self.combo_mes.get()
        self.controller.registrar_pago(alu_id, monto, mes)

    def solicitar_exportar_pagos(self):
        self.controller.exportar_pagos_csv()

    def solicitar_morosos(self):
        self.controller.mostrar_reporte_morosos()

    def mostrar_ventana_morosos(self, datos, mes):
        top = ctk.CTkToplevel(self)
        top.title(f"Reporte de Morosidad - {mes}")
        top.geometry("700x400")
        
        ctk.CTkLabel(top, text=f"Alumnos pendientes de pago: {mes}", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkButton(top, text="Exportar Lista a CSV", fg_color="green", command=lambda: self.controller.exportar_morosos_csv(datos, mes)).pack(pady=5)
        
        style = ttk.Style()
        columns = ("ID", "Alumno", "Grado", "Apoderado", "Teléfono")
        tree = ttk.Treeview(top, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
            
        tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        for fila in datos:
            tree.insert("", "end", values=fila)
