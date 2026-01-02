import csv
from typing import List, Any

# Intentar importar reportlab, manejar error si no existe
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

class ReportService:
    @staticmethod
    def exportar_csv(file_path: str, headers: List[str], datos: List[Any]):
        """Exporta datos a CSV manejando codificación y valores nulos."""
        # Limpiar datos: reemplazar None con cadena vacía
        datos_limpios = [[(str(x) if x is not None else "") for x in row] for row in datos]
        
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(datos_limpios)

    @staticmethod
    def generar_ficha_alumno_pdf(file_path: str, datos_alumno: tuple, pagos: List[tuple], nombre_escuela: str):
        """Genera el PDF de la ficha del alumno."""
        if not HAS_REPORTLAB:
            raise ImportError("La librería 'reportlab' no está instalada.")

        nombre_alu, grado, fecha_reg, nombre_apo, tel_apo, email_apo = datos_alumno
        
        # Manejo de valores nulos
        tel_apo = tel_apo if tel_apo else "No registrado"
        email_apo = email_apo if email_apo else "No registrado"
        fecha_reg = fecha_reg if fecha_reg else "No registrada"

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        
        # Encabezado
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Ficha del Estudiante")
        
        # Datos Alumno
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Nombre del Alumno: {nombre_alu}")
        c.drawString(50, height - 120, f"Grado/Curso: {grado}")
        c.drawString(350, height - 120, f"Fecha Registro: {fecha_reg}")
        
        c.line(50, height - 140, width - 50, height - 140)
        
        # Datos Apoderado
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
        
        for p in pagos[:15]: # Mostrar solo los últimos 15
            mes, monto, fecha = p
            c.drawString(50, y, str(mes))
            c.drawString(200, y, f"${monto:,.0f}")
            c.drawString(350, y, str(fecha) if fecha else "")
            y -= 15

        # Pie de página
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, f"Generado por Sistema de Gestión Escolar - {nombre_escuela}")
        
        c.save()

    @staticmethod
    def generar_recibo_pago_pdf(file_path: str, datos_pago: tuple, nombre_escuela: str):
        """Genera un recibo de pago individual."""
        if not HAS_REPORTLAB: return

        # datos_pago: (id, nombre_alu, grado, monto, mes, fecha)
        id_pago, nombre_alu, grado, monto, mes, fecha = datos_pago
        
        # Usamos media carta o similar para recibos, pero letter está bien por simplicidad
        c = canvas.Canvas(file_path, pagesize=letter)
        
        # Diseño tipo "Voucher"
        c.setLineWidth(2)
        c.rect(50, 500, 500, 250) # Marco
        
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 720, f"RECIBO DE PAGO - {nombre_escuela.upper()}")
        
        c.setFont("Helvetica", 12)
        c.drawString(70, 680, f"N° de Transacción: #{id_pago:06d}")
        c.drawString(350, 680, f"Fecha: {fecha}")
        
        c.line(70, 670, 530, 670)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(70, 630, f"Recibimos de: {nombre_alu}")
        c.setFont("Helvetica", 12)
        c.drawString(70, 610, f"Grado/Curso: {grado}")
        
        c.drawString(70, 570, f"La suma de: ${monto:,.0f}")
        c.drawString(70, 550, f"Por concepto de: Mensualidad {mes}")
        
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(300, 520, "Gracias por su pago.")
        
        c.save()
