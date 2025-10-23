import os
import json
import uuid
from typing import List, Dict, Any
from datapizza.clients.openai import OpenAIClient
from datapizza.vectorstores.qdrant import QdrantVectorstore
from datapizza.embedders.openai import OpenAIEmbedder
from datapizza.core.vectorstore import VectorConfig
from datapizza.type import Chunk, DenseEmbedding
from models import Ticket, Source, PastTicket

class RAGEngine:
    def __init__(self):
        # Initialize Qdrant Cloud connection
        self.vectorstore = self._initialize_qdrant()

        # Initialize OpenAI embedder
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. Using placeholder for demo.")
            api_key = "placeholder-key"

        self.embedder = OpenAIEmbedder(
            api_key=api_key,
            model_name="text-embedding-3-small"
        )

        # Initialize DataPizza AI client for generation
        self.ai_client = OpenAIClient(
            api_key=api_key,
            model="gpt-4o-mini",
            system_prompt="You are a helpful assistant that generates professional responses to customer support tickets based on company documentation and past successful resolutions."
        )

        # Collections
        self.kb_collection = "knowledge_base"
        self.tickets_collection = "past_tickets"

        # Load and index data
        self.load_and_index_data()

    def _initialize_qdrant(self) -> QdrantVectorstore:
        """Initialize connection to Qdrant Cloud"""
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if not qdrant_url:
            print("Warning: QDRANT_URL not found. Using in-memory storage for demo.")
            return QdrantVectorstore(location=":memory:")

        # Extract host from URL (remove https:// and port)
        host = qdrant_url.replace("https://", "").replace("http://", "")
        if host.endswith("/"):
            host = host[:-1]

        print(f"Connecting to Qdrant Cloud at {host}")
        return QdrantVectorstore(
            host=host,
            port=None,  # Use default HTTPS port for cloud
            api_key=qdrant_api_key
        )

    def load_and_index_data(self):
        """Load and index knowledge base and past tickets in Qdrant"""
        print("Loading and indexing data...")

        # Create collections if they don't exist
        self._create_collections()

        # Load and index knowledge base
        self._load_and_index_knowledge_base()

        # Load and index past tickets
        self._load_and_index_past_tickets()

        print("Data loading and indexing completed!")

    def _create_collections(self):
        """Create Qdrant collections for knowledge base and past tickets"""
        vector_config = [VectorConfig(name="embedding", dimensions=1536)]

        try:
            # Create knowledge base collection
            self.vectorstore.create_collection(
                collection_name=self.kb_collection,
                vector_config=vector_config
            )
            print(f"Created collection: {self.kb_collection}")
        except Exception as e:
            print(f"Collection {self.kb_collection} might already exist: {e}")

        try:
            # Create past tickets collection
            self.vectorstore.create_collection(
                collection_name=self.tickets_collection,
                vector_config=vector_config
            )
            print(f"Created collection: {self.tickets_collection}")
        except Exception as e:
            print(f"Collection {self.tickets_collection} might already exist: {e}")

    def _load_and_index_knowledge_base(self):
        """Load knowledge base files and index them in Qdrant"""
        kb_path = "data/knowledge_base"
        chunks = []

        for filename in os.listdir(kb_path):
            if filename.endswith('.txt'):
                with open(os.path.join(kb_path, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    sections = self._split_into_sections(content, filename)

                    for section in sections:
                        # Generate embedding using DataPizza AI
                        try:
                            if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "placeholder-key":
                                embedding_vector = self.embedder.embed(section['content'], model_name="text-embedding-3-small")
                            else:
                                # Fallback: create dummy embedding for demo
                                embedding_vector = [0.0] * 1536

                            chunk = Chunk(
                                id=str(uuid.uuid4()),
                                text=section['content'],
                                metadata={
                                    "title": section['title'],
                                    "source_file": section['source_file'],
                                    "type": "knowledge_base"
                                },
                                embeddings=[DenseEmbedding(name="embedding", vector=embedding_vector)]
                            )
                            chunks.append(chunk)
                        except Exception as e:
                            print(f"Error generating embedding for section {section['id']}: {e}")

        # Add chunks to Qdrant
        if chunks:
            try:
                self.vectorstore.add(chunks, collection_name=self.kb_collection)
                print(f"Indexed {len(chunks)} knowledge base sections")
            except Exception as e:
                print(f"Error adding chunks to knowledge base collection: {e}")

    def _load_and_index_past_tickets(self):
        """Load past tickets and index them in Qdrant"""
        chunks = []

        with open("data/past_tickets.json", 'r', encoding='utf-8') as f:
            tickets_data = json.load(f)

            for ticket_data in tickets_data:
                # Combine subject, message, and response for embedding
                combined_text = f"{ticket_data['subject']} {ticket_data['message']} {ticket_data['response']}"

                try:
                    if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "placeholder-key":
                        embedding_vector = self.embedder.embed(combined_text, model_name="text-embedding-3-small")
                    else:
                        # Fallback: create dummy embedding for demo
                        embedding_vector = [0.0] * 1536

                    chunk = Chunk(
                        id=str(uuid.uuid4()),
                        text=ticket_data['response'],  # Store the response as main text
                        metadata={
                            "ticket_id": ticket_data['id'],
                            "category": ticket_data['category'],
                            "subject": ticket_data['subject'],
                            "message": ticket_data['message'],
                            "type": "past_ticket",
                            "tags": ticket_data['tags']
                        },
                        embeddings=[DenseEmbedding(name="embedding", vector=embedding_vector)]
                    )
                    chunks.append(chunk)
                except Exception as e:
                    print(f"Error generating embedding for ticket {ticket_data['id']}: {e}")

        # Add chunks to Qdrant
        if chunks:
            try:
                self.vectorstore.add(chunks, collection_name=self.tickets_collection)
                print(f"Indexed {len(chunks)} past tickets")
            except Exception as e:
                print(f"Error adding chunks to past tickets collection: {e}")

    def _split_into_sections(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Split knowledge base content into smaller, searchable sections"""
        sections = []
        lines = content.split('\n')
        current_section = ""
        current_title = filename.replace('.txt', '').replace('_', ' ').title()

        for line in lines:
            if line.startswith('===') and current_section.strip():
                # Save previous section
                sections.append({
                    'id': f"{filename}_{len(sections)}",
                    'title': current_title,
                    'content': current_section.strip(),
                    'type': 'knowledge_base',
                    'source_file': filename
                })
                current_section = ""
                continue
            elif line.startswith('==='):
                current_title = line.replace('=', '').strip()
                continue

            current_section += line + '\n'

        # Add the last section
        if current_section.strip():
            sections.append({
                'id': f"{filename}_{len(sections)}",
                'title': current_title,
                'content': current_section.strip(),
                'type': 'knowledge_base',
                'source_file': filename
            })

        return sections

    def search_relevant_documents(self, query: str, top_k: int = 5) -> List[Source]:
        """Search for relevant documents using Qdrant semantic similarity"""
        sources = []

        try:
            # Generate query embedding
            if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "placeholder-key":
                query_vector = self.embedder.embed(query, model_name="text-embedding-3-small")
            else:
                # Fallback for demo
                query_vector = [0.0] * 1536

            # Search knowledge base
            try:
                kb_results = self.vectorstore.search(
                    collection_name=self.kb_collection,
                    query_vector=query_vector,
                    k=min(top_k, 3)
                )

                for chunk in kb_results:
                    if hasattr(chunk, 'metadata') and chunk.metadata:
                        sources.append(Source(
                            id=chunk.id,
                            title=chunk.metadata.get('title', 'Knowledge Base'),
                            snippet=self._extract_snippet(chunk.text, query),
                            relevance=0.8,  # Qdrant doesn't return scores in current version
                            type='knowledge_base'
                        ))
            except Exception as e:
                print(f"Error searching knowledge base: {e}")

            # Search past tickets
            try:
                ticket_results = self.vectorstore.search(
                    collection_name=self.tickets_collection,
                    query_vector=query_vector,
                    k=min(top_k, 2)
                )

                for chunk in ticket_results:
                    if hasattr(chunk, 'metadata') and chunk.metadata:
                        sources.append(Source(
                            id=chunk.metadata.get('ticket_id', chunk.id),
                            title=f"Past Ticket: {chunk.metadata.get('subject', 'Unknown')}",
                            snippet=self._extract_snippet(chunk.text, query),
                            relevance=0.7,  # Slightly lower than knowledge base
                            type='past_ticket'
                        ))
            except Exception as e:
                print(f"Error searching past tickets: {e}")

        except Exception as e:
            print(f"Error in search: {e}")
            return []

        # Sort by relevance and return top_k
        sources.sort(key=lambda x: x.relevance, reverse=True)
        return sources[:top_k]

    def _extract_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Extract a relevant snippet from the text"""
        text = text.strip()
        if len(text) <= max_length:
            return text

        # Try to find the most relevant part
        query_words = query.lower().split()
        text_lower = text.lower()

        # Find the best position to start the snippet
        best_pos = 0
        best_score = 0

        for i in range(0, len(text) - max_length, 50):
            snippet = text[i:i + max_length].lower()
            score = sum(1 for word in query_words if word in snippet)
            if score > best_score:
                best_score = score
                best_pos = i

        snippet = text[best_pos:best_pos + max_length]

        # Try to end at a sentence boundary
        last_period = snippet.rfind('.')
        if last_period > max_length * 0.7:
            snippet = snippet[:last_period + 1]
        else:
            snippet += "..."

        return snippet.strip()

    def generate_response(self, ticket: Ticket, tone: str = "professional") -> Dict[str, Any]:
        """Generate a response for the ticket using RAG"""
        try:
            # Create search query from ticket
            query = f"{ticket.subject} {ticket.message}"

            # Find relevant sources
            sources = self.search_relevant_documents(query, top_k=5)

            # Build context from sources
            context = self._build_context(sources)

            # Create prompt for AI
            prompt = self._create_prompt(ticket, context, tone)

            # Generate response using DataPizza AI
            if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "placeholder-key":
                try:
                    ai_response = self.ai_client.invoke(prompt)
                    response_text = ai_response.text if hasattr(ai_response, 'text') else str(ai_response)
                except Exception as e:
                    print(f"AI generation error: {e}")
                    response_text = self._generate_fallback_response(ticket, sources)
            else:
                response_text = self._generate_fallback_response(ticket, sources)

            # Calculate confidence score
            confidence = self._calculate_confidence(sources)

            # Generate reasoning
            reasoning = self._generate_reasoning(ticket, sources)

            return {
                "suggested_response": response_text,
                "confidence_score": confidence,
                "sources": sources,
                "reasoning": reasoning
            }

        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "suggested_response": "Mi dispiace, c'è stato un errore nella generazione della risposta. Vi ricontatteremo al più presto.",
                "confidence_score": 0.1,
                "sources": [],
                "reasoning": "Error in AI processing"
            }

    def _build_context(self, sources: List[Source]) -> str:
        """Build context string from sources"""
        context_parts = []
        for source in sources:
            context_parts.append(f"[{source.type.upper()}] {source.title}:\n{source.snippet}\n")
        return "\n".join(context_parts)

    def _create_prompt(self, ticket: Ticket, context: str, tone: str) -> str:
        """Create the prompt for AI generation"""
        tone_instructions = {
            "professional": "Usa un tono professionale ma cordiale",
            "friendly": "Usa un tono amichevole e informale",
            "technical": "Usa un tono tecnico e dettagliato"
        }

        tone_instruction = tone_instructions.get(tone, "Usa un tono professionale")

        prompt = f"""Sei un assistente che aiuta gli operatori del customer service a rispondere ai ticket dei clienti.

CONTESTO DA DOCUMENTI AZIENDALI:
{context}

TICKET DA GESTIRE:
Categoria: {ticket.category}
Priorità: {ticket.priority}
Oggetto: {ticket.subject}
Messaggio: {ticket.message}

ISTRUZIONI:
- Genera una risposta basandoti SOLO sui documenti forniti
- {tone_instruction}
- Sii specifico e actionable
- Includi numeri di telefono, email, o procedure quando rilevanti
- Non inventare informazioni non presenti nei documenti
- Rispondi in italiano
- Mantieni la risposta sotto le 300 parole

RISPOSTA:"""

        return prompt

    def _generate_fallback_response(self, ticket: Ticket, sources: List[Source]) -> str:
        """Generate a fallback response when AI is not available"""
        if not sources:
            return "Grazie per aver contattato il nostro supporto. Il suo ticket è stato preso in carico e sarà gestito dal team competente entro 24 ore. La ricontatteremo non appena avremo maggiori informazioni."

        # Create a simple response based on sources
        if ticket.category.lower() == "it":
            return f"Grazie per la segnalazione del problema tecnico. Basandoci sulla nostra documentazione, Le suggeriamo di contattare l'Helpdesk IT al numero 800-123-456 o via email a helpdesk@company.com. Il team è disponibile dal lunedì al venerdì dalle 8:00 alle 18:00 e potrà assisterla nella risoluzione del problema."
        elif ticket.category.lower() == "hr":
            return f"Per la sua richiesta relativa alle risorse umane, può trovare le informazioni necessarie accedendo al portale HR su hr.company.com. Per assistenza diretta, può contattare l'ufficio HR al numero 800-555-123 o via email a hr@company.com, disponibile dal lunedì al venerdì dalle 9:00 alle 17:00."
        else:
            return f"Grazie per averci contattato. Abbiamo ricevuto la sua richiesta e il nostro team la gestirà con la massima priorità. Per ulteriori informazioni può contattare il nostro customer service al numero 800-555-100. Saremo lieti di assisterla."

    def _calculate_confidence(self, sources: List[Source]) -> float:
        """Calculate confidence score based on source relevance"""
        if not sources:
            return 0.1

        # Average relevance of top sources
        top_sources = sources[:3]
        avg_relevance = sum(source.relevance for source in top_sources) / len(top_sources)

        # Boost confidence if we have multiple relevant sources
        source_bonus = min(len(sources) * 0.1, 0.3)

        confidence = min(avg_relevance + source_bonus, 1.0)
        return round(confidence, 2)

    def _generate_reasoning(self, ticket: Ticket, sources: List[Source]) -> str:
        """Generate reasoning for the response"""
        if not sources:
            return "Nessun documento rilevante trovato nella knowledge base aziendale."

        source_types = set(source.type for source in sources)
        reasoning_parts = []

        if 'knowledge_base' in source_types:
            kb_sources = [s for s in sources if s.type == 'knowledge_base']
            reasoning_parts.append(f"Consultati {len(kb_sources)} documenti della knowledge base aziendale")

        if 'past_ticket' in source_types:
            ticket_sources = [s for s in sources if s.type == 'past_ticket']
            reasoning_parts.append(f"Analizzati {len(ticket_sources)} ticket simili risolti in passato")

        avg_relevance = sum(s.relevance for s in sources[:3]) / min(3, len(sources))
        reasoning_parts.append(f"Rilevanza media delle fonti: {avg_relevance:.0%}")

        return ". ".join(reasoning_parts) + "."