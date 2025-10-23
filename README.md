# 🤖 AI Ticket Assistant

Un sistema di assistenza AI per operatori customer service che utilizza **DataPizza AI** e **Qdrant Cloud** per generare risposte intelligenti ai ticket aziendali basandosi su documentazione aziendale e ticket storici.

## 🎯 Caratteristiche Principali

- **RAG (Retrieval-Augmented Generation)** con DataPizza AI + Qdrant Cloud
- **Ricerca semantica** nella knowledge base aziendale e ticket passati
- **Generazione automatica** di risposte contestualizzate
- **Interface moderna** single-page application
- **Confidence scoring** per valutare l'affidabilità delle risposte
- **Visualizzazione fonti** utilizzate per la generazione

## 🏗️ Architettura

```
Frontend (HTML/JS/Tailwind) → FastAPI Backend → DataPizza AI → Qdrant Cloud
                                      ↓
                              Knowledge Base + Past Tickets
```

### Stack Tecnologico
- **Backend**: FastAPI + DataPizza AI
- **Vector DB**: Qdrant Cloud
- **Embedding**: OpenAI text-embedding-3-small
- **LLM**: OpenAI GPT-4o-mini
- **Frontend**: HTML5 + Tailwind CSS + JavaScript Vanilla

## 📊 Demo Data

Il sistema include dati mock per la demo:

### Knowledge Base (3 file):
- **IT Procedures**: VPN, email, account, supporto tecnico
- **HR Policies**: ferie, permessi, smart working, welfare
- **Customer Service SLA**: tempi consegna, rimborsi, reclami

### Past Tickets (7 esempi):
- Ticket IT risolti (VPN, Outlook, ecc.)
- Ticket HR risolti (ferie, permessi, ecc.)
- Ticket Customer Service risolti (ritardi, resi, ecc.)

### Ticket Demo (3 scenari):
- 🔧 **IT/Alta**: Problemi accesso VPN
- 👥 **HR/Media**: Richiesta ferie estive
- 📞 **CS/Alta**: Ritardo consegna ordine urgente

## 🚀 Setup e Installazione

### 1. Prerequisiti

- Python 3.10+
- Account [OpenAI](https://platform.openai.com/api-keys)
- Account [Qdrant Cloud](https://cloud.qdrant.io/)

### 2. Clonare e Setup

```bash
git clone <repository-url>
cd ticket-datapizza

# Setup backend
cd backend
python -m pip install -r requirements.txt
```

### 3. Configurazione Ambiente

Copia il file di esempio e configura le credenziali:

```bash
cp .env.example .env
```

Edita il file `.env` con le tue credenziali:

```env
# OpenAI API Key (obbligatorio)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Qdrant Cloud (obbligatorio)
QDRANT_URL=https://your-cluster-id.eu-central.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION=knowledge_base

# Opzionale
DATAPIZZA_LOG_LEVEL=INFO
```

### 4. Avvio del Sistema

**Backend (Terminale 1):**
```bash
cd backend
python main.py
```

Il server sarà disponibile su: http://localhost:8000

**Frontend (Terminale 2 o Browser):**
```bash
cd frontend
# Opzione 1: Apri index.html direttamente nel browser
open index.html

# Opzione 2: Server HTTP locale (consigliato)
python -m http.server 3000
# Vai su http://localhost:3000
```

## 🎬 Come Usare la Demo

### 1. Primo Avvio
- Il backend caricherà automaticamente i dati nella knowledge base
- Verifica nei log che le collezioni Qdrant siano create correttamente
- L'interfaccia mostrerà 3 ticket di esempio

### 2. Demo Flow
1. **Apri l'app** → Vedrai 3 ticket aperti
2. **Clicca su un ticket** → Si apre la vista dettagliata
3. **Click "Suggerisci Risposta con AI"** → AI analizza documenti
4. **Visualizza risultato**:
   - Risposta suggerita (modificabile)
   - Confidence score con barra colorata
   - Fonti utilizzate con snippet
   - Ragionamento AI
5. **Modifica la risposta** se necessario
6. **Invia** → Mostra conferma successo

### 3. Test Scenarios

**Scenario IT (VPN):**
- Mostra ricerca in documentazione IT
- Fonti: procedure VPN, troubleshooting, contatti
- Confidence alta (80%+)

**Scenario HR (Ferie):**
- Ricerca policy HR e procedure
- Fonti: portal HR, tempistiche, documenti
- Confidence media-alta (70-85%)

**Scenario Customer Service (Ritardo):**
- Combina SLA + past tickets simili
- Fonti: policy rimborsi, compensazioni, escalation
- Confidence alta se trova ticket simili

## 🔧 Configurazione Avanzata

### Toni di Risposta
Il sistema supporta 3 toni modificabili nel frontend:
- **Professionale**: Default, formale ma cordiale
- **Amichevole**: Più informale e colloquiale
- **Tecnico**: Dettagliato e specifico

### Soglie di Confidenza
Modificabili in `rag_engine.py`:
```python
def _calculate_confidence(self, sources):
    # Soglia minima similarità: 0.3
    # Confidence bassa: < 60%
    # Confidence media: 60-80%
    # Confidence alta: > 80%
```

### Vector Search Tuning
```python
# In search_relevant_documents():
kb_results = self.vectorstore.search(
    collection_name=self.kb_collection,
    query_vector=query_vector,
    k=3  # Top K documenti knowledge base
)
```

## 📈 Metriche e Monitoring

### Logging DataPizza AI
```bash
export DATAPIZZA_LOG_LEVEL=DEBUG
export DATAPIZZA_AGENT_LOG_LEVEL=DEBUG
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Qdrant Collections Status
Le collezioni vengono create automaticamente all'avvio:
- `knowledge_base`: documenti aziendali
- `past_tickets`: ticket storici risolti

## 🛠️ Sviluppo e Personalizzazione

### Aggiungere Nuovi Documenti
1. Metti i file `.txt` in `data/knowledge_base/`
2. Riavvia il backend per re-indicizzare
3. Usa il formato con sezioni `=== TITOLO ===`

### Modificare i Ticket Demo
Edita `data/past_tickets.json` e riavvia il backend.

### Personalizzare il Frontend
Il file `frontend/index.html` contiene tutto:
- HTML struttura
- CSS con Tailwind CDN
- JavaScript vanilla per interazioni

### Estendere il Backend
- `models.py`: Modelli dati Pydantic
- `rag_engine.py`: Logica RAG con DataPizza AI
- `main.py`: Server FastAPI e endpoints

## 🐛 Troubleshooting

### Errori Comuni

**1. "RAG engine not available"**
```bash
# Verifica credenziali API
echo $OPENAI_API_KEY
echo $QDRANT_URL

# Controlla connessione Qdrant
curl -X GET "$QDRANT_URL/collections" -H "api-key: $QDRANT_API_KEY"
```

**2. "Error generating embedding"**
- Verifica quota OpenAI API
- Controlla validità API key
- Fallback: sistema usa embedding dummy per demo

**3. "Collection already exists"**
- Normale al primo avvio
- Per reset: elimina collezioni da Qdrant Cloud console

**4. CORS Errors Frontend**
- Usa server HTTP locale invece di file://
- Oppure aggiungi origin specifico in `main.py`

### Debug Mode
```bash
# Backend verbose
python main.py --debug

# Frontend console
# Apri DevTools → Console per errori JS
```

## 📞 Support

Per problemi tecnici:
- Verifica setup seguendo questa guida
- Controlla logs backend per errori specifici
- Testa health check endpoints
- Verifica connessione Qdrant Cloud

## 🔄 Roadmap Future

- [ ] Autenticazione utenti
- [ ] Database persistente per ticket
- [ ] Chat multi-turno con AI
- [ ] Feedback loop per migliorare risposte
- [ ] Analytics e metriche avanzate
- [ ] Integrazione con sistemi CRM/ticketing esistenti

---

**Powered by DataPizza AI** 🍕
Un framework moderno per AI production-ready!