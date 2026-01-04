import csv
from typing import List, Any
from datetime import datetime

# Intentar importar reportlab, manejar error si no existe
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER
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

        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = styles["Heading1"]
        title_style.alignment = TA_CENTER
        elements.append(Paragraph(f"Ficha del Estudiante - {nombre_escuela}", title_style))
        elements.append(Spacer(1, 20))
        
        # Datos del Alumno y Apoderado (Tabla)
        data_info = [
            ["Información del Alumno", "", "Información del Apoderado", ""],
            ["Nombre:", nombre_alu, "Nombre:", nombre_apo],
            ["Grado:", grado, "Teléfono:", tel_apo],
            ["Fecha Reg:", fecha_reg, "Email:", email_apo]
        ]
        
        t_info = Table(data_info, colWidths=[80, 180, 80, 180])
        t_info.setStyle(TableStyle([
            ('SPAN', (0,0), (1,0)), # Título Alumno
            ('SPAN', (2,0), (3,0)), # Título Apoderado
            ('BACKGROUND', (0,0), (3,0), colors.lightgrey),
            ('FONTNAME', (0,0), (3,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 20))
        
        # Historial de Pagos
        elements.append(Paragraph("Historial de Pagos", styles["Heading2"]))
        elements.append(Spacer(1, 10))
        
        data_pagos = [["Mes", "Monto", "Fecha Pago"]]
        for p in pagos:
            mes, monto, fecha = p
            data_pagos.append([mes, f"${monto:,.0f}", str(fecha) if fecha else "Pendiente"])
        
        if not pagos:
            data_pagos.append(["Sin registros", "-", "-"])
        
        t_pagos = Table(data_pagos, colWidths=[150, 150, 200])
        t_pagos.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.beige]),
        ]))
        elements.append(t_pagos)

        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Generado por Sistema de Gestión Escolar - {datetime.now().strftime('%d/%m/%Y')}", styles["Italic"]))
        
        doc.build(elements)

    @staticmethod
    def generar_recibo_pago_pdf(file_path: str, datos_pago: tuple, nombre_escuela: str):
        """Genera un recibo de pago individual."""
        if not HAS_REPORTLAB: return

        # datos_pago: (id, nombre_alu, grado, monto, mes, fecha)
        id_pago, nombre_alu, grado, monto, mes, fecha = datos_pago
        
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = styles["Heading1"]
        title_style.alignment = TA_CENTER
        elements.append(Paragraph(f"RECIBO DE PAGO - {nombre_escuela.upper()}", title_style))
        elements.append(Spacer(1, 20))
        
        # Datos
        data = [
            ["N° Transacción:", f"#{id_pago:06d}"],
            ["Fecha:", str(fecha)],
            ["Recibimos de:", nombre_alu],
            ["Grado/Curso:", grado],
            ["Concepto:", f"Mensualidad {mes}"],
            ["Monto Total:", f"${monto:,.0f}"]
        ]
        
        t = Table(data, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BOX', (0,0), (-1,-1), 2, colors.black),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 30))
        
        footer_style = styles["Italic"]
        footer_style.alignment = TA_CENTER
        elements.append(Paragraph("Gracias por su pago.", footer_style))
        
        doc.build(elements)
