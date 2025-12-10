from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from datetime import datetime
import os
import json
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
            category="Reclamo Regalo",
            priority="critical",
            subject="MIO FIGLIO HA RICEVUTO CARBONE - VERGOGNA!",
            message="Buongiorno, sono Maria Rossi, la madre di Tommy (child_id: CH-8847). Stamattina mio figlio ha aperto il pacco e invece della PlayStation 5 che aveva chiesto c'era un pezzo di CARBONE. Tommy ha pianto per due ore! È stato bravissimo tutto l'anno: fa i compiti, aiuta in casa, è gentile con la sorellina. Non capisco questo errore IMPERDONABILE. Siamo clienti fedeli da 5 anni e questo è il trattamento che riceviamo? Voglio spiegazioni IMMEDIATE e il regalo corretto consegnato entro oggi, altrimenti contatterò tutti i giornali. Non scherzate con me.",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-002",
            category="Regalo Sbagliato",
            priority="high",
            subject="Regalo completamente sbagliato per mia figlia",
            message="Salve, mi chiamo Giulia Bianchi e scrivo per mia figlia Sofia di 8 anni. Sofia aveva chiesto una Barbie Dreamhouse e invece ha ricevuto... un set di attrezzi da meccanico?! Mia figlia è devastata, era il regalo che sognava da mesi. Ho le prove della letterina che abbiamo spedito insieme. Come è possibile un errore del genere? Potete sistemare questa situazione? Sofia non smette di piangere.",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-003",
            category="Mancata Consegna",
            priority="critical",
            subject="Babbo Natale NON è passato - Emergenza!",
            message="Sono Francesco Verdi, padre di due gemelli di 6 anni (Marco e Luca). Stamattina sotto l'albero NON C'ERA NIENTE. I bambini sono traumatizzati, pensano di essere stati cattivi. Abbiamo controllato: camino pulito, biscotti e latte pronti, letterine inviate a Novembre. I nostri figli sono nella lista 'nice', ho verificato io stesso! Come è possibile che ci abbiate SALTATI? Pretendo una risposta e una soluzione OGGI. I miei figli stanno piangendo disperatamente.",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-004",
            category="Naughty Score Contestato",
            priority="high",
            subject="Contestazione punteggio 'cattivo' di Pierre",
            message="Bonjour, sono Isabelle Méchant da Lyon. Ho ricevuto una notifica che mio figlio Pierre ha un 'naughty_score' di 78 e riceverà carbone. Questo è INACCETTABILE! Pierre ha fatto UNA marachella tutto l'anno (ha rotto un vaso per sbaglio!) e voi lo condannate così? I suoi compagni di classe che fanno i bulli hanno ricevuto regali normalmente! Voglio sapere ESATTAMENTE cosa risulta nel vostro database e chi ha deciso questo punteggio assurdo. Attendo risposta urgente.",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-005",
            category="Regalo Danneggiato",
            priority="medium",
            subject="LEGO arrivato in mille pezzi - pacco distrutto",
            message="Salve, sono Andrea Neri. Il regalo per mio figlio Matteo (LEGO Star Wars Ultimate Collector) è arrivato con la scatola completamente DISTRUTTA. Matteo ha 10 anni e colleziona LEGO da quando ne aveva 5, questo era il pezzo forte della sua collezione. Mancano pezzi ovunque, il libretto istruzioni è strappato. 300 euro di regalo rovinato! Le renne hanno usato il pacco come palla da calcio? Voglio un rimborso o una sostituzione.",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-006",
            category="Richiesta Speciale",
            priority="medium",
            subject="Bambina malata - per favore aiutateci",
            message="Gentile Babbo Natale, sono Elena Conti. Mia figlia Aurora di 7 anni è in ospedale da 3 mesi per una malattia seria. Il suo unico desiderio era un unicorno peluche gigante rosa, quello che canta. Il pacco è arrivato ma era VUOTO, solo carta da imballaggio. Aurora ha creduto di essere stata 'dimenticata' da Babbo Natale e questo le ha spezzato il cuore. Per favore, vi prego, potete rimediare? È l'unica cosa che la fa sorridere. Allego foto della letterina che ha scritto dall'ospedale.",
            created_at=datetime.now()
        ),
        Ticket(
            id="NP-2025-007",
            category="Doppio Carbone",
            priority="critical",
            subject="ENTRAMBI i miei figli hanno ricevuto carbone - ASSURDO",
            message="INCREDIBILE! Sono Roberto Martini, padre di Emma (9 anni) e Giulio (7 anni). ENTRAMBI i miei figli hanno trovato carbone sotto l'albero. Emma ha voti perfetti a scuola, fa volontariato alla parrocchia! Giulio è il bambino più buono del quartiere, lo dicono tutti! Il vostro sistema è COMPLETAMENTE ROTTO. Voglio parlare con Mrs. Claus personalmente. Ho le pagelle, le lettere delle maestre, tutto quello che serve per dimostrare che i miei figli sono ANGEL. RISPONDETE SUBITO!",
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

@app.post("/api/tickets/generate-response-stream")
async def generate_response_stream(request: GenerateResponseRequest):
    """
    SSE endpoint for real-time tool streaming.
    Yields events as the agent executes tools.
    """
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not available"
        )

    async def event_generator():
        try:
            async for event in rag_engine.generate_response_stream(
                ticket=request.ticket,
                image_base64=request.image_base64,
                regeneration_feedback=request.regeneration_feedback
            ):
                # Format as SSE: "data: {...}\n\n"
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            print(f"SSE Error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
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