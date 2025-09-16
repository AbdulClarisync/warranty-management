from utils.embedder import Embedder
from vector_db.qdrant_manager import QdrantManager
from llm.mistral_client import ask_mistral
from config import COLLECTION_NAME

def answer_query(user_question, warranty_id=None, top_k=3):
    embedder = Embedder()
    q_vector = embedder.embed([user_question])[0]
    
    qdrant = QdrantManager(COLLECTION_NAME)
    
    if warranty_id:
        results = qdrant.search(q_vector, top_k=top_k, filter={"warranty_id": warranty_id})
    else:
        results = qdrant.search(q_vector, top_k=top_k)
    
    if not results:
        return {
            "answer": "Maaf kijiye, is query ka relevant warranty record nahi mila.",
            "confidence": 0.0,
            "sources": []
        }

    print("Raw Results from Qdrant:")
    for r in results:
        print(r)

    context = "\n\n".join([r["text"] for r in results])

    prompt = f"""
You are a warranty assistant. 
Answer the user query ONLY based on the provided context. 
If the answer is not present in the context, say "The warranty document does not mention this."

Context:
{context}

User Question:
{user_question}

"""
    
    response = ask_mistral(prompt)
    
    return {
        "answer": response["response"],
        "confidence": sum(r["score"] for r in results) / len(results),  # avg score
        "sources": list(set([r["metadata"]["source"] for r in results]))
    }


if __name__ == "__main__":
    query = " Is my Motherboard is claimable?"
    result = answer_query(query)   
    print("\nUser Query:", query)
    print("Answer:", result["answer"])
    print("Confidence:", result["confidence"])
    print("Sources:", result["sources"])
