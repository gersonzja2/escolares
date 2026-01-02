from backend.database import SchoolDB
from backend.services import ReportService
from backend.whatsapp_service import WhatsAppService
from frontend.interfaz import AppEscolar
from tkinter import messagebox, filedialog, simpledialog
import time
import re
from datetime import datetime
import threading
import shutil
from typing import List, Optional, Any
import sys
import os
import json

class SchoolController:
    MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    INICIO_CLASES_IDX = 2  # Marzo es el índice 2
    CONFIG_FILE = "config.json"
    BACKUP_DIR = "backups"

    def __init__(self):
        # 1. Cargar configuración de persistencia (última DB usada)
        self.app_config = self._cargar_config_app()
        last_db = self.app_config.get("last_db_path")
        
        if last_db and os.path.exists(last_db):
            self.db = SchoolDB(last_db)
        else:
            self.db = SchoolDB() # Usa la por defecto si no hay config
            
        # 2. Guardar la ruta actual y crear backup automático de seguridad
        self._guardar_config_app(self.db.db_path)
        self._crear_backup_automatico()

        # Cargar configuración
        self.nombre_escuela = self.db.obtener_configuracion("nombre_escuela") or "Escuela Modelo"
        self.mostrar_grafico = (self.db.obtener_configuracion("mostrar_grafico") or "1") == "1"
        self.admin_telefono = self.db.obtener_configuracion("admin_telefono") or ""
        self.dia_cobranza = int(self.db.obtener_configuracion("dia_cobranza") or "5")
        
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

    def guardar_ajustes(self, nombre_escuela, mostrar_grafico, admin_tel, dia_cobranza):
        if not nombre_escuela:
            messagebox.showerror("Error", "El nombre de la escuela no puede estar vacío")
            return
        
        try:
            dia = int(dia_cobranza)
            if not (1 <= dia <= 31): raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El día de cobranza debe ser un número entre 1 y 31")
            return

        self.db.guardar_configuracion("nombre_escuela", nombre_escuela)
        self.db.guardar_configuracion("mostrar_grafico", "1" if mostrar_grafico else "0")
        self.db.guardar_configuracion("admin_telefono", admin_tel)
        self.db.guardar_configuracion("dia_cobranza", str(dia))
        
        self.nombre_escuela = nombre_escuela
        self.mostrar_grafico = mostrar_grafico
        self.admin_telefono = admin_tel
        self.dia_cobranza = dia
        
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
            
            # Guardar preferencia y asegurar copia
            self._guardar_config_app(self.db.db_path)
            self._crear_backup_automatico()

            # 2. Recargar configuración
            self.nombre_escuela = self.db.obtener_configuracion("nombre_escuela") or "Nueva Escuela"
            self.mostrar_grafico = (self.db.obtener_configuracion("mostrar_grafico") or "1") == "1"
            self.admin_telefono = self.db.obtener_configuracion("admin_telefono") or ""
            self.dia_cobranza = int(self.db.obtener_configuracion("dia_cobranza") or "5")
            
            # 3. Actualizar UI (Título y Configuración)
            self.view.title(f"Sistema de Gestión Escolar - {self.nombre_escuela}")
            self.view.actualizar_ui_configuracion(self.nombre_escuela, self.mostrar_grafico, self.admin_telefono, self.dia_cobranza)

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
        datos = self._validar_datos_apoderado(nombre, tel, email)
        if not datos:
            return
        
        nombre, tel, email = datos
        self.db.agregar_apoderado(nombre, tel, email)
        self.view.mostrar_mensaje_estado("Apoderado guardado correctamente")
        self.view.limpiar_form_apoderado()
        self.actualizar_apoderados() # Actualizar lista en pestaña inscripción

    def editar_apoderado(self, id: int, nombre: str, tel: str, email: str, window: Any):
        datos = self._validar_datos_apoderado(nombre, tel, email)
        if not datos:
            return
            
        nombre, tel, email = datos
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

        if self.db.verificar_estudiante_existente(nombre, grado):
            messagebox.showerror("Error", f"El alumno '{nombre}' ya está inscrito en el grado '{grado}'.")
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

    def generar_recibo_pago(self, id_pago: int):
        datos = self.db.obtener_pago_detalle(id_pago)
        if not datos:
            messagebox.showerror("Error", "No se encontraron detalles del pago")
            return
        
        datos_pago = datos[0]
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"Recibo_{id_pago}.pdf", title="Guardar Recibo")
        if not file_path: return

        self.view.configure(cursor="watch")
        # Reutilizamos el worker thread para no congelar la UI
        threading.Thread(target=lambda: self._worker_recibo(file_path, datos_pago), daemon=True).start()

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

        self.view.configure(cursor="watch") # Cambiar cursor a espera
        def worker():
            try:
                pagos = self.db.obtener_pagos_alumno(id_alumno)
                ReportService.generar_ficha_alumno_pdf(file_path, datos_alumno, pagos, self.nombre_escuela)
                self.view.after(0, lambda: self._finalizar_tarea_visual("Ficha PDF generada correctamente"))
            except Exception as e:
                self.view.after(0, lambda: self._finalizar_tarea_visual(f"Error: {e}", es_error=True))

        threading.Thread(target=worker, daemon=True).start()

    def enviar_recordatorio_pago(self, id_alumno: int):
        # 1. Obtener datos de contacto
        datos = self.db.obtener_datos_cobranza(id_alumno)
        if not datos:
            messagebox.showerror("Error", "No se encontraron datos para este alumno.")
            return
        
        nombre_apo, telefono, nombre_alu = datos[0]

        # 2. Calcular Deuda
        deuda = self._calcular_deuda_alumno(id_alumno)
        
        if not deuda:
            messagebox.showinfo("Información", f"El alumno {nombre_alu} está al día en sus pagos.")
            return

        deuda_str = ", ".join(deuda)
        telefono = telefono.strip() if telefono else ""

        # 3. Validar y Enviar
        if not telefono.startswith("+"):
            messagebox.showwarning("Formato Incorrecto", "El teléfono debe incluir código de país (Ej: +52...) para usar WhatsApp.")
            return

        mensaje = (f"Estimado/a {nombre_apo}, le recordamos que el alumno {nombre_alu} "
                   f"tiene pendientes las mensualidades de: {deuda_str}. "
                   f"Favor regularizar. Atte, {self.nombre_escuela}")

        if messagebox.askyesno("Enviar WhatsApp", f"¿Enviar recordatorio a {telefono}?\n\nMensaje: {mensaje}"):
            self._ejecutar_envio_whatsapp(telefono, mensaje)

    def enviar_anuncio_general(self):
        """Envía un mensaje a todos los apoderados registrados."""
        apoderados = self.db.obtener_telefonos_apoderados()
        if not apoderados:
            messagebox.showinfo("Info", "No hay apoderados con teléfono registrado.")
            return
            
        mensaje = simpledialog.askstring("Anuncio General", "Ingrese el mensaje para TODOS los apoderados:")
        if not mensaje: return

        if not messagebox.askyesno("Confirmar envío masivo", f"Se enviará el mensaje a {len(apoderados)} contactos.\nEsto tomará tiempo y abrirá múltiples pestañas.\n¿Continuar?"):
            return

        self.view.mostrar_mensaje_estado("Iniciando envío masivo...")
        
        def worker():
            enviados = 0
            errores = 0
            for nombre, tel in apoderados:
                tel = tel.strip()
                if not tel.startswith("+"):
                    errores += 1
                    continue
                
                msg_personalizado = f"Hola {nombre}. {mensaje}"
                if WhatsAppService.enviar_mensaje(tel, msg_personalizado):
                    enviados += 1
                else:
                    errores += 1
                # Espera de seguridad entre mensajes para dar tiempo al navegador
                time.sleep(8) 
            
            self.view.after(0, lambda: messagebox.showinfo("Reporte", f"Envío finalizado.\nEnviados: {enviados}\nFallidos/Sin formato: {errores}"))
            self.view.after(0, lambda: self.view.mostrar_mensaje_estado("Envío masivo finalizado."))

        threading.Thread(target=worker, daemon=True).start()

    def enviar_recordatorio_morosos_masivo(self):
        """Busca todos los alumnos con deuda y envía recordatorios a sus apoderados."""
        estudiantes = self.db.obtener_estudiantes_completo()
        morosos = []
        
        # Filtrar quiénes tienen deuda
        for est in estudiantes:
            # est: id, nombre, grado, fecha, nombre_apo, tel, email
            id_alu, nombre_alu, _, _, nombre_apo, tel, _ = est
            deuda = self._calcular_deuda_alumno(id_alu)
            if deuda and tel:
                morosos.append((nombre_apo, tel, nombre_alu, deuda))
        
        if not morosos:
            messagebox.showinfo("Info", "No se encontraron alumnos con deuda y teléfono registrado.")
            return

        if not messagebox.askyesno("Confirmar Cobranza Masiva", f"Se encontraron {len(morosos)} alumnos morosos con teléfono.\n¿Desea enviar los recordatorios por WhatsApp?"):
            return

        self.view.mostrar_mensaje_estado("Iniciando cobranza masiva...")
        
        def worker():
            enviados = 0
            errores = 0
            for nombre_apo, tel, nombre_alu, deuda in morosos:
                tel = tel.strip()
                if not tel.startswith("+"):
                    errores += 1
                    continue
                
                deuda_str = ", ".join(deuda)
                mensaje = (f"Estimado/a {nombre_apo}, le recordamos que el alumno {nombre_alu} "
                           f"tiene pendientes: {deuda_str}. Favor regularizar. Atte, {self.nombre_escuela}")
                
                if WhatsAppService.enviar_mensaje(tel, mensaje):
                    enviados += 1
                else:
                    errores += 1
                time.sleep(8)
            
            self.view.after(0, lambda: messagebox.showinfo("Reporte Cobranza", f"Proceso finalizado.\nEnviados: {enviados}\nFallidos: {errores}"))
            self.view.after(0, lambda: self.view.mostrar_mensaje_estado("Cobranza masiva finalizada."))

        threading.Thread(target=worker, daemon=True).start()

    def _worker_recibo(self, file_path, datos_pago):
        try:
            ReportService.generar_recibo_pago_pdf(file_path, datos_pago, self.nombre_escuela)
            self.view.after(0, lambda: self._finalizar_tarea_visual("Recibo generado correctamente"))
        except Exception as e:
            self.view.after(0, lambda: self._finalizar_tarea_visual(f"Error: {e}", es_error=True))

    def exportar_pagos_csv(self):
        datos = self.db.obtener_historial_pagos()
        headers = ["ID Pago", "Alumno", "Grado", "Monto", "Mes", "Pagado (1=Sí, 0=No)", "Fecha Pago"]
        self._exportar_csv(datos, headers, "Historial_Pagos.csv", "Guardar historial de pagos")

    def exportar_morosos_csv(self, datos: List[Any], titulo_reporte: str):
        headers = ["ID Alumno", "Nombre", "Grado", "Apoderado", "Teléfono", "Meses Adeudados"]
        # Limpiamos el título para usarlo de nombre de archivo
        nombre_archivo = f"Reporte_{titulo_reporte.replace(' ', '_').replace('(', '').replace(')', '')}.csv"
        self._exportar_csv(datos, headers, nombre_archivo, "Guardar reporte de morosos")

    # --- Métodos de Borrado Masivo ---

    def eliminar_todos_pagos(self):
        if messagebox.askyesno("Confirmar Eliminación", "ADVERTENCIA: ¿Está seguro de que desea eliminar TODOS los registros de pagos?\nEsta acción no se puede deshacer."):
            self.db.eliminar_todos_pagos()
            self.view.mostrar_mensaje_estado("Todos los pagos han sido eliminados.")
            self.actualizar_pagos_ui()
            self.actualizar_dashboard()

    def eliminar_todos_alumnos(self):
        if messagebox.askyesno("Confirmar Eliminación", "ADVERTENCIA: ¿Está seguro de que desea eliminar TODOS los alumnos?\nEsto también eliminará todos los historiales de pago asociados.\nEsta acción no se puede deshacer."):
            self.db.eliminar_todos_estudiantes()
            self.view.mostrar_mensaje_estado("Todos los alumnos y sus pagos han sido eliminados.")
            self.actualizar_alumnos()
            self.actualizar_pagos_ui()
            self.actualizar_dashboard()

    def eliminar_todos_apoderados(self):
        if messagebox.askyesno("Confirmar Eliminación", "ADVERTENCIA: ¿Está seguro de que desea eliminar TODOS los apoderados?\nEsta acción no se puede deshacer."):
            try:
                self.db.eliminar_todos_apoderados()
                self.view.mostrar_mensaje_estado("Todos los apoderados han sido eliminados.")
                self.actualizar_apoderados()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # --- Métodos de Persistencia y Backup Automático ---

    def _cargar_config_app(self):
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _guardar_config_app(self, db_path):
        try:
            config = {"last_db_path": os.path.abspath(db_path)}
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error guardando config: {e}")

    def _crear_backup_automatico(self):
        """Crea una copia de seguridad y mantiene solo las últimas 10."""
        try:
            if not os.path.exists(self.db.db_path): return
            
            # Crear carpeta backups si no existe
            if not os.path.exists(self.BACKUP_DIR):
                os.makedirs(self.BACKUP_DIR)
            
            # Nombre: original_auto_YYYYMMDD_HHMMSS.db
            nombre_base = os.path.basename(self.db.db_path)
            nombre_sin_ext = os.path.splitext(nombre_base)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{nombre_sin_ext}_auto_{timestamp}.db"
            backup_path = os.path.join(self.BACKUP_DIR, backup_name)
            
            shutil.copy(self.db.db_path, backup_path)

            # Limpieza: Mantener solo los 10 archivos más recientes
            archivos = [os.path.join(self.BACKUP_DIR, f) for f in os.listdir(self.BACKUP_DIR) if f.endswith(".db")]
            # Ordenar por fecha de modificación (el más viejo primero)
            archivos.sort(key=os.path.getmtime)
            
            while len(archivos) > 10:
                os.remove(archivos[0]) # Borrar el más viejo
                archivos.pop(0)
                
        except Exception as e:
            print(f"Error creando backup automático: {e}")

    def _ejecutar_envio_whatsapp(self, telefono, mensaje):
        if not WhatsAppService.hay_internet():
            messagebox.showerror("Error", "No se detecta conexión a internet.")
            return

        self.view.mostrar_mensaje_estado("Abriendo WhatsApp Web, por favor espere...")
        
        def worker():
            exito = WhatsAppService.enviar_mensaje(telefono, mensaje)
            if exito:
                self.view.after(0, lambda: self.view.mostrar_mensaje_estado("Mensaje enviado (verifique su navegador)."))
            else:
                self.view.after(0, lambda: messagebox.showerror("Error", "Fallo al enviar mensaje."))

        threading.Thread(target=worker, daemon=True).start()

    # --- Métodos Auxiliares ---

    def _validar_datos_apoderado(self, nombre: str, tel: str, email: str) -> Optional[tuple]:
        nombre = nombre.strip() if nombre else ""
        tel = tel.strip() if tel else ""
        email = email.strip() if email else ""

        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return None
        
        if tel:
            if not re.match(r"^\+[\d\s-]+$", tel):
                messagebox.showwarning("Aviso", "Se recomienda usar el formato internacional (+52...) para las funciones de WhatsApp.")
            elif not re.match(r"^\+?[\d\s-]+$", tel):
                messagebox.showerror("Error", "El teléfono contiene caracteres inválidos")
                return None

        if not self._validar_email(email):
            messagebox.showerror("Error", "El formato del email es inválido (ej: correo@dominio.com)")
            return None
            
        return nombre, tel, email

    def _calcular_deuda_alumno(self, id_alumno: int) -> List[str]:
        now = datetime.now()
        mes_actual_idx = now.month - 1
        
        # Si el día actual es menor al día de cobranza, el mes actual no se considera deuda
        if now.day < self.dia_cobranza:
            mes_actual_idx -= 1
            
        if mes_actual_idx < self.INICIO_CLASES_IDX:
             return []

        meses_requeridos = self.MESES[self.INICIO_CLASES_IDX : mes_actual_idx + 1]
        pagos = self.db.obtener_pagos_alumno(id_alumno)
        meses_pagados = {p[0] for p in pagos}
        
        return [m for m in meses_requeridos if m not in meses_pagados]

    def _validar_email(self, email: str) -> bool:
        # Regex mejorado para validación de email
        if email and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return False
        return True

    def leer_documentacion(self, nombre_archivo: str) -> str:
        """Lee un archivo de texto/markdown buscando en la ruta correcta (exe o script)."""
        path = None
        if getattr(sys, 'frozen', False):
            # Si es ejecutable (PyInstaller), buscar en carpeta temporal _MEIPASS o junto al exe
            if hasattr(sys, '_MEIPASS'):
                path = os.path.join(sys._MEIPASS, nombre_archivo)
            else:
                path = os.path.join(os.path.dirname(sys.executable), nombre_archivo)
        else:
            # Si es script, buscar en la raíz del proyecto (subir desde src/)
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), nombre_archivo)
            
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error al leer el archivo: {e}"
        return "Archivo de documentación no encontrado.\nAsegúrese de que el archivo .md esté en la carpeta del programa."

    def _exportar_csv(self, datos: List[Any], headers: List[str], default_name: str, title: str):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv")], 
            initialfile=default_name, 
            title=title
        )
        if not file_path: 
            return

        self.view.configure(cursor="watch") # Cambiar cursor a espera
        def worker():
            try:
                ReportService.exportar_csv(file_path, headers, datos)
                self.view.after(0, lambda: self._finalizar_tarea_visual("Archivo exportado correctamente"))
            except Exception as e:
                self.view.after(0, lambda: self._finalizar_tarea_visual(f"Error: {e}", es_error=True))

        threading.Thread(target=worker, daemon=True).start()

    def _finalizar_tarea_visual(self, mensaje, es_error=False):
        """Restaura el cursor y muestra mensaje."""
        self.view.configure(cursor="")
        if es_error:
            messagebox.showerror("Error", mensaje)
        else:
            self.view.mostrar_mensaje_estado(mensaje)

if __name__ == "__main__":
    controller = SchoolController()
    controller.iniciar()