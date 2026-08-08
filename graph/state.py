from typing import TypedDict, List, Optional, Annotated
from datetime import datetime
import operator



class InsuranceState(TypedDict):
    """
    État partagé entre tous les agents LangGraph
    """
    # Input
    raw_email: str
    client_id: Optional[str]

    # Agent 1 — Compréhension
    client_needs: Optional[dict]
    client_anonymized: Optional[dict]

    # Agent 2 — Sélection RAG
    selected_agents: Optional[List[dict]]
    rag_scores: Optional[dict]

    # Agent 3 — Emails
    emails_sent: Optional[List[dict]]

    # Agent 4 — Offres RAG
    offers_collected: Optional[List[dict]]

    # Agent 5 — Rapport
    final_report: Optional[str]

    # Medallion
    silver_id: Optional[int]

    # Metadata MLOps
    metadata: Annotated[List[dict], operator.add]
    errors: Annotated[List[str], operator.add]
    start_time: Optional[str]
    status: Optional[str]
    confidence: Optional[float]
    needs_human_review: Optional[bool]