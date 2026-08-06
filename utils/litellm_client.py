import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()

AZURE_ENDPOINT = "https://marine-insurance-agent-resource.services.ai.azure.com/openai/v1/chat/completions"
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

from litellm import completion

PROVIDERS = {
    "groq": {
        "model": "groq/llama-3.3-70b-versatile",
        "timeout": 30
    }
}

def call_azure_direct(prompt: str, temperature: float = 0.1, max_tokens: int = 500) -> dict:
    """
    Appel Azure direct via requests — contourne LiteLLM pour Azure
    """
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_API_KEY
    }
    body = {
        "model": "Phi-4-mini-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    start = time.time()
    response = requests.post(AZURE_ENDPOINT, headers=headers, json=body, timeout=120)
    response.raise_for_status()
    data = response.json()
    return {
        "content": data["choices"][0]["message"]["content"],
        "tokens_used": data["usage"]["total_tokens"],
        "response_time": round(time.time() - start, 2),
        "provider": "azure",
        "model": "Phi-4-mini-instruct"
    }

def call_llm(prompt: str, temperature: float = 0.1, max_tokens: int = 500, provider: str = "groq") -> dict:
    """
    Appel LLM unifié — Groq principal, Azure fallback direct
    """
    providers_order = ["groq", "azure"] if provider == "groq" else ["azure", "groq"]

    for attempt in range(3):
        for p in providers_order:
            try:
                start_time = time.time()
                print(f"🔄 LiteLLM — Appel via {p.upper()}...")

                if p == "azure":
                    return call_azure_direct(prompt, temperature, max_tokens)

                # Groq via LiteLLM
                config = PROVIDERS[p]
                response = completion(
                    model=config["model"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=config["timeout"]
                )
                return {
                    "content": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens,
                    "response_time": round(time.time() - start_time, 2),
                    "provider": p,
                    "model": config["model"]
                }

            except Exception as e:
                if "rate_limit" in str(e).lower():
                    print(f"⏳ Rate limit — attente 15s...")
                    time.sleep(15)
                    break
                print(f"⚠️ {p.upper()} failed : {e}")
                continue

    raise Exception("Tous les providers ont échoué après 3 tentatives")