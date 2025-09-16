from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import uuid
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME

class QdrantManager:
    def __init__(self, collection_name):
        self.client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            prefer_grpc=True
        )
        self.collection_name = collection_name
        
    def store_chunks(self, chunks, embeddings, warranty_id, metadata):
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk,
                    "warranty_id": warranty_id,
                    "source": metadata.get("source", ""),
                    "product": metadata.get("product", ""),
                    "section": metadata.get("section", "general")
                }
            ))
        
        # Upsert in batches of 100
        for i in range(0, len(points), 100):
            batch = points[i:i+100]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            
        return len(points)

    def search(self, query_vector, top_k=3, filter=None):
        qdrant_filter = None
        if filter and "warranty_id" in filter:
            qdrant_filter = Filter(
                must=[
                    FieldCondition(
                        key="warranty_id",
                        match=MatchValue(value=filter["warranty_id"])
                    )
                ]
            )
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter
        )
        
        # ✅ correct key use karo
        return [
            {
                "text": r.payload.get("text"),
                "metadata": r.payload,
                "score": r.score
            }
            for r in results
        ]