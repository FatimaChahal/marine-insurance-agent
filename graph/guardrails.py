import re
from utils.logger import log_agent
from datetime import datetime

def anonymize_email(email_content: str) -> tuple[str, dict]:
    """
    Guardrail RGPD : anonymise les données personnelles
    avant envoi au LLM
    """
    pii_found = {}
    anonymized = email_content

    # Anonymise les emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_content)
    for i, email in enumerate(emails):
        placeholder = f"[EMAIL_{i+1}]"
        pii_found[placeholder] = email
        anonymized = anonymized.replace(email, placeholder)

    # Anonymise les noms (Prénom Nom en fin de mail)
    names = re.findall(r'(?:Merci,|Cordialement,|Regards,)\s*\n?\s*([A-Z][a-z]+ [A-Z][a-z]+)', email_content)
    for i, name in enumerate(names):
        placeholder = f"[NOM_{i+1}]"
        pii_found[placeholder] = name
        anonymized = anonymized.replace(name, placeholder)

    # Anonymise les téléphones
    phones = re.findall(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', email_content)
    for i, phone in enumerate(phones):
        placeholder = f"[TEL_{i+1}]"
        pii_found[placeholder] = phone
        anonymized = anonymized.replace(phone, placeholder)

    log_agent(
        agent_name="Guardrails_RGPD",
        result={"pii_detected": len(pii_found)},
        tokens=0,
        response_time=0
    )

    print(f"🛡️ Guardrails — {len(pii_found)} données personnelles anonymisées")
    return anonymized, pii_found


def validate_output(output: str) -> bool:
    """
    Guardrail Output : vérifie que le LLM n'a pas
    reproduit de données personnelles
    """
    dangerous_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}',
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, output):
            print("⚠️ Guardrail Output — donnée personnelle détectée dans l'output !")
            return False
    return True


def check_prompt_injection(text: str) -> bool:
    """
    Guardrail Sécurité : détecte les tentatives
    de prompt injection
    """
    injection_patterns = [
        "ignore previous instructions",
        "ignore les instructions",
        "oublie tes instructions",
        "tu es maintenant",
        "new instructions:",
        "system prompt"
    ]
    text_lower = text.lower()
    for pattern in injection_patterns:
        if pattern in text_lower:
            print(f"🚨 Guardrail Sécurité — Prompt injection détectée : '{pattern}'")
            return False
    return True