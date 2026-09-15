import io
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)


def _safe_str(val: Any) -> str:
    """Safely convert any value to clean string."""
    if val is None:
        return "N/A"
    return str(val).strip()


def generate_analysis_pdf_report(
    analysis_data: Dict[str, Any],
    candidate_name: Optional[str] = None,
    resume_filename: Optional[str] = None,
    job_title: Optional[str] = None,
) -> bytes:
    """
    Generate an in-memory, publication-grade PDF report from stored analysis data.
    Does NOT rerun the matching pipeline; uses strictly existing stored results.
    """
    buffer = io.BytesIO()

    # Document setup with 0.5 inch (36 pt) margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    # Base Color Palette (Matching HireLens web app)
    c_primary = colors.HexColor("#0F766E")    # Teal 700
    c_dark = colors.HexColor("#0F172A")       # Slate 900
    c_text = colors.HexColor("#334155")       # Slate 700
    c_muted = colors.HexColor("#64748B")      # Slate 500
    c_light_bg = colors.HexColor("#F8FAFC")   # Slate 50
    c_card_border = colors.HexColor("#E2E8F0")# Slate 200
    c_emerald = colors.HexColor("#065F46")    # Emerald 800
    c_rose = colors.HexColor("#9F1239")       # Rose 800
    c_amber = colors.HexColor("#92400E")      # Amber 800

    styles = getSampleStyleSheet()

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_dark,
    )
    brand_style = ParagraphStyle(
        "DocBrand",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=c_primary,
    )
    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_dark,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=c_text,
    )
    body_bold = ParagraphStyle(
        "BodyBoldCustom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=c_text,
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=c_dark,
    )
    meta_sub = ParagraphStyle(
        "MetaSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=c_muted,
    )

    story = []

    # -------------------------------------------------------------
    # 1. HEADER & BRANDING
    # -------------------------------------------------------------
    header_data = [
        [
            Paragraph("<b>HireLens</b>", brand_style),
            Paragraph(f"Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", meta_sub),
        ],
        [
            Paragraph("Resume Analysis & Job Match Report", title_style),
            Paragraph(f"Analysis ID: {_safe_str(analysis_data.get('id') or analysis_data.get('analysis_id'))[:12]}", meta_sub),
        ],
    ]
    t_header = Table(header_data, colWidths=[380, 160])
    t_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=2, spaceAfter=8))

    # -------------------------------------------------------------
    # 2. OVERVIEW INFO TABLE
    # -------------------------------------------------------------
    resolved_job = job_title or analysis_data.get("job_title") or "Target Job Match Evaluation"
    resolved_filename = resume_filename or analysis_data.get("resume_filename") or "Candidate Resume"
    resolved_candidate = candidate_name or "Authenticated Candidate"

    meta_table_data = [
        [
            Paragraph("<b>Target Position:</b>", table_cell_bold),
            Paragraph(_safe_str(resolved_job), table_cell),
            Paragraph("<b>Candidate Name:</b>", table_cell_bold),
            Paragraph(_safe_str(resolved_candidate), table_cell),
        ],
        [
            Paragraph("<b>Resume File:</b>", table_cell_bold),
            Paragraph(_safe_str(resolved_filename), table_cell),
            Paragraph("<b>Engine Model:</b>", table_cell_bold),
            Paragraph("Deterministic NLP / Normalized TF Cosine", table_cell),
        ],
    ]
    t_meta = Table(meta_table_data, colWidths=[90, 180, 95, 175])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_light_bg),
        ("BOX", (0, 0), (-1, -1), 0.75, c_card_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, c_card_border),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 3. OVERALL SCORE & SUB-SCORE BREAKDOWN
    # -------------------------------------------------------------
    overall_score = float(analysis_data.get("overall_score", 0.0))
    breakdown = analysis_data.get("score_breakdown", {})
    weights = analysis_data.get("weights", {})

    skill_score = float(breakdown.get("skill_score", 0.0))
    text_score = float(breakdown.get("text_similarity_score", 0.0))
    exp_score = float(breakdown.get("experience_score", 0.0))
    ats_score = float(breakdown.get("ats_quality_score", 0.0))

    w_skill = int(float(weights.get("skill", 0.40)) * 100)
    w_text = int(float(weights.get("text_similarity", 0.30)) * 100)
    w_exp = int(float(weights.get("experience", 0.15)) * 100)
    w_ats = int(float(weights.get("ats", 0.15)) * 100)

    story.append(Paragraph("Overall Match Score &amp; Sub-Score Breakdown", h2_style))

    score_box_data = [
        [
            Paragraph(f"<font size=22 color='{c_primary.hexval()}'><b>{overall_score:.1f}%</b></font><br/><font size=7 color='#64748B'>COMPOSITE SCORE</font>", ParagraphStyle("ScoreLg", alignment=1)),
            Paragraph(f"<b>Skill Match ({w_skill}% Weight):</b> {skill_score:.1f}%<br/>"
                      f"<b>Text Similarity ({w_text}% Weight):</b> {text_score:.1f}% (Normalized TF Cosine)<br/>"
                      f"<b>Experience &amp; Education ({w_exp}% Weight):</b> {exp_score:.1f}%<br/>"
                      f"<b>ATS Structural Quality ({w_ats}% Weight):</b> {ats_score:.1f}%", body_style),
        ]
    ]
    t_score = Table(score_box_data, colWidths=[140, 400])
    t_score.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0FDFA")), # Light teal
        ("BOX", (0, 0), (-1, -1), 1, c_primary),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_score)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 4. ROLE RECOMMENDATIONS (TAXONOMY FIT)
    # -------------------------------------------------------------
    roles = analysis_data.get("role_recommendations", [])
    if roles:
        story.append(Paragraph("Role Recommendations (Taxonomy Fit)", h2_style))
        story.append(Paragraph(
            "Deterministic alignment between candidate skills and standard technical role profiles "
            "(evaluated independently from the target job description):",
            meta_sub
        ))
        story.append(Spacer(1, 4))

        role_table_data = [
            [
                Paragraph("<b>Role</b>", table_cell_bold),
                Paragraph("<b>Score</b>", table_cell_bold),
                Paragraph("<b>Fit Level</b>", table_cell_bold),
                Paragraph("<b>Matched Skills</b>", table_cell_bold),
                Paragraph("<b>Core Skills to Strengthen</b>", table_cell_bold),
            ]
        ]
        for r in roles[:5]:  # Top 5 roles
            matched_str = ", ".join(r.get("matched_skills", [])) or "None detected"
            missing_str = ", ".join(r.get("missing_core_skills", [])[:4]) or "None"
            role_table_data.append([
                Paragraph(r.get("role", "N/A"), table_cell_bold),
                Paragraph(f"{float(r.get('score', 0)):.1f}%", table_cell),
                Paragraph(r.get("fit_level", "N/A"), table_cell),
                Paragraph(matched_str, table_cell),
                Paragraph(missing_str, table_cell),
            ])

        t_roles = Table(role_table_data, colWidths=[105, 45, 65, 160, 165])
        t_roles.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_light_bg),
            ("BOX", (0, 0), (-1, -1), 0.75, c_card_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_card_border),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_roles)
        story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 5. SKILL MATCH & PRIORITIZED SKILL GAPS
    # -------------------------------------------------------------
    matching_skills = analysis_data.get("matching_skills", [])
    prioritized_gaps = analysis_data.get("prioritized_skill_gaps", [])

    story.append(Paragraph("Skill Analysis &amp; Prioritized Skill Gaps", h2_style))

    matched_text = ", ".join(matching_skills) if matching_skills else "No direct skill matches detected."
    story.append(Paragraph(f"<b>Matched Skills ({len(matching_skills)}):</b> {matched_text}", body_style))
    story.append(Spacer(1, 4))

    if prioritized_gaps:
        gap_table_data = [
            [
                Paragraph("<b>Missing Skill</b>", table_cell_bold),
                Paragraph("<b>Priority</b>", table_cell_bold),
                Paragraph("<b>Category</b>", table_cell_bold),
                Paragraph("<b>Requirement</b>", table_cell_bold),
                Paragraph("<b>Suggested Action</b>", table_cell_bold),
            ]
        ]
        for gap in prioritized_gaps[:8]:  # Up to 8 gaps
            prio = gap.get("priority", "medium").upper()
            prio_color = c_rose if prio == "HIGH" else (c_amber if prio == "MEDIUM" else c_text)
            prio_p = Paragraph(f"<font color='{prio_color.hexval()}'><b>{prio}</b></font>", table_cell)

            gap_table_data.append([
                Paragraph(gap.get("skill", "N/A"), table_cell_bold),
                prio_p,
                Paragraph(gap.get("category", "N/A"), table_cell),
                Paragraph(gap.get("required_or_preferred", "N/A").title(), table_cell),
                Paragraph(gap.get("action", "N/A"), table_cell),
            ])

        t_gaps = Table(gap_table_data, colWidths=[80, 50, 60, 65, 285])
        t_gaps.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_light_bg),
            ("BOX", (0, 0), (-1, -1), 0.75, c_card_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_card_border),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_gaps)
        story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 6. ATS STRUCTURAL HEALTH & RECOMMENDATIONS
    # -------------------------------------------------------------
    ats_breakdown = analysis_data.get("ats_breakdown", {})
    ats_details = ats_breakdown.get("details", {})
    ats_recs = analysis_data.get("ats_recommendations", [])

    sec_comp = float(ats_details.get("section_completeness_score", 0.0))
    verb_score = float(ats_details.get("action_verb_score", 0.0))
    metric_count = int(ats_details.get("metrics_count", 0))
    sections_found = ", ".join(ats_details.get("sections_found", [])) or "None"
    sections_missing = ", ".join(ats_details.get("sections_missing", [])) or "None"

    story.append(Paragraph("ATS Health &amp; Format Optimization", h2_style))

    ats_summary_data = [
        [
            Paragraph(f"<b>Overall ATS Score:</b> {float(ats_breakdown.get('score', 0)):.1f}%", body_style),
            Paragraph(f"<b>Section Completeness:</b> {sec_comp:.1f}%", body_style),
            Paragraph(f"<b>Action Verb Density:</b> {verb_score:.1f}%", body_style),
            Paragraph(f"<b>Quantifiable Metrics:</b> {metric_count} detected", body_style),
        ]
    ]
    t_ats_sum = Table(ats_summary_data, colWidths=[135, 135, 135, 135])
    t_ats_sum.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_light_bg),
        ("BOX", (0, 0), (-1, -1), 0.75, c_card_border),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_ats_sum)
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Sections Found:</b> {sections_found} | <b>Missing Sections:</b> {sections_missing}", meta_sub))
    story.append(Spacer(1, 4))

    if ats_recs:
        for idx, rec in enumerate(ats_recs[:4], start=1):
            prio = rec.get("priority", "medium").upper()
            story.append(Paragraph(
                f"<b>{idx}. {rec.get('title', 'ATS Advice')}</b> [{prio} PRIORITY]<br/>"
                f"<i>Observation:</i> {rec.get('issue', '')}<br/>"
                f"<b>Action:</b> {rec.get('action', '')}",
                body_style
            ))
            story.append(Spacer(1, 3))

    # -------------------------------------------------------------
    # 7. UNIFIED IMPROVEMENT RECOMMENDATIONS
    # -------------------------------------------------------------
    unified = analysis_data.get("unified_recommendations", [])
    if unified:
        story.append(Spacer(1, 6))
        story.append(Paragraph("Unified Improvement Roadmap", h2_style))
        for idx, rec in enumerate(unified[:6], start=1):
            prio = rec.get("priority", "medium").upper()
            rec_type = rec.get("type", "General").replace("_", " ").title()
            story.append(Paragraph(
                f"<b>{idx}. [{rec_type}] {rec.get('title', 'Suggestion')}</b> — <i>{prio} Priority</i><br/>"
                f"<b>Reason:</b> {rec.get('reason', '')}<br/>"
                f"<b>Recommended Action:</b> {rec.get('action', '')}",
                body_style
            ))
            story.append(Spacer(1, 3.5))

    # -------------------------------------------------------------
    # FOOTER NOTE
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_card_border, spaceBefore=4, spaceAfter=4))
    story.append(Paragraph(
        "<b>HireLens</b> — Open, Mathematical &amp; Explainable Resume Analysis • "
        "Weights: 40% Skill Match, 30% Normalized TF Cosine Similarity, 15% Experience/Education, 15% ATS Quality • "
        "Report generated deterministically without opaque black-box AI.",
        meta_sub
    ))

    # Build the document
    doc.build(story)
    return buffer.getvalue()
