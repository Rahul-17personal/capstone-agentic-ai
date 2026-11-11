"""Generate downloadable PDF, DOCX and PPTX PitchIntel reports."""
from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape
from typing import Any

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor as PptxRGB
from pptx.util import Inches as PptxInches, Pt as PptxPt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether,
)


def _items(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None and str(item).strip()]


def _paragraphs(story: list, title: str, text: Any, styles) -> None:
    if text is None or not str(text).strip():
        return
    story.append(Paragraph(escape(title), styles["Heading2"]))
    story.append(Paragraph(escape(str(text)).replace("\n", "<br/>"), styles["BodyText"]))
    story.append(Spacer(1, 5 * mm))


def _bullets(story: list, title: str, values: Any, styles) -> None:
    items = _items(values)
    if not items:
        return
    story.append(Paragraph(escape(title), styles["Heading2"]))
    for item in items:
        story.append(Paragraph("&#8226;&nbsp; " + escape(item), styles["BodyText"]))
    story.append(Spacer(1, 4 * mm))


def _source_rows(research: dict) -> list[dict]:
    sources = research.get("sources", []) if isinstance(research, dict) else []
    return [s for s in sources if isinstance(s, dict) and s.get("url")]


def build_pdf(payload: dict) -> bytes:
    analysis = payload["analysis"]
    research = payload.get("competitive_research") or {}
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
        topMargin=17*mm, bottomMargin=17*mm, title="PitchIntel AI Report",
        author="PitchIntel AI",
    )
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle("ReportTitle", parent=base["Title"], textColor=colors.HexColor("#17233e"), alignment=TA_CENTER, fontSize=23, leading=28, spaceAfter=7*mm),
        "Subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], textColor=colors.HexColor("#64748b"), alignment=TA_CENTER, fontSize=9, spaceAfter=9*mm),
        "Heading2": ParagraphStyle("Section", parent=base["Heading2"], textColor=colors.HexColor("#315fc9"), fontSize=13, leading=16, spaceBefore=5*mm, spaceAfter=2*mm),
        "BodyText": ParagraphStyle("ReportBody", parent=base["BodyText"], fontSize=9, leading=14, textColor=colors.HexColor("#334155"), spaceAfter=2*mm),
    }
    company = str(payload.get("company_name") or "Sales Pitch Review")
    story = [
        Paragraph("PitchIntel AI", styles["Title"]),
        Paragraph(escape(company) + " · Sales Pitch & Competitive Intelligence", styles["Subtitle"]),
    ]
    score = analysis.get("overall_score", "—")
    score_table = Table(
        [[Paragraph("<b>Overall pitch score</b>", styles["BodyText"]),
          Paragraph(f"<b>{escape(str(score))}/100</b>", styles["BodyText"])]],
        colWidths=[110*mm, 55*mm],
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#eef3ff")),
        ("BOX", (0,0), (-1,-1), .5, colors.HexColor("#d9e3fa")),
        ("PADDING", (0,0), (-1,-1), 9),
    ]))
    story += [score_table, Spacer(1, 5*mm)]
    _paragraphs(story, "Executive summary", analysis.get("executive_summary"), styles)
    metric_names = [
        ("Messaging quality", "messaging_quality"),
        ("Value proposition", "value_proposition"),
        ("Target audience clarity", "target_audience_clarity"),
        ("Call to action", "call_to_action"),
    ]
    metric_table = [["Assessment metric", "Score"]]
    metric_table += [[label, f"{analysis.get(key, '—')}/100"] for label, key in metric_names]
    table = Table(metric_table, colWidths=[120*mm, 45*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17233e")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#dce3ef")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f9fc")]),
        ("PADDING", (0,0), (-1,-1), 7),
    ]))
    story += [Paragraph("Performance metrics", styles["Heading2"]), table]
    for title, key in [
        ("Strengths", "strengths"), ("Weaknesses and risks", "weaknesses"),
        ("Missing information", "missing_information"), ("Recommendations", "recommendations"),
    ]:
        _bullets(story, title, analysis.get(key), styles)
    _paragraphs(story, "Improved sales pitch", analysis.get("improved_pitch"), styles)
    _paragraphs(story, "Competitor context", analysis.get("competitor_context"), styles)
    if research:
        story.append(PageBreak())
        story.append(Paragraph("Competitive intelligence", styles["Heading1"]))
        _paragraphs(story, "Market overview", research.get("market_overview"), styles)
        _bullets(story, "Competitive themes", research.get("competitive_themes"), styles)
        _bullets(story, "Pitch opportunities", research.get("pitch_opportunities"), styles)
        for finding in research.get("findings", []):
            if not isinstance(finding, dict):
                continue
            story.append(Paragraph(escape(str(finding.get("name", "Competitor"))), styles["Heading2"]))
            _paragraphs(story, "Summary", finding.get("summary"), styles)
            _paragraphs(story, "Positioning", finding.get("positioning"), styles)
            _bullets(story, "Products and features", finding.get("products_and_features"), styles)
            _bullets(story, "Pricing observations", finding.get("pricing_observations"), styles)
            _bullets(story, "Differentiators", finding.get("differentiators"), styles)
            _bullets(story, "Caveats", finding.get("caveats"), styles)
    sources = _source_rows(research)
    if sources:
        story.append(Paragraph("Research sources", styles["Heading2"]))
        for source in sources:
            url = escape(str(source["url"]), {'"': "&quot;"})
            label = escape(str(source.get("title") or source["url"]))
            story.append(Paragraph(f"{escape(str(source.get('source_id', '')))} · <link href=\"{url}\" color=\"#315fc9\">{label}</link>", styles["BodyText"]))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("AI-generated report. Verify important claims and pricing against linked source pages.", styles["Subtitle"]))
    doc.build(story)
    return buffer.getvalue()


def _add_docx_heading(doc: Document, title: str, level: int = 1) -> None:
    doc.add_heading(title, level=level)


def _docx_bullets(doc: Document, title: str, values: Any) -> None:
    items = _items(values)
    if not items:
        return
    _add_docx_heading(doc, title, 2)
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def build_docx(payload: dict) -> bytes:
    analysis = payload["analysis"]
    research = payload.get("competitive_research") or {}
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(.65)
    section.bottom_margin = Inches(.65)
    title = doc.add_heading("PitchIntel AI", 0)
    title.alignment = 1
    subtitle = doc.add_paragraph(f"{payload.get('company_name') or 'Sales Pitch Review'} · Sales Pitch & Competitive Intelligence")
    subtitle.alignment = 1
    doc.add_heading("Executive summary", 1)
    doc.add_paragraph(str(analysis.get("executive_summary", "")))
    doc.add_heading(f"Overall pitch score: {analysis.get('overall_score', '—')}/100", 1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Light Shading Accent 1"
    table.rows[0].cells[0].text = "Assessment metric"
    table.rows[0].cells[1].text = "Score"
    for label, key in [
        ("Messaging quality", "messaging_quality"),
        ("Value proposition", "value_proposition"),
        ("Target audience clarity", "target_audience_clarity"),
        ("Call to action", "call_to_action"),
    ]:
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = f"{analysis.get(key, '—')}/100"
    for title, key in [
        ("Strengths", "strengths"), ("Weaknesses and risks", "weaknesses"),
        ("Missing information", "missing_information"), ("Recommendations", "recommendations"),
    ]:
        _docx_bullets(doc, title, analysis.get(key))
    doc.add_heading("Improved sales pitch", 1)
    doc.add_paragraph(str(analysis.get("improved_pitch", "")))
    doc.add_heading("Competitor context", 1)
    doc.add_paragraph(str(analysis.get("competitor_context", "")))
    if research:
        doc.add_page_break()
        doc.add_heading("Competitive intelligence", 1)
        doc.add_heading("Market overview", 2)
        doc.add_paragraph(str(research.get("market_overview", "")))
        _docx_bullets(doc, "Competitive themes", research.get("competitive_themes"))
        _docx_bullets(doc, "Pitch opportunities", research.get("pitch_opportunities"))
        for finding in research.get("findings", []):
            if not isinstance(finding, dict):
                continue
            doc.add_heading(str(finding.get("name", "Competitor")), 2)
            doc.add_paragraph(str(finding.get("summary", "")))
            doc.add_paragraph("Positioning: " + str(finding.get("positioning", "")))
            for title, key in [
                ("Products and features", "products_and_features"),
                ("Pricing observations", "pricing_observations"),
                ("Differentiators", "differentiators"),
                ("Caveats", "caveats"),
            ]:
                _docx_bullets(doc, title, finding.get(key))
        sources = _source_rows(research)
        if sources:
            doc.add_heading("Research sources", 2)
            for source in sources:
                p = doc.add_paragraph(style="List Bullet")
                p.add_run(f"{source.get('source_id', '')} · {source.get('title') or source['url']} — ")
                p.add_run(str(source["url"]))
    footer = section.footer.paragraphs[0]
    footer.text = "PitchIntel AI · AI-generated report · Verify important claims against source pages"
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _pptx_title(slide, title: str, subtitle: str | None = None) -> None:
    slide.shapes.title.text = title
    for paragraph in slide.shapes.title.text_frame.paragraphs:
        paragraph.font.name = "Aptos Display"
        paragraph.font.size = PptxPt(28)
        paragraph.font.bold = True
        paragraph.font.color.rgb = PptxRGB(23, 35, 62)
    if subtitle:
        box = slide.shapes.add_textbox(PptxInches(.7), PptxInches(1.15), PptxInches(11.8), PptxInches(.5))
        p = box.text_frame.paragraphs[0]
        p.text = subtitle
        p.font.size = PptxPt(13)
        p.font.color.rgb = PptxRGB(100, 116, 139)


def _pptx_bullet_slide(prs, title: str, items: list[str]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    _pptx_title(slide, title)
    frame = slide.placeholders[1].text_frame
    frame.clear()
    frame.word_wrap = True
    for index, item in enumerate(items[:12]):
        p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        p.text = item[:500]
        p.level = 0
        p.font.size = PptxPt(18)
        p.space_after = PptxPt(12)


def build_pptx(payload: dict) -> bytes:
    analysis = payload["analysis"]
    research = payload.get("competitive_research") or {}
    prs = Presentation()
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    _pptx_title(slide, "PitchIntel AI", f"{payload.get('company_name') or 'Sales Pitch Review'} · Sales Pitch & Competitive Intelligence")
    subtitle = slide.placeholders[1]
    subtitle.text = "Strategic pitch assessment and competitive landscape"
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    _pptx_title(slide, "Executive summary")
    box = slide.shapes.add_textbox(PptxInches(.8), PptxInches(1.6), PptxInches(11.6), PptxInches(2.4))
    box.text_frame.text = str(analysis.get("executive_summary", ""))[:1800]
    box.text_frame.paragraphs[0].font.size = PptxPt(21)
    score_box = slide.shapes.add_textbox(PptxInches(.8), PptxInches(4.3), PptxInches(4), PptxInches(1))
    score_box.text_frame.text = f"Overall pitch score: {analysis.get('overall_score', '—')}/100"
    score_box.text_frame.paragraphs[0].font.size = PptxPt(24)
    metrics = [
        f"Messaging quality: {analysis.get('messaging_quality', '—')}/100",
        f"Value proposition: {analysis.get('value_proposition', '—')}/100",
        f"Target audience clarity: {analysis.get('target_audience_clarity', '—')}/100",
        f"Call to action: {analysis.get('call_to_action', '—')}/100",
    ]
    _pptx_bullet_slide(prs, "Pitch performance metrics", metrics)
    for title, key in [
        ("Strengths", "strengths"), ("Weaknesses and risks", "weaknesses"),
        ("Missing information", "missing_information"), ("Recommendations", "recommendations"),
    ]:
        _pptx_bullet_slide(prs, title, _items(analysis.get(key)))
    _pptx_bullet_slide(prs, "Improved sales pitch", [str(analysis.get("improved_pitch", ""))])
    if research:
        _pptx_bullet_slide(prs, "Competitive intelligence overview", [
            str(research.get("market_overview", "")),
            *[f"Theme: {x}" for x in _items(research.get("competitive_themes"))],
            *[f"Pitch opportunity: {x}" for x in _items(research.get("pitch_opportunities"))],
        ])
        for finding in research.get("findings", []):
            if not isinstance(finding, dict):
                continue
            _pptx_bullet_slide(prs, str(finding.get("name", "Competitor")) + " profile", [
                str(finding.get("summary", "")),
                "Positioning: " + str(finding.get("positioning", "")),
                *[f"Feature: {x}" for x in _items(finding.get("products_and_features"))],
                *[f"Pricing: {x}" for x in _items(finding.get("pricing_observations"))],
                *[f"Differentiator: {x}" for x in _items(finding.get("differentiators"))],
                *[f"Caveat: {x}" for x in _items(finding.get("caveats"))],
            ])
        sources = _source_rows(research)
        if sources:
            _pptx_bullet_slide(prs, "Research sources", [
                f"{s.get('source_id', '')} · {s.get('title') or s['url']} — {s['url']}"
                for s in sources
            ])
    buffer = BytesIO()
    prs.save(buffer)
    return buffer.getvalue()
