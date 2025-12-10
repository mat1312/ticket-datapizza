
import sys
import os
import pathlib
import json

# Add backend to sys.path
backend_path = pathlib.Path(__file__).parent
sys.path.append(str(backend_path))

from rag_engine import RAGEngine
from models import Ticket
from dotenv import load_dotenv

load_dotenv()
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

def verify():
    print("🚀 Initializing RAGEngine...")
    try:
        engine = RAGEngine()
    except Exception as e:
        print(f"❌ Init failed: {e}")
        return

    # Mock Ticket - Use the one from the screenshot/complaint (Naughty List)
    # The user was looking at a ticket about "Tommy" with naughty score 73
    ticket = Ticket(
        id="NP-TEST",
        category="Customer Service",
        priority="critical",
        subject="Reclamo Carbone",
        message="Mia madre è furiosa perché Tommy (CH-8847) ha ricevuto carbone. Il score è 73. Come gestisco?",
        created_at=None
    )

    print("🤖 Generating Response...")
    try:
        response = engine.generate_response(ticket)
        print("\n✅ Response Parsing Complete!")
        
        print(f"Coal Alert: {response.coal_alert}")
        print(f"Action Checklist ({len(response.action_checklist)} items):")
        for item in response.action_checklist:
            print(f"  - {item}")
            
        print("-" * 40)
        print("Final Response:")
        print(response.final_response)
        print("-" * 40)
        print(f"Tool Calls: {len(response.tool_calls)}")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
