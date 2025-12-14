# Ufficio Reclami Polo Nord

Un sistema di gestione ticket basato su AI per l'assistenza clienti del Polo Nord. Utilizza **DataPizza AI** con architettura multi-agente e **Qdrant** per la ricerca semantica.

## Descrizione

L'applicazione simula un ufficio reclami dove i genitori scrivono a Babbo Natale per lamentarsi di regali sbagliati, carbone ricevuto ingiustamente, o consegne mancate. L'AI analizza ogni reclamo consultando:

- **Database SQL** (SQLite): informazioni sui bambini, naughty score, inventario regali
- **Knowledge Base**: manuali operativi, protocolli elfi, regolamenti
- **Ticket Storici**: casi passati simili già risolti

## Stack Tecnologico

| Componente | Tecnologia |
|------------|------------|
| **AI Framework** | **[DataPizza AI](https://datapizza.tech)** |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ *Agents* | Multi-Agent System (Master + Sub-agents), Planning, Tool Use |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ *Clients* | OpenAIClient (GPT-4.1), Structured Responses (Pydantic), Streaming |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ *Memory* | Context Preservation, Tracing |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ *RAG* | ChunkEmbedder, RecursiveSplitter, QdrantVectorstore |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ *Tools* | SQLDatabase (SQLite), Function Calling |
| Backend | FastAPI + Python |
| Database | SQLite (Relational), Qdrant (Vector) |
| Frontend | HTML + Tailwind CSS + JavaScript |

## DataPizza AI Features Implementation

Il progetto sfrutta appieno l'ecosistema **DataPizza AI**:

*   **Agents Core**: Architettura multi-agente con `Agent` e comunicazione inter-agente (`can_call`).
*   **Advanced RAG Pipeline**:
    *   **Ingestion**: Utilizzo di `RecursiveSplitter` per chunking semantico intelligente.
    *   **Embedding**: Implementazione di `ChunkEmbedder` per processamento batch ottimizzato.
    *   **Vector Store**: Integrazione nativa con `QdrantVectorstore` per la ricerca semantica.
*   **Strumenti e Connettività**:
    *   **SQLDatabase Tool**: Introspezione schema ed esecuzione query sicure su SQLite.
    *   **Custom Tools**: Decoratore `@tool` per funzioni Python custom con tracing integrato.
*   **Observability & Robustness**:
    *   **Tracing**: Monitoraggio granulare tramite `ContextTracing`.
    *   **Structured Outputs**: Garanzia di formato JSON valido tramite `client.structured_response` e modelli Pydantic.

## Struttura Progetto

```
ticket-datapizza/
├── backend/
│   ├── main.py              # Server FastAPI
│   ├── rag_engine.py        # Engine multi-agente
│   ├── models.py            # Modelli Pydantic
│   └── ingest_tickets.py    # Script indicizzazione
├── frontend/
│   └── index.html           # Interfaccia utente
├── data/
│   ├── knowledge_base/      # Manuali e protocolli
│   │   ├── customer_service_handbook.txt
│   │   ├── elf_protocols.txt
│   │   ├── gift_regulations.txt
│   │   ├── hr_policies.txt
│   │   ├── it_security_manual.txt
│   │   └── sleigh_manual.txt
│   └── past_tickets.json    # Ticket storici
├── northpole.db             # Database SQLite
├── requirements.txt
└── README.md
```

## Architettura Multi-Agente

Il sistema utilizza tre agenti specializzati:

1. **SQL Expert**: interroga il database per recuperare dati su bambini e inventario
2. **History Expert**: cerca nei manuali e nei ticket passati
3. **Master Agent**: coordina gli altri agenti e genera la risposta finale

```
[Reclamo Genitore] → Master Agent
                         ├── SQL Expert → Database
                         └── History Expert → Vector DB (Manuali + Ticket)
                                  ↓
                         [Risposta Strutturata + Azioni da Fare]
```

## Setup

### Prerequisiti

- Python 3.10+
- Account OpenAI con API key
- (Opzionale) Account Qdrant Cloud

### Installazione

```bash
# Clona il repository
git clone <repository-url>
cd ticket-datapizza

# Crea virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Installa dipendenze
pip install -r requirements.txt
```

### Configurazione

Crea un file `.env` nella root del progetto:

```env
OPENAI_API_KEY=sk-your-api-key-here

# Opzionale - Qdrant Cloud (altrimenti usa in-memory)
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
```

### Avvio

### Avvio

```bash
# Setup completo (Database & RAG)
python backend/scripts/setup_db.py
python backend/scripts/setup_rag.py

# Avvia il server
python backend/main.py
```

Apri il browser su `http://localhost:8000`

## Funzionalità

### Ticket Demo

L'applicazione include 7 ticket di esempio, tutti reclami di genitori:

| ID | Scenario |
|----|----------|
| NP-2025-001 | Madre furiosa per carbone al figlio |
| NP-2025-002 | Regalo completamente sbagliato |
| NP-2025-003 | Babbo Natale non è passato |
| NP-2025-004 | Contestazione naughty score |
| NP-2025-005 | Regalo arrivato danneggiato |
| NP-2025-006 | Richiesta speciale bambina malata |
| NP-2025-007 | Entrambi i figli con carbone |

### Knowledge Base

I manuali coprono diverse aree operative:

- **Customer Service Handbook**: gestione reclami, escalation, toni di comunicazione
- **Elf Protocols**: turni lavoro, sicurezza, codici emergenza
- **Gift Regulations**: oggetti proibiti, regole sostituzione, packaging
- **HR Policies**: ferie, malattia, straordinari
- **IT Security Manual**: VPN, credenziali, sicurezza database
- **Sleigh Manual**: specifiche tecniche slitta Mark-VII

### Database

Tabelle SQLite disponibili:

**children_log**
- id, name, city, naughty_score, last_incident, gift_requested, status

**inventory**
- id, item_name, quantity, category

### Coal Alert

Se un bambino ha `naughty_score > 50`, il sistema attiva automaticamente il "Coal Alert" e applica il protocollo carbone secondo le linee guida.

## API Endpoints

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/tickets/examples` | GET | Lista ticket demo |
| `/api/tickets/generate-response` | POST | Genera risposta AI |
| `/api/tickets/generate-response-stream` | POST | Genera risposta in streaming (SSE) |

## Sviluppo

### Aggiungere nuovi manuali

1. Crea un file `.txt` in `data/knowledge_base/`
2. Riavvia il backend per re-indicizzare

### Modificare i ticket demo

I ticket sono definiti in `backend/main.py` nella funzione `get_example_tickets()`.

### Configurare il database

Modifica `populate_db.py` per aggiungere nuovi bambini o oggetti all'inventario.

## Tecnologie Utilizzate

- [DataPizza AI](https://datapizza.tech) - Framework per agenti AI
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework Python
- [Qdrant](https://qdrant.tech/) - Vector database
- [Tailwind CSS](https://tailwindcss.com/) - Styling

## Licenza

MIT License

---

Progetto demo per DataPizza AI
