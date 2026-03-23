from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Image as RLImage, Table, TableStyle,
                                 HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

# ─────────────────────────────────────────────
# COLOR PALETTE (Premium Dark Medical)
# ─────────────────────────────────────────────
DARK_BG      = colors.HexColor('#0d1117')
ACCENT_BLUE  = colors.HexColor('#00aaff')
ACCENT_TEAL  = colors.HexColor('#00c9a7')
WHITE        = colors.white
LIGHT_GREY   = colors.HexColor('#c9d1d9')
MID_GREY     = colors.HexColor('#30363d')
RED_ALERT    = colors.HexColor('#e74c3c')
GREEN_OK     = colors.HexColor('#2ecc71')

# ─────────────────────────────────────────────
# GENERATE FULL PDF REPORT
# ─────────────────────────────────────────────
def generate_pdf_report(report_data, save_path):
    """
    Generates a full premium PDF radiology report.

    report_data dict keys:
    - patient_name, patient_age, patient_gender, patient_id
    - doctor_name, doctor_designation
    - scan_date, scan_id
    - predicted_label, confidence, all_scores
    - original_img_path, heatmap_img_path, overlay_img_path
    - findings, recommendation
    - hospital_name, hospital_subtitle
    """

    doc = SimpleDocTemplate(
        save_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── HEADER ──────────────────────────────
    header_style = ParagraphStyle('header',
        fontSize=20, fontName='Helvetica-Bold',
        textColor=ACCENT_BLUE, alignment=TA_CENTER, spaceAfter=4)

    sub_style = ParagraphStyle('sub',
        fontSize=10, fontName='Helvetica',
        textColor=LIGHT_GREY, alignment=TA_CENTER, spaceAfter=2)

    story.append(Paragraph(report_data.get('hospital_name', 'Radiology AI Centre'), header_style))
    story.append(Paragraph(report_data.get('hospital_subtitle', 'Advanced Chest X-Ray Diagnostic System'), sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=10))

    # ── REPORT TITLE ────────────────────────
    title_style = ParagraphStyle('title',
        fontSize=15, fontName='Helvetica-Bold',
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=10)

    story.append(Paragraph("CHEST X-RAY AI DIAGNOSTIC REPORT", title_style))

    # ── PATIENT INFO TABLE ───────────────────
    label_style = ParagraphStyle('label',
        fontSize=9, fontName='Helvetica-Bold', textColor=ACCENT_TEAL)
    value_style = ParagraphStyle('value',
        fontSize=9, fontName='Helvetica', textColor=LIGHT_GREY)

    patient_data = [
        [Paragraph("Patient Name:", label_style),
         Paragraph(report_data.get('patient_name', 'N/A'), value_style),
         Paragraph("Scan Date:", label_style),
         Paragraph(report_data.get('scan_date', datetime.now().strftime('%d %b %Y')), value_style)],

        [Paragraph("Age / Gender:", label_style),
         Paragraph(f"{report_data.get('patient_age','N/A')} / {report_data.get('patient_gender','N/A')}", value_style),
         Paragraph("Scan ID:", label_style),
         Paragraph(report_data.get('scan_id', 'N/A'), value_style)],

        [Paragraph("Patient ID:", label_style),
         Paragraph(report_data.get('patient_id', 'N/A'), value_style),
         Paragraph("Reporting Doctor:", label_style),
         Paragraph(report_data.get('doctor_name', 'N/A'), value_style)],
    ]

    patient_table = Table(patient_data, colWidths=[3*cm, 6*cm, 3.5*cm, 6*cm])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), MID_GREY),
        ('GRID',        (0,0), (-1,-1), 0.5, ACCENT_BLUE),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [MID_GREY, DARK_BG]),
        ('TOPPADDING',  (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.3*inch))

    # ── AI PREDICTION RESULT ─────────────────
    result_label = report_data.get('predicted_label', 'Unknown')
    confidence   = report_data.get('confidence', 0)

    result_color = RED_ALERT if result_label != 'Normal' else GREEN_OK
    result_style = ParagraphStyle('result',
        fontSize=14, fontName='Helvetica-Bold',
        textColor=result_color, alignment=TA_CENTER, spaceAfter=5)

    story.append(Paragraph(f"AI DIAGNOSIS: {result_label.upper()}", result_style))
    story.append(Paragraph(f"Confidence Score: {confidence}%", sub_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY, spaceAfter=10))

    # ── CONFIDENCE SCORES TABLE ──────────────
    score_title = ParagraphStyle('st',
        fontSize=10, fontName='Helvetica-Bold',
        textColor=ACCENT_TEAL, spaceAfter=5)
    story.append(Paragraph("Class Confidence Breakdown:", score_title))

    score_data = [[
        Paragraph("Disease Class", label_style),
        Paragraph("Confidence %", label_style),
        Paragraph("Risk Level", label_style)
    ]]
    for s in report_data.get('all_scores', []):
        risk = "HIGH" if s['confidence'] > 60 else ("MODERATE" if s['confidence'] > 30 else "LOW")
        score_data.append([
            Paragraph(s['class'], value_style),
            Paragraph(f"{s['confidence']}%", value_style),
            Paragraph(risk, value_style)
        ])

    score_table = Table(score_data, colWidths=[6*cm, 4*cm, 4*cm])
    score_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  ACCENT_BLUE),
        ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [MID_GREY, DARK_BG]),
        ('GRID',        (0,0), (-1,-1), 0.5, ACCENT_BLUE),
        ('TOPPADDING',  (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.3*inch))

    # ── X-RAY IMAGES ────────────────────────
    story.append(Paragraph("Scan Images:", score_title))

    img_row = []
    img_labels = []

    for img_path, label in [
        (report_data.get('original_img_path'), 'Original X-Ray'),
        (report_data.get('heatmap_img_path'),  'Grad-CAM Heatmap'),
        (report_data.get('overlay_img_path'),  'Overlay Analysis')
    ]:
        if img_path and os.path.exists(img_path):
            img_row.append(RLImage(img_path, width=4.5*cm, height=4.5*cm))
            img_labels.append(Paragraph(label, sub_style))
        else:
            img_row.append(Paragraph("Not available", value_style))
            img_labels.append(Paragraph(label, sub_style))

    img_table = Table([img_row, img_labels], colWidths=[6*cm, 6*cm, 6*cm])
    img_table.setStyle(TableStyle([
        ('ALIGN',   (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',  (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',    (0,0), (-1,-1), 0.5, MID_GREY),
        ('BACKGROUND', (0,0), (-1,-1), DARK_BG),
        ('TOPPADDING',  (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
    ]))
    story.append(img_table)
    story.append(Spacer(1, 0.3*inch))

    # ── FINDINGS & RECOMMENDATION ────────────
    story.append(Paragraph("Radiologist Findings:", score_title))
    findings_style = ParagraphStyle('findings',
        fontSize=9, fontName='Helvetica',
        textColor=LIGHT_GREY, leading=14,
        borderPadding=8, spaceAfter=10)
    story.append(Paragraph(
        report_data.get('findings', 'No findings entered.'),
        findings_style))

    story.append(Paragraph("Recommendation:", score_title))
    story.append(Paragraph(
        report_data.get('recommendation', 'Please consult a licensed radiologist.'),
        findings_style))

    # ── FOOTER ──────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT_BLUE, spaceBefore=10))
    footer_style = ParagraphStyle('footer',
        fontSize=7, fontName='Helvetica',
        textColor=MID_GREY, alignment=TA_CENTER)
    story.append(Paragraph(
        "⚠️ This report is AI-assisted. Final diagnosis must be confirmed by a licensed radiologist. "
        f"Generated on {datetime.now().strftime('%d %B %Y at %I:%M %p')}",
        footer_style))

    # ── BUILD PDF ────────────────────────────
    doc.build(story)
    return save_path
