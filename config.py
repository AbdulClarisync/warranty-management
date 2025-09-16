import os
LLM_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

QDRANT_URL = "https://0f829c53-bf38-4dd1-95a9-a890d366d0bb.us-west-2-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.g11ODLoj1MxC1HGNCaye5A9oFgx6u3E4EAwdeXcX2fk"                  # Replace with your API key
COLLECTION_NAME = "warranty-management"
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
#EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5") # Great balance of speed & accuracy
#EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5") #Better accuracy, slightly slower
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5") # Best accuracy, needs more resources
