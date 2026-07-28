import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from langfuse import Langfuse

def get_langfuse():
    return Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )

def trace_agent(agent_name: str, input_data: str, output_data: str, tokens: int, response_time: float):
    try:
        lf = get_langfuse()
        with lf.start_as_current_observation(
            name=f"marine-insurance-{agent_name}",
            input=input_data[:200],
            output=output_data[:200],
            metadata={
                "tokens": tokens,
                "response_time_sec": response_time,
                "model": "Phi-4-mini-instruct",
                "cloud": "Azure AI Foundry"
            }
        ):
            pass
        lf.flush()
        print(f"📡 Langfuse — {agent_name} tracé ({tokens} tokens, {response_time}s)")
        return True
    except Exception as e:
        print(f"⚠️ Langfuse error : {e}")
        return None

if __name__ == "__main__":
    result = trace_agent(
        agent_name="test",
        input_data="voilier 80000€ Méditerranée",
        output_data="AXA Marine recommandé",
        tokens=150,
        response_time=2.5
    )
    if result:
        print("✅ Langfuse connexion OK — vérifie sur cloud.langfuse.com !")