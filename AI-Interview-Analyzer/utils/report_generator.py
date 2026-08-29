from __future__ import annotations
from io import BytesIO
from datetime import datetime

def make_pdf(candidate: dict, scores: dict, results: list[dict], feedback: dict) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    except ImportError as exc:
        raise RuntimeError("PDF reporting requires ReportLab. Run: pip install -r requirements.txt") from exc
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleBlue", parent=styles["Title"], textColor=colors.HexColor("#123B6D"))
    story = [Paragraph("AI Interview Analyzer", title), Paragraph("Mock Interview Performance Report", styles["Heading2"]), Spacer(1, 10)]
    meta = [["Candidate", candidate.get("name", "Candidate")], ["Domain", candidate.get("domain", "—")], ["Experience", candidate.get("experience", "—")], ["Generated", datetime.now().strftime("%d %b %Y, %H:%M")], ["Questions", str(len(results))]]
    table = Table(meta, colWidths=[4*cm, 12*cm]); table.setStyle(TableStyle([("BACKGROUND", (0,0),(0,-1),colors.HexColor("#E8F2FC")),("GRID",(0,0),(-1,-1),.25,colors.lightgrey),("PADDING",(0,0),(-1,-1),6)])); story += [table, Spacer(1, 16)]
    story.append(Paragraph("Performance summary", styles["Heading2"]))
    summary = [["Overall", f"{scores['overall']}/100"], ["Technical / answer", f"{scores['technical']}/100"], ["Communication", f"{scores['communication']}/100"], ["Voice feature indicator", f"{scores['voice']}/100"], ["Expression-based indicator", f"{scores['behavior']}/100"]]
    t = Table(summary, colWidths=[9*cm, 7*cm]); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#123B6D")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.25,colors.lightgrey),("PADDING",(0,0),(-1,-1),6)])); story += [t, Spacer(1, 16)]
    story += [Paragraph("Personalized feedback", styles["Heading2"]), Paragraph(feedback.get("summary", ""), styles["BodyText"])]
    for heading, key in [("Strengths", "strengths"), ("Recommended improvements", "improvements"), ("Practice topics", "practice_topics")]:
        story += [Spacer(1, 6), Paragraph(heading, styles["Heading3"])]
        for item in feedback.get(key, []): story.append(Paragraph(f"• {item}", styles["BodyText"]))
    story += [PageBreak(), Paragraph("Question-wise analysis", styles["Heading2"])]
    for i, result in enumerate(results, 1):
        story.append(Paragraph(f"Q{i}. {result['question']}", styles["Heading3"]))
        story.append(Paragraph(f"Answer: {result['answer_score']:.0f}/100 | Voice indicator: {result.get('voice',{}).get('voice_score',0):.0f}/100 | Detected facial expression: {result.get('emotion',{}).get('dominant_emotion','Not available')}", styles["BodyText"]))
        improvements = result.get("feedback", {}).get("improvements", [])
        if improvements: story.append(Paragraph("Feedback: " + "; ".join(improvements), styles["BodyText"]))
        story.append(Spacer(1, 8))
    story += [Spacer(1, 8), Paragraph("Important note: AI answer ratings and voice/expression values are supportive, non-diagnostic indicators. Facial expressions and audio features do not prove confidence, emotion, ability, or personality.", styles["Italic"])]
    doc.build(story)
    return buffer.getvalue()
