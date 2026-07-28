import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mlflow
from datetime import datetime

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("marine-insurance-agent")

def log_pipeline_run(metadata: list, rag_scores: dict, duration: float, status: str):
    """
    Log chaque run du pipeline dans MLflow
    """
    with mlflow.start_run(run_name=f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        
        # Paramètres
        mlflow.log_param("model", "Phi-4-mini-instruct")
        mlflow.log_param("cloud", "Azure AI Foundry")
        mlflow.log_param("nb_agents", 5)
        mlflow.log_param("rag_enabled", True)
        mlflow.log_param("guardrails_enabled", True)

        # Métriques pipeline
        mlflow.log_metric("duration_sec", duration)
        mlflow.log_metric("status", 1 if status == "completed" else 0)

        # Métriques RAG
        if rag_scores:
            for agent_score in rag_scores.get("agents_scores", []):
                mlflow.log_metric(
                    f"rag_score_{agent_score['nom'].replace(' ', '_')}",
                    agent_score["score"]
                )

        # Métriques tokens par agent
        total_tokens = 0
        for m in metadata:
            if "tokens" in m:
                mlflow.log_metric(f"tokens_{m['agent']}", m["tokens"])
                total_tokens += m["tokens"]
        mlflow.log_metric("total_tokens", total_tokens)

        print(f"✅ MLflow — Run loggé (durée: {duration}s, tokens: {total_tokens})")

if __name__ == "__main__":
    test_metadata = [
        {"agent": "Agent1", "tokens": 200, "time": 3.1},
        {"agent": "Agent2_RAG", "rag_results": 3},
        {"agent": "Agent3", "tokens": 250, "emails_sent": 3},
        {"agent": "Agent4", "tokens": 300, "offers": 3},
        {"agent": "Agent5", "tokens": 400}
    ]
    test_rag_scores = {
        "agents_scores": [
            {"nom": "Allianz Maritime", "score": 0.539},
            {"nom": "MAIF Mer", "score": 0.523},
            {"nom": "Swiss Life Nautique", "score": 0.497}
        ]
    }
    log_pipeline_run(test_metadata, test_rag_scores, 32.6, "completed")
    print("✅ Vérifie avec : mlflow ui")