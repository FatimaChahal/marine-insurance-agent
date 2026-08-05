import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
from utils.azure_client import call_phi
from utils.logger import log_agent

def collect_offers(client_needs: dict, selected_agents: list) -> list:
    agents_list = ", ".join([a['nom'] for a in selected_agents])

    prompt = f"""
    Simule {len(selected_agents)} offres d'assurance maritime de : {agents_list}
    Pour : {client_needs['type_bateau']} de {client_needs['valeur_estimee']}€, 
    zone {client_needs['zone_navigation']}.
    JSON : [{{"agent":"...","prime_annuelle":"...","franchise":"...","garanties":"...","note":8}}]
    """

    result = call_phi(prompt, temperature=0.1, max_tokens=400)
    log_agent("Agent4_OfferCollector", result, result["tokens_used"], result["response_time"])

    content = re.sub(r"```json|```", "", result["content"]).strip()
    offers = json.loads(content)

    print(f"✅ Agent 4 — {len(offers)} offres collectées et comparées")
    return offers

if __name__ == "__main__":
    test_needs = {
        "type_bateau": "voilier",
        "valeur_estimee": 80000,
        "zone_navigation": "Méditerranée-Atlantique"
    }
    test_agents = [
        {"nom": "AXA Marine"},
        {"nom": "Swiss Life Nautique"},
        {"nom": "Allianz Maritime"}
    ]
    collect_offers(test_needs, test_agents)