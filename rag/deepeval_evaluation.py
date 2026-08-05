import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric
)
from deepeval.test_case import LLMTestCase
from rag.vectorstore import search_agents

def evaluate_rag_deepeval(query: str, answer: str, contexts: list) -> dict:
    """
    Évaluation RAG avec DeepEval — métriques production-grade
    """
    print("\n📊 DeepEval — Évaluation qualité RAG...")

    test_case = LLMTestCase(
        input=query,
        actual_output=answer,
        retrieval_context=contexts,
        expected_output=answer
    )

    metrics = [
        AnswerRelevancyMetric(threshold=0.5, model="gpt-4o-mini"),
        FaithfulnessMetric(threshold=0.5, model="gpt-4o-mini"),
        ContextualPrecisionMetric(threshold=0.5, model="gpt-4o-mini"),
        ContextualRecallMetric(threshold=0.5, model="gpt-4o-mini"),
    ]

    results = {}
    for metric in metrics:
        metric.measure(test_case)
        name = metric.__class__.__name__.replace("Metric", "")
        results[name] = round(metric.score, 3)
        emoji = "🟢" if metric.score > 0.7 else "🟡" if metric.score > 0.5 else "🔴"
        print(f"   {emoji} {name} : {metric.score:.3f}")

    return results


if __name__ == "__main__":
    query = "voilier 80000€ traversée Méditerranée Atlantique assistance 24h"
    rag_results = search_agents(query, n_results=3)
    contexts = [r["description"] for r in rag_results]
    answer = f"Les agents recommandés sont : {', '.join([r['nom'] for r in rag_results])}"
    
    results = evaluate_rag_deepeval(query, answer, contexts)
    print(f"\n✅ Scores DeepEval : {results}")