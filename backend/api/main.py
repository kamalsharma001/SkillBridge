import sys
import os
import tempfile
import logging
import csv
import subprocess
import random
import time
import json
from typing import Dict, Any, List, Optional

# Add the parent directory (ai-career-engine) to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

def sanitize_profile(cand: dict) -> dict:
    if "skills" in cand and isinstance(cand["skills"], list):
        for s in cand["skills"]:
            if isinstance(s, dict):
                try:
                    prof = float(s.get("proficiency", 0.0))
                    if prof > 1.0: prof = prof / 100.0 if prof <= 100.0 else 1.0
                    if prof < 0.0: prof = 0.0
                    s["proficiency"] = prof
                except Exception:
                    s["proficiency"] = 0.5
                
                try:
                    s["experience_months"] = int(float(s.get("experience_months", 0)))
                except Exception:
                    s["experience_months"] = 0
                    
    if "experience_years" in cand:
        try:
            cand["experience_years"] = float(cand["experience_years"])
        except Exception:
            cand["experience_years"] = 0.0
            
    if isinstance(cand.get("projects"), list):
        valid_projects = []
        for p in cand["projects"]:
            if isinstance(p, dict):
                valid_projects.append(p)
        cand["projects"] = valid_projects
    else:
        cand["projects"] = []
        
    if not isinstance(cand.get("education"), list):
        cand["education"] = [str(cand.get("education"))] if cand.get("education") else []
    else:
        cand["education"] = [str(e) for e in cand["education"] if e]
        
    if isinstance(cand.get("certifications"), list):
        cand["certifications"] = [str(c) for c in cand["certifications"] if c]
    else:
        cand["certifications"] = []
        
    if isinstance(cand.get("courses_completed"), list):
        cand["courses_completed"] = [str(c) for c in cand["courses_completed"] if c]
    else:
        cand["courses_completed"] = []
        
    return cand

from orchestrator.agent_orchestrator import AgentOrchestrator
from services.llm_service import LLMService
from api.resume_parser import parse_resume_to_profile
from config.settings import Settings

app = FastAPI(title="SkillBridge AI Career Engine API")

# Allow all origins for seamless single-port frontend (5173) and tablet access
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    candidate: Dict[str, Any]
    target_role: str
    include_llm_reasoning: Optional[bool] = None
    model: Optional[str] = None
    agent: Optional[str] = None

class RunCodeRequest(BaseModel):
    language: str
    code: str

class GDEvaluateRequest(BaseModel):
    topic: str
    transcript: str

class GDRoomJoinRequest(BaseModel):
    participant_id: str
    name: str
    avatar: Optional[str] = None

class GDRoomLeaveRequest(BaseModel):
    participant_id: str

class GDRoomSpeakRequest(BaseModel):
    participant_id: str
    name: str
    text: str
    audio_data: Optional[str] = None

class CodeRoomJoinRequest(BaseModel):
    participant_id: str
    name: str
    avatar: Optional[str] = None

class CodeRoomLeaveRequest(BaseModel):
    participant_id: str

class CodeRoomSyncRequest(BaseModel):
    participant_id: str
    client_id: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None
    challenge_id: Optional[str] = None

class CodeRoomRunRequest(BaseModel):
    participant_id: str
    name: Optional[str] = "Collaborator"
    code: Optional[str] = None
    language: Optional[str] = None

class CodeRoomChatRequest(BaseModel):
    participant_id: str
    name: str
    text: str

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Extracts text from PDF/DOCX and uses LLM to structure into CandidateProfile."""
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    max_size = 5 * 1024 * 1024
    temp_path = ""
    try:
        content = await file.read(max_size + 1)
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="Resume file must be 5MB or smaller")

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as buffer:
            buffer.write(content)
            temp_path = buffer.name
            
        # Parse resume to structured CandidateProfile dict
        llm_service = LLMService()
        structured_profile = await parse_resume_to_profile(temp_path, llm_service)
        structured_profile = sanitize_profile(structured_profile)
        
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            
        return {"profile": structured_profile}
        
    except HTTPException:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        raise
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        logging.error(f"Resume parsing failed: {e}")
        raise HTTPException(status_code=400, detail="Resume parsing failed. Please ensure the file is a valid PDF or DOCX with readable text.")

@app.post("/api/analyze-career")
async def analyze_career(request: AnalyzeRequest):
    """Runs the 6-agent AI pipeline for the provided candidate profile."""
    from database.data_service import DataService
    data_source = os.getenv("DATA_SOURCE", "json")
    data_service = DataService(data_source=data_source)
    orchestrator = AgentOrchestrator(data_service=data_service)
    
    # Format context for orchestrator
    context = {
        "candidate": sanitize_profile(request.candidate),
        "target_role": {"name": request.target_role},
    }
    if request.include_llm_reasoning is not None:
        context["include_llm_reasoning"] = request.include_llm_reasoning
    if request.model is not None:
        context["llm_model"] = request.model
    if request.agent is not None and request.agent != "all":
        # Run only the selected Python agent and return its result
        try:
            single = await orchestrator.run_single_agent_async(request.agent, context)
            return {"success": True, "data": single}
        except Exception as e:
            logging.error(f"Single agent execution failed, falling back to full pipeline: {e}")
    
    try:
        result = await orchestrator.run_career_pipeline_async(context)
        return {"success": True, "data": result}
    except Exception as e:
        logging.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# ==============================================================================
# INTEGRATED PLACEMENT ARENA ENDPOINTS (PORT 8000 UNIFIED BACKEND)
# ==============================================================================

def execute_code_payload(lang: str, code: str) -> dict:
    """Executes Python, JavaScript (Node.js), Java (OpenJDK 21), or C++ (g++) safely with a timeout."""
    lang = lang.lower().strip()
    code = code or ""
    
    if not code.strip():
        return {"ok": False, "output": "No code provided to execute."}

    if lang in ("python", "py"):
        ext = ".py"
        cmd = [sys.executable]
    elif lang in ("javascript", "js", "node"):
        ext = ".js"
        cmd = ["node"]
    elif lang in ("java",):
        ext = ".java"
        cmd = ["java"]
    elif lang in ("cpp", "c++"):
        ext = ".cpp"
        cmd = None
    else:
        return {"ok": False, "output": f"Unsupported language: {lang}. Choose Python, JavaScript, Java, or C++."}

    with tempfile.TemporaryDirectory() as tmpdir:
        # Java requires Main.java matching class name
        filename = "Main.java" if lang == "java" else f"solution{ext}"
        code_file = os.path.join(tmpdir, filename)
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)

        if lang in ("cpp", "c++"):
            exe_file = os.path.join(tmpdir, "solution.exe" if sys.platform == "win32" else "solution")
            try:
                compile_res = subprocess.run(
                    ["g++", code_file, "-o", exe_file],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if compile_res.returncode != 0:
                    return {"ok": False, "output": f"Compilation Error:\n{compile_res.stderr or compile_res.stdout}"}
                cmd = [exe_file]
            except FileNotFoundError:
                return {"ok": False, "output": "g++ compiler not found on this system. Please test with Python, JavaScript, or Java."}

        try:
            exec_args = cmd if lang in ("cpp", "c++") else cmd + [code_file]
            exec_res = subprocess.run(
                exec_args,
                capture_output=True,
                text=True,
                timeout=8,
            )
            out = (exec_res.stdout + ("\n" + exec_res.stderr if exec_res.stderr else "")).strip()
            return {"ok": exec_res.returncode == 0, "output": out or "[Execution completed with no output]"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "output": "Execution timed out (8-second safety limit reached)."}
        except Exception as e:
            return {"ok": False, "output": f"Execution error: {str(e)}"}

@app.post("/api/run-code")
async def run_code(req: RunCodeRequest):
    """Executes Python, JavaScript (Node.js), Java (OpenJDK), or C++ (g++) safely with a timeout."""
    return execute_code_payload(req.language, req.code)

@app.get("/api/aptitude-questions")
async def get_aptitude_questions(count: int = 15, shuffle: bool = True):
    """Returns curated aptitude questions parsed from 100-question CSV bank, randomly sampled."""
    csv_candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "arena-backend", "data", "aptitude_quiz.csv"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "aptitude_quiz.csv"),
    ]
    
    questions = []
    for csv_path in csv_candidates:
        if os.path.exists(csv_path):
            try:
                with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        q_text = row.get("question", "").strip()
                        if not q_text:
                            continue
                        ans = (row.get("correct_answer") or "a").lower().strip()
                        expl = row.get("explanation") or f"Option {ans.upper()} is correct according to standard aptitude derivations."
                        questions.append({
                            "id": row.get("id") or f"Q{len(questions)+1}",
                            "category": row.get("category", "General"),
                            "difficulty": row.get("difficulty", "Medium"),
                            "question": q_text,
                            "options": [
                                row.get("option_a", ""),
                                row.get("option_b", ""),
                                row.get("option_c", ""),
                                row.get("option_d", ""),
                            ],
                            "correctIndex": 0 if ans == "a" else (1 if ans == "b" else (2 if ans == "c" else 3)),
                            "explanation": expl
                        })
                if questions:
                    break
            except Exception as e:
                logging.warning(f"Failed to read CSV questions: {e}")

    # Fallback built-in question set if CSV not found
    if not questions:
        questions = [
            {
                "id": "Q001",
                "category": "Quantitative Aptitude",
                "difficulty": "Easy",
                "question": "A shopkeeper sells an item for Rs. 460 after giving an 8% discount on marked price. What is the marked price?",
                "options": ["Rs. 500", "Rs. 510", "Rs. 520", "Rs. 490"],
                "correctIndex": 0,
                "explanation": "Marked Price = Selling Price / (1 - Discount%) = 460 / 0.92 = Rs. 500."
            },
            {
                "id": "Q002",
                "category": "Logical Reasoning",
                "difficulty": "Easy",
                "question": "If 'CAT' is coded as '3120', how is 'DOG' coded using alphabetical positional values (D=4, O=15, G=7)?",
                "options": ["4157", "4715", "7154", "4 15 7"],
                "correctIndex": 0,
                "explanation": "Positional values concatenated: D(4), O(15), G(7) gives 4157."
            },
            {
                "id": "Q003",
                "category": "Verbal Ability",
                "difficulty": "Easy",
                "question": "Choose the word that is an exact synonym for 'Benevolent'.",
                "options": ["Cruel", "Kind", "Selfish", "Arrogant"],
                "correctIndex": 1,
                "explanation": "Benevolent means well-meaning and kindly."
            },
            {
                "id": "Q004",
                "category": "Quantitative Aptitude",
                "difficulty": "Medium",
                "question": "A can complete a task in 12 days and B in 18 days. Working together, how many days will they take?",
                "options": ["6.4 days", "7.2 days", "8.0 days", "9.0 days"],
                "correctIndex": 1,
                "explanation": "Combined rate = 1/12 + 1/18 = 5/36. Total days = 36 / 5 = 7.2 days."
            },
            {
                "id": "Q005",
                "category": "Logical Reasoning",
                "difficulty": "Medium",
                "question": "In a row of children, Ravi is 7th from the left and 12th from the right. How many children are there in total?",
                "options": ["18", "19", "20", "17"],
                "correctIndex": 0,
                "explanation": "Total = (Left Position + Right Position) - 1 = (7 + 12) - 1 = 18."
            }
        ]

    total_pool = len(questions)
    if shuffle and count > 0 and count < total_pool:
        selected_questions = random.sample(questions, count)
    elif count > 0:
        selected_questions = questions[:count]
    else:
        selected_questions = questions
        
    return {"questions": selected_questions, "total_pool": total_pool}

# ==========================================
# GD ROOMS MANAGER (GD000 - GD999)
# ==========================================
TOTAL_GD_ROOMS = 1000
GD_ROOMS_STATE: Dict[str, dict] = {}

def get_gd_topics_pool() -> List[dict]:
    topics_candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "gd_topics_250.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "gd_topics_250.json"),
    ]
    for p in topics_candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data
            except Exception as e:
                logging.warning(f"Error loading {p}: {e}")
    return [
        {
            "id": "TOPIC001",
            "title": "Generative AI in White-Collar Work: Augmentation vs Job Displacement",
            "category": "Technology, AI & Innovation",
            "starter_pros": "Boosts analytical velocity and routine coding by 10x.",
            "starter_cons": "Threatens junior hiring pipelines and creates IP dilemmas.",
            "key_discussion_points": ["Impact on early-career roles", "Governance and IP", "Retraining balance"],
            "duration_seconds": 600
        }
    ]

def get_or_create_room(room_id: str) -> dict:
    if room_id not in GD_ROOMS_STATE:
        GD_ROOMS_STATE[room_id] = {
            "room_id": room_id,
            "participants": [],
            "status": "waiting",
            "locked_at": None,
            "duration_seconds": 600,
            "topic": None,
            "turn_order": [],
            "current_turn_index": 0,
            "turn_start_time": None,
            "phase": "waiting",
            "transcripts": []
        }
    return GD_ROOMS_STATE[room_id]

def update_room_timing(room: dict):
    if room["status"] != "in_discussion" or not room["locked_at"]:
        return

    now = time.time()
    elapsed = now - room["locked_at"]

    if elapsed >= room["duration_seconds"]:
        room["status"] = "completed"
        room["phase"] = "completed"
        return

    if room["phase"] == "individual_turns":
        active_ids = {p["id"] for p in room["participants"]}
        room["turn_order"] = [tid for tid in room["turn_order"] if tid in active_ids]

        if not room["turn_order"]:
            room["phase"] = "open_discussion"
            return

        turn_start = room.get("turn_start_time") or now
        if now - turn_start >= 60.0:
            room["current_turn_index"] += 1
            room["turn_start_time"] = now

            if room["current_turn_index"] >= len(room["turn_order"]):
                room["phase"] = "open_discussion"

def lock_room_internal(room: dict) -> dict:
    if len(room["participants"]) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 participants required to lock room and begin discussion.")
    
    now = time.time()
    pool = get_gd_topics_pool()
    selected_topic = random.choice(pool)
    
    turn_ids = [p["id"] for p in room["participants"]]
    random.shuffle(turn_ids)
    
    room["status"] = "in_discussion"
    room["locked_at"] = now
    room["topic"] = selected_topic
    room["turn_order"] = turn_ids
    room["current_turn_index"] = 0
    room["turn_start_time"] = now
    room["phase"] = "individual_turns"
    return room

def format_room_response(room: dict) -> dict:
    update_room_timing(room)
    now = time.time()
    
    current_speaker_id = None
    turn_time_left = 0
    total_time_left = 0
    
    if room["status"] == "in_discussion" and room["locked_at"]:
        total_time_left = max(0, int(room["duration_seconds"] - (now - room["locked_at"])))
        
        if room["phase"] == "individual_turns" and room["turn_order"]:
            if room["current_turn_index"] < len(room["turn_order"]):
                current_speaker_id = room["turn_order"][room["current_turn_index"]]
                turn_time_left = max(0, int(60 - (now - (room["turn_start_time"] or now))))

    mapped_participants = []
    for p in room["participants"]:
        pid = p["id"]
        if room["phase"] == "individual_turns":
            is_speaking = (pid == current_speaker_id)
            mic_closed = not is_speaking
        elif room["phase"] == "open_discussion":
            is_speaking = False
            mic_closed = False
        else:
            is_speaking = False
            mic_closed = True
            
        mapped_participants.append({
            "id": pid,
            "name": p["name"],
            "avatar": p.get("avatar", ""),
            "joined_at": p.get("joined_at", now),
            "is_speaking": is_speaking,
            "mic_closed": mic_closed
        })
        
    current_speaker_name = None
    if current_speaker_id:
        speaker_obj = next((p for p in room["participants"] if p["id"] == current_speaker_id), None)
        if speaker_obj:
            current_speaker_name = speaker_obj["name"]

    return {
        "room_id": room["room_id"],
        "status": room["status"],
        "phase": room["phase"],
        "participants_count": len(room["participants"]),
        "max_capacity": 6,
        "participants": mapped_participants,
        "topic": room["topic"],
        "turn_order": room["turn_order"],
        "current_turn_index": room["current_turn_index"],
        "current_speaker_id": current_speaker_id,
        "current_speaker_name": current_speaker_name,
        "turn_time_left": turn_time_left,
        "total_time_left": total_time_left,
        "transcripts": room.get("transcripts", [])[-20:]
    }

class GDRoomConnectionManager:
    """Manages active WebSockets and real-time event broadcasting for GD Placement rooms."""
    def __init__(self):
        # Mapping: room_id -> { WebSocket: { "participant_id": str, "name": str } }
        self.rooms: Dict[str, Dict[WebSocket, dict]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, participant_id: str, name: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][websocket] = {
            "participant_id": participant_id,
            "name": name,
            "joined_at": time.time()
        }

        room = get_or_create_room(room_id)
        now = time.time()
        existing = next((p for p in room["participants"] if p["id"] == participant_id), None)
        if existing:
            existing["name"] = name
            existing["last_seen"] = now
        else:
            if len(room["participants"]) < 6 and room["status"] == "waiting":
                assigned_name = name.strip() or f"Candidate {len(room['participants'])+1}"
                existing_names = [p.get("name", "").lower() for p in room["participants"]]
                if assigned_name.lower() in existing_names:
                    assigned_name = f"{assigned_name} #{len(room['participants'])+1}"

                room["participants"].append({
                    "id": participant_id,
                    "name": assigned_name,
                    "avatar": f"https://api.dicebear.com/7.x/bottts/svg?seed={participant_id}",
                    "joined_at": now,
                    "last_seen": now
                })

        formatted = format_room_response(room)

        # Send full initial room state to newly connected client
        await self.send_to(websocket, {
            "type": "room_state",
            "room_id": room_id,
            "state": formatted
        })

        # Broadcast room_update to all other peers in the room
        await self.broadcast(room_id, {
            "type": "room_update",
            "room_id": room_id,
            "state": formatted,
            "event": "peer_joined",
            "participant_id": participant_id,
            "name": name
        }, exclude=websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        participant_id = None
        if room_id in self.rooms and websocket in self.rooms[room_id]:
            participant_id = self.rooms[room_id][websocket].get("participant_id")
            del self.rooms[room_id][websocket]
            if not self.rooms[room_id]:
                del self.rooms[room_id]

        if room_id in GD_ROOMS_STATE and participant_id:
            room = GD_ROOMS_STATE[room_id]
            if room["status"] == "waiting":
                room["participants"] = [p for p in room["participants"] if p["id"] != participant_id]

    async def send_to(self, websocket: WebSocket, payload: dict):
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception:
            pass

    async def broadcast(self, room_id: str, payload: dict, exclude: Optional[WebSocket] = None):
        if room_id not in self.rooms:
            return
        dead_sockets = []
        for ws in list(self.rooms[room_id].keys()):
            if ws != exclude:
                try:
                    await ws.send_text(json.dumps(payload))
                except Exception:
                    dead_sockets.append(ws)
        for dead_ws in dead_sockets:
            self.disconnect(dead_ws, room_id)

    async def send_to_peer(self, room_id: str, target_participant_id: str, payload: dict):
        if room_id not in self.rooms:
            return
        for ws, info in list(self.rooms[room_id].items()):
            if info.get("participant_id") == target_participant_id:
                try:
                    await ws.send_text(json.dumps(payload))
                except Exception:
                    pass
                break

gd_manager = GDRoomConnectionManager()

@app.get("/api/gd-topics")
async def get_gd_topics():
    """Returns 250 curated trending Group Discussion topics."""
    pool = get_gd_topics_pool()
    return {"topics": pool, "total": len(pool)}

@app.get("/api/gd-rooms")
async def list_gd_rooms(search: Optional[str] = None, status_filter: Optional[str] = None, page: int = 1, limit: int = 24):
    """Returns directory of GD000-GD999 rooms with real-time occupancy and status."""
    all_room_ids = [f"GD{i:03d}" for i in range(TOTAL_GD_ROOMS)]
    
    if search:
        search_upper = search.upper().strip()
        all_room_ids = [rid for rid in all_room_ids if search_upper in rid]
        
    now = time.time()
    results = []
    for rid in all_room_ids:
        r = get_or_create_room(rid)
        
        # Clean up stale participants who closed browser / refreshed without clean leave in waiting mode
        if r["status"] == "waiting":
            r["participants"] = [
                p for p in r["participants"]
                if (now - p.get("last_seen", p.get("joined_at", now))) < 25.0
            ]
            
        update_room_timing(r)
        
        p_count = len(r["participants"])
        st = r["status"]
        
        if status_filter == "available" and (p_count >= 6 or st != "waiting"):
            continue
        if status_filter == "in_session" and st != "in_discussion":
            continue
        if status_filter == "waiting" and (st != "waiting" or p_count == 0):
            continue
            
        results.append({
            "room_id": rid,
            "participants_count": p_count,
            "max_capacity": 6,
            "status": st,
            "phase": r["phase"],
            "topic_title": r["topic"]["title"] if r["topic"] else None,
            "is_locked": st in ["in_discussion", "completed"],
            "can_join": p_count < 6 and st == "waiting",
            "can_lock": p_count >= 2 and st == "waiting"
        })
        
    total_count = len(results)
    start_idx = (page - 1) * limit
    paged = results[start_idx : start_idx + limit]
    
    return {
        "rooms": paged,
        "total_rooms": total_count,
        "page": page,
        "limit": limit,
        "active_students": sum(len(r["participants"]) for r in GD_ROOMS_STATE.values())
    }

@app.get("/api/gd-rooms/{room_id}/state")
async def get_gd_room_state(room_id: str, participant_id: Optional[str] = None):
    room = get_or_create_room(room_id)
    now = time.time()

    # Heartbeat: refresh last_seen for active participant
    if participant_id:
        for p in room["participants"]:
            if p["id"] == participant_id:
                p["last_seen"] = now
                break

    # Prune stale participants who disconnected/refreshed in waiting phase (>25s inactive)
    if room["status"] == "waiting":
        room["participants"] = [
            p for p in room["participants"]
            if (now - p.get("last_seen", p.get("joined_at", now))) < 25.0
        ]

    return format_room_response(room)

@app.post("/api/gd-rooms/{room_id}/join")
async def join_gd_room(room_id: str, req: GDRoomJoinRequest):
    room = get_or_create_room(room_id)
    now = time.time()
    
    # Prune stale participants if waiting (>25s without heartbeat)
    if room["status"] == "waiting":
        room["participants"] = [
            p for p in room["participants"]
            if (now - p.get("last_seen", p.get("joined_at", now))) < 25.0
        ]
        
    update_room_timing(room)
    
    # If room is in active discussion, allow existing participant to rejoin cleanly
    existing = next((p for p in room["participants"] if p["id"] == req.participant_id), None)
    if room["status"] in ["in_discussion", "completed"]:
        if existing:
            existing["last_seen"] = now
            return format_room_response(room)
        raise HTTPException(status_code=400, detail=f"Room {room_id} is locked for an ongoing discussion.")
    
    if existing:
        existing["name"] = req.name or existing.get("name", "Candidate")
        existing["avatar"] = req.avatar or existing.get("avatar", "")
        existing["last_seen"] = now
    else:
        if len(room["participants"]) >= 6:
            raise HTTPException(status_code=400, detail=f"Room {room_id} is full (6/6 participants max).")
        
        # Each active user is strictly treated as their own entity
        assigned_name = (req.name or "").strip() or f"Candidate {len(room['participants'])+1}"
        existing_names = [p.get("name", "").lower() for p in room["participants"]]
        if assigned_name.lower() in existing_names:
            assigned_name = f"{assigned_name} #{len(room['participants'])+1}"

        room["participants"].append({
            "id": req.participant_id,
            "name": assigned_name,
            "avatar": req.avatar or f"https://api.dicebear.com/7.x/bottts/svg?seed={req.participant_id}",
            "joined_at": now,
            "last_seen": now
        })
    
    # AUTO-LOCK when room limit is full (6 members)!
    if len(room["participants"]) == 6 and room["status"] == "waiting":
        lock_room_internal(room)
        
    resp = format_room_response(room)
    await gd_manager.broadcast(room_id, {
        "type": "room_update",
        "room_id": room_id,
        "state": resp,
        "event": "peer_joined",
        "participant_id": req.participant_id
    })
    return resp

@app.post("/api/gd-rooms/{room_id}/leave")
async def leave_gd_room(room_id: str, req: GDRoomLeaveRequest):
    room = get_or_create_room(room_id)
    update_room_timing(room)
    
    p_id = req.participant_id
    room["participants"] = [p for p in room["participants"] if p["id"] != p_id]
    
    # If leaving during individual turns
    if room["phase"] == "individual_turns":
        if room["current_turn_index"] < len(room["turn_order"]) and room["turn_order"][room["current_turn_index"]] == p_id:
            room["turn_order"] = [tid for tid in room["turn_order"] if tid != p_id]
            room["turn_start_time"] = time.time()
            if room["current_turn_index"] >= len(room["turn_order"]):
                room["phase"] = "open_discussion"
        else:
            room["turn_order"] = [tid for tid in room["turn_order"] if tid != p_id]
            if not room["turn_order"]:
                room["phase"] = "open_discussion"

    if len(room["participants"]) == 0:
        room["status"] = "waiting"
        room["phase"] = "waiting"
        room["locked_at"] = None
        room["topic"] = None
        room["turn_order"] = []
        room["current_turn_index"] = 0
        room["transcripts"] = []

    resp = format_room_response(room)
    await gd_manager.broadcast(room_id, {
        "type": "room_update",
        "room_id": room_id,
        "state": resp,
        "event": "peer_left",
        "participant_id": p_id
    })
    return resp

@app.post("/api/gd-rooms/{room_id}/lock")
async def lock_gd_room(room_id: str):
    room = get_or_create_room(room_id)
    if room["status"] in ["in_discussion", "completed"]:
        return format_room_response(room)
    lock_room_internal(room)
    resp = format_room_response(room)
    await gd_manager.broadcast(room_id, {
        "type": "room_update",
        "room_id": room_id,
        "state": resp,
        "event": "room_locked"
    })
    return resp

@app.post("/api/gd-rooms/{room_id}/speak")
async def speak_in_gd_room(room_id: str, req: GDRoomSpeakRequest):
    room = get_or_create_room(room_id)
    update_room_timing(room)
    
    if room["phase"] == "individual_turns":
        active_speaker = room["turn_order"][room["current_turn_index"]] if room["current_turn_index"] < len(room["turn_order"]) else None
        if active_speaker != req.participant_id:
            raise HTTPException(status_code=403, detail="Your mic is currently closed. Wait for your speaking turn.")
    
    transcript_item = {
        "participant_id": req.participant_id,
        "name": req.name,
        "text": req.text,
        "audio_data": req.audio_data,
        "timestamp": time.time()
    }
    room.setdefault("transcripts", []).append(transcript_item)
    resp = format_room_response(room)
    await gd_manager.broadcast(room_id, {
        "type": "room_update",
        "room_id": room_id,
        "state": resp,
        "event": "speech",
        "participant_id": req.participant_id,
        "name": req.name,
        "text": req.text,
        "audio_data": req.audio_data
    })
    return resp

@app.post("/api/gd-evaluate")
async def evaluate_gd(req: GDEvaluateRequest):
    """Evaluates candidate speaking contribution in a GD session."""
    transcript = (req.transcript or "").strip()
    topic = req.topic or "General Topic"
    
    if len(transcript) < 20:
        return {
            "score": 45,
            "clarity": "Needs more detail",
            "reasoning": "Statement was too brief to demonstrate structured arguments or structured reasoning.",
            "suggestions": "Try structuring your points using the PREP method (Point, Reason, Example, Point).",
            "strengths": ["Initial willingness to participate"]
        }

    # Use LLMService if available for synthesis, else compute structured deterministic rubric
    llm = LLMService()
    if llm.client:
        prompt = (
            f"You are a Senior Corporate HR GD Assessor evaluating a student's speech in a placement Group Discussion.\n"
            f"Topic: {topic}\n"
            f"Candidate transcript:\n{transcript}\n\n"
            f"Provide constructive, professional evaluation in JSON format with keys: "
            f"score (0-100), clarity (string), reasoning (string), strengths (array of 2 strings), suggestions (string)."
        )
        try:
            import json_repair
            res_str = await llm.generate_reasoning_async(prompt, transcript)
            eval_data = json_repair.repair_json(res_str, return_objects=True)
            if isinstance(eval_data, dict) and "score" in eval_data:
                return eval_data
        except Exception as e:
            logging.warning(f"LLM GD evaluation fallback: {e}")

    # Deterministic Assessment Rubric based on length, reasoning words, and structure
    word_count = len(transcript.split())
    has_examples = any(w in transcript.lower() for w in ["for example", "for instance", "such as", "because", "therefore", "evidence", "data"])
    has_balance = any(w in transcript.lower() for w in ["however", "on the other hand", "alternatively", "while", "balance", "perspective"])
    
    score = 65
    if word_count > 60: score += 15
    elif word_count > 30: score += 10
    if has_examples: score += 10
    if has_balance: score += 10
    score = min(95, score)

    return {
        "score": score,
        "clarity": "Good and articulate" if score >= 75 else "Moderate articulation",
        "reasoning": "Demonstrated logical structure with topical relevance." if has_examples else "Good baseline point; backing with concrete real-world examples will elevate your impact.",
        "strengths": [
            "Clear stance directly addressing the topic",
            "Constructive tone suitable for group collaboration"
        ],
        "suggestions": "Add data points or a brief counter-perspective before concluding to showcase balanced critical thinking."
    }

# ==============================================================================
# COLLABORATIVE CODE ARENA ROOMS (CODE000 - CODE499, ZERO TIME LIMIT, 4 LANGUAGES)
# ==============================================================================

CODE_TEMPLATES = {
    "python": """# SkillBridge Collaborative Python Environment
def solve(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []

# Test solution
print("Result:", solve([2, 7, 11, 15], 9))
print("Test 2:", solve([3, 2, 4], 6))
""",
    "javascript": """// SkillBridge Collaborative JavaScript (Node.js) Environment
function solve(nums, target) {
    const seen = new Map();
    for (let i = 0; i < nums.length; i++) {
        const diff = target - nums[i];
        if (seen.has(diff)) return [seen.get(diff), i];
        seen.set(nums[i], i);
    }
    return [];
}

console.log("Result:", solve([2, 7, 11, 15], 9));
console.log("Test 2:", solve([3, 2, 4], 6));
""",
    "java": """// SkillBridge Collaborative Java 21 Environment
import java.util.*;

public class Main {
    public static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
            map.put(nums[i], i);
        }
        return new int[0];
    }

    public static void main(String[] args) {
        int[] nums = {2, 7, 11, 15};
        int[] res = twoSum(nums, 9);
        System.out.println("Result: [" + res[0] + ", " + res[1] + "]");
    }
}
""",
    "cpp": """// SkillBridge Collaborative C++ (MinGW 15) Environment
#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for (int i = 0; i < nums.size(); i++) {
        int diff = target - nums[i];
        if (seen.count(diff)) return {seen[diff], i};
        seen[nums[i]] = i;
    }
    return {};
}

int main() {
    vector<int> nums = {2, 7, 11, 15};
    auto res = twoSum(nums, 9);
    cout << "Result: [" << res[0] << ", " << res[1] << "]" << endl;
    return 0;
}
"""
}

CODE_ROOMS_STATE: Dict[str, dict] = {}
TOTAL_CODE_ROOMS = 500  # CODE000 to CODE499

class CodeRoomConnectionManager:
    """Manages active WebSockets and real-time event broadcasting for Code Arena rooms."""
    def __init__(self):
        # Mapping: room_id -> { WebSocket: { "participant_id": str, "name": str } }
        self.rooms: Dict[str, Dict[WebSocket, dict]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, participant_id: str, name: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][websocket] = {
            "participant_id": participant_id,
            "name": name,
            "joined_at": time.time()
        }
        
        # Ensure room exists and register participant
        room = get_or_create_code_room(room_id)
        now = time.time()
        existing = next((p for p in room["participants"] if p["id"] == participant_id), None)
        if existing:
            existing["name"] = name
            existing["last_seen"] = now
        else:
            if len(room["participants"]) < room["max_capacity"]:
                room["participants"].append({
                    "id": participant_id,
                    "name": name,
                    "avatar": f"https://api.dicebear.com/7.x/bottts/svg?seed={participant_id}",
                    "joined_at": now,
                    "last_seen": now
                })

        # Send full initial room state to newly connected client
        await self.send_to(websocket, {
            "type": "room_state",
            "room_id": room_id,
            "state": room
        })

        # Broadcast peer_joined to others in room
        await self.broadcast(room_id, {
            "type": "peer_joined",
            "room_id": room_id,
            "participant_id": participant_id,
            "name": name,
            "participants": room["participants"]
        }, exclude=websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        participant_id = None
        if room_id in self.rooms and websocket in self.rooms[room_id]:
            participant_id = self.rooms[room_id][websocket].get("participant_id")
            del self.rooms[room_id][websocket]
            if not self.rooms[room_id]:
                del self.rooms[room_id]
                
        # Update participants in room state
        if room_id in CODE_ROOMS_STATE and participant_id:
            room = CODE_ROOMS_STATE[room_id]
            room["participants"] = [p for p in room["participants"] if p["id"] != participant_id]

    async def send_to(self, websocket: WebSocket, payload: dict):
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception:
            pass

    async def broadcast(self, room_id: str, payload: dict, exclude: Optional[WebSocket] = None):
        if room_id not in self.rooms:
            return
        dead_sockets = []
        for ws in list(self.rooms[room_id].keys()):
            if ws != exclude:
                try:
                    await ws.send_text(json.dumps(payload))
                except Exception:
                    dead_sockets.append(ws)
        for dead_ws in dead_sockets:
            self.disconnect(dead_ws, room_id)

code_manager = CodeRoomConnectionManager()

def get_or_create_code_room(room_id: str) -> dict:
    if room_id not in CODE_ROOMS_STATE:
        CODE_ROOMS_STATE[room_id] = {
            "room_id": room_id,
            "title": f"Collaborative Workspace {room_id}",
            "participants": [],
            "max_capacity": 8,
            "language": "python",
            "challenge_id": "two-sum",
            "code": CODE_TEMPLATES["python"],
            "terminal_output": "SkillBridge Collaborative Execution Engine ready.\nSupports Python, JavaScript, Java, and C++.\nClick 'Run Code' to execute across all peer screens.",
            "last_run_status": "success",
            "last_run_by": None,
            "last_run_time": None,
            "created_at": time.time(),
            # No time limit!
            "messages": [
                {
                    "id": "msg_init",
                    "sender_id": "system",
                    "sender_name": "System",
                    "text": f"Collaborative workspace {room_id} initialized. Code and terminal output sync across all connected peers without time limits.",
                    "timestamp": time.time()
                }
            ]
        }
    return CODE_ROOMS_STATE[room_id]

def prune_stale_code_participants(room: dict):
    now = time.time()
    room["participants"] = [
        p for p in room["participants"]
        if (now - p.get("last_seen", p.get("joined_at", now))) < 35.0
    ]

@app.get("/api/code-rooms")
async def list_code_rooms(search: Optional[str] = None, status_filter: Optional[str] = None, page: int = 1, limit: int = 24):
    """Returns directory of CODE000-CODE499 collaborative rooms with live occupancy."""
    all_room_ids = [f"CODE{i:03d}" for i in range(TOTAL_CODE_ROOMS)]
    
    if search:
        search_upper = search.upper().strip()
        all_room_ids = [rid for rid in all_room_ids if search_upper in rid]
        
    results = []
    for rid in all_room_ids:
        if rid in CODE_ROOMS_STATE:
            r = CODE_ROOMS_STATE[rid]
            prune_stale_code_participants(r)
            p_count = len(r["participants"])
            lang = r["language"]
            ch_id = r["challenge_id"]
            title = r["title"]
            last_st = r["last_run_status"]
            max_cap = r["max_capacity"]
        else:
            p_count = 0
            lang = "python"
            ch_id = "two-sum"
            title = f"Collaborative Workspace {rid}"
            last_st = None
            max_cap = 8
            
        if status_filter == "active" and p_count == 0:
            continue
        if status_filter == "available" and p_count >= max_cap:
            continue
            
        results.append({
            "room_id": rid,
            "title": title,
            "participants_count": p_count,
            "max_capacity": max_cap,
            "language": lang,
            "challenge_id": ch_id,
            "last_run_status": last_st,
            "can_join": p_count < max_cap
        })
        
    total_count = len(results)
    start_idx = (page - 1) * limit
    paged = results[start_idx : start_idx + limit]
    
    return {
        "rooms": paged,
        "total_rooms": total_count,
        "page": page,
        "limit": limit,
        "active_coders": sum(len(r["participants"]) for r in CODE_ROOMS_STATE.values())
    }

@app.get("/api/code-rooms/{room_id}/state")
async def get_code_room_state(room_id: str, participant_id: Optional[str] = None):
    room = get_or_create_code_room(room_id)
    now = time.time()
    
    # Heartbeat
    if participant_id:
        for p in room["participants"]:
            if p["id"] == participant_id:
                p["last_seen"] = now
                break
                
    prune_stale_code_participants(room)
    return room

@app.post("/api/code-rooms/{room_id}/join")
async def join_code_room(room_id: str, req: CodeRoomJoinRequest):
    room = get_or_create_code_room(room_id)
    prune_stale_code_participants(room)
    now = time.time()
    
    existing = next((p for p in room["participants"] if p["id"] == req.participant_id), None)
    if existing:
        existing["name"] = req.name or existing.get("name", "Collaborator")
        existing["avatar"] = req.avatar or existing.get("avatar", "")
        existing["last_seen"] = now
    else:
        req_name = (req.name or "").strip()
        same_name = next((p for p in room["participants"] if (p.get("name") or "").strip().lower() == req_name.lower()), None) if req_name else None
        if same_name:
            same_name["id"] = req.participant_id
            same_name["last_seen"] = now
        else:
            if len(room["participants"]) >= room["max_capacity"]:
                raise HTTPException(status_code=400, detail=f"Room {room_id} is full ({room['max_capacity']}/{room['max_capacity']} max).")
            room["participants"].append({
                "id": req.participant_id,
                "name": req.name or f"Coder {len(room['participants'])+1}",
                "avatar": req.avatar or f"https://api.dicebear.com/7.x/bottts/svg?seed={req.participant_id}",
                "joined_at": now,
                "last_seen": now
            })
            
    # Broadcast join event to connected WebSockets
    await code_manager.broadcast(room_id, {
        "type": "peer_joined",
        "room_id": room_id,
        "participants": room["participants"]
    })
    return room

@app.post("/api/code-rooms/{room_id}/leave")
async def leave_code_room(room_id: str, req: CodeRoomLeaveRequest):
    room = get_or_create_code_room(room_id)
    room["participants"] = [p for p in room["participants"] if p["id"] != req.participant_id]
    await code_manager.broadcast(room_id, {
        "type": "peer_left",
        "room_id": room_id,
        "participant_id": req.participant_id,
        "participants": room["participants"]
    })
    return room

@app.post("/api/code-rooms/{room_id}/sync-code")
async def sync_code_room(room_id: str, req: CodeRoomSyncRequest):
    room = get_or_create_code_room(room_id)
    if req.language and req.language in CODE_TEMPLATES:
        if req.language != room["language"] and not req.code:
            room["code"] = CODE_TEMPLATES[req.language]
        room["language"] = req.language
        
    if req.code is not None:
        room["code"] = req.code
        
    if req.challenge_id:
        room["challenge_id"] = req.challenge_id
        
    await code_manager.broadcast(room_id, {
        "type": "code_change",
        "room_id": room_id,
        "code": room["code"],
        "language": room["language"],
        "client_id": req.client_id,
        "sender_id": req.participant_id,
        "timestamp": time.time()
    })
    return room

@app.post("/api/code-rooms/{room_id}/run")
async def run_code_in_room(room_id: str, req: CodeRoomRunRequest):
    room = get_or_create_code_room(room_id)
    lang = req.language or room["language"]
    code_to_run = req.code if req.code is not None else room["code"]
    
    # Save active code before running
    room["code"] = code_to_run
    room["language"] = lang
    
    start_time = time.time()
    exec_res = execute_code_payload(lang, code_to_run)
    elapsed = round(time.time() - start_time, 2)
    
    status_label = "0 (SUCCESS)" if exec_res["ok"] else "1 (ERROR)"
    full_output = f"{exec_res['output']}\n\n---------------------------------------\nProcess exited with status {status_label} in {elapsed}s"
    
    room["terminal_output"] = full_output
    room["last_run_status"] = "success" if exec_res["ok"] else "error"
    room["last_run_by"] = req.name or "Collaborator"
    room["last_run_time"] = time.time()
    
    # Append notification into room chat
    room.setdefault("messages", []).append({
        "id": f"msg_run_{int(time.time()*1000)}",
        "sender_id": "system",
        "sender_name": "Execution Engine",
        "text": f"▶️ {req.name or 'Collaborator'} executed {lang.upper()} code — {status_label}",
        "timestamp": time.time()
    })
    
    await code_manager.broadcast(room_id, {
        "type": "code_run_result",
        "room_id": room_id,
        "terminal_output": full_output,
        "last_run_status": room["last_run_status"],
        "last_run_by": room["last_run_by"],
        "last_run_time": room["last_run_time"],
        "messages": room["messages"]
    })
    return room

@app.post("/api/code-rooms/{room_id}/chat")
async def post_code_room_chat(room_id: str, req: CodeRoomChatRequest):
    room = get_or_create_code_room(room_id)
    text = (req.text or "").strip()
    if text:
        chat_item = {
            "id": f"msg_{int(time.time()*1000)}",
            "sender_id": req.participant_id,
            "sender_name": req.name,
            "text": text,
            "timestamp": time.time()
        }
        room.setdefault("messages", []).append(chat_item)
        if len(room["messages"]) > 50:
            room["messages"] = room["messages"][-50:]
            
        await code_manager.broadcast(room_id, {
            "type": "chat_message",
            "room_id": room_id,
            "message": chat_item,
            "messages": room["messages"]
        })
    return room

# --- Dedicated Real-Time WebSocket for Collaborative Code Arena ---
@app.websocket("/ws/code/{room_id}")
async def code_room_ws(websocket: WebSocket, room_id: str):
    query_params = dict(websocket.query_params)
    pid = query_params.get("participant_id") or f"coder_{int(time.time()*1000)%100000}"
    coder_name = query_params.get("name") or "Developer"

    await code_manager.connect(websocket, room_id, pid, coder_name)
    room = get_or_create_code_room(room_id)

    try:
        while True:
            raw_text = await websocket.receive_text()
            if not raw_text:
                continue
            try:
                msg = json.loads(raw_text)
            except Exception:
                continue

            msg_type = msg.get("type")

            if msg_type == "code_change":
                code = msg.get("code")
                lang = msg.get("language")
                client_id = msg.get("client_id")
                if code is not None:
                    room["code"] = code
                if lang:
                    room["language"] = lang
                await code_manager.broadcast(room_id, {
                    "type": "code_change",
                    "code": code,
                    "language": lang or room["language"],
                    "client_id": client_id,
                    "sender_id": pid,
                    "sender_name": coder_name,
                    "timestamp": time.time()
                }, exclude=websocket)

            elif msg_type == "cursor_update":
                cursor = msg.get("cursor")
                client_id = msg.get("client_id")
                await code_manager.broadcast(room_id, {
                    "type": "cursor_update",
                    "cursor": cursor,
                    "client_id": client_id,
                    "sender_id": pid,
                    "sender_name": coder_name
                }, exclude=websocket)

            elif msg_type == "language_change":
                lang = msg.get("language")
                code = msg.get("code")
                if lang:
                    room["language"] = lang
                    if code is not None:
                        room["code"] = code
                    elif lang in CODE_TEMPLATES:
                        room["code"] = CODE_TEMPLATES[lang]
                await code_manager.broadcast(room_id, {
                    "type": "language_change",
                    "language": room["language"],
                    "code": room["code"],
                    "sender_id": pid,
                    "sender_name": coder_name
                }, exclude=websocket)

            elif msg_type == "chat_message":
                text = (msg.get("text") or "").strip()
                if text:
                    chat_item = {
                        "id": f"msg_{int(time.time()*1000)}",
                        "sender_id": pid,
                        "sender_name": coder_name,
                        "text": text,
                        "timestamp": time.time()
                    }
                    room.setdefault("messages", []).append(chat_item)
                    if len(room["messages"]) > 50:
                        room["messages"] = room["messages"][-50:]
                    await code_manager.broadcast(room_id, {
                        "type": "chat_message",
                        "message": chat_item,
                        "messages": room["messages"]
                    })

            elif msg_type == "code_run":
                lang = msg.get("language") or room["language"]
                code_to_run = msg.get("code") if msg.get("code") is not None else room["code"]
                room["code"] = code_to_run
                room["language"] = lang

                await code_manager.broadcast(room_id, {
                    "type": "code_run_started",
                    "sender_id": pid,
                    "sender_name": coder_name,
                    "language": lang
                })

                start_time = time.time()
                exec_res = execute_code_payload(lang, code_to_run)
                elapsed = round(time.time() - start_time, 2)
                status_label = "0 (SUCCESS)" if exec_res["ok"] else "1 (ERROR)"
                full_output = f"{exec_res['output']}\n\n---------------------------------------\nProcess exited with status {status_label} in {elapsed}s"

                room["terminal_output"] = full_output
                room["last_run_status"] = "success" if exec_res["ok"] else "error"
                room["last_run_by"] = coder_name
                room["last_run_time"] = time.time()

                run_msg = {
                    "id": f"msg_run_{int(time.time()*1000)}",
                    "sender_id": "system",
                    "sender_name": "Execution Engine",
                    "text": f"▶️ {coder_name} executed {lang.upper()} code — {status_label}",
                    "timestamp": time.time()
                }
                room.setdefault("messages", []).append(run_msg)

                await code_manager.broadcast(room_id, {
                    "type": "code_run_result",
                    "terminal_output": full_output,
                    "last_run_status": room["last_run_status"],
                    "last_run_by": coder_name,
                    "last_run_time": room["last_run_time"],
                    "messages": room["messages"]
                })

            elif msg_type == "heartbeat":
                for p in room["participants"]:
                    if p["id"] == pid:
                        p["last_seen"] = time.time()
                        break

    except WebSocketDisconnect:
        code_manager.disconnect(websocket, room_id)
        if room_id in CODE_ROOMS_STATE:
            await code_manager.broadcast(room_id, {
                "type": "peer_left",
                "participant_id": pid,
                "participants": CODE_ROOMS_STATE[room_id]["participants"]
            })
    except Exception as e:
        logging.warning(f"WebSocket error in room {room_id}: {e}")
        code_manager.disconnect(websocket, room_id)

# --- Dedicated Real-Time WebSocket for GD Placement Rooms ---
@app.websocket("/ws/gd/{room_id}")
async def gd_room_ws(websocket: WebSocket, room_id: str):
    query_params = dict(websocket.query_params)
    pid = query_params.get("participant_id") or f"user_{uuid.uuid4().hex[:8]}"
    name = query_params.get("name") or "Candidate"

    await gd_manager.connect(websocket, room_id, pid, name)
    try:
        while True:
            raw_text = await websocket.receive_text()
            data = json.loads(raw_text)
            event_type = data.get("type")
            room = get_or_create_room(room_id)

            if event_type == "heartbeat":
                for p in room["participants"]:
                    if p["id"] == pid:
                        p["last_seen"] = time.time()
                        break
            elif event_type in ["webrtc_offer", "webrtc_answer", "webrtc_ice"]:
                target_id = data.get("target_id")
                if target_id:
                    await gd_manager.send_to_peer(room_id, target_id, {
                        "type": event_type,
                        "sender_id": pid,
                        "data": data.get("data")
                    })
            elif event_type == "speak":
                text = data.get("text", "")
                audio_data = data.get("audio_data")
                if text.strip() or audio_data:
                    transcript_item = {
                        "participant_id": pid,
                        "name": name,
                        "text": text,
                        "audio_data": audio_data,
                        "timestamp": time.time()
                    }
                    room.setdefault("transcripts", []).append(transcript_item)
                    await gd_manager.broadcast(room_id, {
                        "type": "room_update",
                        "room_id": room_id,
                        "state": format_room_response(room),
                        "event": "speech",
                        "participant_id": pid,
                        "name": name,
                        "text": text,
                        "audio_data": audio_data
                    })
    except WebSocketDisconnect:
        gd_manager.disconnect(websocket, room_id)
        if room_id in GD_ROOMS_STATE:
            await gd_manager.broadcast(room_id, {
                "type": "room_update",
                "room_id": room_id,
                "state": format_room_response(GD_ROOMS_STATE[room_id]),
                "event": "peer_left",
                "participant_id": pid
            })
    except Exception as e:
        logging.warning(f"WebSocket error in GD room {room_id}: {e}")
        gd_manager.disconnect(websocket, room_id)

# --- General WebSocket Endpoints ---
@app.websocket("/ws")
@app.websocket("/ws/{client_id}")
async def generic_websocket_endpoint(websocket: WebSocket, client_id: str = "default"):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({"status": "connected", "client": client_id, "data": data}))
    except WebSocketDisconnect:
        pass
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
