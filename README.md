# CivicFix AI 🏙️

> **"From Citizen Report → Verified Action → Resolution"**

CivicFix AI is an **autonomous civic action platform** powered by a multi-agent AI architecture. Citizens report civic issues; AI agents understand, validate, prioritize, route, monitor, and verify resolution — automatically.

---

## 🎯 What Makes It Different

| Feature | Description |
|---|---|
| **Multi-Agent AI** | 10 specialized LangGraph agents collaborate on every complaint |
| **Multimodal Input** | Text, image, and voice reports |
| **Geospatial Intelligence** | Location-aware routing and hotspot detection |
| **Duplicate Detection** | Multiple citizen reports become one actionable civic task |
| **Explainable Priority** | AI explains *why* an issue is urgent |
| **Intelligent Routing** | AI routes to the correct department |
| **SLA Monitoring** | Automated escalation when deadlines are missed |
| **Resolution Verification** | AI compares before/after images to verify resolution |
| **MCP Architecture** | Standardized tool access via Model Context Protocol |
| **Closed-Loop Autonomy** | Complaint → Understand → Verify → Prioritize → Route → Act → Monitor → Verify |

---

## 🏗️ Architecture

```
Citizen Report (Text / Image / Voice)
          │
          ▼
    FastAPI Backend
          │
          ▼
   LangGraph Supervisor
    ┌─────┴──────────────────────────────────┐
    │ Intake → Vision → Location → Validate  │
    │ → Duplicate → Priority → Route → Act   │
    │ → Monitor → Verify Resolution           │
    └─────────────────────────────────────────┘
          │
          ▼
     MCP Tool Layer
  ┌───────────────────┐
  │ Maps / GIS        │
  │ Civic Database    │
  │ Notifications     │
  │ Policy Engine     │
  │ Analytics         │
  └───────────────────┘
          │
          ▼
    SQLite (dev) / PostgreSQL + PostGIS (prod)
```

---

## 🗂️ Project Structure

```
civicfix-ai/
├── frontend/               # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route-level pages
│   │   ├── layouts/        # Layout wrappers
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API clients (Axios)
│   │   ├── store/          # State management
│   │   └── utils/          # Helpers
│   └── package.json
│
├── backend/                # FastAPI + SQLAlchemy + LangGraph
│   ├── app/
│   │   ├── api/            # REST API routers
│   │   ├── core/           # Config, DB, security
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic services
│   │   ├── agents/         # Individual LangGraph agents
│   │   ├── graph/          # LangGraph supervisor + state
│   │   ├── gis/            # GIS service abstraction
│   │   ├── mcp/            # MCP client + server interfaces
│   │   ├── workers/        # Background task workers
│   │   └── main.py         # FastAPI entry point
│   ├── migrations/         # Alembic migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── mcp-servers/            # Standalone MCP tool servers
│   ├── maps/
│   ├── civic/
│   ├── notification/
│   ├── policy/
│   └── analytics/
│
├── database/
│   ├── migrations/         # Additional SQL migrations
│   └── seed/               # Demo seed data
│
├── tests/                  # All tests (unit + integration + API)
├── docker/                 # Docker helper configs
├── docs/                   # Technical documentation
│   ├── architecture.md
│   ├── database.md
│   ├── agents.md
│   ├── mcp.md
│   ├── gis.md
│   ├── api.md
│   └── demo.md
│
├── .env.example            # Environment variable template
├── docker-compose.yml      # Full stack orchestration
└── README.md
```

---

## ⚡ Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/civicfix-ai.git
cd civicfix-ai
cp .env.example .env
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

Development and test startup seeds civic departments, sample complaints, and demo accounts. Demo accounts use `password123` and are for local development only:

- Citizen: `citizen@demo.civicfix.ai`
- Civic officer: `officer@demo.civicfix.ai`
- Administrator: `admin@demo.civicfix.ai`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5173

### 4. Health Check

```bash
curl http://localhost:8000/api/health
# → {"status":"ok","service":"CivicFix AI","version":"1.0.0"}
```

---

## 🐳 Docker (Full Stack)

```bash
# Quick start with SQLite (development)
docker compose up --build

# Production with PostgreSQL + PostGIS. Set POSTGRES_PASSWORD to a URL-safe
# strong password and JWT_SECRET to a separate strong random value in .env.
docker compose -f docker-compose.yml -f docker-compose.production.yml --profile production up --build
```

The SQLite database uses its own volume and does not mask application files. The production compose overlay switches the backend to PostgreSQL, waits for the database health check, and requires production secrets. Demo users and sample complaints are not created in production.

---

## 🗄️ Database Configuration

### SQLite (Default — Zero Config)

```env
DATABASE_URL=sqlite:///./civicfix.db
DATABASE_MODE=sqlite
```

### PostgreSQL + PostGIS (Production)

Use a `postgresql+psycopg://<user>:<URL-encoded-password>@<host>:5432/civicfix` connection URL.

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/civicfix
DATABASE_MODE=postgresql
```

Enable PostGIS extension:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

---

## 🤖 AI Configuration

### Demo Mode (No API Key Required)

```env
AI_PROVIDER=mock
AI_MODE=mock
```

### OpenAI (GPT-4o with Vision)

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

### Google Gemini

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIza...
GOOGLE_MODEL=gemini-1.5-pro
```

### Groq

```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk-...
GROQ_MODEL=openai/gpt-oss-120b
```

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v

# Specific test suites
pytest tests/test_health.py -v
pytest tests/test_auth.py -v
pytest tests/test_complaints.py -v
pytest tests/test_agents.py -v
```

---

## 📚 Documentation

| Document | Description |
|---|---|
| [Architecture](docs/architecture.md) | System architecture overview |
| [Database](docs/database.md) | Database schema and design |
| [Agents](docs/agents.md) | LangGraph multi-agent system |
| [MCP](docs/mcp.md) | Model Context Protocol integration |
| [GIS](docs/gis.md) | Geospatial features |
| [API](docs/api.md) | REST API reference |
| [Demo](docs/demo.md) | Demo scenario walkthrough |
| [Vercel Deployment](docs/VERCEL_DEPLOYMENT.md) | Fullstack Vercel deployment guide |
| [Interview Guide](docs/CIVICFIX_AI_Interview_Guide.md) | Comprehensive interview prep & Q&A |

---

## 🚀 Build Phases

| Phase | Description | Status |
|---|---|---|
| 1 | Project Foundation | ✅ Complete |
| 2 | Authentication & RBAC | ✅ Complete |
| 3 | Citizen Reporting | ✅ Complete |
| 4 | AI Intake & Multimodal | ✅ Complete |
| 5 | LangGraph Multi-Agent | ✅ Complete |
| 6 | Geospatial Intelligence | ✅ Complete |
| 7 | Duplicate Detection | ✅ Complete |
| 8 | Priority & Severity Engine | ✅ Complete |
| 9 | Department Routing | ✅ Complete |
| 10 | MCP Tool Layer | ✅ Complete |
| 11 | Civic Officer Dashboard | ✅ Complete |
| 12 | SLA Monitoring & Escalation | ✅ Complete |
| 13 | Resolution Verification | ✅ Complete |
| 14 | Notifications | ✅ Complete |
| 15 | Analytics & Hotspots | ✅ Complete |
| 16 | Admin Dashboard | ✅ Complete |
| 17 | Testing | ✅ Complete |
| 18 | Docker & Deployment | ✅ Complete |
| 19 | Seed Data | ✅ Complete |
| 20 | Final Integration | ✅ Complete |

---

## 👥 User Roles

| Role | Capabilities |
|---|---|
| **Citizen** | Submit complaints, track status, view resolution |
| **Civic Officer** | View assigned tasks, update status, upload evidence |
| **Admin** | Manage all entities, analytics, system config |

---

## 🔒 Security

- JWT authentication (HS256)
- bcrypt password hashing
- Role-based access control (RBAC)
- Input validation via Pydantic
- File upload validation
- Rate limiting
- CORS configuration
- Audit logging
- No secrets in source code

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
