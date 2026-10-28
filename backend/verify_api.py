import requests
import json

candidate = {
    "candidate_id": "C001",
    "name": "Ananya Sharma",
    "education": ["B.Tech Computer Science"],
    "location": "Bengaluru, India",
    "experience_years": 2.5,
    "skills": [
        {"name": "Python", "proficiency": 0.85},
        {"name": "SQL", "proficiency": 0.72},
        {"name": "Machine Learning", "proficiency": 0.65},
        {"name": "Pandas", "proficiency": 0.82}
    ]
}

payload = {
    "candidate": candidate,
    "target_role": "Data Scientist"
}

res = requests.post("http://localhost:8000/api/analyze-career", json=payload)
if res.status_code == 200:
    data = res.json()["data"]
    
    # Check Skill Gaps
    skill_gaps = data.get("skill_analysis", {}).get("data", {}).get("skill_gaps", [])
    print(f"Skill Gaps Count: {len(skill_gaps)}")
    if len(skill_gaps) == 0:
        print("[FAIL] Skill gaps are empty!")
    else:
        print(f"[SUCCESS] Skill gaps populated: {skill_gaps[0].get('skill')} ...")
    
    # Check LLM Synthesis
    summary = data.get("skill_analysis", {}).get("summary", "")
    print(f"Summary: {summary[:100]}...")
    if "LLM synthesis failed" in summary:
        print("[FAIL] LLM Synthesis failed!")
    else:
        print("[SUCCESS] LLM Synthesis worked!")
else:
    print(f"[FAIL] API Error: {res.status_code} {res.text}")
