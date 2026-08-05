"""
A2A Server — Expose les agents via HTTP selon le protocole Google A2A
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from a2a.agent_cards import AGENT_CARDS, get_agent_card, list_agent_cards
from rag.vectorstore import search_agents
from graph.guardrails import anonymize_email, check_prompt_injection

app = FastAPI(
    title="Marine Insurance A2A Server",
    description="Agent-to-Agent Protocol — Google A2A Standard",
    version="1.0.0"
)

class A2ARequest(BaseModel):
    skill_id: str
    input_data: dict
    caller_agent: str = "external"

# ─── Discovery endpoints ─────────────────────────────────────────────────────

@app.get("/.well-known/agent.json")
def get_main_agent_card():
    """Point d'entrée A2A standard — découverte de l'agent"""
    return {
        "name": "Marine Insurance Multi-Agent System",
        "description": "Pipeline multi-agents pour l'assurance maritime",
        "version": "1.0.0",
        "url": "http://localhost:8001",
        "agents": list_agent_cards()
    }

@app.get("/a2a/agents")
def list_agents():
    """Liste tous les agents disponibles"""
    return {"agents": list_agent_cards()}

@app.get("/a2a/{agent_id}/card")
def get_card(agent_id: str):
    """Retourne la carte d'un agent spécifique"""
    card = get_agent_card(agent_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} non trouvé")
    return card

# ─── Agent endpoints ─────────────────────────────────────────────────────────

@app.post("/a2a/agent1/execute")
def execute_agent1(request: A2ARequest):
    """Agent 1 — Compréhension mail"""
    email = request.input_data.get("email", "")

    if not check_prompt_injection(email):
        raise HTTPException(status_code=400, detail="Prompt injection détectée")

    anonymized, pii_map = anonymize_email(email)

    return {
        "agent": "agent1_understanding",
        "status": "success",
        "output": {
            "anonymized_email": anonymized,
            "pii_detected": len(pii_map),
            "message": "Email anonymisé et prêt pour traitement"
        },
        "caller": request.caller_agent
    }

@app.post("/a2a/agent2/execute")
def execute_agent2(request: A2ARequest):
    """Agent 2 — Sélection RAG"""
    needs = request.input_data.get("needs", {})
    n_results = request.input_data.get("n_results", 3)

    query = f"{needs.get('type_bateau', '')} {needs.get('valeur_estimee', '')}€ {needs.get('zone_navigation', '')}"
    results = search_agents(query, n_results=n_results)

    return {
        "agent": "agent2_selection",
        "status": "success",
        "output": {
            "selected_agents": results,
            "rag_scores": [{"nom": r["nom"], "score": r["score"]} for r in results]
        },
        "caller": request.caller_agent
    }

@app.get("/a2a/health")
def health():
    return {"status": "healthy", "protocol": "A2A", "agents": len(AGENT_CARDS)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)