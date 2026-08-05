import os
import time
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# Configuration des providers
os.environ["AZURE_API_KEY"] = os.getenv("AZURE_API_KEY", "")
os.environ["AZURE_API_BASE"] = os.getenv("AZURE_ENDPOINT", "")
os.environ["AZURE_API_VERSION"] = "2025-01-01-preview"
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

PROVIDERS = {
    "groq": {
        "model": "groq/llama-3.3-70b-versatile",
        "timeout": 30
    },
    "azure": {
        "model": "azure/Phi-4-mini-instruct",
        "timeout": 120
    }
}

def call_llm(prompt: str, temperature: float = 0.1, max_tokens: int = 500, provider: str = "azure") -> dict:
    """
    Appel LLM unifié via LiteLLM — supporte Azure, Groq, OpenAI...
    Fallback automatique si le provider principal échoue
    """
    providers_order = [provider, "groq"] if provider == "azure" else [provider, "azure"]
    
    for p in providers_order:
        try:
            config = PROVIDERS[p]
            start_time = time.time()
            
            print(f"🔄 LiteLLM — Appel via {p.upper()}...")
            
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
            print(f"⚠️ {p.upper()} failed : {e}")
            if p == providers_order[-1]:
                raise Exception(f"Tous les providers ont échoué : {e}")
            print(f"🔄 Fallback vers {providers_order[1].upper()}...")
            continue
    
    for attempt in range(3):
        for p in providers_order:
            try:
                config = PROVIDERS[p]
                start_time = time.time()
                print(f"🔄 LiteLLM — Appel via {p.upper()}...")
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
                    print(f"⏳ Rate limit Groq — attente 15s avant retry...")
                    time.sleep(15)
                    break  # Sort de la boucle providers et retry depuis Groq
                print(f"⚠️ {p.upper()} failed : {e}")
                continue

    raise Exception("Tous les providers ont échoué après 3 tentatives")