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
            id="DEMO-001",
            category="IT",
            priority="high",
            subject="Problemi accesso VPN",
            message="Buongiorno, non riesco ad accedere alla VPN aziendale. Inserisco le credenziali ma ricevo errore 'Autenticazione fallita'. Ho già provato a cambiare la password ma il problema persiste. Ho urgente bisogno di accedere ai file del server per completare il progetto che ha scadenza oggi. Potete aiutarmi a risolvere il prima possibile?",
            created_at=datetime.now()
        ),
        Ticket(
            id="DEMO-002",
            category="HR",
            priority="medium",
            subject="Richiesta ferie estive",
            message="Salve, vorrei richiedere 3 settimane di ferie per il mese di luglio (dal 8 al 29 luglio). È la prima volta che faccio richiesta di ferie così lunghe e non sono sicuro della procedura. Quali documenti devo preparare? Devo avvisare qualcuno in particolare? Quanto tempo prima devo fare la richiesta? Inoltre, volevo sapere se è possibile suddividerle in 2 settimane + 1 settimana separata.",
            created_at=datetime.now()
        ),
        Ticket(
            id="DEMO-003",
            category="Customer Service",
            priority="high",
            subject="Ritardo consegna ordine urgente",
            message="Il mio ordine #CS2024-1456 doveva essere consegnato 5 giorni fa ed è ancora in 'elaborazione'. È un ordine urgente per un regalo di compleanno che è oggi! Il cliente è molto arrabbiato e minaccia di annullare tutti gli ordini futuri. Ha già avuto problemi simili in passato con i nostri tempi di consegna. Come posso gestire questa situazione? Offrite compensazioni per i ritardi? Il cliente è un cliente premium con oltre 3000€ di ordini nell'ultimo anno.",
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
        # Generate response using RAG
        result = rag_engine.generate_response(
            ticket=request.ticket,
            tone=request.tone or "professional"
        )

        return GenerateResponseResponse(
            suggested_response=result["suggested_response"],
            confidence_score=result["confidence_score"],
            sources=result["sources"],
            reasoning=result["reasoning"]
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
    uvicorn.run(app, host="0.0.0.0", port=8000)