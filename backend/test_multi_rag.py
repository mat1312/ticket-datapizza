"""
Test script for Multi-Collection RAG.
Verifies that the agent calls BOTH tools: search_knowledge_base and search_past_tickets.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from models import Ticket
from rag_engine import RAGEngine

def main():
    print("=" * 60)
    print("VERIFICATION: MULTI-COLLECTION RAG")
    print("=" * 60)
    
    engine = RAGEngine()
    
    # Create a ticket that references a past issue
    test_ticket = Ticket(
        id="TEST-MULTI-001",
        subject="Engine overheating again",
        message="The plasma injectors are acting up like they did in past tickets. What was the fix? Also check the manual.",
        priority="high",
        category="Sleigh Maintenance"
    )
    
    print(f"\n📨 Test Ticket:\nSubject: {test_ticket.subject}\nMessage: {test_ticket.message}\n")
    
    print("🤖 Generazione Risposta...")
    response = engine.generate_response(test_ticket)
    
    print("\n" + "=" * 60)
    print("📊 RESULT ANALYSIS")
    print("=" * 60)
    
    # Check tool calls
    tools_used = [tc.tool_name for tc in response.tool_calls]
    print(f"\n🛠️ Tools Used: {tools_used}")
    
    has_manual_search = 'search_knowledge_base' in tools_used
    has_ticket_search = 'search_past_tickets' in tools_used
    
    print(f"✅ Manual Search: {'YES' if has_manual_search else 'NO'}")
    print(f"✅ Past Ticket Search: {'YES' if has_ticket_search else 'NO'}")
    
    print("\n📝 Final Response:")
    print(response.final_response)
    
    if has_manual_search and has_ticket_search:
        print("\n🎉 SUCCESS: Both tools were called!")
    else:
        print("\n⚠️ PARTIAL: Not all tools were called.")

if __name__ == "__main__":
    main()
