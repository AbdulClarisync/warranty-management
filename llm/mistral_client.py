import requests
import tiktoken
from config import LLM_API_URL, MODEL_NAME

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def ask_mistral(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(LLM_API_URL, json=payload)
    response.raise_for_status()

    data = response.json()

    answer = data["response"]
    prompt_tokens = count_tokens(prompt)
    completion_tokens = count_tokens(answer)
    total_tokens = prompt_tokens + completion_tokens

    return {
        "response": answer,
        "tokens": {
            "prompt": prompt_tokens,
            "completion": completion_tokens,
            "total": total_tokens
        }
    }
