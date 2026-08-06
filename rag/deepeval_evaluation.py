import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, ContextualPrecisionMetric
from deepeval.test_case import LLMTestCase
from utils.litellm_client import call_llm
from rag.vectorstore import search_agents


class GroqEvaluator(DeepEvalBaseLLM):
    """
    LLM custom pour DeepEval — utilise Groq via LiteLLM
    """
    def __init__(self):
        self.model_name = "groq/llama-3.3-70b-versatile"

    def load_model(self):
        return self

    def generate(self, prompt: str, *args, **kwargs) -> str:
        result = call_llm(prompt, temperature=0.1, max_tokens=500, provider="groq")
        return result["content"]

    async def a_generate(self, prompt: str, *args, **kwargs) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return self.model_name


def evaluate_rag_deepeval(query: str, answer: str, contexts: list) -> dict:
    """
    Évaluation RAG avec DeepEval et Groq comme LLM juge
    """
    print("\n📊 DeepEval — Évaluation qualité RAG...")

    evaluator = GroqEvaluator()

    test_case = LLMTestCase(
        input=query,
        actual_output=answer,
        retrieval_context=contexts,
        expected_output=answer
    )

    metrics = [
        AnswerRelevancyMetric(threshold=0.5, model=evaluator, verbose_mode=False),
        FaithfulnessMetric(threshold=0.5, model=evaluator, verbose_mode=False),
        ContextualPrecisionMetric(threshold=0.5, model=evaluator, verbose_mode=False),
    ]

    results = {}
    for metric in metrics:
        try:
            metric.measure(test_case)
            name = metric.__class__.__name__.replace("Metric", "")
            score = round(metric.score, 3)
            results[name] = score
            emoji = "🟢" if score > 0.7 else "🟡" if score > 0.5 else "🔴"
            print(f"   {emoji} {name} : {score}")
        except Exception as e:
            print(f"   ⚠️ {metric.__class__.__name__} error : {e}")

    return results


if __name__ == "__main__":
    query = "voilier 80000€ traversée Méditerranée Atlantique assistance 24h"
    rag_results = search_agents(query, n_results=3)
    contexts = [r["description"] for r in rag_results]
    answer = f"Les agents recommandés sont : {', '.join([r['nom'] for r in rag_results])}"

    print(f"Query : {query}")
    print(f"Answer : {answer}")
    print(f"Contexts : {len(contexts)} documents")

    results = evaluate_rag_deepeval(query, answer, contexts)
    print(f"\n✅ Scores DeepEval : {results}")