import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from dotenv import load_dotenv
load_dotenv()

from utils.azure_client import call_phi
from rag.vectorstore import search_agents

def evaluate_faithfulness(answer: str, contexts: list) -> float:
    """
    Mesure si la réponse est bien ancrée dans les contextes
    """
    context_text = " ".join(contexts)
    prompt = f"""
    Contextes disponibles : {context_text[:500]}
    Réponse générée : {answer}
    
    La réponse est-elle fidèle aux contextes ? Réponds avec un score entre 0 et 1.
    JSON : {{"score": 0.9, "raison": "..."}}
    """
    result = call_phi(prompt, temperature=0.1, max_tokens=100)
    content = re.sub(r"```json|```", "", result["content"]).strip()
    try:
        import json
        data = json.loads(content)
        return float(data["score"])
    except:
        return 0.5

def evaluate_relevancy(query: str, answer: str) -> float:
    """
    Mesure si la réponse répond bien à la question
    """
    prompt = f"""
    Question : {query}
    Réponse : {answer}
    
    La réponse répond-elle bien à la question ? Score entre 0 et 1.
    JSON : {{"score": 0.9, "raison": "..."}}
    """
    result = call_phi(prompt, temperature=0.1, max_tokens=100)
    content = re.sub(r"```json|```", "", result["content"]).strip()
    try:
        import json
        data = json.loads(content)
        return float(data["score"])
    except:
        return 0.5

def evaluate_rag(query: str, answer: str, contexts: list) -> dict:
    """
    Évaluation qualité RAG custom — sans dépendance externe
    """
    print("\n📊 RAG Evaluation — Évaluation qualité...")

    faithfulness = evaluate_faithfulness(answer, contexts)
    relevancy = evaluate_relevancy(query, answer)
    
    # Context precision : ratio de contextes pertinents
    context_precision = len([c for c in contexts if any(
        word in c.lower() for word in query.lower().split()
    )]) / len(contexts) if contexts else 0

    results = {
        "faithfulness": round(faithfulness, 3),
        "answer_relevancy": round(relevancy, 3),
        "context_precision": round(context_precision, 3),
    }

    print(f"✅ RAG Evaluation scores :")
    for metric, score in results.items():
        emoji = "🟢" if score > 0.7 else "🟡" if score > 0.5 else "🔴"
        print(f"   {emoji} {metric} : {score}")

    return results


if __name__ == "__main__":
    query = "voilier 80000€ traversée Méditerranée Atlantique assistance 24h"
    rag_results = search_agents(query, n_results=3)
    contexts = [r["description"] for r in rag_results]
    answer = f"Les agents recommandés sont : {', '.join([r['nom'] for r in rag_results])}"
    evaluate_rag(query, answer, contexts)