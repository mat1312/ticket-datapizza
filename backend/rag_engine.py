"""
RAG Engine con Multi-Agent Pattern (Best Practices datapizza-ai)
"""
import os
import json
from typing import Optional, List
from datapizza.agents import Agent
from datapizza.tools import tool
from datapizza.tracing import ContextTracing
from datapizza.clients.openai import OpenAIClient
from datapizza.embedders.openai import OpenAIEmbedder
from datapizza.vectorstores.qdrant import QdrantVectorstore
from datapizza.core.vectorstore import VectorConfig
from datapizza.type import Chunk, DenseEmbedding
from datapizza.tools.SQLDatabase import SQLDatabase
from models import Ticket, OpsResponse, ToolCall

# ====== DATAPIZZA LOGGING BEST PRACTICES ======
os.environ.setdefault("DATAPIZZA_LOG_LEVEL", "INFO")
os.environ.setdefault("DATAPIZZA_AGENT_LOG_LEVEL", "DEBUG")  # Debug for agents
os.environ.setdefault("DATAPIZZA_TRACE_CLIENT_IO", "TRUE")  # Log client I/O


class RAGEngine:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ Warning: OPENAI_API_KEY not found.")
            api_key = "placeholder"

        # Initialize OpenAI Client (shared across agents)
        self.client = OpenAIClient(api_key=api_key, model="gpt-4.1-mini")
        
        # Tool calls tracker - reset per request
        self.tool_calls_log: List[ToolCall] = []
        
        # Event queue for streaming (set during streaming requests)
        self._event_queue = None
        
        # ====== 1. OFFICIAL SQL DATABASE TOOL (Best Practice) ======
        self.db_tool = SQLDatabase(db_uri="sqlite:///northpole.db")
        
        # ====== 2. QDRANT VECTOR STORE FOR RAG ======
        self.vectorstore = self._initialize_qdrant()
        self.embedder = OpenAIEmbedder(
            api_key=api_key,
            model_name="text-embedding-3-small"
        )
        self.kb_collection = "northpole_manuals"
        self.tickets_collection = "northpole_tickets"
        
        # Reference to self for closures
        engine_self = self

        # ====== HELPER: Push event to streaming queue ======
        def _push_event(event: dict):
            """Push event to streaming queue if available"""
            print(f"📤 [PUSH_EVENT] {event.get('type', 'unknown')} - {event.get('tool_name', 'N/A')}")
            if engine_self._event_queue is not None:
                engine_self._event_queue.put(event)
                print(f"   ✅ Event pushed to queue")
            else:
                print(f"   ⚠️ No event queue available!")

        # ====== 3. DEFINE TOOLS WITH TRACING ======
        @tool
        def search_knowledge_base(query: str) -> str:
            """Cerca nei manuali tecnici e nei protocolli degli elfi per procedure o riparazioni."""
            print(f"\n💡 [TOOL] search_knowledge_base: {query}")
            
            # Push START event
            _push_event({
                "type": "tool_start",
                "tool_name": "search_knowledge_base",
                "tool_input": query[:200]
            })
            
            try:
                result = engine_self.search_manuals(query)
                status = "error" if "Error" in result else "success"
            except Exception as e:
                result = f"Error executing tool: {str(e)}"
                status = "error"
            
            # Push COMPLETE event
            _push_event({
                "type": "tool_complete",
                "tool_name": "search_knowledge_base",
                "tool_input": query[:200],
                "tool_output": str(result)[:500],
                "status": status
            })
            
            engine_self.tool_calls_log.append(ToolCall(
                tool_name="search_knowledge_base",
                tool_input=query,
                tool_output=str(result)[:500],
                status=status
            ))
            print(f"   ➡️ Found: {len(str(result))} chars")
            return result

        @tool
        def search_past_tickets(query: str) -> str:
            """Cerca nei ticket passati per vedere come sono stati risolti problemi simili."""
            print(f"\n🔍 [TOOL] search_past_tickets: {query}")
            _push_event({"type": "tool_start", "tool_name": "search_past_tickets", "tool_input": query[:200]})
            
            try:
                result = engine_self.search_past_tickets(query)
                status = "error" if "Error" in result else "success"
            except Exception as e:
                result = f"Error executing tool: {str(e)}"
                status = "error"
            
            _push_event({"type": "tool_complete", "tool_name": "search_past_tickets", "tool_input": query[:200], "tool_output": str(result)[:500], "status": status})
            engine_self.tool_calls_log.append(ToolCall(tool_name="search_past_tickets", tool_input=query, tool_output=str(result)[:500], status=status))
            print(f"   ➡️ Found: {len(str(result))} chars")
            return result

        # ====== 4. CREATE SQL TOOL WRAPPERS WITH LOGGING ======
        
        @tool
        def list_tables() -> str:
            """Lista tutte le tabelle disponibili nel database."""
            print(f"\n🗄️ [SQL TOOL] list_tables")
            _push_event({"type": "tool_start", "tool_name": "list_tables", "tool_input": ""})
            
            try:
                result = engine_self.db_tool.list_tables()
                status = "success"
            except Exception as e:
                 result = f"Error: {str(e)}"
                 status = "error"
            
            _push_event({"type": "tool_complete", "tool_name": "list_tables", "tool_input": "", "tool_output": str(result)[:500], "status": status})
            engine_self.tool_calls_log.append(ToolCall(tool_name="list_tables", tool_input="", tool_output=str(result)[:500], status=status))
            print(f"   ➡️ Tables: {result}")
            return str(result)
        
        @tool
        def get_table_schema(table_name: str) -> str:
            """Ottieni lo schema di una tabella del database."""
            print(f"\n🗄️ [SQL TOOL] get_table_schema: {table_name}")
            _push_event({"type": "tool_start", "tool_name": "get_table_schema", "tool_input": table_name})
            
            try:
                result = engine_self.db_tool.get_table_schema(table_name)
                status = "success"
            except Exception as e:
                result = f"Error: {str(e)}"
                status = "error"
            
            _push_event({"type": "tool_complete", "tool_name": "get_table_schema", "tool_input": table_name, "tool_output": str(result)[:500], "status": status})
            engine_self.tool_calls_log.append(ToolCall(tool_name="get_table_schema", tool_input=table_name, tool_output=str(result)[:500], status=status))
            print(f"   ➡️ Schema: {str(result)[:200]}...")
            return str(result)
        
        @tool
        def run_sql_query(query: str) -> str:
            """Esegui una query SQL sul database (tabelle: children_log, inventory)."""
            print(f"\n🗄️ [SQL TOOL] run_sql_query: {query}")
            _push_event({"type": "tool_start", "tool_name": "run_sql_query", "tool_input": query[:200]})
            
            try:
                result = engine_self.db_tool.run_sql_query(query)
                status = "error" if "Error" in str(result) else "success"
            except Exception as e:
                result = f"Error: {str(e)}"
                status = "error"
            
            _push_event({"type": "tool_complete", "tool_name": "run_sql_query", "tool_input": query[:200], "tool_output": str(result)[:500], "status": status})
            engine_self.tool_calls_log.append(ToolCall(tool_name="run_sql_query", tool_input=query, tool_output=str(result)[:500], status=status))
            print(f"   ➡️ Result: {str(result)[:200]}...")
            return str(result)

        # ====== 5. CREATE SPECIALIZED AGENTS ======
        
        # SQL Expert Agent
        self.sql_agent = Agent(
            name="sql_expert",
            client=self.client,
            system_prompt="""Sei un esperto SQL del database del Polo Nord.

SCHEMA DATABASE:
- Tabella `children_log`: id, name, city, naughty_score, last_incident, gift_requested, status
- Tabella `inventory`: id, item_name, quantity, category

REGOLE:
- Usa `list_tables` per vedere le tabelle disponibili
- Usa `get_table_schema` prima di scrivere query complesse
- Usa `run_sql_query` per eseguire le query
- Gli ID sono INTEGER, non stringhe come 'CH-8847'
- DEVI SEMPRE eseguire almeno una query prima di rispondere
- Rispondi in modo conciso con i dati trovati""",
            tools=[list_tables, get_table_schema, run_sql_query],
            max_steps=10  # Limite anti-loop
        )

        # RAG/Manual Expert Agent
        self.rag_agent = Agent(
            name="history_expert",
            client=self.client,
            system_prompt="""Sei un esperto di memoria storica del Polo Nord.

Il tuo compito è consultare DUE fonti di informazione:
1. `search_knowledge_base`: manuali tecnici e procedure ufficiali
2. `search_past_tickets`: ticket passati risolti per trovare precedenti simili

Quando ricevi una domanda:
1. CONSULTA ENTRAMBE le fonti se necessario
2. Sintetizza le informazioni combinando teoria (manuali) e pratica (ticket passati)
3. Cita se la soluzione viene da un manuale o da un vecchio ticket ("Come visto nel ticket NP-XXX...")""",
            tools=[search_knowledge_base, search_past_tickets],
            max_steps=10  # Limite anti-loop
        )

        # ====== 5. MASTER AGENT WITH can_call ======
        schema_json = OpsResponse.model_json_schema()
        
        self.master_agent = Agent(
            name="UfficioReclamiAI",
            client=self.client,
            system_prompt=f"""Sei l'assistente AI dell'Ufficio Reclami Polo Nord.
Gestisci i ticket di supporto e generi risposte da inviare ai clienti.

REGOLA FONDAMENTALE - Per OGNI richiesta DEVI:
1. Chiamare `sql_expert` per ottenere dati dal database (bambini, inventario, statistiche)
2. Chiamare `history_expert` per consultare manuali e storico dei problemi
3. Sintetizzare le risposte in un unico report JSON.

SPECIFICHE CAMPI (LEGGI ATTENTAMENTE):
- thought_process: Il tuo ragionamento interno (NON visibile al cliente)
- sql_query_used: Le query SQL eseguite
- action_checklist: Lista di 2-3 azioni concrete da fare internamente (es. "Aggiornare inventario", "Notificare elfi")
- coal_alert: True se naughty_score > 50
- final_response: ⚠️ IMPORTANTISSIMO ⚠️ Questa è la RISPOSTA EMAIL DA INVIARE AL CLIENTE. 
  Deve essere cortese, professionale, e rispondere direttamente alla richiesta del ticket.
  Esempio: "Gentile [nome], grazie per averci contattato. [risposta al problema]... Cordiali saluti, Il Team del Polo Nord"
  NON deve essere un'analisi interna, ma la vera risposta da copiare/incollare e mandare al cliente!

⚠️ NON rispondere MAI senza aver consultato ENTRAMBI gli esperti.

LOGICA COAL ALERT:
- Se un bambino ha `naughty_score` > 50, imposta `coal_alert` a True

LA TUA RISPOSTA FINALE DEVE ESSERE UN OGGETTO JSON VALIDO:
{schema_json}

Rispondi SEMPRE in italiano.""",
            max_steps=15  # Limite più alto per master agent (chiama sub-agents)
        )
        
        # Enable Multi-Agent Communication
        self.master_agent.can_call(self.sql_agent)
        self.master_agent.can_call(self.rag_agent)

    def _initialize_qdrant(self):
        """Initialize Qdrant vector store (in-memory or remote)"""
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url:
            return QdrantVectorstore(location=":memory:")
        
        host = qdrant_url.replace("https://", "").replace("http://", "")
        if host.endswith("/"): 
            host = host[:-1]
        
        return QdrantVectorstore(
            host=host,
            port=None,
            api_key=qdrant_api_key
        )

    def _ensure_collection_exists(self, collection_name: str):
        """Create collection if it doesn't exist"""
        try:
            collections = self.vectorstore.get_collections()
            if collection_name not in collections:
                print(f"📦 Creating collection '{collection_name}'...")
                self.vectorstore.create_collection(
                    collection_name=collection_name,
                    vector_config=[VectorConfig(
                        name="text-embedding-3-small",
                        dimensions=1536
                    )]
                )
                return True
            return False
        except Exception as e:
            print(f"Error with collection: {e}")
            try:
                self.vectorstore.create_collection(
                    collection_name=collection_name,
                    vector_config=[VectorConfig(
                        name="text-embedding-3-small",
                        dimensions=1536
                    )]
                )
                return True
            except:
                return False

    def search_manuals(self, query: str, top_k: int = 3) -> str:
        """Search vector db for relevant manual content"""
        try:
            query_vector = self.embedder.embed(query)
            results = self.vectorstore.search(
                collection_name=self.kb_collection,
                query_vector=query_vector,
                k=top_k
            )
            if not results:
                return "Nessuna informazione rilevante trovata nei manuali."
            return "\n---\n".join([
                f"[{r.metadata.get('source', 'unknown')}]: {r.text}" 
                for r in results
            ])
        except Exception as e:
            return f"Errore nella ricerca: {str(e)}"

    def search_past_tickets(self, query: str, top_k: int = 3) -> str:
        """Search vector db for relevant past tickets"""
        try:
            query_vector = self.embedder.embed(query)
            results = self.vectorstore.search(
                collection_name=self.tickets_collection,
                query_vector=query_vector,
                k=top_k
            )
            if not results:
                return "Nessun ticket passato simile trovato."
            
            # Format results nicely
            formatted_results = []
            for r in results:
                score = r.score if hasattr(r, 'score') else 0.0
                formatted_results.append(
                    f"[Ticket Simile - Score {score:.2f}]:\n{r.text}"
                )
                
            return "\n---\n".join(formatted_results)
        except Exception as e:
            return f"Errore nella ricerca ticket: {str(e)}"

    def generate_response(self, ticket: Ticket, image_base64: Optional[str] = None, regeneration_feedback: Optional[str] = None) -> OpsResponse:
        """Generate response using Multi-Agent Pattern with tracing"""
        # Reset tool calls log
        self.tool_calls_log = []
        
        # Construct input
        task_input = f"""TICKET DA GESTIRE:
Oggetto: {ticket.subject}
Messaggio: {ticket.message}

ISTRUZIONI:
1. CHIAMA sql_expert per cercare dati rilevanti nel database
2. CHIAMA history_expert per consultare manuali E ticket passati
3. Sintetizza tutto in una risposta JSON"""

        if image_base64:
            task_input += "\n\n[Immagine allegata - analizzala per valutazione danni]"
        
        # Aggiungi feedback per rigenerazione se presente
        if regeneration_feedback:
            task_input += f"""

⚠️ FEEDBACK UTENTE PER RIGENERAZIONE:
{regeneration_feedback}

IMPORTANTE: Rigenera la risposta tenendo conto di questo feedback specifico.
Mantieni le stesse fonti di dati ma modifica il tono, lo stile o il contenuto come richiesto."""

        # Run with ContextTracing (Best Practice)
        with ContextTracing().trace("ufficio_reclami_multi_agent"):
            try:
                print("\n" + "="*60)
                print("🏢 UFFICIO RECLAMI AI - Multi-Agent Request")
                print("="*60)
                
                # Run master agent (will call sub-agents via can_call)
                result = self.master_agent.run(task_input)
                
                response_text = result.text if hasattr(result, 'text') else str(result)
                
                # Clean markdown code blocks
                response_text = response_text.replace("```json", "").replace("```", "").strip()
                
                # Parse JSON response
                # Use Structured Response for robust parsing
                try:
                    parsing_instruction = f"""
                    You are a JSON parser. 
                    Extract the operational response from the following text and format it strictly according to the schema.
                    Ignore any conversational filler before or after the JSON.
                    
                    IMPORTANT: You MUST populate 'action_checklist' with specific actionable steps inferred from the text if they are not explicitly listed.
                    
                    TEXT TO PARSE:
                    {response_text}
                    """
                    
                    structured_result = self.client.structured_response(
                        input=parsing_instruction,
                        output_cls=OpsResponse
                    )
                    
                    # Get the parsed object
                    ops_data = structured_result.structured_data[0]
                    
                    # Inject tracked tool calls
                    ops_data.tool_calls = self.tool_calls_log
                    
                    return ops_data

                except Exception as parse_error:
                    print(f"⚠️ Structured Response Failed: {parse_error}")
                    # Fallback to regex if even structured response failed (unlikely but safe)
                    import re
                    json_str = response_text
                    match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                    else:
                        match = re.search(r'\{.*\}', response_text, re.DOTALL) 
                        if match:
                            json_str = match.group(0)
                    
                    data = json.loads(json_str)
                    data['tool_calls'] = [tc.model_dump() for tc in self.tool_calls_log]
                    return OpsResponse(**data)
                    
            except Exception as e:
                print(f"❌ Multi-Agent Error: {e}")
                return OpsResponse(
                    thought_process=f"Error: {str(e)}",
                    sql_query_used="N/A",
                    action_checklist=["Contact Admin"],
                    coal_alert=False,
                    final_response="Errore di sistema. Controllare i log.",
                    tool_calls=self.tool_calls_log
                )

    def _build_task_input(self, ticket: Ticket, image_base64: Optional[str] = None, regeneration_feedback: Optional[str] = None) -> str:
        """Build the task input string for the agent"""
        task_input = f"""TICKET DA GESTIRE:
Oggetto: {ticket.subject}
Messaggio: {ticket.message}

ISTRUZIONI:
1. CHIAMA sql_expert per cercare dati rilevanti nel database
2. CHIAMA history_expert per consultare manuali E ticket passati
3. Sintetizza tutto in una risposta JSON"""

        if image_base64:
            task_input += "\n\n[Immagine allegata - analizzala per valutazione danni]"
        
        if regeneration_feedback:
            task_input += f"""

⚠️ FEEDBACK UTENTE PER RIGENERAZIONE:
{regeneration_feedback}

IMPORTANTE: Rigenera la risposta tenendo conto di questo feedback specifico.
Mantieni le stesse fonti di dati ma modifica il tono, lo stile o il contenuto come richiesto."""
        
        return task_input

    async def generate_response_stream(self, ticket: Ticket, image_base64: Optional[str] = None, regeneration_feedback: Optional[str] = None):
        """
        Async generator that yields SSE events as tools execute.
        Uses a queue-based approach with threading for true real-time streaming.
        """
        import asyncio
        import threading
        from queue import Queue
        import time
        
        # Reset tool calls log
        self.tool_calls_log = []
        
        # Queue for streaming events
        event_queue = Queue()
        self._event_queue = event_queue  # Enable tool wrappers to push directly
        
        # Build task input
        task_input = self._build_task_input(ticket, image_base64, regeneration_feedback)
        
        print("\n" + "="*60)
        print("🏢 UFFICIO RECLAMI AI - Streaming Request")
        print("="*60)
        
        def run_agent():
            """Run agent in background thread, push events to queue"""
            try:
                # Use stream_invoke for step-by-step execution
                step_index = 0
                accumulated_text = ""
                
                for step in self.master_agent.stream_invoke(task_input):
                    step_index += 1
                    print(f"\n📍 Step {step_index}")
                    
                    # Push step info event
                    event_queue.put({
                        "type": "step",
                        "step": step_index,
                        "message": f"Step {step_index} in corso..."
                    })
                    
                    # NOTE: tool_start and tool_complete events are pushed directly 
                    # by the tool wrapper functions via _push_event(), so we don't 
                    # need to push them here again.
                    
                    # Check for text content (thoughts)
                    if hasattr(step, 'text') and step.text:
                        accumulated_text = step.text
                        event_queue.put({
                            "type": "thought",
                            "content": step.text[:300],
                            "step": step_index
                        })
                
                # Parse final response
                response_text = accumulated_text.replace("```json", "").replace("```", "").strip()
                
                try:
                    # Use Structured Response for robust parsing of the accumulated stream
                    parsing_instruction = f"""
                    You are a JSON parser. 
                    Extract the operational response from the following text and format it strictly according to the schema.
                    Ignore any conversational filler before or after the JSON.
                    
                    IMPORTANT: You MUST populate 'action_checklist' with specific actionable steps inferred from the text if they are not explicitly listed.
                    
                    TEXT TO PARSE:
                    {response_text}
                    """
                    
                    structured_result = self.client.structured_response(
                        input=parsing_instruction,
                        output_cls=OpsResponse
                    )
                    
                    ops_data = structured_result.structured_data[0]
                    
                    event_queue.put({
                        "type": "complete",
                        "response": {
                            "suggested_response": ops_data.final_response,
                            "thought_process": ops_data.thought_process,
                            "sql_query_used": ops_data.sql_query_used,
                            "action_checklist": ops_data.action_checklist,
                            "coal_alert": ops_data.coal_alert
                        }
                    })

                except Exception as parse_error:
                    print(f"⚠️ Structured Response Failed (Stream): {parse_error}")
                    # Fallback to regex
                    import re
                    json_str = response_text
                    
                    match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                    else:
                        match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if match:
                            json_str = match.group(0)
                    
                    data = json.loads(json_str) 
                    event_queue.put({
                        "type": "complete",
                        "response": {
                            "suggested_response": data.get("final_response", response_text),
                            "thought_process": data.get("thought_process", ""),
                            "sql_query_used": data.get("sql_query_used", "N/A"),
                            "action_checklist": data.get("action_checklist", []),
                            "coal_alert": data.get("coal_alert", False)
                        }
                    })
                except Exception as parse_error:
                    print(f"⚠️ JSON Parse Error: {parse_error}")
                    event_queue.put({
                        "type": "complete",
                        "response": {
                            "suggested_response": response_text or "Errore nel parsing",
                            "thought_process": "Parsing failed",
                            "sql_query_used": "N/A",
                            "action_checklist": ["Review logs"],
                            "coal_alert": False
                        }
                    })
                    
            except Exception as e:
                print(f"❌ Agent Error: {e}")
                event_queue.put({"type": "error", "message": str(e)})
            finally:
                event_queue.put(None)  # Signal completion
        
        # Yield initial connection event
        yield {"type": "connected", "message": "Connessione al Polo Nord stabilita"}
        
        # Start agent in background thread
        agent_thread = threading.Thread(target=run_agent, daemon=True)
        agent_thread.start()
        
        # Stream events from queue
        loop = asyncio.get_event_loop()
        while True:
            # Non-blocking queue get using run_in_executor
            event = await loop.run_in_executor(None, lambda: event_queue.get(timeout=60))
            
            if event is None:  # Completion signal
                break
                
            yield event
            await asyncio.sleep(0.05)  # Small delay for smoother streaming
        
        # Cleanup
        self._event_queue = None

    def index_manuals(self, knowledge_base_path: str = "data/knowledge_base"):
        """Index all .txt files from knowledge_base folder into vector store"""
        import uuid
        import pathlib
        
        kb_path = pathlib.Path(knowledge_base_path)
        if not kb_path.exists():
            print(f"❌ Knowledge base path not found: {kb_path}")
            return
        
        # Ensure collection exists
        self._ensure_collection_exists(self.kb_collection)
        
        chunks_to_add = []
        
        for txt_file in kb_path.glob("*.txt"):
            print(f"📄 Processing: {txt_file.name}")
            content = txt_file.read_text(encoding="utf-8")
            
            # Chunk by paragraphs
            sections = content.split("\n\n")
            
            for i, section in enumerate(sections):
                section = section.strip()
                if len(section) < 20:
                    continue
                
                try:
                    embedding = self.embedder.embed(section)
                    chunk = Chunk(
                        id=str(uuid.uuid4()),
                        text=section,
                        metadata={
                            "source": txt_file.name,
                            "section_index": i
                        },
                        embeddings=[DenseEmbedding(
                            name="text-embedding-3-small",
                            vector=embedding
                        )]
                    )
                    chunks_to_add.append(chunk)
                except Exception as e:
                    print(f"Error embedding: {e}")
        
        if chunks_to_add:
            print(f"📥 Adding {len(chunks_to_add)} chunks to vector store...")
            self.vectorstore.add(chunks_to_add, collection_name=self.kb_collection)
            print("✅ Indexing complete!")
        else:
            print("No chunks to add.")

    def index_tickets(self, tickets_path: str = "data/past_tickets.json"):
        """Index past tickets into vector store"""
        import uuid
        import pathlib
        
        tickets_file = pathlib.Path(tickets_path)
        if not tickets_file.exists():
            print(f"❌ Tickets file not found: {tickets_file}")
            return

        # Ensure collection
        self._ensure_collection_exists(self.tickets_collection)

        try:
            tickets_data = json.loads(tickets_file.read_text(encoding="utf-8"))
            chunks_to_add = []

            for ticket in tickets_data:
                # Create a rich representation for embedding
                text_content = (
                    f"TICKET ID: {ticket.get('id')}\n"
                    f"SUBJECT: {ticket.get('subject')}\n"
                    f"ISSUE: {ticket.get('message')}\n"
                    f"RESOLUTION: {ticket.get('response')}\n"
                    f"TAGS: {', '.join(ticket.get('tags', []))}"
                )
                
                print(f"🎫 Processing Ticket: {ticket.get('id')}")
                
                embedding = self.embedder.embed(text_content)
                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    text=text_content,
                    metadata={
                        "source": "past_tickets_json",
                        "ticket_id": ticket.get('id'),
                        "category": ticket.get('category')
                    },
                    embeddings=[DenseEmbedding(
                        name="text-embedding-3-small",
                        vector=embedding
                    )]
                )
                chunks_to_add.append(chunk)

            if chunks_to_add:
                print(f"📥 Adding {len(chunks_to_add)} tickets to '{self.tickets_collection}'...")
                self.vectorstore.add(chunks_to_add, collection_name=self.tickets_collection)
                print("✅ Ticket Indexing complete!")

        except Exception as e:
            print(f"Error indexing tickets: {e}")