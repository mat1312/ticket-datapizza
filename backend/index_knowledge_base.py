"""
Script to index knowledge base files into the vector store.
Run this once after setting up the project to populate the vector database.
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
    print("NORTH POLE KNOWLEDGE BASE INDEXER")
    print("=" * 50)
    
    print("\nInitializing RAG Engine...")
    engine = RAGEngine()
    
    print("\nIndexing knowledge base files...")
    engine.index_manuals("data/knowledge_base")
    
    print("\n" + "=" * 50)
    print("INDEXING COMPLETE!")
    print("=" * 50)
    
    # Test search
    print("\nTesting search functionality...")
    test_query = "sleigh engine overheating"
    results = engine.search_manuals(test_query)
    print(f"\nQuery: '{test_query}'")
    print(f"Results:\n{results[:500]}...")

if __name__ == "__main__":
    main()
