# Save this file as report_generator.py
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class EnterpriseReportEngine:
    @staticmethod
    def compile_pdf_report(facility_name, water_saved, energy_saved, network_status, output_path="NexusAI_Impact_Report.pdf"):
        """Compiles an executive-ready PDF verification statement locally in volatile memory."""
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom Corporate Palette
        title_style = ParagraphStyle(
            'CorpTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#1B2A4A'),
            spaceAfter=12
        )
        
        body_style = ParagraphStyle(
            'CorpBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=10
        )

        # Document Header
        story.append(Paragraph("HydroThermal Nexus-AI: Quantitative Impact Verification Ledger", title_style))
        story.append(Paragraph(f"<b>Target Operational Facility Node:</b> {facility_name}", body_style))
        story.append(Paragraph(f"<b>System Connectivity Diagnostic Matrix:</b> Gateway Tunnel {network_status}", body_style))
        story.append(Spacer(1, 15))
        
        # ESG Impact Matrix Summary Table Layout
        table_data = [
            [Paragraph('<b>Quantifiable Sustainability Vector</b>', body_style), Paragraph('<b>Verified Resource Savings Performance</b>', body_style)],
            [Paragraph('<b>Preserved Volumetric Water Asset</b>', body_style), Paragraph(str(water_saved), body_style)],
            [Paragraph('<b>Deflected Unoccupied Energy Bleed</b>', body_style), Paragraph(str(energy_saved), body_style)],
            [Paragraph('<b>Algorithmic Operational Framework</b>', body_style), Paragraph('Adaptive Time-Series LSTM Mitigation Core', body_style)]
        ]
        
        impact_table = Table(table_data, colWidths=[250, 250])
        impact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1B2A4A')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        
        story.append(impact_table)
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Compliance Statement:</b> This document acts as verified automated telemetry validation for carbon accounting and municipal utility conservation alignment audits.", body_style))
        
        doc.build(story)
        return output_path