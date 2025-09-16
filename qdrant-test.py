# create_collection.py
from qdrant_client import QdrantClient
from qdrant_client.http import models
from config import COLLECTION_NAME 

client = QdrantClient(
 url="https://0f829c53-bf38-4dd1-95a9-a890d366d0bb.us-west-2-0.aws.cloud.qdrant.io:6333",  # Qdrant Cloud URL or http://localhost:6333
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.g11ODLoj1MxC1HGNCaye5A9oFgx6u3E4EAwdeXcX2fk"  # Only required for Qdrant Cloud

)

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(
        size=1024,
        distance=models.Distance.COSINE
    ),
)

print(f"✅ Collection '{COLLECTION_NAME}' created successfully!")

