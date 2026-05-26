#import
import io
from typing import Union
from pypdf import PdfReader
from docx import Document


def extract_pdf_text(file: Union[str, io.BytesIO]) -> str:
    try:
        reader = PdfReader(file)
        
        if len(reader.pages) == 0:
            raise ValueError("PDF file contains no pages")
        
        text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                continue
        
        if not text.strip():
            raise ValueError("No text could be extracted from PDF. The file might contain only images or be password-protected.")
        
        return text.strip()
    except Exception as e:
        if "password" in str(e).lower():
            raise ValueError("PDF file is password-protected. Please provide an unlocked PDF.")
        elif "corrupt" in str(e).lower():
            raise ValueError("PDF file appears to be corrupted. Please try a different file.")
        else:
            raise ValueError(f"Error extracting PDF text: {str(e)}. Please ensure the PDF contains selectable text.")


def extract_docx_text(file: Union[str, io.BytesIO]) -> str:
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        
        if not text.strip():
            raise ValueError("No text could be extracted from DOCX file. The document might be empty.")
        
        return text.strip()
    except Exception as e:
        if "not a zip file" in str(e).lower():
            raise ValueError("Invalid DOCX file format. Please ensure the file is a valid Word document.")
        else:
            raise ValueError(f"Error extracting DOCX text: {str(e)}. Please ensure the file is a valid Word document.")
