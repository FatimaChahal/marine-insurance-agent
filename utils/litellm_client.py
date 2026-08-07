import os
import time
import requests
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

AZURE_ENDPOINT = "https://marine-insurance-agent-resource.services.ai.azure.com/openai/v1/chat/completions"
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")

os.environ["CEREBRAS_API_KEY"] = os.getenv("CEREBRAS_API_KEY", "")

PROVIDERS = {
    "cerebras": {
    "model": "cerebras/gpt-oss-120b",
    "timeout": 30
    },
    "groq": {
        "model": "groq/llama-3.3-70b-versatile",
        "timeout": 30
    },
    "azure": {
        "model": "azure_direct",
        "timeout": 120
    }
}

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")

def call_cerebras_direct(prompt: str, temperature: float = 0.1, max_tokens: int = 500) -> dict:
    """
    Appel Cerebras direct via requests
    """
    import time
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CEREBRAS_API_KEY}"
    }
    body = {
        "model": "gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    start = time.time()
    response = requests.post(
        "https://api.cerebras.ai/v1/chat/completions",
        headers=headers,
        json=body,
        timeout=60
    )
    response.raise_for_status()
    data = response.json()
    return {
        "content": data["choices"][0]["message"]["content"],
        "tokens_used": data["usage"]["total_tokens"],
        "response_time": round(time.time() - start, 2),
        "provider": "cerebras",
        "model": "gpt-oss-120b"
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

def call_llm(prompt: str, temperature: float = 0.1, max_tokens: int = 500, provider: str = "cerebras") -> dict:
    providers_order = ["cerebras", "groq", "azure"]

    for attempt in range(3):
        for p in providers_order:
            try:
                start_time = time.time()
                print(f"🔄 LiteLLM — Appel via {p.upper()}...")

                if p == "azure":
                    return call_azure_direct(prompt, temperature, max_tokens)
                
                if p == "cerebras":
                    return call_cerebras_direct(prompt, temperature, max_tokens)

                # Groq via LiteLLM
                config = PROVIDERS["groq"]
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
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    print(f"⏳ Rate limit — attente 10s...")
                    time.sleep(10)
                    break
                print(f"⚠️ {p.upper()} failed : {e}")
                continue

    raise Exception("Tous les providers ont échoué après 3 tentatives")