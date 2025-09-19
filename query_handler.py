import os
import json
from datetime import datetime

from utils.embedder import Embedder
from vector_db.qdrant_manager import QdrantManager
from llm.mistral_client import ask_mistral
from config import COLLECTION_NAME



def merge_results(results_a, results_b, top_k=10):
    """
    Merge two result sets (direct + expanded) by unique chunk IDs.
    Fallback: use hash of text if no ID is found.
    Keep the highest score if duplicate.
    """
    merged = {}
    for r in results_a + results_b:
        # Try different ways to identify a chunk
        chunk_id = (
            r.get("id") or
            r.get("chunk_id") or
            r.get("metadata", {}).get("chunk_id") or
            hash(r.get("text", ""))
        )

        if chunk_id not in merged or r["score"] > merged[chunk_id]["score"]:
            merged[chunk_id] = r

    # sort by score desc
    return sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:top_k]


def save_log_file(log_data, prefix="warranty_query"):
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"output/{prefix}_{timestamp}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    print(f"[LOG] Saved log file: {file_name}")


def answer_query(user_question, warranty_id=None, top_k=10):
    log = {
        "user_question": user_question,
        "expanded_query": None,
        "retrieved_chunks": [],
        "reranked_order": [],
        "context_used": None,
        "final_answer": None,
        "confidence": None,
        "sources": []
    }

    print(f"[DEBUG] Original User Query: '{user_question}'")
    
    # 🔹 Step 1: Expand the query
    expansion_prompt = f"""
    Generate a comprehensive multi-perspective description for a warranty document search query. 
    The description will be used to find the most relevant passages to answer the user's question. 

    Original User Query: {user_question}

    Your generated description should:
    1. Be a full, detailed sentence.
    2. Include synonyms and related terms (e.g., "claimable" -> "covered", "replaced under warranty").
    3. Speculate on what a relevant warranty document passage might contain.

    Generated Query:
    """
    try:
        expanded_query_response = ask_mistral(expansion_prompt)
        expanded_query = expanded_query_response["response"].strip()
        log["expanded_query"] = expanded_query
        print(f"[DEBUG] Expanded Query: '{expanded_query}'")
    except Exception as e:
        print(f"[WARNING] Query expansion failed: {e}")
        expanded_query = user_question
        log["expanded_query"] = expanded_query

    # Step 2: Embed queries
    embedder = Embedder()
    orig_vec = embedder.embed([user_question])[0]
    exp_vec  = embedder.embed([expanded_query])[0]

    qdrant = QdrantManager(COLLECTION_NAME)
    filter_params = {"warranty_id": warranty_id} if warranty_id else None

    results_orig = qdrant.search(orig_vec, top_k=top_k, filter=filter_params)
    results_exp  = qdrant.search(exp_vec, top_k=top_k, filter=filter_params)

    # 🔹 Step 3: Merge results
    results = merge_results(results_orig, results_exp, top_k=top_k)
    log["retrieved_chunks"] = results

    if not results:
        log["final_answer"] = "The warranty document does not mention this."
        log["confidence"] = 0.0
        save_log_file(log)
        return log
        return {
            "answer": "The warranty document does not mention this.",
            "confidence": 0.0,
            "sources": []
        }

    print("\n[DEBUG] Top retrieved chunks (merged):")
    for i, r in enumerate(results):
        print(f"Chunk {i}: Score={r['score']:.4f}")
        print(f"Text: {r['text'][:200]}...")
        print(f"Source: {r['metadata']['source']}\n")

    # 🔹 Step 4: Re-ranking with LLM
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
        log["reranked_order"] = reranked_indices
    except Exception as e:
        print(f"[WARNING] Re-ranking failed, using original order: {e}")
        results = results[:3]

    # 🔹 Step 5: Build context for answer
    context = "\n\n".join([f"Document excerpt: {r['text']}" for r in results])
    log["context_used"] = context

    answer_prompt = f"""
    You are a warranty specialist assistant. 
    Answer the user's question based ONLY on the provided warranty document excerpts.

    IMPORTANT INSTRUCTIONS:
    1. Always explain WHY the claim is covered or not (refer to covered parts/items in the context).
    2. If the information is not explicitly stated in the context, say 
       "The warranty document does not mention this" and explain which items are listed instead.
    3. For claimable items, only say YES if the context explicitly states it's covered.
    4. Be precise and concise in your answer.
    5. At the end, add a confidence estimate of your answer (High/Medium/Low).

    Context:
    {context}

    User Question: {user_question}

    Answer (with reasoning and confidence):
    """
    
    response = ask_mistral(answer_prompt)

    # 🔹 Step 6: Hybrid confidence score
    top_scores = [r["score"] for r in results]
    retriever_conf = max(top_scores) if top_scores else 0
    llm_conf_text = response["response"].lower()
    if "high" in llm_conf_text:
        llm_conf = 0.9
    elif "medium" in llm_conf_text:
        llm_conf = 0.6
    elif "low" in llm_conf_text:
        llm_conf = 0.3
    else:
        llm_conf = 0.5

    final_confidence = round(0.6 * retriever_conf + 0.4 * llm_conf, 2)
    log["final_answer"] = response["response"]
    log["confidence"] = final_confidence
    log["sources"] = list({r["metadata"]["source"] for r in results})

    save_log_file(log)
    return log
    


if __name__ == "__main__":
    query = "My Car windows are broken can i clame"
    result = answer_query(query)
    print("\nFinal Result:")
    print(json.dumps(result, indent=2))
