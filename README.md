# SkillBridge

> **Enterprise AI Career Calibration & Technical Placement Arena**

SkillBridge is a unified career acceleration and placement readiness platform designed for engineering candidates, universities, and enterprise hiring pipelines. It bridges the gap between candidate qualifications and industry benchmarks through multi-agent career reasoning, real-time WebRTC group discussions, collaborative coding arenas, and adaptive technical assessments.

---

## 🏛️ System Architecture

The repository is structured into two decoupled, production-ready modules:

```text
Skill_Bridge/
├── backend/                  # FastAPI Application & AI Multi-Agent Orchestrator
│   ├── agents/               # Domain-specific reasoning agents
│   ├── api/                  # FastAPI REST endpoints & WebSocket handlers
│   ├── config/               # Settings & environment variables
│   ├── data/                 # Benchmark taxonomies & mock fixtures
│   ├── database/             # SAP HANA Cloud & local data connector
│   ├── engines/              # Vector retrieval & resume parsing engines
│   ├── orchestrator/         # Multi-agent workflow orchestrator
│   ├── Dockerfile            # Production Python container specification
│   ├── requirements.txt      # Backend Python dependencies
│   └── .env.example          # Environment configuration template
│
├── frontend/                 # Next.js 16 Client & Real-Time Arenas
│   ├── src/
│   │   ├── app/
│   │   │   ├── careerarena/  # Resume parsing & AI career calibration
│   │   │   ├── skillsarena/  # GD Room, Code Arena, and Aptitude Arena
│   │   │   ├── components/   # UI components & interactive simulators
│   │   │   └── utils/        # Dynamic API & WebSocket resolvers
│   ├── public/               # Static assets & icons
│   ├── Dockerfile            # Production Node container specification
│   ├── package.json          # Frontend dependencies & build scripts
│   └── .env.example          # Client environment configuration
│
├── docker-compose.yml        # Orchestration for containerized deployment
├── .env.example              # Unified root environment template
├── .gitignore                # Production git ignore rules
└── README.md                 # System documentation
```

---

## 🌟 Core Modules

### 1. CareerArena
- **Resume Parsing & Skill Extraction:** Automatically extracts technical competencies, work history, and academic projects from PDF and DOCX resumes.
- **Multi-Agent Alignment Pipeline:** Orchestrates multi-agent reasoning to evaluate readiness, calculate role compatibility, and identify critical competency gaps.
- **Smart Semantic Matching:** Calibrates candidate skills against verified industry benchmarks across software engineering, data science, DevOps, and cloud architectures.
- **Adaptive Curriculum Roadmaps:** Generates prioritized learning paths with curated courses and targeted milestone projects.

### 2. Placement GD Room (SkillsArena)
- **Live Human Voice Mesh (WebRTC):** Employs an ultra-low latency peer-to-peer WebRTC audio mesh (`stun:stun.l.google.com:19302`) streaming real candidate audio directly between participants without artificial speech synthesis.
- **Automated Turn Management:** Enforces individual speaking turns and open floor discussion phases with synchronized countdown timers.
- **Real-Time Transcription:** Continuous Web Speech API transcription capturing candidate arguments for post-session analytics.
- **Multi-Candidate Presence:** Real-time participant state synchronization over WebSockets (`/ws/gd/{room_id}`).

### 3. Code Arena (SkillsArena)
- **Real-Time Collaborative Coding:** Simultaneous multi-candidate code editing powered by Monaco Editor with instant operational synchronization across peers.
- **Multi-Language Support:** First-class syntax support and execution environments for Python, JavaScript, Java, and C++.
- **Live Room Synchronization:** Code changes, language changes, candidate cursor presence, and terminal output synchronize in real-time across all joined peers via WebSockets (`/ws/code-arena/{room_id}`).
- **Interactive Workspace Chat:** Integrated chat sidebar allowing participants to communicate during pairing sessions.

### 4. Aptitude Arena (SkillsArena)
- **Timed Assessment Rounds:** Interactive problem sets covering quantitative aptitude, logical reasoning, and core computing fundamentals.
- **Instant Readiness Calibration:** Score calculation and immediate feedback integrated into the candidate's career readiness profile.

---

## 🚀 Quick Start (Docker Deployment)

The fastest way to deploy the complete SkillBridge stack is using Docker Compose:

### 1. Clone & Configure
```bash
git clone https://github.com/your-username/Skill_Bridge.git
cd Skill_Bridge

# Copy and configure environment variables
cp .env.example .env
cp backend/.env.example backend/.env
```

### 2. Launch Services
```bash
docker-compose up --build
```

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 💻 Manual Development Setup

If running locally without Docker:

### Backend Setup (Python 3.11+)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run FastAPI development server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup (Node.js 20+)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Run Next.js development server
npm run dev
```

The application will be accessible at [http://localhost:5173](http://localhost:5173).

---

## 📡 API Reference & WebSocket Protocols

| Endpoint | Protocol | Purpose |
| :--- | :--- | :--- |
| `GET /api/health` | HTTP | Service health and component status check |
| `POST /api/parse-resume` | HTTP | Extract skills, education, and credentials from resume file |
| `POST /api/analyze-career` | HTTP | Execute multi-agent career readiness and RAG pipeline |
| `GET /api/gd-rooms` | HTTP | List active GD rooms and participant counts |
| `POST /api/gd-rooms` | HTTP | Create a new GD session room |
| `GET /api/gd-rooms/{rid}/state` | HTTP | Fetch room state snapshot with participant presence heartbeat |
| `POST /api/gd-rooms/{rid}/speak` | HTTP | Record candidate speech argument to transcript history |
| `WS /ws/gd/{room_id}` | WebSocket | GD room presence, speaking turns, and WebRTC audio signaling |
| `GET /api/code-arena/rooms` | HTTP | List active collaborative code rooms |
| `POST /api/code-arena/rooms` | HTTP | Create a new collaborative code room |
| `POST /api/code-arena/run` | HTTP | Execute code snippet (Python, JS, Java, C++) |
| `WS /ws/code-arena/{room_id}` | WebSocket | Real-time code sync, language sync, and collaborative chat |

---

## 🔐 Environment Variables

Key configuration variables defined in `.env`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | AI provider (`gemini`, `nvidia`, `openai`) | `gemini` |
| `GEMINI_API_KEY` | Google Gemini API key for career reasoning | `None` |
| `DATA_SOURCE` | Storage backend (`json` for fixtures, `hana` for Cloud) | `json` |
| `HANA_HOST` | SAP HANA Cloud host instance | `None` |
| `NEXT_PUBLIC_API_BASE` | Frontend API base URL | `http://localhost:8000` |

---

## 🛡️ Production Verification & Quality

- **Type Safety:** Full TypeScript verification across all frontend components (`npx tsc --noEmit`).
- **Python Compilation:** Verified bytecode compilation across all backend modules (`python -m py_compile`).
- **WebRTC Peer Mesh:** Audio-only WebRTC peer connections with automated cleanup on participant departure.
- **Resilience:** Graceful fallbacks for both database queries and LLM reasoning engines.

---

## 📄 License
This project is licensed under the MIT License.
