# SkillBridge AI Career Engine — Multi-Agent Orchestrator

The AI Career Engine is an enterprise multi-agent reasoning system that calibrates candidate qualifications, calculates role alignment, pinpoints skill gaps, and synthesizes adaptive learning roadmaps.

---

## 🏛️ Architecture Overview

The engine executes a coordinated 6-agent sequential pipeline:

```text
[ Candidate Resume ] 
       │
       ▼
[ Resume Extraction Engine ] ──> Candidate Profile Schema
       │
       ▼
[ DataService (In-Memory RAG Layer) ] ──> Target Roles & Curricula
       │
       ▼
[ AgentOrchestrator ]
  ├── 1. Profile Intelligence Agent
  ├── 2. Skill Gap Analysis Agent
  ├── 3. Industry Intelligence Agent
  ├── 4. Career Research Agent
  ├── 5. Learning & Curriculum Agent
  └── 6. Opportunity Matching Agent
       │
       ▼
[ Calibrated Readiness & Multi-Agent Consensus ]
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY
```

### 3. Run FastAPI Backend
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📡 API Endpoints

- `GET /api/health` — Health and system status
- `POST /api/parse-resume` — Extracts skills and education from PDF/DOCX resumes
- `POST /api/analyze-career` — Runs the full multi-agent career reasoning pipeline
- `WS /ws/gd/{room_id}` — Placement GD room real-time turn sync and WebRTC audio signaling
- `WS /ws/code-arena/{room_id}` — Real-time Monaco collaborative code synchronization

---

## 🧪 Testing

Run automated tests:
```bash
pytest tests/ -v
```
