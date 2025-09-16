from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
    
    def embed(self, text):
        if isinstance(text, str):
            return self.model.encode([text])[0].tolist()
        return self.model.encode(text).tolist()