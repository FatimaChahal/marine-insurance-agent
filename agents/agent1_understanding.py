import json
import re
from utils.azure_client import call_phi
from utils.logger import log_agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def understand_client_email(email_content: str) -> dict:
    """
    Agent 1 : Comprend le mail du client et extrait les besoins
    """
    prompt = f"""
    Tu es un expert en assurance maritime.
    Analyse ce mail et extrait les informations en JSON :
    - type_bateau : type de bateau
    - valeur_estimee : valeur en euros (nombre uniquement)
    - zone_navigation : zone de navigation
    - duree_souhaitee : durée souhaitée
    - besoins_specifiques : besoins particuliers
    - urgence : haute/moyenne/basse
    
    Mail : {email_content}
    
    Réponds UNIQUEMENT en JSON valide, sans explication.
    """

    result = call_phi(prompt, temperature=0.1, max_tokens=300)
    
    log_agent(
        agent_name="Agent1_Understanding",
        result=result,
        tokens=result["tokens_used"],
        response_time=result["response_time"]
    )

    content = result["content"]
    content = re.sub(r"```json|```", "", content).strip()
    needs = json.loads(content)
    
    print(f"✅ Agent 1 — Besoins extraits : {json.dumps(needs, ensure_ascii=False, indent=2)}")
    return needs

if __name__ == "__main__":
    test_email = """
    Bonjour,
    Je souhaite assurer mon voilier de 12 mètres (valeur 80 000€) 
    pour une traversée Méditerranée-Atlantique prévue en septembre.
    J'ai besoin d'une couverture tous risques incluant assistance 24h/24.
    Pouvez-vous me faire des propositions rapidement ?
    Merci, Jean Dupont
    """
    understand_client_email(test_email)