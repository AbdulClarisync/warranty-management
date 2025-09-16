from qdrant_client import QdrantClient

COLLECTION_NAME = "warranty-management"
# Initialize client
client = QdrantClient(
 url="https://0f829c53-bf38-4dd1-95a9-a890d366d0bb.us-west-2-0.aws.cloud.qdrant.io:6333",  # Qdrant Cloud URL or http://localhost:6333
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.g11ODLoj1MxC1HGNCaye5A9oFgx6u3E4EAwdeXcX2fk"  # Only required for Qdrant Cloud

)

# Fetch a record by ID
point_id = "404bffc1-530e-467b-b93f-54f26c81b6aa"  # The ID you mentioned
record = client.retrieve(
    collection_name=COLLECTION_NAME,
    ids=[point_id],
    with_payload=True,
    with_vectors=True  # 👈 Set this True to also return the vector
)

print(record)
