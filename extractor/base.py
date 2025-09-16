class BaseExtractor:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_text(self):
        raise NotImplementedError("Extractor must implement extract_text")
