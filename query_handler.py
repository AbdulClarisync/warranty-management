from utils.embedder import Embedder
from vector_db.qdrant_manager import QdrantManager
from llm.mistral_client import ask_mistral
from config import COLLECTION_NAME
import json

def answer_query(user_question, warranty_id=None, top_k=10):
    """
    Process a user query against warranty documents with enhanced retrieval
    """
    print(f"[DEBUG] Original User Query: '{user_question}'")
    
    expansion_prompt = f""" Generate a comprehensive multi-perspective description for a warranty document search query. The description will be used to find the most relevant passages to answer the user's question. Original User Query: {user_question} Your generated description should: 1. Be a full, detailed sentence. 2. Include synonyms and related terms (e.g., "claimable" -> "covered", "replaced under warranty"). 3. Speculate on what a relevant warranty document passage might contain. Generated Query: """ 
    try: 
        expanded_query_response = ask_mistral(expansion_prompt) 
        expanded_query = expanded_query_response["response"].strip() 
        print(f"[DEBUG] Expanded Query: '{expanded_query}'")
    except Exception as e: 
        print(f"[WARNING] Query expansion failed: {e}") 
        expanded_query = user_question 
   
    embedder = Embedder()
    q_vector = embedder.embed([user_question])[0]
    
    qdrant = QdrantManager(COLLECTION_NAME)
    
    filter_params = {"warranty_id": warranty_id} if warranty_id else None
    results = qdrant.search(q_vector, top_k=top_k, filter=filter_params)
    
    if not results:
        return {
            "answer": "The warranty document does not mention this.",
            "confidence": 0.0,
            "sources": []
        }

    print("\n[DEBUG] Top retrieved chunks from Qdrant:")
    for i, r in enumerate(results):
        print(f"Chunk {i}: Score={r['score']:.4f}")
        print(f"Text: {r['text'][:200]}...")
        print(f"Source: {r['metadata']['source']}\n")

    try:
        rerank_prompt = f"""
        You are a helpful assistant. You will be given a query and a list of text passages from warranty documents.
        Re-sort the list of passages by how directly and completely they answer the query.
        Return ONLY a JSON list of the sorted passage IDs (0-indexed), from most to least relevant.

        Query: {user_question}

        Passages:
        """
        for i, res in enumerate(results):
            rerank_prompt += f"[ID: {i}] {res['text'][:300]}...\n\n"

        rerank_prompt += "\nReturn a JSON list of indices, e.g., [2, 0, 1, ...]"

        rerank_response = ask_mistral(rerank_prompt)
        reranked_indices = json.loads(rerank_response["response"].strip())
        
        results = [results[i] for i in reranked_indices][:3]
        print("[DEBUG] Re-ranking applied successfully. New order:", reranked_indices)
        
    except Exception as e:
        print(f"[WARNING] Re-ranking failed, using original order: {e}")
        results = results[:3]


    context = "\n\n".join([f"Document excerpt: {r['text']}" for r in results])

    prompt = f"""
    You are a warranty specialist assistant. 
    Answer the user's question based ONLY on the provided warranty document excerpts.
    
    IMPORTANT INSTRUCTIONS:
    1. If the information is not explicitly stated in the context, say "The warranty document does not mention this."
    2. If the context suggests an answer but doesn't state it explicitly, still say it's not mentioned.
    3. For claimable items, only say yes if the context explicitly states it's covered.
    4. Be precise and concise in your answer.
    5. At the end, add a confidence estimate of your answer (High/Medium/Low) based on how clearly the context addresses the query.

    
    Context:
    {context}
    
    User Question: {user_question}
    
    Answer:
    """
    
    response = ask_mistral(prompt)
    
    top_scores = [r["score"] for r in results]
    avg_confidence = sum(top_scores) / len(top_scores) if top_scores else 0
    
    return {
        "answer": response["response"],
        "confidence": avg_confidence,
        "sources": list(set([r["metadata"]["source"] for r in results]))
    }


if __name__ == "__main__":
    query = "Cosmetic Damage (scratches, dents, paint wear)"
    result = answer_query(query)   
    print("\nFinal Result:")
    print("User Query:", query)
    print("Answer:", result["answer"])
    print("Confidence:", result["confidence"])
    print("Sources:", result["sources"])