import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
from utils.azure_client import call_phi
from utils.logger import log_agent

AGENTS_MARITIMES = [
    {"nom": "AXA Marine", "specialite": "voiliers", "zones": ["Méditerranée", "Atlantique"]},
    {"nom": "Generali Nautique", "specialite": "voiliers et moteurs", "zones": ["Méditerranée", "Manche"]},
    {"nom": "Allianz Maritime", "specialite": "grands voiliers", "zones": ["Atlantique"]},
    {"nom": "MAIF Mer", "specialite": "plaisance", "zones": ["Méditerranée"]},
    {"nom": "Swiss Life Nautique", "specialite": "yachts de luxe", "zones": ["Méditerranée", "Atlantique"]},
]

def select_agents(client_needs: dict) -> list:
    agents_list = ", ".join([f"{a['nom']} ({a['specialite']}, {'/'.join(a['zones'])})" for a in AGENTS_MARITIMES])
    
    prompt = f"""
    Client : {client_needs['type_bateau']} de {client_needs['valeur_estimee']}€, 
    zone {client_needs['zone_navigation']}, urgence {client_needs['urgence']}.
    Agents : {agents_list}
    Sélectionne les 2-3 agents les plus pertinents.
    JSON : [{{"nom": "...", "raison": "..."}}]
    """

    result = call_phi(prompt, temperature=0.1, max_tokens=300)
    log_agent("Agent2_Selection", result, result["tokens_used"], result["response_time"])

    content = re.sub(r"```json|```", "", result["content"]).strip()
    agents = json.loads(content)
    
    print(f"✅ Agent 2 — {len(agents)} agents sélectionnés sur {len(AGENTS_MARITIMES)}")
    return agents

if __name__ == "__main__":
    test_needs = {
        "type_bateau": "voilier",
        "valeur_estimee": 80000,
        "zone_navigation": "Méditerranée-Atlantique",
        "urgence": "haute"
    }
    select_agents(test_needs)