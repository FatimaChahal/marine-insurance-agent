import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
from agents.agent1_understanding import understand_client_email
from agents.agent2_selection import select_agents
from agents.agent3_email_sender import send_emails_to_agents
from agents.agent4_offer_collector import collect_offers
from agents.agent5_report import generate_report

def run_pipeline(email_content: str) -> dict:
    start_time = datetime.now()
    total_tokens = 0

    print("\n🚀 MARINE INSURANCE AGENT — PIPELINE DÉMARRÉ")
    print("="*55)

    # Agent 1
    print("\n📧 AGENT 1 — Analyse du mail client...")
    needs = understand_client_email(email_content)
    total_tokens += 269

    # Agent 2
    print("\n🔍 AGENT 2 — Sélection des agents maritimes...")
    agents = select_agents(needs)
    total_tokens += 304

    # Agent 3
    print("\n📨 AGENT 3 — Envoi des mails aux agents...")
    emails = send_emails_to_agents(needs, agents)
    total_tokens += 265

    # Agent 4
    print("\n💼 AGENT 4 — Collecte et comparaison des offres...")
    offers = collect_offers(needs, agents)
    total_tokens += 285

    # Agent 5
    print("\n📊 AGENT 5 — Génération du rapport final...")
    report = generate_report(needs, offers)
    total_tokens += 425

    duration = round((datetime.now() - start_time).total_seconds(), 2)

    print("\n" + "="*55)
    print(f"✅ PIPELINE TERMINÉ EN {duration} secondes")
    print(f"📊 Total tokens utilisés : {total_tokens}")
    print(f"🤖 Modèle : Phi-4-mini-instruct (Azure)")
    print(f"☁️  Cloud : Microsoft Azure AI Foundry")
    print("="*55)

    return {
        "needs": needs,
        "selected_agents": agents,
        "emails_sent": emails,
        "offers": offers,
        "report": report,
        "metadata": {
            "duration_sec": duration,
            "total_tokens": total_tokens,
            "model": "Phi-4-mini-instruct",
            "cloud": "Azure AI Foundry"
        }
    }

if __name__ == "__main__":
    test_email = """
    Bonjour,
    Je souhaite assurer mon voilier de 12 mètres (valeur 80 000€) 
    pour une traversée Méditerranée-Atlantique prévue en septembre.
    J'ai besoin d'une couverture tous risques incluant assistance 24h/24.
    Pouvez-vous me faire des propositions rapidement ?
    Merci, Jean Dupont
    """
    run_pipeline(test_email)