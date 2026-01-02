import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

# Intentar importar matplotlib para gráficos
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AppEscolar(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.title("Sistema de Gestión Escolar")
        self.geometry("1200x800")

        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Barra de estado (Footer)
        self.lbl_estado = ctk.CTkLabel(self, text="Listo", anchor="w", text_color="gray")
        self.lbl_estado.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        self.tab_inicio = self.tab_view.add("Inicio")
        self.tab_inscripcion = self.tab_view.add("Inscripción y Alumnos")
        self.tab_apoderados = self.tab_view.add("Apoderados")
        self.tab_pagos = self.tab_view.add("Mensualidades")
        self.tab_config = self.tab_view.add("Configuración")

        self.mapa_apoderados = {}
        self.mapa_estudiantes_pago = {}
        self.ventana_morosos = None

        self.setup_ui_inicio()
        self.setup_ui_apoderados()
        self.setup_ui_inscripcion()
        self.setup_ui_pagos()
        self.setup_ui_configuracion()

    def mostrar_mensaje_estado(self, mensaje, es_error=False):
        color = "red" if es_error else "green"
        self.lbl_estado.configure(text=mensaje, text_color=color)
        # Restaurar mensaje por defecto "Listo" después de 4 segundos (4000 ms)
        self.after(4000, lambda: self.lbl_estado.configure(text="Listo", text_color="gray"))

    def ordenar_columnas(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        # Intentar ordenar como número (manejando símbolos de moneda)
        try:
            l.sort(key=lambda t: float(t[0].replace("$", "").replace(",", "")), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        # Alternar orden para el próximo clic
        tree.heading(col, command=lambda: self.ordenar_columnas(tree, col, not reverse))

    def setup_ui_inicio(self):
        self.tab_inicio.grid_columnconfigure((0, 1), weight=1)
        
        # Título de bienvenida
        ctk.CTkLabel(self.tab_inicio, text="Panel de Control", font=("Arial", 24, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # Tarjeta 1: Total Alumnos
        self.card_alumnos = ctk.CTkFrame(self.tab_inicio, fg_color="#3B8ED0")
        self.card_alumnos.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(self.card_alumnos, text="Total Alumnos", font=("Arial", 16), text_color="white").pack(pady=(10,0))
        self.lbl_total_alumnos = ctk.CTkLabel(self.card_alumnos, text="0", font=("Arial", 32, "bold"), text_color="white")
        self.lbl_total_alumnos.pack(pady=(0,10))

        # Tarjeta 2: Ingresos del Mes
        self.card_ingresos = ctk.CTkFrame(self.tab_inicio, fg_color="#2CC985")
        self.card_ingresos.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
        self.lbl_titulo_ingresos = ctk.CTkLabel(self.card_ingresos, text="Ingresos Mes Actual", font=("Arial", 16), text_color="white")
        self.lbl_titulo_ingresos.pack(pady=(10,0))
        self.lbl_total_ingresos = ctk.CTkLabel(self.card_ingresos, text="$0", font=("Arial", 32, "bold"), text_color="white")
        self.lbl_total_ingresos.pack(pady=(0,10))

        # Accesos Rápidos
        frame_acciones = ctk.CTkFrame(self.tab_inicio, fg_color="transparent")
        frame_acciones.grid(row=2, column=0, columnspan=2, pady=20)
        
        ctk.CTkLabel(frame_acciones, text="Accesos Rápidos:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(frame_acciones, text="+ Nuevo Alumno", command=lambda: self.tab_view.set("Inscripción y Alumnos")).pack(side="left", padx=10)
        ctk.CTkButton(frame_acciones, text="+ Registrar Pago", command=lambda: self.tab_view.set("Mensualidades")).pack(side="left", padx=10)
        
        ctk.CTkLabel(frame_acciones, text="|", text_color="gray").pack(side="left", padx=10)
        
        ctk.CTkLabel(frame_acciones, text="Mes:").pack(side="left", padx=5)
        self.combo_mes_dashboard = ctk.CTkComboBox(frame_acciones, values=self.controller.MESES, width=110, command=self.solicitar_actualizar_dashboard)
        self.combo_mes_dashboard.set(self.controller.MESES[datetime.now().month - 1])
        self.combo_mes_dashboard.pack(side="left", padx=5)

        ctk.CTkButton(frame_acciones, text="↻", width=40, fg_color="gray", command=self.solicitar_actualizar_dashboard).pack(side="left", padx=5)

        # Gráfico de Alumnos por Grado
        self.frame_grafico = ctk.CTkFrame(self.tab_inicio, fg_color="transparent")
        self.frame_grafico.grid(row=3, column=0, columnspan=2, pady=20, sticky="nsew")
        self.tab_inicio.grid_rowconfigure(3, weight=1)
        
        self.actualizar_grafico_alumnos()

    def actualizar_grafico_alumnos(self):
        # Limpiar gráfico anterior si existe
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        if not self.controller.mostrar_grafico:
            self.frame_grafico.grid_remove()
            return
        
        self.frame_grafico.grid()
        if not HAS_MATPLOTLIB:
            ctk.CTkLabel(self.frame_grafico, text="Instale 'matplotlib' para ver gráficos estadísticos\n(pip install matplotlib)", text_color="gray").pack(expand=True)
            return

        datos = self.controller.obtener_estadisticas_grado()
        if not datos:
            ctk.CTkLabel(self.frame_grafico, text="No hay datos suficientes para generar el gráfico.", text_color="gray").pack(expand=True)
            return

        grados = [d[0] for d in datos]
        cantidades = [d[1] for d in datos]

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(grados, cantidades, color="#3B8ED0")
        ax.set_title("Distribución de Alumnos por Grado")
        ax.set_ylabel("Cantidad de Alumnos")
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def actualizar_tarjetas_dashboard(self, total_alumnos, ingresos, mes):
        self.lbl_total_alumnos.configure(text=str(total_alumnos))
        self.lbl_total_ingresos.configure(text=f"${ingresos:,.2f}")
        self.lbl_titulo_ingresos.configure(text=f"Ingresos de {mes}")

    def solicitar_actualizar_dashboard(self, event=None):
        mes = self.combo_mes_dashboard.get()
        self.controller.actualizar_dashboard(mes)

    def setup_ui_configuracion(self):
        frame = self.tab_config
        
        ctk.CTkLabel(frame, text="Configuración General", font=("Arial", 20, "bold")).pack(pady=20)
        
        ctk.CTkLabel(frame, text="Nombre de la Escuela (para reportes):").pack(pady=5)
        self.entry_nombre_escuela = ctk.CTkEntry(frame, width=300)
        self.entry_nombre_escuela.pack(pady=5)
        # Cargar valor actual
        if hasattr(self.controller, 'nombre_escuela'):
            self.entry_nombre_escuela.insert(0, self.controller.nombre_escuela)
            
        self.switch_grafico = ctk.CTkSwitch(frame, text="Mostrar Gráfico en Dashboard")
        self.switch_grafico.pack(pady=5)
        if getattr(self.controller, 'mostrar_grafico', True):
            self.switch_grafico.select()
        else:
            self.switch_grafico.deselect()

        ctk.CTkLabel(frame, text="Tema de la Aplicación:").pack(pady=(20, 5))
        self.combo_tema = ctk.CTkOptionMenu(frame, values=["System", "Light", "Dark"], command=self.cambiar_tema)
        self.combo_tema.set("System")
        self.combo_tema.pack(pady=5)

        ctk.CTkButton(frame, text="Guardar Configuración", command=self.solicitar_guardar_config).pack(pady=20)
        
        # Sección Multi-Escuela
        ctk.CTkLabel(frame, text="Gestión de Colegios", font=("Arial", 16, "bold")).pack(pady=(20, 10))
        frame_escuelas = ctk.CTkFrame(frame, fg_color="transparent")
        frame_escuelas.pack()
        ctk.CTkButton(frame_escuelas, text="📂 Abrir Otra Escuela", command=self.controller.cargar_escuela).pack(side="left", padx=5)
        ctk.CTkButton(frame_escuelas, text="➕ Crear Nueva Escuela", fg_color="green", command=self.controller.nueva_escuela).pack(side="left", padx=5)

        # Ayuda y Documentación
        ctk.CTkLabel(frame, text="Ayuda y Documentación", font=("Arial", 16, "bold")).pack(pady=(20, 10))
        frame_ayuda = ctk.CTkFrame(frame, fg_color="transparent")
        frame_ayuda.pack()
        ctk.CTkButton(frame_ayuda, text="📖 Manual de Usuario", command=lambda: self.abrir_visor_documentacion("Manual de Usuario", "MANUAL_USUARIO.md")).pack(side="left", padx=5)
        ctk.CTkButton(frame_ayuda, text="ℹ️ Acerca de (Léeme)", command=lambda: self.abrir_visor_documentacion("Acerca de", "README.md")).pack(side="left", padx=5)

        ctk.CTkLabel(frame, text="Mantenimiento", font=("Arial", 16, "bold")).pack(pady=(40, 10))
        ctk.CTkButton(frame, text="Crear Respaldo de Base de Datos (Backup)", fg_color="#E0A800", text_color="black", command=self.controller.realizar_backup).pack(pady=10)

        # Zona de Peligro
        ctk.CTkLabel(frame, text="Zona de Peligro (Borrado Masivo)", font=("Arial", 14, "bold"), text_color="#D35B58").pack(pady=(20, 10))
        
        frame_danger = ctk.CTkFrame(frame, fg_color="transparent")
        frame_danger.pack()
        
        ctk.CTkButton(frame_danger, text="Borrar Todos los Pagos", fg_color="#D35B58", hover_color="#C72C41", width=180, command=self.controller.eliminar_todos_pagos).pack(side="left", padx=5)
        ctk.CTkButton(frame_danger, text="Borrar Todos los Alumnos", fg_color="#D35B58", hover_color="#C72C41", width=180, command=self.controller.eliminar_todos_alumnos).pack(side="left", padx=5)
        ctk.CTkButton(frame_danger, text="Borrar Todos los Apoderados", fg_color="#D35B58", hover_color="#C72C41", width=180, command=self.controller.eliminar_todos_apoderados).pack(side="left", padx=5)

    def abrir_visor_documentacion(self, titulo, nombre_archivo):
        contenido = self.controller.leer_documentacion(nombre_archivo)
        
        top = ctk.CTkToplevel(self)
        top.title(titulo)
        top.geometry("800x600")
        
        # Area de texto con scroll
        textbox = ctk.CTkTextbox(top, font=("Consolas", 12))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("0.0", contenido)
        textbox.configure(state="disabled") # Solo lectura

    def cambiar_tema(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    def actualizar_ui_configuracion(self, nombre_escuela, mostrar_grafico):
        self.entry_nombre_escuela.delete(0, 'end')
        self.entry_nombre_escuela.insert(0, nombre_escuela)
        if mostrar_grafico:
            self.switch_grafico.select()
        else:
            self.switch_grafico.deselect()

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
            self.tree_apoderados.heading(col, command=lambda c=col: self.ordenar_columnas(self.tree_apoderados, c, False))
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
            self.tree_alumnos.heading(col, command=lambda c=col: self.ordenar_columnas(self.tree_alumnos, c, False))
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
        # datos_alumno viene de la DB: (id, nombre, grado, apoderado_id, fecha_registro)
        id_alu, nombre, grado, apo_id, *_ = datos_alumno
        
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
        self.mapa_apoderados = {nombre: id for id, nombre in lista_apoderados}
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
            # Reemplazar None con cadena vacía para visualización
            fila = [x if x is not None else "" for x in fila]
            # fila viene como: (id, nombre, grado, fecha_reg, apo_nombre, apo_tel, apo_email)
            # UI espera: (ID, Nombre, Grado, Apoderado, Contacto)
            fila_ui = (fila[0], fila[1], fila[2], fila[4], fila[5])
            self.tree_alumnos.insert("", "end", values=fila_ui)

    def solicitar_eliminacion(self):
        selected = self.tree_alumnos.selection()
        if selected:
            item = self.tree_alumnos.item(selected[0])
            id_alumno = item['values'][0]
            self.controller.eliminar_alumno(id_alumno)

    def solicitar_guardar_config(self):
        self.controller.guardar_ajustes(self.entry_nombre_escuela.get(), self.switch_grafico.get())

    def setup_ui_pagos(self):
        frame = self.tab_pagos
        frame.grid_columnconfigure(1, weight=1)
        
        # Panel Izquierdo: Formulario de Pago
        panel_pago = ctk.CTkFrame(frame)
        panel_pago.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ctk.CTkLabel(panel_pago, text="Seleccionar Alumno:").pack(pady=5)
        self.combo_alu_pago = ctk.CTkComboBox(panel_pago, values=[])
        self.combo_alu_pago.set("")
        self.combo_alu_pago.pack(pady=5)

        ctk.CTkLabel(panel_pago, text="Mes a Pagar:").pack(pady=5)
        self.combo_mes = ctk.CTkComboBox(panel_pago, values=self.controller.MESES)
        self.combo_mes.pack(pady=5)
        
        ctk.CTkLabel(panel_pago, text="Monto:").pack(pady=5)
        self.entry_pago_monto = ctk.CTkEntry(panel_pago)
        self.entry_pago_monto.pack()
        
        ctk.CTkButton(panel_pago, text="Registrar Pago", command=self.solicitar_pago).pack(pady=20)
        
        # Sección de Administración
        ctk.CTkLabel(panel_pago, text="--- Administración ---", text_color="gray").pack(pady=(10, 5))
        ctk.CTkButton(panel_pago, text="Modificar Seleccionado", fg_color="#E0A800", text_color="black", command=self.solicitar_modificar_pago).pack(pady=5)
        ctk.CTkButton(panel_pago, text="📄 Imprimir Recibo", fg_color="#3B8ED0", command=self.solicitar_recibo).pack(pady=5)
        ctk.CTkButton(panel_pago, text="Eliminar Seleccionado", fg_color="red", command=self.solicitar_eliminar_pago).pack(pady=5)

        # Sección de Reportes
        ctk.CTkLabel(panel_pago, text="--- Reportes ---", text_color="gray").pack(pady=(20, 5))
        ctk.CTkLabel(panel_pago, text="Mes de Corte:").pack(pady=2)
        self.combo_mes_reporte = ctk.CTkComboBox(panel_pago, values=self.controller.MESES)
        # Seleccionar mes actual por defecto
        mes_actual_idx = datetime.now().month - 1
        self.combo_mes_reporte.set(self.controller.MESES[mes_actual_idx])
        self.combo_mes_reporte.pack(pady=5)
        ctk.CTkButton(panel_pago, text="Ver Morosos", fg_color="#D35B58", hover_color="#C72C41", command=self.solicitar_morosos).pack(pady=5)
        ctk.CTkButton(panel_pago, text="Exportar Historial CSV", fg_color="green", command=self.solicitar_exportar_pagos).pack(pady=5)

        # Panel Derecho: Historial
        panel_derecho = ctk.CTkFrame(frame, fg_color="transparent")
        panel_derecho.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        panel_derecho.grid_rowconfigure(1, weight=1)
        panel_derecho.grid_columnconfigure(0, weight=1)

        # Buscador de Pagos
        frame_busqueda = ctk.CTkFrame(panel_derecho, fg_color="transparent")
        frame_busqueda.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.entry_busqueda_pagos = ctk.CTkEntry(frame_busqueda, placeholder_text="Buscar pago por alumno...")
        self.entry_busqueda_pagos.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_busqueda_pagos.bind("<Return>", lambda event: self.solicitar_busqueda_pagos())
        
        ctk.CTkButton(frame_busqueda, text="Buscar", width=100, command=self.solicitar_busqueda_pagos).pack(side="right")

        style = ttk.Style()
        columns = ("ID", "Alumno", "Monto", "Mes", "Estado", "Fecha")
        self.tree_pagos = ttk.Treeview(panel_derecho, columns=columns, show="headings")
        for col in columns:
            self.tree_pagos.heading(col, text=col)
            self.tree_pagos.heading(col, command=lambda c=col: self.ordenar_columnas(self.tree_pagos, c, False))
            width = 140 if col == "Fecha" else 90
            self.tree_pagos.column(col, width=width)
        self.tree_pagos.grid(row=1, column=0, sticky="nsew")
        self.tree_pagos.bind("<Double-1>", self.on_double_click_pago)

    def actualizar_combo_estudiantes_pago(self, lista_estudiantes):
        self.mapa_estudiantes_pago = {nombre: id for id, nombre in lista_estudiantes}
        values = list(self.mapa_estudiantes_pago.keys())
        self.combo_alu_pago.configure(values=values)
        if values: 
            self.combo_alu_pago.set(values[0])
        else:
            self.combo_alu_pago.set("")

    def actualizar_tabla_pagos(self, datos):
        for item in self.tree_pagos.get_children():
            self.tree_pagos.delete(item)
        for fila in datos:
            # fila viene como: (id, nombre, grado, monto, mes, pagado, fecha_pago)
            # UI espera: (ID, Alumno, Monto, Mes, Estado, Fecha)
            # Saltamos el grado (índice 2) para la vista de tabla, pero lo mantenemos en CSV
            fila_ui = [fila[0], fila[1], fila[3], fila[4], fila[5], fila[6]]
            
            # Convertir el booleano 1/0 a texto
            fila_ui[4] = "Pagado" if fila_ui[4] else "Pendiente"
            # Manejar registros antiguos sin fecha
            if fila_ui[5] is None: fila_ui[5] = ""
            self.tree_pagos.insert("", "end", values=fila_ui)

    def solicitar_pago(self):
        alu_str = self.combo_alu_pago.get()
        alu_id = self.mapa_estudiantes_pago.get(alu_str)
        monto = self.entry_pago_monto.get()
        mes = self.combo_mes.get()
        self.controller.registrar_pago(alu_id, monto, mes)

    def solicitar_exportar_pagos(self):
        self.controller.exportar_pagos_csv()

    def solicitar_recibo(self):
        selected = self.tree_pagos.selection()
        if selected:
            item = self.tree_pagos.item(selected[0])
            id_pago = item['values'][0]
            self.controller.generar_recibo_pago(id_pago)
        else:
            messagebox.showwarning("Aviso", "Seleccione un pago del historial para generar el recibo.")

    def solicitar_busqueda_pagos(self):
        termino = self.entry_busqueda_pagos.get()
        self.controller.buscar_pagos(termino)

    def on_double_click_pago(self, event):
        self.solicitar_modificar_pago()

    def solicitar_morosos(self):
        mes = self.combo_mes_reporte.get()
        self.controller.mostrar_reporte_morosos(mes)

    def solicitar_eliminar_pago(self):
        selected = self.tree_pagos.selection()
        if selected:
            item = self.tree_pagos.item(selected[0])
            id_pago = item['values'][0]
            self.controller.eliminar_pago(id_pago)
        else:
            messagebox.showwarning("Aviso", "Seleccione un pago del historial para eliminar.")

    def solicitar_modificar_pago(self):
        selected = self.tree_pagos.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Seleccione un pago del historial para modificar.")
            return

        item = self.tree_pagos.item(selected[0])
        values = item['values']
        id_pago = values[0]
        monto = values[2]
        mes = values[3]

        top = ctk.CTkToplevel(self)
        top.title("Modificar Pago")
        top.geometry("300x250")
        top.grab_set()

        ctk.CTkLabel(top, text="Mes:").pack(pady=5)
        combo_mes = ctk.CTkComboBox(top, values=self.controller.MESES)
        combo_mes.set(mes)
        combo_mes.pack(pady=5)

        ctk.CTkLabel(top, text="Monto:").pack(pady=5)
        entry_monto = ctk.CTkEntry(top)
        entry_monto.insert(0, str(monto))
        entry_monto.pack(pady=5)

        ctk.CTkButton(top, text="Guardar Cambios", command=lambda: self.controller.modificar_pago(id_pago, entry_monto.get(), combo_mes.get(), top)).pack(pady=20)

    def mostrar_ventana_morosos(self, datos, titulo):
        if self.ventana_morosos is not None and self.ventana_morosos.winfo_exists():
            self.ventana_morosos.destroy()

        self.ventana_morosos = ctk.CTkToplevel(self)
        top = self.ventana_morosos
        top.title(titulo)
        top.geometry("900x450") # Ventana más ancha para ver los meses
        
        ctk.CTkLabel(top, text=titulo, font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkButton(top, text="Exportar Lista a CSV", fg_color="green", command=lambda: self.controller.exportar_morosos_csv(datos, titulo)).pack(pady=5)
        
        style = ttk.Style()
        columns = ("ID", "Alumno", "Grado", "Apoderado", "Teléfono", "Meses Adeudados")
        tree = ttk.Treeview(top, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Meses Adeudados":
                tree.column(col, width=300) # Más espacio para la lista de meses
            else:
                tree.column(col, width=100)
            
        tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        for fila in datos:
            tree.insert("", "end", values=fila)
