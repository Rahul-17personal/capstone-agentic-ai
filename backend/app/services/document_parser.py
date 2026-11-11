import fitz
from docx import Document
from pptx import Presentation


def extract_text(file_path: str, extension: str) -> str:
    """Extract selectable text from PDF, DOCX or PPTX."""
    extension = extension.lower()
    if extension == ".pdf":
        with fitz.open(file_path) as pdf:
            return "\n".join(page.get_text() for page in pdf)

    if extension == ".docx":
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        table_text = [
            " | ".join(cell.text.strip() for cell in row.cells)
            for table in doc.tables
            for row in table.rows
        ]
        return "\n".join(paragraphs + table_text)

    if extension == ".pptx":
        presentation = Presentation(file_path)
        slide_text = []
        for number, slide in enumerate(presentation.slides, start=1):
            parts = []
            for shape in slide.shapes:
                if getattr(shape, "has_text_frame", False) and shape.text.strip():
                    parts.append(shape.text.strip())
                if getattr(shape, "has_table", False):
                    for row in shape.table.rows:
                        parts.append(" | ".join(cell.text for cell in row.cells))
            slide_text.append(f"Slide {number}:\n" + "\n".join(parts))
        return "\n\n".join(slide_text)

    raise ValueError(f"Unsupported file format: {extension}")
