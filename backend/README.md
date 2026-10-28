# AI Career Engine (Agent-Driven Career Platform)

An agentic AI architecture designed to provide continuous, explainable, and precise career guidance, skill gap analysis, course sequencing, opportunity matching, and industry intelligence.

---

## 🏛️ Agent Architecture

```
                         USER PROFILE
                              │
                    ┌─────────▼─────────┐
                    │  AGENT ORCHESTRATOR │
                    └─────────┬─────────┘
                              │
       ┌──────────┬───────────┼───────────┬───────────┐
       ▼          ▼           ▼           ▼           ▼
   CAREER      SKILL       LEARNING   OPPORTUNITY  INDUSTRY
   RESEARCH   ANALYSIS       AGENT       AGENT    INTELLIGENCE
     AGENT       AGENT                                   AGENT
       │          │           │           │              │
       └──────────┴───────────┼───────────┴──────────────┘
                              ▼
                    PROFILE INTELLIGENCE
                           AGENT
                              │
                              ▼
                       SHARED STATE
```

---

## ⚙️ Core Design Principle: Agent Orchestration + Deterministic Engines

Agents decide what intelligence to request and format explanations, while **deterministic engines** execute exact numerical computations:

1. **`SkillAnalysisAgent`** → Delegates to **`SkillGapEngine`** & **`SkillEngine`**
2. **`CareerResearchAgent`** → Delegates to **`MarketEngine`** & evidence documents
3. **`LearningAgent`** → Delegates to **`RecommendationEngine`** for sequenced step generation
4. **`OpportunityAgent`** → Delegates to **`MatchingEngine`** for sub-scores & explainable matching
5. **`IndustryIntelligenceAgent`** → Delegates to **`MarketEngine`** for real skill trends
6. **`ProfileIntelligenceAgent`** → Delegates to **`ReadinessEngine`** & **`RoadmapEngine`**

The LLM layer is intentionally thin. SAP HANA and the deterministic engines produce a compact verified fact pack first, then the six overview perspectives run in parallel:

| Perspective | Default model |
|-------------|---------------|
| Technical Analysis | `gemini-3.7-flash` |
| Career Analysis | `gemini-3.7-flash` |
| Industry Analysis | `gemini-3.7-flash` |
| Learning Analysis | `gemini-3.7-flash` |
| Opportunity Analysis | `gemini-3.7-flash` |
| Profile Analysis | `gemini-3.7-flash` |

Set `GEMINI_THINKING_LEVEL=low` for the fastest interactive dashboard experience, or raise it to `medium`/`high` when deeper synthesis matters more than latency.

---

## 🚀 Running the Engine

### Run Demo CLI
```bash
python demo.py
```

### Run Unit Tests
```bash
python -m unittest discover -s tests
```

---

## 🔒 Protected Career Gap Policy
Career interruptions marked as `protected: true` (such as family care, medical, or parental leave) are explicitly isolated in `MatchingEngine` and `ReadinessEngine` so that candidate score metrics are never penalized.

---

## 🗄️ SAP HANA Cloud Integration

The AI Career Engine supports two data modes:

| Mode | Config | Data Source | Use Case |
|------|--------|-------------|----------|
| **JSON** (default) | `DATA_SOURCE=json` | `data/*.json` test fixtures | Local dev, unit tests, demos |
| **HANA** | `DATA_SOURCE=hana` | SAP HANA Cloud | Production, real ONET/ESCO/SKILLBRIDGE data |

### Architecture

```
Agent Orchestrator
       │
       ▼
   DataService  ──── data_source="json" ──→  data/*.json files
       │
       └──── data_source="hana" ──→  Repository Layer
                                        ├── ONetRepository      → ONET schema
                                        ├── ESCORepository      → ESCO schema
                                        └── SkillBridgeRepository → SYNTHETIC schema
                                                    │
                                               SAP HANA Cloud
```

All deterministic engines (SkillGapEngine, MatchingEngine, ReadinessEngine, etc.) remain **unchanged** — they receive data from the DataService layer regardless of source.

---

### Setup: SAP HANA Cloud Connection

#### 1. Install Dependencies

```bash
cd ai-career-engine
pip install -r requirements.txt
```

This installs `hdbcli` (SAP HANA Python client) and `python-dotenv`.

#### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your SAP HANA Cloud credentials:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Gemini API key for resume parsing and six-perspective synthesis | `AIza...` |
| `LLM_PROVIDER` | Primary LLM provider | `gemini` |
| `LLM_MODEL` | Default model for the overview layer | `gemini-3.7-flash` |
| `GEMINI_THINKING_LEVEL` | Gemini reasoning effort for low-latency synthesis | `low` |
| `LLM_PARALLEL_REQUESTS` | Max concurrent perspective calls | `6` |
| `HANA_HOST` | SAP HANA Cloud hostname | `your-host.hanacloud.ondemand.com` |
| `HANA_PORT` | Connection port | `443` |
| `HANA_USER` | Database user | `DBADMIN` |
| `HANA_PASSWORD` | Database password | `your-password` |
| `HANA_ENCRYPT` | Enable TLS encryption | `true` |
| `DATA_SOURCE` | Data mode toggle | `json` or `hana` |
| `ENABLE_LLM_SYNTHESIS` | Enable Gemini synthesis without a per-request override | `true` |

> ⚠️ **Never commit `.env`** — it is already in `.gitignore`.

#### 3. Test the Connection

```bash
python test_hana.py
```

Expected output:
```
===========================================================
  SAP HANA Cloud Connectivity Test
===========================================================

[*] Testing SAP HANA Cloud connection...

[OK] Connected successfully!
     User:    DBADMIN
     Schema:  ...
     Version: ...

[*] Testing schema access...
     ONET.OCCUPATION_DATA: 1016 rows
     ESCO.SKILLS: 13890 rows
     SYNTHETIC.CANDIDATES: 500 rows
```

#### 4. Run in HANA Mode

Set `DATA_SOURCE=hana` in your `.env` file, then:

```bash
python demo.py
```

The orchestrator will automatically fetch candidates, jobs, courses, and occupational data from SAP HANA Cloud instead of JSON files.

#### 5. Run Tests

```bash
# All tests (HANA tests auto-skip if credentials missing)
python -m pytest tests/ -v

# Specific test suites
python -m pytest tests/test_hana_connection.py -v
python -m pytest tests/test_onet_repository.py -v
python -m pytest tests/test_esco_repository.py -v
python -m pytest tests/test_skillbridge_repository.py -v
python -m pytest tests/test_data_service.py -v
```

---

### HANA Schemas

The following schemas must be available in SAP HANA Cloud:

| Schema | Tables | Description |
|--------|--------|-------------|
| `ONET` | `OCCUPATION_DATA`, `ESSENTIAL_SKILLS`, `TRANSFERABLE_SKILLS`, `KNOWLEDGE`, `ABILITIES`, `WORK_ACTIVITIES` | O*NET v31.0 occupational data |
| `ESCO` | `SKILLS`, `OCCUPATIONS`, `OCCUPATION_SKILL_RELATIONS`, `SKILL_SKILL_RELATIONS`, `SKILLS_HIERARCHY`, `ISCO_GROUPS` | ESCO v1.2.1 classification data |
| `SYNTHETIC` | `CANDIDATES`, `CANDIDATE_SKILLS`, `JOBS`, `JOB_SKILLS`, `COURSES` | Project-specific candidates, jobs, and courses |

