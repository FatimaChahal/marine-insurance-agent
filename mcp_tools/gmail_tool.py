import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def send_email_via_mcp(to: str, subject: str, body: str) -> dict:
    """
    Envoie un mail via MCP Gmail connecté à Claude
    """
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": f"Send an email to {to} with subject '{subject}' and body: {body}"
                }],
                "mcp_servers": [{
                    "type": "url",
                    "url": "https://gmailmcp.googleapis.com/mcp/v1",
                    "name": "gmail-mcp"
                }]
            }
        )

        if response.status_code == 200:
            print(f"✅ MCP Gmail — Mail envoyé à {to}")
            return {"status": "sent", "to": to, "subject": subject}
        else:
            print(f"⚠️ MCP Gmail error : {response.status_code}")
            return {"status": "error", "detail": response.text}

    except Exception as e:
        print(f"⚠️ MCP Gmail exception : {e}")
        return {"status": "error", "detail": str(e)}


def save_report_to_drive(report: str, filename: str) -> dict:
    """
    Sauvegarde le rapport final dans Google Drive via MCP
    """
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": f"Create a Google Doc named '{filename}' with this content: {report[:500]}"
                }],
                "mcp_servers": [{
                    "type": "url",
                    "url": "https://drivemcp.googleapis.com/mcp/v1",
                    "name": "drive-mcp"
                }]
            }
        )

        if response.status_code == 200:
            print(f"✅ MCP Drive — Rapport sauvegardé : {filename}")
            return {"status": "saved", "filename": filename}
        else:
            print(f"⚠️ MCP Drive error : {response.status_code}")
            return {"status": "error", "detail": response.text}

    except Exception as e:
        print(f"⚠️ MCP Drive exception : {e}")
        return {"status": "error", "detail": str(e)}