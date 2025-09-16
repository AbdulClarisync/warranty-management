# utils/text_splitter.py (Improved version)
import re

class TextSplitter:
    def __init__(self, chunk_size=500, min_chunk_size=100):
        self.chunk_size = chunk_size
        self.min_chunk_size = min_chunk_size
        
    def split(self, text):
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # First split by sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
                
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())
            
        return chunks