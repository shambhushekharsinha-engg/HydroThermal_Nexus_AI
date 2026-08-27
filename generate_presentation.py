import os
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def draw_background(canvas, doc):
    width, height = doc.pagesize
    canvas.saveState()
    canvas.setFillColor(HexColor("#0A192F"))
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setStrokeColor(HexColor("#64FFDA"))
    canvas.setLineWidth(2)
    canvas.line(40, 40, width-40, 40)
    canvas.line(40, height-40, width-40, height-40)
    canvas.restoreState()

def create_presentation(filename):
    doc = SimpleDocTemplate(
        filename, 
        pagesize=landscape(letter),
        leftMargin=50, rightMargin=50,
        topMargin=50, bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    # ── Custom Styles for Dark Theme ──
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=42, leading=48,
        textColor=HexColor("#64FFDA"), alignment=TA_CENTER,
        spaceAfter=20
    )
    
    slide_title_style = ParagraphStyle(
        'SlideTitle', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=30, leading=36,
        textColor=HexColor("#64FFDA"), alignment=TA_LEFT,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', parent=styles['Heading2'],
        fontName='Helvetica-Oblique', fontSize=22, leading=28,
        textColor=HexColor("#E6F1FF"), alignment=TA_CENTER,
        spaceAfter=15
    )

    details_style = ParagraphStyle(
        'DetailsStyle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=18, leading=24,
        textColor=HexColor("#8892B0"), alignment=TA_CENTER,
        spaceAfter=8
    )
    
    link_style = ParagraphStyle(
        'LinkStyle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=16, leading=22,
        textColor=HexColor("#00D4FF"), alignment=TA_CENTER,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyStyle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=16, leading=22,
        textColor=HexColor("#E6F1FF"), alignment=TA_LEFT,
        spaceAfter=12
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle', parent=body_style,
        leftIndent=25, bulletIndent=12, spaceAfter=10
    )

    caption_style = ParagraphStyle(
        'CaptionStyle', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=12, leading=16,
        textColor=HexColor("#8892B0"), alignment=TA_CENTER,
        spaceAfter=10
    )

    story = []

    # ---------------- SLIDE 1: TITLE ----------------
    story.append(Spacer(1, 30))
    story.append(Paragraph("HydroThermal Nexus-AI (v3.0)", title_style))
    story.append(Paragraph("Autonomous intelligence, human-authorized actuation.", subtitle_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Developer:</b> Shambhu Shekhar Sinha", details_style))
    story.append(Paragraph("<b>College / University:</b> Greater Noida Institute of Technology", details_style))
    story.append(Spacer(1, 25))
    story.append(Paragraph("🔗 <b>Live Prototype:</b> hydrothermal-nexus-ai.streamlit.app", link_style))
    story.append(Paragraph("🔗 <b>GitHub Repo:</b> github.com/shambhushekharsinha-engg/HydroThermal_Nexus_AI", link_style))
    story.append(PageBreak())

    # ---------------- SLIDE 2: INNOVATION & DIFFERENTIATION ----------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("1. Innovation & Platform Differentiation", slide_title_style))
    story.append(Paragraph("Nexus-AI is not just a dashboard; it is an industrial operations decision-support platform bridging anomaly detection with automated mitigation workflows.", body_style))
    
    innovation_data = [
        ["Layer", "Nexus-AI Contribution"],
        ["Detection", "IsolationForest + Adaptive Z-score on 1Hz Telemetry"],
        ["Diagnosis", "Enriched RCA + 3-Level Fault Trees + Confidence % + MTTR"],
        ["Decision", "Mitigation Recommendations (Operator-in-the-loop actuation)"],
        ["Sustainability", "Dynamic Water/Carbon Tracking & Live Financial ESG Impact"],
        ["Governance", "Strict RBAC + Immutable SHA-256 Audit Ledger + PDF Reporting"]
    ]
    t_inn = Table(innovation_data, colWidths=[150, 500])
    t_inn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#112240")),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor("#64FFDA")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 14),
        ('TEXTCOLOR', (0,1), (-1,-1), HexColor("#E6F1FF")),
        ('GRID', (0,0), (-1,-1), 1, HexColor("#8892B0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 10))
    story.append(t_inn)
    story.append(PageBreak())

    # ---------------- SLIDE 3: SYSTEM ARCHITECTURE & DATA FLOW ----------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. System Architecture & Data Flow", slide_title_style))
    story.append(Paragraph("The system processes live telemetry through a strict pipeline, converting raw data into auditable actions.", body_style))
    
    flow_data = [
        ["1. Ingestion", "2. ML Detection", "3. Diagnostics (RCA)", "4. Dispatch & UI"],
        ["1Hz Sensor Data\n(Temp, Vib, PSI)", "IsolationForest\n(Feature Imp.)", "Fault Tree Logic\n+ MTTR Calc", "FastAPI Core\n-> Streamlit UI"],
        ["SQLite WAL\nPersistence", "Z-Score\nThresholding", "Severity\nClassification", "Telegram Alert\n+ PDF Report"]
    ]
    t_flow = Table(flow_data, colWidths=[170]*4)
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#112240")),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor("#64FFDA")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('TEXTCOLOR', (0,1), (-1,-1), HexColor("#E6F1FF")),
        ('GRID', (0,0), (-1,-1), 1, HexColor("#8892B0")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 15))
    story.append(t_flow)
    story.append(PageBreak())

    # ---------------- SLIDE 4: TECHNOLOGY & RELIABILITY ----------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Technology Stack & Reliability", slide_title_style))
    tech_data = [
        ["Layer", "Technologies Utilized", "Responsibility"],
        ["Frontend UI", "Streamlit, Plotly, PyDeck (3D)", "Dashboards, Twin, Interaction"],
        ["Backend API", "FastAPI, Pydantic, Uvicorn", "REST Endpoints, Multi-threading"],
        ["Machine Learning", "Scikit-Learn (IsolationForest)", "Anomaly Detection, Explainability"],
        ["Database", "SQLite3 (WAL mode)", "Telemetry, Audit Ledger, Settings"],
        ["Alerts & Reports", "Telegram Bot API, ReportLab", "Incident Dispatch & PDF Generation"],
        ["Deployment & CI", "Docker, Pytest, GitHub Actions", "Containerization & Reliability Testing"]
    ]
    t_tech = Table(tech_data, colWidths=[140, 260, 280])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#112240")),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor("#64FFDA")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 14),
        ('TEXTCOLOR', (0,1), (-1,-1), HexColor("#E6F1FF")),
        ('GRID', (0,0), (-1,-1), 1, HexColor("#8892B0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 10))
    story.append(t_tech)
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Testing & Reliability:</b> The project includes a 42-test Pytest suite covering auth, RBAC, ML endpoints, ESG calculations, and rate-limiting. Ensures an evaluation-ready prototype with production-style architecture.", body_style))
    story.append(PageBreak())

    # ---------------- SLIDE 5: BENCHMARKS & METHODOLOGY ----------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Simulated Evaluation Benchmark & Metrics", slide_title_style))
    story.append(Paragraph("<b>Dataset & Environment:</b> Evaluated on a simulated 1Hz telemetry benchmark across a 14,400-sample test window. Includes nominal data and 3 injected anomaly classes (Local Deployment: Intel i7 / Python 3.11).", body_style))
    story.append(Spacer(1, 15))
    
    metrics = [
        "• <b>Detection Precision:</b> 94.2% (True anomalies accurately flagged).",
        "• <b>Detection Recall:</b> 97.5% (Successful capture of injected fault cascades).",
        "• <b>RUL Prediction Error:</b> MAE ± 14.5 hours (on a 40,000-hour component lifespan).",
        "• <b>API Latency (p95):</b> < 11.4 ms for REST payload processing.",
        "• <b>ML Inference Latency:</b> 3.8 ms per batch via IsolationForest.",
        "• <b>Alert Delivery Latency:</b> < 1.2s via Telegram Bot API.",
        "• <b>Projected MTTR Impact:</b> Estimated 35% reduction in diagnosis time based on the simulated RCA workflow."
    ]
    for m in metrics:
        story.append(Paragraph(m, bullet_style))
    story.append(PageBreak())

    # ---------------- SLIDE 6: END-TO-END WALKTHROUGH ----------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. End-to-End Walkthrough: Anomaly Loop", slide_title_style))
    story.append(Paragraph("How the system reacts to a <b>Pipe Rupture</b> event:", body_style))
    
    walkthrough = [
        "1. <b>Telemetry Spike:</b> Sensors record sharp drop in Water Pressure and Flow.",
        "2. <b>Isolation Forest:</b> ML bounds flag the data points as anomalous (Score -0.85).",
        "3. <b>RCA Engine:</b> Rule-engine processes the ML flags -> Maps to 'Pipe Rupture' fault tree (92% Confidence).",
        "4. <b>Mitigation UI:</b> Operator receives UI warning & mitigation recommendation.",
        "5. <b>Human-in-the-Loop Actuation:</b> Operator clicks 'Engage Safety Valve'.",
        "6. <b>Telegram Alert:</b> Dispatcher pushes the incident details to the engineering team.",
        "7. <b>Audit Ledger & Reporting:</b> SHA-256 hash records the operator's intervention; PDF Report generated."
    ]
    for w in walkthrough:
        story.append(Paragraph(w, bullet_style))
    story.append(PageBreak())

    # ---------------- PROTOTYPE SCREENSHOT SHOWCASE ----------------

    screenshot_groups = [
        ("Prototype: Command Center & Digital Twin", 
         "Project Demo/frontend/Main_Command_Center_Dashboard.png", "Command Center: Live telemetry, dynamic KPIs, and 3 anomaly injection missions.",
         "Project Demo/frontend/GeoSpatial_Digital_Twin.png", "Digital Twin: 3D PyDeck representation tracking equipment states spatially."),
         
        ("Prototype: Analytics & Root Cause Analysis", 
         "Project Demo/frontend/Telemetry_and_Analytics_Console.png", "Analytics Console: IsolationForest ML bounds mapping live sensor deviations.",
         "Project Demo/frontend/RCA_Diagnostic_Engine.png", "RCA Engine: Fault cascade trees, confidence scores, and MTTR diagnostics."),
         
        ("Prototype: Alerts & ESG Tracking", 
         "Project Demo/frontend/Alert_Management_Center.png", "Alert Center: Telegram dispatch gateway with severity-based escalation.",
         "Project Demo/frontend/ESG_Carbon_and_Sustainability_Dashboard.png", "ESG Dashboard: Live carbon footprint offsets and financial efficiency tracking."),
         
        ("Prototype: AI Assistant & Audit Ledger", 
         "Project Demo/frontend/AI_Assistant_Chat_Interface.png", "AI Assistant: Domain-aware ESG copilot with quick-action prompt chips.",
         "Project Demo/frontend/Immutable_Audit_Ledger.png", "Audit Ledger: SHA-256 immutable logging of all operational interventions."),
         
        ("Prototype: Authentication & API Backend", 
         "Project Demo/frontend/User_Login_and_Demo_Credentials.png", "Authentication: Role-Based Access Control (Admin, Operator, Viewer).",
         "Project Demo/backend/FastAPI_Backend_Endpoints_Swagger.png", "Backend API: Comprehensive REST Swagger documentation via FastAPI.")
    ]

    for title, img1_path, desc1, img2_path, desc2 in screenshot_groups:
        story.append(Spacer(1, 10))
        story.append(Paragraph(title, slide_title_style))
        story.append(Spacer(1, 10))
        
        i1 = Image(img1_path, width=320, height=190, kind='proportional') if os.path.exists(img1_path) else Paragraph("[Image missing]", caption_style)
        i2 = Image(img2_path, width=320, height=190, kind='proportional') if os.path.exists(img2_path) else Paragraph("[Image missing]", caption_style)
        
        p1 = Paragraph(desc1, caption_style)
        p2 = Paragraph(desc2, caption_style)
        
        img_table = Table(
            [[i1, i2], [p1, p2]], 
            colWidths=[340, 340]
        )
        img_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        
        story.append(img_table)
        story.append(PageBreak())

    # ---------------- SLIDE: CONCLUSION ----------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("Thank You!", title_style))
    story.append(Paragraph("Production-style architecture / evaluation-ready prototype.", subtitle_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("🔗 github.com/shambhushekharsinha-engg/HydroThermal_Nexus_AI", link_style))

    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"Final Presentation generated successfully: {filename}")

if __name__ == "__main__":
    output_filename = "Shambhu_Shekhar_Sinha_HydroThermal_Nexus_AI_Presentation.pdf"
    create_presentation(output_filename)
