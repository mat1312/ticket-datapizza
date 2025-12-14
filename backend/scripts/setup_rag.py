"""
Script to setup the RAG Vector Store.
Indexes both knowledge base manuals and past tickets.
"""
import os
import sys
import json
import uuid
import pathlib

# Add backend to path to allow importing rag_engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add root to path for loading .env correctly if needed (rag_engine handles it too)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

from dotenv import load_dotenv
load_dotenv()

from rag_engine import RAGEngine
from datapizza.type import Chunk, DenseEmbedding
from datapizza.embedders import ChunkEmbedder
from datapizza.modules.splitters import RecursiveSplitter
from datapizza.modules.parsers.text_parser import parse_text

def setup_rag():
    print("=" * 50)
    print("NORTH POLE RAG SETUP")
    print("=" * 50)
    
    print("\n🔧 Initializing RAG Engine...")
    engine = RAGEngine()
    
    # Initialize helpers for better ingestion
    chunk_embedder = ChunkEmbedder(client=engine.embedder)
    splitter = RecursiveSplitter(max_char=1000, overlap=100)
    
    # 1. INDEX KNOWLEDGE BASE
    print("\n📚 Indexing Knowledge Base...")
    kb_path = os.path.join(root_dir, "data", "knowledge_base")
    kb_dir = pathlib.Path(kb_path)
    
    if not kb_dir.exists():
        print(f"❌ Knowledge base path not found: {kb_path}")
    else:
        # Ensure collection
        engine._ensure_collection_exists(engine.kb_collection)
        all_kb_chunks = []
        
        for txt_file in kb_dir.glob("*.txt"):
            print(f"   📄 Processing: {txt_file.name}")
            content = txt_file.read_text(encoding="utf-8")
            
            # Use TextParser + RecursiveSplitter for robust chunking
            doc_node = parse_text(content, metadata={"source": txt_file.name})
            chunks = splitter.split(doc_node)
            
            # Convert to Datapizza Chunk objects
            for i, c in enumerate(chunks):
                # Ensure we have a string content
                text = c.text if hasattr(c, 'text') else str(c)
                chunk_obj = Chunk(
                    id=str(uuid.uuid4()),
                    text=text,
                    metadata={"source": txt_file.name, "chunk_index": i}
                )
                all_kb_chunks.append(chunk_obj)
        
        if all_kb_chunks:
            print(f"   🧠 Embedding {len(all_kb_chunks)} chunks (batch)...")
            # Batch embedding using ChunkEmbedder
            embedded_chunks = chunk_embedder.embed(all_kb_chunks)
            
            # Add to vectorstore (fix: manually map embeddings if needed or if add supports chunks with embeddings directly)
            # QdrantVectorstore.add expects chunks with embeddings
            engine.vectorstore.add(embedded_chunks, collection_name=engine.kb_collection)
            print(f"   ✅ Added {len(embedded_chunks)} manual chunks.")
        else:
            print("   ⚠️ No knowledge base content found.")

    # 2. INDEX PAST TICKETS
    print("\n🎫 Indexing Past Tickets...")
    tickets_path = os.path.join(root_dir, "data", "past_tickets.json")
    
    if not os.path.exists(tickets_path):
        print(f"❌ Tickets file not found: {tickets_path}")
    else:
        engine._ensure_collection_exists(engine.tickets_collection)
        
        try:
            with open(tickets_path, 'r', encoding='utf-8') as f:
                tickets_data = json.load(f)
            
            all_ticket_chunks = []
            
            for ticket in tickets_data:
                # Create rich representation
                text_content = (
                    f"TICKET ID: {ticket.get('id')}\n"
                    f"SUBJECT: {ticket.get('subject')}\n"
                    f"ISSUE: {ticket.get('message')}\n"
                    f"RESOLUTION: {ticket.get('response')}\n"
                    f"TAGS: {', '.join(ticket.get('tags', []))}"
                )
                
                chunk_obj = Chunk(
                    id=str(uuid.uuid4()),
                    text=text_content,
                    metadata={
                        "source": "past_tickets_json",
                        "ticket_id": ticket.get('id'),
                        "category": ticket.get('category')
                    }
                )
                all_ticket_chunks.append(chunk_obj)
            
            if all_ticket_chunks:
                print(f"   🧠 Embedding {len(all_ticket_chunks)} tickets (batch)...")
                embedded_ticket_chunks = chunk_embedder.embed(all_ticket_chunks)
                engine.vectorstore.add(embedded_ticket_chunks, collection_name=engine.tickets_collection)
                print(f"   ✅ Added {len(embedded_ticket_chunks)} tickets.")
            
        except Exception as e:
            print(f"❌ Error indexing tickets: {e}")

    print("\n✅ RAG Setup complete!")

    # Test Search
    print("\n🔎 Verification Search (Manuals): 'sleeve'")
    try:
        res = engine.search_manuals("sleeve")
        print(f"Result snippet: {res[:100]}...")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    setup_rag()
