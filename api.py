import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from graph.pipeline import build_pipeline
from graph.state import InsuranceState

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "marine-insurance-secret-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="API Key invalide ou manquante"
        )
    return api_key

app = FastAPI(
    title="Marine Insurance Agent API",
    description="Multi-agent pipeline pour l'assurance maritime — Azure AI Foundry + LangGraph",
    version="1.0.0"
)

# ─── Modèles ────────────────────────────────────────────────────────────────
class EmailRequest(BaseModel):
    email_content: str
    client_id: str = "anonymous"

class PipelineResponse(BaseModel):
    status: str
    client_id: str
    selected_agents: list
    offers_count: int
    final_report: str
    rag_scores: dict
    metadata: list
    duration_sec: float

# ─── Routes ─────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service": "Marine Insurance Agent",
        "version": "1.0.0",
        "stack": ["Azure AI Foundry", "LangGraph", "RAG ChromaDB", "Langfuse", "Guardrails RGPD"],
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze", response_model=PipelineResponse, dependencies=[Depends(verify_api_key)])
def analyze_email(request: EmailRequest):
    """
    Analyse un mail client et retourne les meilleures offres d'assurance maritime
    """
    try:
        start = datetime.now()
        pipeline = build_pipeline()

        initial_state = InsuranceState(
            raw_email=request.email_content,
            client_needs=None,
            client_anonymized=None,
            selected_agents=None,
            rag_scores=None,
            emails_sent=None,
            offers_collected=None,
            final_report=None,
            metadata=[],
            errors=[],
            start_time=datetime.now().isoformat(),
            status="running"
        )

        result = pipeline.invoke(initial_state)
        duration = round((datetime.now() - start).total_seconds(), 2)

        return PipelineResponse(
            status=result["status"],
            client_id=request.client_id,
            selected_agents=[a["nom"] for a in result["selected_agents"]],
            offers_count=len(result["offers_collected"]),
            final_report=result["final_report"],
            rag_scores=result["rag_scores"] or {},
            metadata=result["metadata"],
            duration_sec=duration
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
def list_agents():
    """
    Liste tous les agents maritimes disponibles dans la base RAG
    """
    from rag.vectorstore import search_agents
    agents = search_agents("assurance maritime voilier", n_results=5)
    return {"agents": agents, "total": len(agents)}