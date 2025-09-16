import docx
from .base import BaseExtractor

class DocxExtractor(BaseExtractor):
    def extract_text(self):
        doc = docx.Document(self.file_path)
        return "\n".join([p.text for p in doc.paragraphs])
