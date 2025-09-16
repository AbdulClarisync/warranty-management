from PyPDF2 import PdfReader
from .base import BaseExtractor

class PDFExtractor(BaseExtractor):
    def extract_text(self):
        reader = PdfReader(self.file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
