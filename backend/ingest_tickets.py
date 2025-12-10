"""
Script to ingest past tickets into Qdrant vector store.
Run this to populate the 'northpole_tickets' collection.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from rag_engine import RAGEngine

def main():
    print("=" * 50)
    print("NORTH POLE PAST TICKETS INGESTER")
    print("=" * 50)
    
    print("\nInitializing RAG Engine...")
    engine = RAGEngine()
    
    print("\nIndexing past tickets...")
    engine.index_tickets("data/past_tickets.json")
    
    print("\n" + "=" * 50)
    print("TICKET INDEXING COMPLETE!")
    print("=" * 50)
    
    # Test search
    print("\nTesting search functionality...")
    test_query = "sleigh overheating problem"
    results = engine.search_past_tickets(test_query)
    print(f"\nQuery: '{test_query}'")
    print(f"Results:\n{results[:500]}...")

if __name__ == "__main__":
    main()
