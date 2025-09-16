import os
from extractor.pdf_extractor import PDFExtractor
from extractor.docx_extractor import DocxExtractor

def load_and_extract(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        extractor = PDFExtractor(file_path)
    elif ext == '.docx':
        extractor = DocxExtractor(file_path)
    else:
        raise Exception("Unsupported file type")
    
    return extractor.extract_text()
