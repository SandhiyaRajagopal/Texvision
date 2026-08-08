import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from database.models import Inspection
from typing import List

def generate_pdf_report(inspection: Inspection, defects: List[dict], output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    elements = []
    
    # Title
    elements.append(Paragraph("Fabric Defect Inspection Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Meta Information
    verdict_color = colors.green if inspection.final_verdict == "PASS" else (colors.orange if inspection.final_verdict == "REWORK" else colors.red)
    
    meta_data = [
        ["Company Name:", inspection.company_name, "Date:", inspection.timestamp.strftime("%Y-%m-%d %H:%M:%S")],
        ["Operator Name:", inspection.operator_name, "Inspection ID:", inspection.id],
        ["Roll ID:", inspection.roll_id, "Batch ID:", inspection.batch_id],
        ["Fabric Type:", inspection.fabric_type, "Final Verdict:", inspection.final_verdict]
    ]
    
    meta_table = Table(meta_data, colWidths=[90, 150, 90, 150])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (3,3), (3,3), verdict_color),
        ('TEXTCOLOR', (3,3), (3,3), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    
    elements.append(meta_table)
    elements.append(Spacer(1, 20))
    
    # Annotated Image
    if inspection.annotated_image_path and os.path.exists(inspection.annotated_image_path):
        elements.append(Paragraph("Inspection Image:", styles['Heading2']))
        img = Image(inspection.annotated_image_path, width=400, height=300)
        elements.append(img)
        elements.append(Spacer(1, 20))
        
    # Quality Summary
    elements.append(Paragraph(f"Quality Score: {inspection.quality_score}/100", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # Defects Table
    elements.append(Paragraph("Detected Defects:", styles['Heading3']))
    
    if defects:
        table_data = [["Type", "Confidence", "Dimensions (cm)", "Area (cm2)", "Severity", "Suggestion"]]
        for d in defects:
            table_data.append([
                d.get('class_name', ''),
                f"{d.get('confidence', 0):.2f}",
                f"{d.get('width_cm', 0)} x {d.get('height_cm', 0)}",
                f"{d.get('area_cm2', 0)}",
                d.get('severity', ''),
                d.get('suggestion', '')
            ])
            
        t = Table(table_data, colWidths=[60, 60, 100, 60, 70, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No defects detected.", styles['Normal']))
        
    # Build PDF
    try:
        doc.build(elements)
    except Exception as e:
        import utils.logger as log_utils
        logger = log_utils.setup_logger("report_generator")
        logger.error(f"Error generating PDF: {e}")
