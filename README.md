# AI-CRM-HCP — Pharma Sales Intelligence

An AI-powered CRM for pharmaceutical sales representatives that enables dual-mode interaction logging: **Traditional Form** and **AI Chat Assistant** powered by LangGraph + Groq (Gemma 2 9B IT).

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────┐
│              React Frontend              │
│    Redux Toolkit │ MUI │ Axios │ Inter   │
└─────────────────┬────────────────────────┘
                  │ REST API
┌─────────────────┴────────────────────────┐
│              FastAPI Backend             │
│  ┌────────────┐  ┌─────────────────────┐ │
│  │ CRUD APIs  │  │  LangGraph Agent    │ │
│  │            │  │  ┌───────────────┐  │ │
│  │ Interaction│  │  │ Intent Router │  │ │
│  │ Doctor     │  │  └──────┬────────┘  │ │
│  │            │  │    ┌────┴────┐      │ │
│  └────────────┘  │    │ 5 Tools │      │ │
│                  │    └────┬────┘      │ │
│  ┌────────────┐  │    ┌────┴────┐      │ │
│  │  Service   │  │    │  Groq   │      │ │
│  │  Layer     │  │    │ LLM     │      │ │
│  └────────────┘  │    └─────────┘      │ │
│                  └─────────────────────┘ │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────┴────────────────────────┐
│            PostgreSQL Database           │
│  HCP │ Interaction │ Material │ Sample   │
└──────────────────────────────────────────┘
```

---

## 🧰 Technology Stack

| Layer     | Technologies                                      |
|-----------|---------------------------------------------------|
| Frontend  | React, Redux Toolkit, Material UI, Axios, Inter   |
| Backend   | FastAPI, SQLAlchemy, Pydantic                      |
| AI        | LangGraph, LangChain, Groq (Gemma 2 9B IT)        |
| Database  | PostgreSQL                                         |
| Build     | Vite (frontend), Uvicorn (backend)                 |

---

## 📁 Folder Structure

```
AI-CRM-HCP/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatAssistant/ChatAssistant.jsx
│       │   ├── InteractionForm/InteractionForm.jsx
│       │   ├── AIResponseCard/AIResponseCard.jsx
│       │   └── Navbar/Navbar.jsx
│       ├── pages/
│       │   └── LogInteraction.jsx
│       ├── redux/
│       │   ├── slices/
│       │   │   ├── interactionSlice.js
│       │   │   ├── chatSlice.js
│       │   │   └── doctorSlice.js
│       │   └── store.js
│       ├── services/
│       │   └── api.js
│       ├── theme.js
│       ├── App.jsx
│       └── main.jsx
├── backend/
│   └── app/
│       ├── api/
│       │   ├── interactions.py
│       │   ├── doctors.py
│       │   └── chat.py
│       ├── models/
│       │   └── models.py
│       ├── schemas/
│       │   └── schemas.py
│       ├── services/
│       │   └── interaction_service.py
│       ├── graph/
│       │   └── graph.py          ← LangGraph workflow
│       ├── tools/
│       │   └── tools.py          ← 5 agent tools
│       ├── prompts/
│       │   └── prompts.py
│       ├── utils/
│       │   ├── llm.py
│       │   └── seed.py
│       ├── database/
│       │   └── database.py
│       └── main.py
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL running locally
- Groq API key ([get one here](https://console.groq.com))

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env and set your GROQ_API_KEY and DATABASE_URL

# Create the database
psql -U postgres -c "CREATE DATABASE ai_crm;"

# Seed sample data
python -m app.utils.seed

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🔑 Environment Variables

| Variable       | Description                          | Example                                          |
|----------------|--------------------------------------|--------------------------------------------------|
| `DATABASE_URL` | PostgreSQL connection string         | `postgresql://postgres:postgres@localhost:5432/ai_crm` |
| `GROQ_API_KEY` | Groq API key for Gemma 2 9B IT      | `gsk_...`                                        |

---

## 🤖 LangGraph Workflow

The agent uses a **StateGraph** with conditional routing based on intent classification:

```
User Message
     │
     ▼
┌─────────────────┐
│ Understand Intent│ ← LLM classifies into 6 categories
└────────┬────────┘
         │
    ┌────▼────┐
    │  Router  │ ← Conditional edges
    └────┬────┘
         │
    ┌────┴───────────────────────────────────┐
    │          │          │         │         │
    ▼          ▼          ▼         ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐
│ Log  │ │ Edit │ │Search│ │ Hist │ │Recommend │
│ Tool │ │ Tool │ │ Tool │ │ Tool │ │  Tool    │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └────┬─────┘
   │        │        │        │           │
   └────────┴────────┴────────┴───────────┘
                     │
                     ▼
           ┌─────────────────┐
           │Generate Response │ ← LLM synthesizes final output
           └────────┬────────┘
                    │
                    ▼
              Final Response
```

### Agent State

```python
AgentState = {
    "user_input": str,
    "conversation_history": list[dict],
    "intent": str,           # Classified intent
    "tool_output": str,      # Raw tool result
    "final_response": str,   # Natural language response
    "extracted_entities": dict,
    "interaction_id": int,
    "tool_used": str,
}
```

---

## 🔧 Five Agent Tools

### 1. Log Interaction (`log_interaction`)
Extracts structured data from natural language and saves to the database.

**Input**: Natural language description of a doctor meeting
**Process**: LLM extraction → Entity parsing → Doctor lookup/creation → DB save
**Output**: Saved interaction with ID, entities, and confirmation

**Example**:
> "Met Dr Sharma today. Discussed GlucoCare. Doctor liked efficacy but worried about price. Asked for two samples. Follow up next Tuesday."

### 2. Edit Interaction (`edit_interaction`)
Modifies an existing interaction based on natural language instructions.

**Input**: Edit instruction + optional interaction ID
**Process**: Fetch record → LLM interprets changes → Apply updates
**Output**: Updated interaction details

**Example**:
> "Change the follow-up to Friday instead"

### 3. Search HCP (`search_hcp`)
Searches doctors by name, specialization, hospital, or city.

**Input**: Search query
**Process**: Fuzzy database search across multiple fields
**Output**: Matching doctors with interaction counts

**Example**:
> "Find Dr Sharma" or "Search cardiologists in Mumbai"

### 4. Interaction History (`interaction_history`)
Retrieves past interactions for a specific doctor.

**Input**: Doctor name + optional limit
**Process**: Doctor lookup → Fetch sorted interactions
**Output**: Chronological interaction list with details

**Example**:
> "Show my last 5 meetings with Dr Sharma"

### 5. Follow-up Recommendation (`followup_recommendation`)
AI-generated follow-up suggestions based on interaction history and sentiment trends.

**Input**: Doctor name
**Process**: Fetch history → Analyze sentiment trend → LLM recommendation
**Output**: Actionable next steps, timing, materials, talking points

**Example**:
> "What should I do next with Dr Sharma?"

---

## 📡 API Endpoints

### Interactions (CRUD)
| Method | Endpoint                    | Description              |
|--------|-----------------------------|--------------------------|
| POST   | `/api/interactions`         | Create new interaction   |
| GET    | `/api/interactions`         | List all interactions    |
| GET    | `/api/interactions/{id}`    | Get single interaction   |
| PUT    | `/api/interactions/{id}`    | Update interaction       |
| DELETE | `/api/interactions/{id}`    | Delete interaction       |

### Doctors
| Method | Endpoint              | Description            |
|--------|-----------------------|------------------------|
| GET    | `/api/doctors`        | List/search doctors    |
| GET    | `/api/doctors/{id}`   | Get doctor details     |
| POST   | `/api/doctors`        | Create new doctor      |

### AI Agent
| Method | Endpoint       | Description                   |
|--------|----------------|-------------------------------|
| POST   | `/api/chat`    | Chat with AI assistant        |
| POST   | `/api/agent`   | Direct agent invocation       |

---

## 🎨 UI Design

Split-screen layout with dual interaction modes:

```
┌─────────────────────────────────────────┐
│            AI-CRM HCP Navbar            │
├────────────────────┬────────────────────┤
│   Traditional Form │   AI Assistant     │
│                    │                    │
│ • Doctor Search    │ • Chat Interface   │
│ • Date / Type      │ • Suggested Actions│
│ • Topics           │ • Entity Extraction│
│ • Materials List   │ • Auto-fill Form   │
│ • Samples List     │ • Tool Indicators  │
│ • Sentiment        │ • Typing Animation │
│ • Outcome          │                    │
│ • Follow-up        │                    │
│ • [Save] [Reset]   │ • [Send] [Clear]   │
└────────────────────┴────────────────────┘
```

---

## 🔮 Future Improvements

- Voice-to-text interaction logging
- Live entity extraction while typing
- Confidence scores for extracted fields
- Conversation history sidebar
- AI-generated follow-up reminders
- Audit log showing what the AI changed
- Dashboard with analytics and charts
- Multi-language support
- Offline mode with sync
- Export to PDF/Excel

---

## 📄 License

MIT
