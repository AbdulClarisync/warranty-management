from utils.file_loader import load_and_extract
from llm.mistral_client import ask_mistral
from utils.parser import parse_llm_response
from utils.text_splitter import TextSplitter
from utils.embedder import Embedder
from vector_db.qdrant_manager import QdrantManager
from utils.logger import save_log
from config import COLLECTION_NAME, EMBEDDING_MODEL
import json
import time
from utils.cleaner import clean_text


def update_laravel(warranty_id, structured_data):
    print(f"\n Updating Laravel (warranty ID: {warranty_id})")
    print(f"Title: {structured_data['title']}")
    print(f"Expiry Date: {structured_data['expiry_date']}")
    print(f"Claimable Items: {structured_data['claimable_items'][:1]}...")
    print(f"Non-Claimable Items: {structured_data['non_claimable_items'][:1]}...")
    # requests.patch(f"https://laravel-app/warranties/{warranty_id}", json=structured_data)

def process_warranty(file_path, warranty_id, product_name):
    start_time = time.time()
    print(f"\n Processing warranty (ID: {warranty_id}) for {product_name}")
    
    start_extract = time.time()
    raw_text = load_and_extract(file_path)
    extracted_text = clean_text(raw_text)
    extract_duration = time.time() - start_extract
    print(f" Text extracted ({len(extracted_text)} chars) in {extract_duration:.2f}s")
    
    start_llm = time.time()
    prompt = f"""
You are an AI assistant that analyzes warranty or insurance-related documents.
From the given text, extract the following:

1. Title of the document
2. Expiry Date (in YYYY-MM-DD format if available)
3. List of Attachment names (if mentioned)
4. Claimable items (if any mentioned, with reasoning if possible)
5. Non-claimable items (with reasoning if possible)

Only extract information if it exists in the text. Do not make up anything.

Text:
{extracted_text}
"""
    response_data = ask_mistral(prompt)
    answer = response_data["response"]
    tokens = response_data["tokens"]
    llm_duration = time.time() - start_llm
    
    print("\nRaw LLM Response:\n")
    print(answer)

    structured_data = parse_llm_response(answer)
    print("\nParsed Structured Output:\n")
    print(structured_data)
    print(f" Structured data extracted in {llm_duration:.2f}s")
    
    update_laravel(warranty_id, structured_data)
    
    start_vector = time.time()
    splitter = TextSplitter()
    chunks = splitter.split(extracted_text)
    print(f" Split into {len(chunks)} chunks")
    
    embedder = Embedder()
    embeddings = embedder.embed(chunks)
    
    qdrant = QdrantManager(COLLECTION_NAME)
    stored_points = qdrant.store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        warranty_id=warranty_id,
        metadata={
            "source": file_path,
            "product": product_name
        }
    )
    vector_duration = time.time() - start_vector
    print(f" Stored {stored_points} vectors in Qdrant in {vector_duration:.2f}s")
    
    total_duration = time.time() - start_time
    save_log(file_path, "warranty_extraction", tokens, total_duration, structured_data)
    
    print("\n Processing Complete!")
    print(f" Total time: {total_duration:.2f} seconds")
    print(f" Tokens Used: {tokens['total']} (Prompt: {tokens['prompt']}, Completion: {tokens['completion']})")
    
    return structured_data

if __name__ == "__main__":
    WARRANTY_ID = 4
    PRODUCT_NAME = "LAPTOP WARRANTY CERTIFICATE"
    FILE_PATH = "samples/laptop.pdf"
    
    result = process_warranty(FILE_PATH, WARRANTY_ID, PRODUCT_NAME)
    
    print("\nFinal Structured Output:")
    print(json.dumps(result, indent=2))