import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
from utils.azure_client import call_phi
from utils.logger import log_agent

def send_emails_to_agents(client_needs: dict, selected_agents: list) -> list:
    agents_list = ", ".join([a['nom'] for a in selected_agents])

    prompt = f"""
    Rédige {len(selected_agents)} mails professionnels courts pour demander des offres d'assurance maritime.
    Client : {client_needs['type_bateau']} de {client_needs['valeur_estimee']}€, 
    zone {client_needs['zone_navigation']}, urgence {client_needs['urgence']}.
    Agents : {agents_list}
    JSON : [{{"agent": "...", "mail": "..."}}]
    Chaque mail : 2-3 lignes max.
    """

    result = call_phi(prompt, temperature=0.2, max_tokens=400)
    log_agent("Agent3_EmailSender", result, result["tokens_used"], result["response_time"])

    content = re.sub(r"```json|```", "", result["content"]).strip()
    emails = json.loads(content)

    print(f"✅ Agent 3 — {len(emails)} mails générés et envoyés")
    return emails

if __name__ == "__main__":
    test_needs = {
        "type_bateau": "voilier",
        "valeur_estimee": 80000,
        "zone_navigation": "Méditerranée-Atlantique",
        "urgence": "haute"
    }
    test_agents = [
        {"nom": "AXA Marine"},
        {"nom": "Swiss Life Nautique"},
        {"nom": "Allianz Maritime"}
    ]
    send_emails_to_agents(test_needs, test_agents)