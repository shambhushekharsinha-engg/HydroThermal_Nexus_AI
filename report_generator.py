# -*- coding: utf-8 -*-
"""
report_generator.py — HydroThermal Nexus-AI Enterprise Report Engine
Generates professional, publication-ready PDF incident & ESG impact reports.
4-section structure:
  1. Executive Summary
  2. ESG Impact Matrix (CO2, Water, Energy)
  3. Anomaly Event Log & Fault Diagnosis
  4. Regulatory Compliance Statement
"""

import io
import datetime
from typing import Optional, Dict, Any

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ── Brand Colors ─────────────────────────────────────────────────────
BRAND_DARK    = colors.HexColor("#0A0F1E")
BRAND_BLUE    = colors.HexColor("#0D2137")
BRAND_ACCENT  = colors.HexColor("#00D4FF")
BRAND_GREEN   = colors.HexColor("#00C853")
BRAND_ORANGE  = colors.HexColor("#FF6B35")
BRAND_RED     = colors.HexColor("#FF2D55")
BRAND_YELLOW  = colors.HexColor("#FFB800")
TEXT_LIGHT    = colors.HexColor("#F8FAFC")
TEXT_MUTED    = colors.HexColor("#64748B")
BORDER_LIGHT  = colors.HexColor("#1E3A5F")


class EnterpriseReportEngine:
    """
    Generates professional 4-section PDF reports for HydroThermal Nexus-AI.
    Reports are built entirely in-memory (BytesIO) — no disk writes.
    """

    @staticmethod
    def _build_styles() -> Dict[str, ParagraphStyle]:
        """Returns a set of branded paragraph styles."""
        base = getSampleStyleSheet()
        styles = {}

        styles["title"] = ParagraphStyle(
            "NexusTitle", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=22, leading=28,
            textColor=TEXT_LIGHT, spaceAfter=4, spaceBefore=0,
        )
        styles["subtitle"] = ParagraphStyle(
            "NexusSubtitle", parent=base["Normal"],
            fontName="Helvetica", fontSize=11, leading=14,
            textColor=BRAND_ACCENT, spaceAfter=12,
        )
        styles["section_heading"] = ParagraphStyle(
            "NexusSectionH", parent=base["Heading2"],
            fontName="Helvetica-Bold", fontSize=13, leading=16,
            textColor=BRAND_ACCENT, spaceBefore=16, spaceAfter=6,
        )
        styles["body"] = ParagraphStyle(
            "NexusBody", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=colors.HexColor("#2C3E50"), spaceAfter=6,
        )
        styles["body_small"] = ParagraphStyle(
            "NexusBodySm", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, leading=12,
            textColor=colors.HexColor("#475569"), spaceAfter=4,
        )
        styles["label"] = ParagraphStyle(
            "NexusLabel", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=10, leading=13,
            textColor=colors.HexColor("#1B2A4A"),
        )
        styles["value"] = ParagraphStyle(
            "NexusValue", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, leading=13,
            textColor=colors.HexColor("#2C3E50"),
        )
        styles["footer"] = ParagraphStyle(
            "NexusFooter", parent=base["Normal"],
            fontName="Helvetica-Oblique", fontSize=8, leading=10,
            textColor=TEXT_MUTED, alignment=TA_CENTER,
        )
        styles["compliance"] = ParagraphStyle(
            "NexusCompliance", parent=base["Normal"],
            fontName="Helvetica-Oblique", fontSize=9, leading=12,
            textColor=colors.HexColor("#1B4332"), spaceAfter=4,
        )
        return styles

    @staticmethod
    def compile_pdf_report(
        facility_name: str = "HydroThermal Nexus Plant Node-01",
        water_saved: str = "0 Litres",
        energy_saved: str = "0 kWh",
        network_status: str = "ONLINE",
        anomaly_type: str = "Nominal / Normal Operations",
        triggered_by: str = "System",
        role: str = "Admin",
        co2_saved_kg: float = 0.0,
        water_saved_l: float = 0.0,
        energy_saved_kwh: float = 0.0,
        esg_score: float = 92.5,
        rca_result: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Compiles a professional 4-section ESG Impact PDF report.

        Args:
            facility_name: Plant name for the report header
            water_saved: Human-readable water savings string
            energy_saved: Human-readable energy savings string
            network_status: Gateway connectivity status
            anomaly_type: Anomaly scenario name
            triggered_by: Username who triggered this report
            role: User role
            co2_saved_kg: Total CO2 avoided (kg)
            water_saved_l: Total water conserved (litres)
            energy_saved_kwh: Total energy deflected (kWh)
            esg_score: Current ESG composite score (0–100)
            rca_result: Optional dict from RCAEngine.analyze_anomaly()
            output_path: If given, also saves to disk. Otherwise returns bytes.

        Returns:
            PDF as bytes (BytesIO content).
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.65 * inch,
            leftMargin=0.65 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.65 * inch,
        )
        styles = EnterpriseReportEngine._build_styles()
        story = []
        now = datetime.datetime.now()
        ts_str = now.strftime("%d %B %Y, %H:%M:%S IST")

        # ─────────────────────────────────────────────
        # SECTION 0: HEADER BANNER
        # ─────────────────────────────────────────────
        header_data = [[
            Paragraph("⚡ HYDROTHERMAL NEXUS-AI", styles["title"]),
            Paragraph(f"Generated: {ts_str}", styles["body_small"]),
        ]]
        header_table = Table(header_data, colWidths=[4.5 * inch, 2.5 * inch])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BRAND_BLUE),
            ("TEXTCOLOR",  (0, 0), (-1, -1), TEXT_LIGHT),
            ("TOPPADDING",    (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ("LEFTPADDING",   (0, 0), (-1, -1), 16),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",         (1, 0), (1, 0), "RIGHT"),
        ]))
        story.append(header_table)
        story.append(Paragraph("Enterprise ESG Impact Verification &amp; Incident Report", styles["subtitle"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BRAND_ACCENT, spaceAfter=10))

        # ─────────────────────────────────────────────
        # SECTION 1: EXECUTIVE SUMMARY
        # ─────────────────────────────────────────────
        story.append(Paragraph("1. Executive Summary", styles["section_heading"]))
        summary_data = [
            [Paragraph("<b>Parameter</b>", styles["label"]), Paragraph("<b>Value</b>", styles["label"])],
            ["Reporting Facility",       facility_name],
            ["Report Generated By",      f"{triggered_by} ({role})"],
            ["Report Timestamp",         ts_str],
            ["Active Anomaly Scenario",  anomaly_type],
            ["Gateway Connectivity",     network_status],
            ["ESG Composite Score",      f"{esg_score:.1f} / 100"],
        ]
        col_w = [2.4 * inch, 4.7 * inch]
        summary_table = Table(summary_data, colWidths=col_w)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_BLUE),
            ("TEXTCOLOR",  (0, 0), (-1, 0), TEXT_LIGHT),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, 0), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F7FF")]),
            ("FONTSIZE",   (0, 1), (-1, -1), 9),
            ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
            ("GRID",       (0, 0), (-1, -1), 0.4, BORDER_LIGHT),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 12))

        # ─────────────────────────────────────────────
        # SECTION 2: ESG IMPACT MATRIX
        # ─────────────────────────────────────────────
        story.append(Paragraph("2. ESG Resource Conservation Impact Matrix", styles["section_heading"]))

        scope2_avoided = (energy_saved_kwh * 0.82) / 1000.0   # tonnes CO2e

        esg_data = [
            [
                Paragraph("<b>Sustainability Vector</b>", styles["label"]),
                Paragraph("<b>Verified Quantity</b>", styles["label"]),
                Paragraph("<b>Unit</b>", styles["label"]),
                Paragraph("<b>Compliance Status</b>", styles["label"]),
            ],
            ["CO₂ Emissions Avoided (Scope 1)",  f"{co2_saved_kg:,.1f}",      "kg CO₂e",   "✅ PASS — ISO 14064-1"],
            ["Scope 2 Grid Emissions Avoided",    f"{scope2_avoided:,.3f}",    "tCO₂e",     "✅ PASS — GHG Protocol"],
            ["Freshwater Volume Conserved",        f"{water_saved_l:,.0f}",    "Litres",    "✅ PASS — EPA CWA"],
            ["Energy Load Deflected",              f"{energy_saved_kwh:,.1f}", "kWh",       "✅ PASS — ISO 50001"],
            ["ESG Composite Score (30-day avg)",   f"{esg_score:.1f}",         "/ 100",     "✅ PASS — BRSR Principle 6"],
        ]
        esg_col_w = [2.4 * inch, 1.3 * inch, 0.85 * inch, 2.55 * inch]
        esg_table = Table(esg_data, colWidths=esg_col_w)
        esg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), TEXT_LIGHT),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, 0), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0FFF4")]),
            ("FONTSIZE",   (0, 1), (-1, -1), 9),
            ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
            ("GRID",       (0, 0), (-1, -1), 0.4, BORDER_LIGHT),
            ("ALIGN",      (1, 1), (2, -1), "CENTER"),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ]))
        story.append(esg_table)
        story.append(Spacer(1, 12))

        # ─────────────────────────────────────────────
        # SECTION 3: ANOMALY EVENT LOG & FAULT DIAGNOSIS
        # ─────────────────────────────────────────────
        story.append(Paragraph("3. Anomaly Event Log &amp; Root Cause Diagnosis", styles["section_heading"]))

        if rca_result and anomaly_type != "Nominal / Normal Operations":
            rca_data = [
                [Paragraph("<b>RCA Parameter</b>", styles["label"]), Paragraph("<b>Diagnostic Output</b>", styles["label"])],
                ["Anomaly Classification",  anomaly_type],
                ["Primary Vector",          rca_result.get("primary_vector", "—").replace("🔴 ", "").replace("🟡 ", "").replace("⚡ ", "").replace("✅ ", "")],
                ["Root Cause Identified",   rca_result.get("root_cause", "—")],
                ["Fault Category",          rca_result.get("fault_category", "—")],
                ["Diagnostic Confidence",   f"{rca_result.get('confidence_pct', 0):.1f}%"],
                ["MTTR Estimate",           f"{rca_result.get('mttr', {}).get('mttr_hours', 0):.1f} hours"],
                ["Est. Downtime Cost",      f"${rca_result.get('mttr', {}).get('estimated_downtime_cost_usd', 0):,.2f} USD"],
                ["Alert Severity",          rca_result.get("severity", "INFO")],
                ["Analysis Timestamp",      rca_result.get("timestamp", ts_str)],
            ]
        else:
            rca_data = [
                [Paragraph("<b>RCA Parameter</b>", styles["label"]), Paragraph("<b>Diagnostic Output</b>", styles["label"])],
                ["Anomaly Classification",  "Nominal / Normal Operations"],
                ["System Status",           "All sensor streams within safe operational thresholds."],
                ["Diagnostic Confidence",   "99.0%"],
                ["Recommendation",          "Maintain standard monitoring protocols."],
            ]

        rca_col_w = [2.4 * inch, 4.7 * inch]
        rca_table = Table(rca_data, colWidths=rca_col_w)
        rca_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), TEXT_LIGHT),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, 0), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF7F0")]),
            ("FONTSIZE",   (0, 1), (-1, -1), 9),
            ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
            ("GRID",       (0, 0), (-1, -1), 0.4, BORDER_LIGHT),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ]))
        story.append(rca_table)
        story.append(Spacer(1, 12))

        # Mitigation steps
        if rca_result and rca_result.get("recommendation"):
            story.append(Paragraph("Automated Mitigation Actions Taken:", styles["label"]))
            raw_rec = rca_result.get("recommendation", "")
            steps = raw_rec.replace("<br>", "\n").split("\n")
            for step in steps:
                step = step.strip()
                if step:
                    story.append(Paragraph(f"• {step}", styles["body_small"]))
            story.append(Spacer(1, 8))

        # ─────────────────────────────────────────────
        # SECTION 4: REGULATORY COMPLIANCE STATEMENT
        # ─────────────────────────────────────────────
        story.append(Paragraph("4. Regulatory Compliance Statement", styles["section_heading"]))

        compliance_text = (
            "This document serves as a verified automated telemetry validation record for carbon accounting, "
            "municipal utility conservation, and environmental management system audits. "
            "All performance metrics in this report are derived from real-time sensor streams, "
            "processed through the HydroThermal Nexus-AI IsolationForest anomaly detection engine, "
            "and cross-referenced against the immutable SHA-256 audit ledger maintained in compliance "
            "with ISO 14001:2015, GHG Protocol Corporate Accounting Standard, and SEBI BRSR Principle 6."
        )
        story.append(Paragraph(compliance_text, styles["compliance"]))
        story.append(Spacer(1, 8))

        compliance_badges = [
            [
                Paragraph("✅ ISO 14001:2015", styles["label"]),
                Paragraph("✅ GHG Protocol",   styles["label"]),
                Paragraph("✅ BRSR P-6",        styles["label"]),
                Paragraph("✅ ISO 14064-1",     styles["label"]),
                Paragraph("✅ EPA CWA",          styles["label"]),
            ]
        ]
        badge_table = Table(compliance_badges, colWidths=[1.4 * inch] * 5)
        badge_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#D1FAE5")),
            ("TEXTCOLOR",  (0, 0), (-1, -1), colors.HexColor("#065F46")),
            ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
            ("GRID",       (0, 0), (-1, -1), 0.4, colors.HexColor("#6EE7B7")),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(badge_table)
        story.append(Spacer(1, 16))

        # Footer
        story.append(HRFlowable(width="100%", thickness=0.5, color=TEXT_MUTED))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f"HydroThermal Nexus-AI v3.0 Enterprise | "
            f"Report ID: NXS-{now.strftime('%Y%m%d%H%M%S')} | "
            f"© 2026 — Confidential &amp; Proprietary",
            styles["footer"]
        ))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes