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

class ToolCall(BaseModel):
    """Rappresenta una singola chiamata a un tool"""
    tool_name: str
    tool_input: str
    tool_output: str
    status: str = "success"  # "success", "error", "pending"

class GenerateResponseRequest(BaseModel):
    ticket: Ticket
    image_base64: Optional[str] = None
    tone: Optional[str] = "professional"
    regeneration_feedback: Optional[str] = None  # Feedback per rigenerazione


class OpsResponse(BaseModel):
    thought_process: str
    sql_query_used: str 
    action_checklist: List[str]
    coal_alert: bool
    final_response: str
    tool_calls: List[ToolCall] = []

class GenerateResponseResponse(BaseModel):
    # Mapping fields from OpsResponse to frontend response
    suggested_response: str
    thought_process: str
    sql_query_used: str
    action_checklist: List[str]
    coal_alert: bool
    tool_calls: List[ToolCall] = []
    confidence_score: float = 1.0 # Default High for Agent
    sources: List[Source] = []
    reasoning: str = "Agentic Reasoning"


class ExampleTicketsResponse(BaseModel):
    tickets: List[Ticket]

class HealthResponse(BaseModel):
    status: str
    message: str