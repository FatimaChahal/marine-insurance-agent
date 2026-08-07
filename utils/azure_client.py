import os
import time
import requests
from dotenv import load_dotenv

import re
import json

load_dotenv()

ENDPOINT = "https://marine-insurance-agent-resource.services.ai.azure.com/openai/v1/chat/completions"
API_KEY = os.getenv("AZURE_API_KEY")
MODEL = "Phi-4-mini-instruct"

# def call_llm(prompt: str, provider: str = "azure") -> dict:
#     if provider == "azure":
#         return call_phi(prompt)
#     elif provider == "groq":
#         return call_groq(prompt) 

def call_phi(prompt: str, temperature: float = 0.1, max_tokens: int = 500, retries: int = 3) -> dict:
    from utils.litellm_client import call_llm
    return call_llm(prompt, temperature=temperature, max_tokens=max_tokens, provider="cerebras")

def parse_json_response(content: str, fallback: list = None) -> list:
    """
    Parse robuste du JSON — gère les cas où le LLM ajoute du texte autour
    """
    try:
        content = re.sub(r"```json|```", "", content).strip()
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(content)
    except (json.JSONDecodeError, Exception):
        print("⚠️ JSON parsing failed — fallback utilisé")
        return fallback or []