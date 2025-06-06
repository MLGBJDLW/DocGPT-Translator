from docx import Document
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def save_to_docx(paragraphs, output_path):
    """
    Save a list of paragraphs to a .docx file.

    Args:
        paragraphs (List[str]): A list of translated paragraphs.
        output_path (str): The path to save the output .docx file.
    """
    doc = Document()
    for paragraph in paragraphs:
        doc.add_paragraph(paragraph)
    doc.save(output_path)

def save_to_pdf(paragraphs, output_path):
    """
    Save a list of paragraphs to a PDF file.

    Args:
        paragraphs (List[str]): A list of translated paragraphs.
        output_path (str): Path to save the output PDF.
    """
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER
    x_margin = 50
    y = height - 50
    line_height = 14

    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        for line in lines:
            if y < 50:  # Start a new page
                c.showPage()
                y = height - 50
            c.drawString(x_margin, y, line)
            y -= line_height
        y -= line_height  # Add space between paragraphs

    c.save()