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
    def __init__(self):
        self.model_name = "cerebras/gpt-oss-120b"

    def load_model(self):
        return self

    def generate(self, prompt: str, *args, **kwargs) -> str:
        result = call_llm(prompt, temperature=0.1, max_tokens=500, provider="cerebras")
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
    from rag.eval_dataset import EVAL_DATASET
    
    print("📊 Évaluation RAG sur dataset complet\n")
    all_scores = []
    
    for i, case in enumerate(EVAL_DATASET):
        print(f"\n[{i+1}/{len(EVAL_DATASET)}] Query : {case['query'][:50]}...")
        
        rag_results = search_agents(case["query"], n_results=3)
        contexts = [r["description"] for r in rag_results]
        answer = f"Agents recommandés : {', '.join([r['nom'] for r in rag_results])}"
        
        # Vérifie si les bons agents sont trouvés
        found = [a for a in case["expected_agents"] if any(a in r["nom"] for r in rag_results)]
        precision = len(found) / len(case["expected_agents"])
        print(f"   🎯 Précision agents attendus : {precision:.0%} ({found})")
        
        scores = evaluate_rag_deepeval(
            query=case["query"],
            answer=answer,
            contexts=contexts
        )
        scores["agent_precision"] = precision
        all_scores.append(scores)
    
    # Moyennes finales
    print("\n" + "="*50)
    print("📊 SCORES FINAUX DEEPEVAL")
    print("="*50)
    metrics = ["AnswerRelevancy", "Faithfulness", "ContextualPrecision", "agent_precision"]
    for m in metrics:
        values = [s.get(m, 0) for s in all_scores]
        avg = round(sum(values) / len(values), 3)
        emoji = "🟢" if avg > 0.7 else "🟡" if avg > 0.5 else "🔴"
        print(f"{emoji} {m} : {avg}")