import json
from datetime import datetime

def log_agent(agent_name: str, result: dict, tokens: int, response_time: float):
    """
    Log structuré de chaque appel agent
    """
    log = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "tokens_used": tokens,
        "response_time_sec": response_time,
        "status": "success"
    }
    print(f"📊 LOG | {json.dumps(log)}")
    return log