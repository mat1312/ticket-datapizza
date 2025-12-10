# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered ticket assistant for customer service operations using **DataPizza AI** and **Qdrant Cloud**. The system uses RAG (Retrieval-Augmented Generation) to generate intelligent responses to support tickets based on company documentation and historical tickets.

## Architecture

- **Backend**: FastAPI application ([backend/main.py](backend/main.py))
- **RAG Engine**: DataPizza AI integration with Qdrant Cloud vectorstore ([backend/rag_engine.py](backend/rag_engine.py))
- **Models**: Pydantic data models ([backend/models.py](backend/models.py))
- **Frontend**: Single-page HTML application with Tailwind CSS ([frontend/index.html](frontend/index.html))
- **Data**: Knowledge base documents and past tickets in JSON format ([data/](data/))

## Common Commands

### Backend Development
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
# Server runs on http://localhost:8000
```

### Frontend Development
```bash
cd frontend
python -m http.server 3000
# Serves on http://localhost:3000
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Environment Configuration

The application requires these environment variables:
- `OPENAI_API_KEY`: OpenAI API key for embeddings and LLM
- `QDRANT_URL`: Qdrant Cloud cluster URL
- `QDRANT_API_KEY`: Qdrant Cloud API key
- `QDRANT_COLLECTION`: Collection name (default: "knowledge_base")
- `PORT`: Server port (default: 8000)

## Key Components

### RAG Engine ([backend/rag_engine.py](backend/rag_engine.py))
- Initializes on startup and loads data into Qdrant collections
- Creates two collections: `knowledge_base` (company docs) and `past_tickets` (historical tickets)
- Uses OpenAI text-embedding-3-small for embeddings
- Uses GPT-4o-mini for response generation
- Includes fallback responses when AI services are unavailable

### Data Structure
- **Knowledge base**: Text files in `data/knowledge_base/` with section markers (`=== TITLE ===`)
- **Past tickets**: JSON array in `data/past_tickets.json` with ticket/response pairs
- **Demo tickets**: 3 example tickets for IT, HR, and Customer Service categories

### API Endpoints
- `GET /api/health`: Health check
- `GET /api/tickets/examples`: Get demo tickets
- `POST /api/tickets/generate-response`: Generate AI response for a ticket

## Development Notes

- The system gracefully handles missing API credentials with fallback responses
- Qdrant collections are created automatically on first run
- Knowledge base documents are split into sections based on `===` markers
- Confidence scoring is based on source relevance and number of matching sources
- Supports multiple response tones: professional, friendly, technical