import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
from datetime import datetime
from langgraph.graph import StateGraph, END
from graph.state import InsuranceState
from graph.guardrails import anonymize_email, validate_output, check_prompt_injection
from rag.vectorstore import search_agents
from utils.azure_client import call_phi, parse_json_response
from utils.logger import log_agent

from monitoring.mlflow_config import log_pipeline_run
from monitoring.langfuse_config import trace_agent
from utils.azure_client import call_phi, parse_json_response
from medallion.pipeline import init_db, save_bronze, save_silver, save_gold

# Init Medallion DB au démarrage
init_db()

# ─── NODE 1 : Guardrails + Compréhension ────────────────────────────────────
def node_understand(state: InsuranceState) -> InsuranceState:
    print("\n📧 AGENT 1 — Guardrails + Compréhension mail...")

    # Guardrail : vérif injection
    if not check_prompt_injection(state["raw_email"]):
        return {**state, "status": "error", "errors": ["Prompt injection détectée"]}

    # Guardrail : anonymisation RGPD
    anonymized_email, pii_map = anonymize_email(state["raw_email"])

    # Appel LLM
    prompt = f"""
    Analyse ce mail et extrait en JSON :
    - type_bateau, valeur_estimee (nombre), zone_navigation,
      duree_souhaitee, besoins_specifiques, urgence (haute/moyenne/basse)
    Mail : {anonymized_email}
    JSON uniquement.
    """
    result = call_phi(prompt, temperature=0.1, max_tokens=300)
    log_agent("Agent1_Understanding", result, result["tokens_used"], result["response_time"])

    content = result["content"]
    content = re.sub(r"```json|```", "", content).strip()
    try:
        needs = json.loads(content)
    except:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        needs = json.loads(match.group()) if match else {}

    print(f"✅ Agent 1 — Besoins extraits, {len(pii_map)} données anonymisées")

    trace_agent(
        agent_name="Agent1_Understanding",
        input_data=state["raw_email"][:200],
        output_data=str(needs)[:200],
        tokens=result["tokens_used"],
        response_time=result["response_time"]
    )

    # Medallion — Bronze + Silver
    bronze_id = save_bronze(
        client_id=state.get("client_id", "anonymous"),
        raw_email=state["raw_email"]
    )
    silver_id = save_silver(
        bronze_id=bronze_id,
        client_id=state.get("client_id", "anonymous"),
        anonymized_email=anonymized_email,
        needs=needs,
        pii_count=len(pii_map)
    )

    return {
        **state,
        "client_needs": needs,
        "client_anonymized": {"email": anonymized_email, "pii_map": pii_map},
        "silver_id": silver_id,
        "metadata": [{"agent": "Agent1", "tokens": result["tokens_used"], "time": result["response_time"]}]
    }

# ─── NODE 2 : RAG Sélection ──────────────────────────────────────────────────
def node_select(state: InsuranceState) -> InsuranceState:
    print("\n🔍 AGENT 2 — Sélection RAG agents maritimes...")

    needs = state["client_needs"]
    query = f"{needs['type_bateau']} {needs['valeur_estimee']}€ {needs['zone_navigation']} {needs['besoins_specifiques']}"

    # RAG ChromaDB
    rag_results = search_agents(query, n_results=3)

    print(f"✅ Agent 2 — {len(rag_results)} agents trouvés via RAG")
    for r in rag_results:
        print(f"   → {r['nom']} (score RAG: {r['score']})")

    trace_agent(
        agent_name="Agent2_RAG_Selection",
        input_data=query,
        output_data=str(rag_results)[:200],
        tokens=0,
        response_time=0
    )

    return {
        **state,
        "selected_agents": rag_results,
        "rag_scores": {"agents_scores": [{"nom": r["nom"], "score": r["score"]} for r in rag_results]},
        "metadata": [{"agent": "Agent2_RAG", "rag_results": len(rag_results)}]
    }

# ─── NODE 3 : Envoi mails ────────────────────────────────────────────────────
def node_send_emails(state: InsuranceState) -> InsuranceState:
    print("\n📨 AGENT 3 — Génération et envoi des mails...")

    needs = state["client_needs"]
    agents = state["selected_agents"]
    agents_list = ", ".join([a['nom'] for a in agents])

    prompt = f"""
    Rédige {len(agents)} mails professionnels courts pour demander des offres d'assurance maritime.
    Client : {needs['type_bateau']} de {needs['valeur_estimee']}€,
    zone {needs['zone_navigation']}, urgence {needs['urgence']}.
    Agents : {agents_list}
    
    Réponds UNIQUEMENT avec ce JSON, sans texte avant ou après :
    [{{"agent": "nom_agent", "mail": "contenu_mail"}}]
    """

    result = call_phi(prompt, temperature=0.1, max_tokens=400)
    log_agent("Agent3_EmailSender", result, result["tokens_used"], result["response_time"])

    content = result["content"]
    emails = parse_json_response(content, fallback=[
        {"agent": a['nom'], "mail": f"Demande d'offre assurance pour voilier {needs['valeur_estimee']}€"}
        for a in agents
    ])

    return {
        **state,
        "emails_sent": emails,
        "metadata": state["metadata"] + [{"agent": "Agent3", "tokens": result["tokens_used"], "emails_sent": len(emails)}]
    }

# ─── NODE 4 : Collecte offres RAG ────────────────────────────────────────────
def node_collect_offers(state: InsuranceState) -> InsuranceState:
    print("\n💼 AGENT 4 — Collecte et comparaison des offres...")

    needs = state["client_needs"]
    agents = state["selected_agents"]
    agents_list = ", ".join([a['nom'] for a in agents])

    prompt = f"""
    Simule {len(agents)} offres d'assurance maritime de : {agents_list}
    Pour : {needs['type_bateau']} de {needs['valeur_estimee']}€,
    zone {needs['zone_navigation']}.
    JSON : [{{"agent":"...","prime_annuelle":"...","franchise":"...","garanties":"...","note":8}}]
    """

    result = call_phi(prompt, temperature=0.1, max_tokens=400)
    log_agent("Agent4_Offers", result, result["tokens_used"], result["response_time"])

    content = result["content"]
    offers = parse_json_response(content, fallback=[
        {"agent": a['nom'], "prime_annuelle": "1200€", "franchise": "500€", "garanties": "RC, dommages", "note": 7}
        for a in agents
    ])

    print(f"✅ Agent 4 — {len(offers)} offres collectées")

    trace_agent(
        agent_name="Agent4_OfferCollector",
        input_data=agents_list,
        output_data=str(offers)[:200],
        tokens=result["tokens_used"],
        response_time=result["response_time"]
    )

    return {
        **state,
        "offers_collected": offers,
        "metadata": [{"agent": "Agent4", "tokens": result["tokens_used"], "offers": len(offers)}]
    }

# ─── NODE 5 : Rapport final ──────────────────────────────────────────────────
def node_report(state: InsuranceState) -> InsuranceState:
    print("\n📊 AGENT 5 — Génération du rapport final...")

    needs = state["client_needs"]
    offers = state["offers_collected"]

    best_offer = min(offers, key=lambda x: int(x['prime_annuelle'].replace('€', '').replace(' ', '')))

    prompt = f"""
    Expert assurance maritime. Client : {needs['type_bateau']} {needs['valeur_estimee']}€,
    zone {needs['zone_navigation']}, besoin : {needs['besoins_specifiques']}.
    Offres : {json.dumps(offers, ensure_ascii=False)}
    Meilleure offre prix : {best_offer['agent']} à {best_offer['prime_annuelle']}
    Rapport client : recommandation justifiée, comparaison rapide, prochaine étape.
    Maximum 10 lignes, ton professionnel.
    """

    result = call_phi(prompt, temperature=0.1, max_tokens=500)
    log_agent("Agent5_Report", result, result["tokens_used"], result["response_time"])

    # Guardrail output
    if not validate_output(result["content"]):
        print("⚠️ Guardrail — données personnelles détectées dans le rapport !")

    print(f"✅ Agent 5 — Rapport généré")

    # Langfuse trace
    trace_agent(
        agent_name="Agent5_Report",
        input_data=str(needs),
        output_data=result["content"][:200],
        tokens=result["tokens_used"],
        response_time=result["response_time"]
    )

    # Medallion — Gold
    save_gold(
        silver_id=state.get("silver_id", 1),
        client_id=state.get("client_id", "anonymous"),
        result={
            "selected_agents": [a["nom"] for a in state["selected_agents"]],
            "offers_count": len(state["offers_collected"]),
            "final_report": result["content"],
            "rag_scores": state["rag_scores"],
            "metadata": state["metadata"],
            "duration_sec": 0
        }
    )

    return {
        **state,
        "final_report": result["content"],
        "status": "completed",
        "metadata": [{"agent": "Agent5", "tokens": result["tokens_used"]}]
    }

# ─── Construction du Graph ───────────────────────────────────────────────────
def should_retry_search(state: InsuranceState) -> str:
    """
    Décision : si moins de 2 agents trouvés → élargir la recherche
    """
    agents = state.get("selected_agents", [])
    if len(agents) < 2:
        print("⚠️ Moins de 2 agents trouvés — élargissement de la recherche...")
        return "retry_search"
    return "send_emails"

def should_retry_offers(state: InsuranceState) -> str:
    """
    Décision : si moins de 2 offres reçues → relancer les mails
    """
    offers = state.get("offers_collected", [])
    if len(offers) < 2:
        print("⚠️ Moins de 2 offres reçues — relance des mails...")
        return "retry_emails"
    return "report"

def node_broad_search(state: InsuranceState) -> InsuranceState:
    """
    Node de fallback : recherche élargie si RAG insuffisant
    """
    print("\n🔄 FALLBACK — Recherche élargie...")
    from rag.vectorstore import search_agents
    
    # Recherche plus large
    rag_results = search_agents("assurance maritime", n_results=5)
    
    print(f"✅ Fallback — {len(rag_results)} agents trouvés")
    
    return {
        **state,
        "selected_agents": rag_results[:3],
        "metadata": state["metadata"] + [{"agent": "Fallback_Search", "reason": "less_than_2_agents"}]
    }

def build_pipeline() -> StateGraph:
    graph = StateGraph(InsuranceState)

    # Nodes
    graph.add_node("understand", node_understand)
    graph.add_node("select", node_select)
    graph.add_node("broad_search", node_broad_search)
    graph.add_node("send_emails", node_send_emails)
    graph.add_node("collect_offers", node_collect_offers)
    graph.add_node("report", node_report)

    # Entry point
    graph.set_entry_point("understand")

    # Edges normaux
    graph.add_edge("understand", "select")

    # Edge conditionnel 1 : assez d'agents ?
    graph.add_conditional_edges(
        "select",
        should_retry_search,
        {
            "retry_search": "broad_search",
            "send_emails": "send_emails"
        }
    )

    # Après fallback → envoyer les mails
    graph.add_edge("broad_search", "send_emails")

    # Edge conditionnel 2 : assez d'offres ?
    graph.add_edge("send_emails", "collect_offers")
    graph.add_conditional_edges(
        "collect_offers",
        should_retry_offers,
        {
            "retry_emails": "send_emails",
            "report": "report"
        }
    )

    graph.add_edge("report", END)

    return graph.compile()

def run_with_monitoring(email_content: str) -> dict:
    """
    Lance le pipeline avec MLflow + Langfuse
    """
    from datetime import datetime
    start = datetime.now()

    pipeline = build_pipeline()
    initial_state = {
        "raw_email": email_content,
        "client_needs": None,
        "client_anonymized": None,
        "selected_agents": None,
        "rag_scores": None,
        "emails_sent": None,
        "offers_collected": None,
        "final_report": None,
        "metadata": [],
        "errors": [],
        "start_time": datetime.now().isoformat(),
        "status": "running"
    }

    result = pipeline.invoke(initial_state)
    duration = round((datetime.now() - start).total_seconds(), 2)

    # Log MLflow
    log_pipeline_run(
        metadata=result["metadata"],
        rag_scores=result["rag_scores"],
        duration=duration,
        status=result["status"]
    )

    return result

if __name__ == "__main__":
    pipeline = build_pipeline()

    initial_state = InsuranceState(
            raw_email=request.email_content,
            client_id=request.client_id,
            client_needs=None,
            client_anonymized=None,
            selected_agents=None,
            rag_scores=None,
            emails_sent=None,
            offers_collected=None,
            final_report=None,
            silver_id=None,
            metadata=[],
            errors=[],
            start_time=datetime.now().isoformat(),
            status="running"
        )

    result = pipeline.invoke(initial_state)

    print("\n" + "="*55)
    print("📊 RÉSUMÉ PIPELINE LANGGRAPH")
    print("="*55)
    print(f"Status : {result['status']}")
    print(f"Agents sélectionnés : {[a['nom'] for a in result['selected_agents']]}")
    print(f"RAG scores : {result['rag_scores']}")
    print(f"Offres collectées : {len(result['offers_collected'])}")
    print(f"Metadata : {len(result['metadata'])} events")
    print("\n📄 RAPPORT FINAL :")
    print(result['final_report'])