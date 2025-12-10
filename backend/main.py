from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import os
from dotenv import load_dotenv

from models import (
    Ticket, GenerateResponseRequest, GenerateResponseResponse,
    ExampleTicketsResponse, HealthResponse
)
from rag_engine import RAGEngine

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Ticket Assistant API",
    description="API for AI-powered customer support ticket assistance",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
import pathlib
frontend_dir = pathlib.Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Initialize RAG engine
rag_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG engine on startup"""
    global rag_engine
    print("Initializing RAG engine...")
    try:
        rag_engine = RAGEngine()
        print("RAG engine initialized successfully")
    except Exception as e:
        print(f"Failed to initialize RAG engine: {e}")
        rag_engine = None

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if rag_engine is None:
        return HealthResponse(
            status="unhealthy",
            message="RAG engine not initialized"
        )

    return HealthResponse(
        status="healthy",
        message="API is running and RAG engine is ready"
    )

@app.get("/api/tickets/examples", response_model=ExampleTicketsResponse)
async def get_example_tickets():
    """Get example tickets for demo"""
    example_tickets = [
        Ticket(
            id="NP-2025-001",
            category="IT Support",
            priority="high",
            subject="VPN Polare non funziona - Urgente!",
            message="Sono l'elfo Sparkle del reparto Confezionamento. Da stamattina non riesco ad accedere alla VPN aziendale. Inserisco le mie credenziali ELF-7842 ma ricevo errore 'Autenticazione Fallita'. Ho già provato a riavviare il computer e verificare la connessione. Ho urgente bisogno di accedere al Database Regali per completare gli ordini del settore Europa che hanno deadline oggi! Il mio Fiocco di Neve Token sembra funzionare. Aiutatemi!",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-002",
            category="HR Elfi",
            priority="medium",
            subject="Richiesta ferie post-Natale",
            message="Salve, sono Jingle del reparto Verniciatura Giocattoli. Dopo la maratona natalizia vorrei richiedere 2 settimane di ferie dal 2 al 16 Gennaio per recuperare le energie. È la mia prima richiesta di ferie lunghe e non conosco la procedura. Quali documenti devo preparare? Devo far firmare qualcuno? Inoltre, dato che ho fatto 847 ore di straordinario a Dicembre, volevo sapere se ho diritto a qualche bonus extra. Grazie!",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-003",
            category="Customer Service",
            priority="critical",
            subject="Genitore furioso - bambino nella Naughty List",
            message="URGENTE! Ho una madre al telefono furiosa perché suo figlio Tommy (child_id: CH-8847) ha ricevuto carbone invece del PlayStation richiesto. Sostiene che il bambino è stato bravissimo tutto l'anno e minaccia di contattare i media. Ho controllato nel database e il naughty_score è 73. La signora è cliente premium con 5 ordini negli ultimi 3 anni. Come devo gestire la situazione? Posso offrire compensazioni? Devo escalare a Mrs. Claus?",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-004",
            category="Manutenzione Slitta",
            priority="critical",
            subject="EMERGENZA - Motore slitta surriscaldato!",
            message="MAYDAY MAYDAY! Sono il co-pilota Blitzen Jr. Siamo sopra la Germania e il motore plasma ha raggiunto 5200K! Gli iniettori sembrano intasati e stiamo perdendo quota. Abbiamo ancora 2000 consegne da fare in Europa. Qual è la procedura di emergenza? Dobbiamo attivare il raffreddamento d'emergenza? C'è un punto di atterraggio sicuro nelle vicinanze? Il codice errore sullo schermo è AG-500!",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-005",
            category="Database Query",
            priority="high",
            subject="Verifica bambino Pierre Méchant - possibile errore naughty score",
            message="Ciao! Ho ricevuto una lamentela dalla famiglia Méchant di Lyon riguardo al loro figlio Pierre. Dicono che il suo naughty_score è troppo alto e vogliono sapere il motivo esatto. Puoi verificare nel database children_log qual è il suo score attuale e qual è stato l'ultimo incidente registrato? Dobbiamo rispondere ai genitori con dati precisi.",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-006",
            category="Inventory Check",
            priority="medium",
            subject="Controllo stock PlayStation 5 e Xbox",
            message="Urgente! Ho bisogno di sapere quante PlayStation 5 e Xbox Series X abbiamo in magazzino. Molti bambini le hanno richieste ma temo che siamo in shortage. Controlla anche in quale settore del warehouse sono stoccate così posso mandare gli elfi a verificare. Se lo stock è basso, devo fare un ordine urgente!",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-007",
            category="Multi-Query",
            priority="critical",
            subject="Report completo bambini Roma e Milano",
            message="Per la riunione di domani con Mrs. Claus ho bisogno di un report completo. Quanti bambini abbiamo registrati nelle città di Rome e Milan? Qual è il loro status (APPROVED, PENDING, COAL)? E qual è la media del naughty_score per queste città? Questi dati sono fondamentali per la presentazione!",
            created_at=datetime.now()
        )
    ]

    return ExampleTicketsResponse(tickets=example_tickets)

@app.post("/api/tickets/generate-response", response_model=GenerateResponseResponse)
async def generate_response(request: GenerateResponseRequest):
    """Generate AI response for a ticket"""
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not available. Please try again later."
        )

    try:
        # Generate response using Agent
        ops_response = rag_engine.generate_response(
            ticket=request.ticket,
            image_base64=request.image_base64,
            regeneration_feedback=request.regeneration_feedback
        )
        
        # Handle dict or object
        if isinstance(ops_response, dict):
             return GenerateResponseResponse(
                suggested_response=ops_response.get("final_response", ""),
                thought_process=ops_response.get("thought_process", ""),
                sql_query_used=ops_response.get("sql_query_used", "N/A"),
                action_checklist=ops_response.get("action_checklist", []),
                coal_alert=ops_response.get("coal_alert", False),
                tool_calls=ops_response.get("tool_calls", []),
                confidence_score=1.0,
                sources=[],
                reasoning=ops_response.get("thought_process", "")
             )
        else:
            return GenerateResponseResponse(
                suggested_response=ops_response.final_response,
                thought_process=ops_response.thought_process,
                sql_query_used=ops_response.sql_query_used,
                action_checklist=ops_response.action_checklist,
                coal_alert=ops_response.coal_alert,
                tool_calls=ops_response.tool_calls,
                confidence_score=1.0,
                sources=[],
                reasoning=ops_response.thought_process
            )

    except Exception as e:
        print(f"Error generating response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )

@app.get("/")
async def root():
    """Redirect to frontend"""
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/index.html")
async def frontend():
    """Serve frontend"""
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {"message": "AI Ticket Assistant API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)