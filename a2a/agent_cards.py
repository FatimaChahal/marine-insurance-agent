"""
A2A Protocol — Agent Cards
Standard Google 2025 pour la communication inter-agents
https://google.github.io/A2A/
"""

from datetime import datetime

AGENT_CARDS = {
    "agent1_understanding": {
        "name": "Marine Insurance Understanding Agent",
        "description": "Comprend et extrait les besoins d'assurance maritime depuis les mails clients",
        "version": "1.0.0",
        "url": "http://localhost:8001/a2a/agent1",
        "capabilities": {
            "input": ["email_text"],
            "output": ["structured_needs"],
            "languages": ["fr", "en"],
            "streaming": False
        },
        "skills": [
            {
                "id": "extract_needs",
                "name": "Extract Insurance Needs",
                "description": "Extrait les besoins d'assurance maritime depuis un mail client",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Mail client brut"}
                    }
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "type_bateau": {"type": "string"},
                        "valeur_estimee": {"type": "number"},
                        "zone_navigation": {"type": "string"},
                        "urgence": {"type": "string"}
                    }
                }
            }
        ],
        "provider": {
            "name": "Marine Insurance Agent — Fatima Chahal",
            "url": "https://github.com/FatimaChahal/marine-insurance-agent"
        },
        "created_at": datetime.now().isoformat()
    },

    "agent2_selection": {
        "name": "Marine Insurance RAG Selection Agent",
        "description": "Sélectionne les agents maritimes les plus pertinents via RAG sémantique",
        "version": "1.0.0",
        "url": "http://localhost:8001/a2a/agent2",
        "capabilities": {
            "input": ["structured_needs"],
            "output": ["selected_agents"],
            "languages": ["fr", "en"],
            "streaming": False
        },
        "skills": [
            {
                "id": "select_agents",
                "name": "Select Maritime Insurance Agents",
                "description": "Recherche sémantique RAG pour sélectionner les meilleurs assureurs",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "needs": {"type": "object"},
                        "n_results": {"type": "integer", "default": 3}
                    }
                }
            }
        ],
        "provider": {
            "name": "Marine Insurance Agent — Fatima Chahal",
            "url": "https://github.com/FatimaChahal/marine-insurance-agent"
        },
        "created_at": datetime.now().isoformat()
    },

    "agent3_email": {
        "name": "Marine Insurance Email Sender Agent",
        "description": "Génère et envoie des demandes de devis aux agents maritimes sélectionnés",
        "version": "1.0.0",
        "url": "http://localhost:8001/a2a/agent3",
        "capabilities": {
            "input": ["selected_agents", "client_needs"],
            "output": ["emails_sent"],
            "languages": ["fr", "en"],
            "streaming": False
        },
        "skills": [
            {
                "id": "send_quote_requests",
                "name": "Send Quote Requests",
                "description": "Génère et envoie des demandes de devis professionnelles"
            }
        ],
        "provider": {
            "name": "Marine Insurance Agent — Fatima Chahal",
            "url": "https://github.com/FatimaChahal/marine-insurance-agent"
        },
        "created_at": datetime.now().isoformat()
    },

    "agent4_offers": {
        "name": "Marine Insurance Offer Collector Agent",
        "description": "Collecte et compare les offres d'assurance maritime reçues",
        "version": "1.0.0",
        "url": "http://localhost:8001/a2a/agent4",
        "capabilities": {
            "input": ["selected_agents", "client_needs"],
            "output": ["offers_comparison"],
            "languages": ["fr", "en"],
            "streaming": False
        },
        "skills": [
            {
                "id": "collect_compare_offers",
                "name": "Collect and Compare Offers",
                "description": "Collecte les offres et les compare selon prime, franchise, garanties"
            }
        ],
        "provider": {
            "name": "Marine Insurance Agent — Fatima Chahal",
            "url": "https://github.com/FatimaChahal/marine-insurance-agent"
        },
        "created_at": datetime.now().isoformat()
    },

    "agent5_report": {
        "name": "Marine Insurance Report Generator Agent",
        "description": "Génère le rapport final de recommandation pour le client",
        "version": "1.0.0",
        "url": "http://localhost:8001/a2a/agent5",
        "capabilities": {
            "input": ["offers_comparison", "client_needs"],
            "output": ["final_report"],
            "languages": ["fr", "en"],
            "streaming": False
        },
        "skills": [
            {
                "id": "generate_report",
                "name": "Generate Recommendation Report",
                "description": "Génère un rapport de recommandation personnalisé pour le client"
            }
        ],
        "provider": {
            "name": "Marine Insurance Agent — Fatima Chahal",
            "url": "https://github.com/FatimaChahal/marine-insurance-agent"
        },
        "created_at": datetime.now().isoformat()
    }
}

def get_agent_card(agent_id: str) -> dict:
    return AGENT_CARDS.get(agent_id, {})

def list_agent_cards() -> list:
    return list(AGENT_CARDS.values())

if __name__ == "__main__":
    import json
    print("🤖 A2A Agent Cards :")
    for agent_id, card in AGENT_CARDS.items():
        print(f"\n--- {card['name']} ---")
        print(f"URL: {card['url']}")
        print(f"Skills: {[s['id'] for s in card['skills']]}")