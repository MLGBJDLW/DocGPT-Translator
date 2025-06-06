from docx import Document
import fitz # PyMuPDF

def read_docx(file_path):
    """
    Read a .docx file and return a list of non-empty paragraphs.
    
    Args:
        file_path (str): Path to the .docx file.

    Returns:
        List[str]: A list of paragraph texts.
    """
    doc = Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return paragraphs

def read_pdf(file_path):
    """
    Read a PDF file and return a list of non-empty lines across all pages.
    
    Args:
        file_path (str): Path to the PDF file.

    Returns:
        List[str]: A list of text lines.
    """
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return [line.strip() for line in full_text.split('\n') if line.strip()]