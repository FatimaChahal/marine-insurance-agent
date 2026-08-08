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
    
    silver_id = None  # ← ajoute cette ligne ici
    
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
    
    # Cherche le JSON même s'il y a du texte avant
    try:
        # Essai direct
        needs = json.loads(content)
    except:
        # Cherche un objet JSON dans le texte
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            needs = json.loads(match.group())
        else:
            # Fallback — structure minimale
            needs = {
                "type_bateau": "bateau",
                "valeur_estimee": 50000,
                "zone_navigation": "Méditerranée",
                "besoins_specifiques": "couverture standard",
                "urgence": "moyenne",
                "duree_souhaitee": "1 an"
            }
            print("⚠️ JSON parsing failed — fallback utilisé")
    
    # Sécurise les clés manquantes
    needs.setdefault("type_bateau", "bateau")
    needs.setdefault("valeur_estimee", 50000)
    needs.setdefault("zone_navigation", "Méditerranée")
    needs.setdefault("besoins_specifiques", "couverture standard")
    needs.setdefault("urgence", "moyenne")

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

    # RAG — tous les agents avec score > seuil
    all_results = search_agents(query, n_results=8)
    
    # Filtre : garde seulement les agents avec score > 0.4
    SCORE_THRESHOLD = 0.4
    relevant_agents = [a for a in all_results if a["score"] > SCORE_THRESHOLD]
    
    # Minimum 2 agents
    if len(relevant_agents) < 2:
        relevant_agents = all_results[:2]

    print(f"✅ Agent 2 — {len(relevant_agents)}/{len(all_results)} agents pertinents (seuil RAG: {SCORE_THRESHOLD})")
    for a in relevant_agents:
        print(f"   → {a['nom']} (score: {a['score']})")

    # DeepEval — évaluation qualité RAG
    # DeepEval — évaluation qualité RAG
    try:
        from rag.deepeval_evaluation import evaluate_rag_deepeval
        query = f"{needs['type_bateau']} {needs['valeur_estimee']}€ {needs['zone_navigation']}"
        answer = f"Agents sélectionnés : {', '.join([a['nom'] for a in relevant_agents])}"
        contexts = [a["description"] for a in relevant_agents]
        deepeval_scores = evaluate_rag_deepeval(query, answer, contexts)
        print(f"📊 DeepEval scores : {deepeval_scores}")
    except Exception as e:
        deepeval_scores = {}
        print(f"⚠️ DeepEval skipped : {e}")

    return {
        **state,
        "selected_agents": relevant_agents,
        "rag_scores": {"agents_scores": [{"nom": a["nom"], "score": a["score"]} for a in relevant_agents]},
        "metadata": state["metadata"] + [{"agent": "Agent2_RAG", "rag_results": len(relevant_agents), "total_candidates": len(all_results)}]
    }

# ─── NODE 3 : Envoi mails ────────────────────────────────────────────────────
def node_send_emails(state: InsuranceState) -> InsuranceState:
    print("\n📨 AGENT 3 — Génération et envoi des mails...")

    needs = state["client_needs"]
    agents = state["selected_agents"]
    agents_list = ", ".join([a['nom'] for a in agents])

    prompt = f"""Pour ces assureurs : {agents_list}
    Client : {needs['type_bateau']} {needs['valeur_estimee']}€, {needs['zone_navigation']}, urgence {needs['urgence']}.
    JSON UNIQUEMENT : [{{"agent":"nom","mail":"texte court du mail"}}]"""

    result = call_phi(prompt, temperature=0.1, max_tokens=600)
    log_agent("Agent3_EmailSender", result, result["tokens_used"], result["response_time"])

    content = result["content"]

    try:
        content_clean = re.sub(r"```json|```", "", content).strip()
        match = re.search(r'\[.*\]', content_clean, re.DOTALL)
        if match:
            emails_raw = json.loads(match.group())
            # Normalise le format — mail peut être string ou dict
            emails = []
            for e in emails_raw:
                mail_content = e.get("mail", "")
                if isinstance(mail_content, dict):
                    mail_content = mail_content.get("corps", str(mail_content))
                emails.append({"agent": e["agent"], "mail": mail_content})
        else:
            raise ValueError("No JSON array found")
    except Exception as ex:
        print(f"⚠️ JSON parsing failed ({ex}) — fallback utilisé")
        emails = [{"agent": a['nom'], "mail": f"Demande d'offre pour {needs['type_bateau']} {needs['valeur_estimee']}€"} for a in agents]

    print(f"✅ Agent 3 — {len(emails)} mails envoyés")
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
    
    from rag.data import get_offer
    
    # Offres basées sur des tarifs réalistes — pas inventées par le LLM
    offers = []
    valeur = float(str(needs.get("valeur_estimee", 50000)).replace("€", "").replace(" ", "") or 50000)
    zone = needs.get("zone_navigation", "Méditerranée")
    
    for agent in agents:
        offer = get_offer(agent["nom"], valeur, zone)
        offers.append(offer)
        print(f"   → {agent['nom']} : {offer['prime_annuelle']} / franchise {offer['franchise']}")

    log_agent("Agent4_Offers", {"content": str(offers)}, len(offers) * 50, 0.1)
    
    print(f"✅ Agent 4 — {len(offers)} offres collectées")
    
    return {
        **state,
        "offers_collected": offers,
        "metadata": state["metadata"] + [{"agent": "Agent4", "offers": len(offers)}]
    }

# ─── NODE 5 : Rapport final ──────────────────────────────────────────────────
def node_report(state: InsuranceState) -> InsuranceState:
    print("\n📊 AGENT 5 — Génération du rapport final...")

    needs = state["client_needs"]
    offers = state["offers_collected"]

    best_offer = min(offers, key=lambda x: int(x['prime_annuelle'].replace('€', '').replace(' ', '')))

    prompt = f"""
    Tu es un expert en assurance maritime.
    Client : {needs['type_bateau']} de {needs['valeur_estimee']}€, 
    zone {needs['zone_navigation']}, besoin : {needs['besoins_specifiques']}.
    
    Offres reçues de {len(offers)} assureurs : {json.dumps(offers, ensure_ascii=False)}
    
    Génère un rapport client avec :
    1. CLASSEMENT des offres de la meilleure à la moins bonne (avec justification)
    2. RECOMMANDATION PRINCIPALE claire avec raisons
    3. TABLEAU COMPARATIF (prime, franchise, garanties, note)
    4. PROCHAINE ÉTAPE pour le client
    
    Format professionnel, clair et concis.
    """

    result = call_phi(prompt, temperature=0.1, max_tokens=1500)
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
    
    test_email = """
    Bonjour,
    Je souhaite assurer mon voilier de 12 mètres (valeur 80 000€) 
    pour une traversée Méditerranée-Atlantique prévue en septembre.
    J'ai besoin d'une couverture tous risques incluant assistance 24h/24.
    Pouvez-vous me faire des propositions rapidement ?
    Merci, Jean Dupont
    """
    
    initial_state = {
        "raw_email": test_email,
        "client_id": "test_client",
        "client_needs": None,
        "client_anonymized": None,
        "selected_agents": None,
        "rag_scores": None,
        "emails_sent": None,
        "offers_collected": None,
        "final_report": None,
        "silver_id": None,
        "metadata": [],
        "errors": [],
        "start_time": datetime.now().isoformat(),
        "status": "running"
    }
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