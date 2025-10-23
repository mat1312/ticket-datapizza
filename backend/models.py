from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Ticket(BaseModel):
    id: str
    category: str
    priority: str
    subject: str
    message: str
    created_at: Optional[datetime] = None

class PastTicket(BaseModel):
    id: str
    category: str
    priority: str
    subject: str
    message: str
    response: str
    resolution: str
    satisfaction: int
    tags: List[str]
    resolved_at: str

class Source(BaseModel):
    id: str
    title: str
    snippet: str
    relevance: float
    type: str  # "knowledge_base" or "past_ticket"

class GenerateResponseRequest(BaseModel):
    ticket: Ticket
    tone: Optional[str] = "professional"

class GenerateResponseResponse(BaseModel):
    suggested_response: str
    confidence_score: float
    sources: List[Source]
    reasoning: str

class ExampleTicketsResponse(BaseModel):
    tickets: List[Ticket]

class HealthResponse(BaseModel):
    status: str
    message: str