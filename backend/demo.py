from __future__ import annotations
import json
import os
import sys
import asyncio

# Force UTF-8 encoding for Windows console to support emojis
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.agent_orchestrator import AgentOrchestrator


async def main():
    sample_file = os.path.join(os.path.dirname(__file__), "examples", "sample_candidate.json")
    if not os.path.exists(sample_file):
        print(f"Error: Sample file not found at {sample_file}")
        return

    with open(sample_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    print("==================================================")
    print("[*] INITIALIZING AI CAREER ENGINE (6-AGENT SYSTEM)")
    print("==================================================")
    print(f"Candidate: {input_data['candidate']['name']} ({input_data['candidate']['current_role']})")
    print(f"Target Role: {input_data['target_role']['name']}")
    print("--------------------------------------------------")

    orchestrator = AgentOrchestrator()
    results = await orchestrator.run_career_pipeline_async(input_data)

    print("\n--- 1. SKILL ANALYSIS ---")
    if results["llm_reasoning"].get("skill_analysis"):
        print(f"\n[AI ASSESSOR]:\n{results['llm_reasoning']['skill_analysis']}\n")
    print("Strengths:")
    for s in results["strengths"]:
        print(f"  [+] {s['name']}: {int(s['proficiency'] * 100)}%")
    
    print("\nPrioritized Skill Gaps:")
    for g in results["skill_gaps"]:
        print(f"  [!] [{g['priority'].upper()}] {g['skill']}: Current {int(g['current_level']*100)}% -> Target {int(g['required_level']*100)}% (Gap: {int(g['gap']*100)}%)")

    print("\n--- 2. CAREER RESEARCH ---")
    if results["llm_reasoning"].get("career_research"):
        print(f"\n[CAREER COACH]:\n{results['llm_reasoning']['career_research']}\n")
    print("Career Transition Paths:")
    for cp in results["career_paths"]:
        print(f"  * {cp['role']} (Fit Score: {int(cp['fit_score']*100)}%)")

    print("\n--- 3. INDUSTRY INTELLIGENCE ---")
    if results["llm_reasoning"].get("industry_intelligence"):
        print(f"\n[INDUSTRY ANALYST]:\n{results['llm_reasoning']['industry_intelligence']}\n")
    print("Market Skill Demand Trends:")
    for t in results["skill_trends"]:
        print(f"  * {t['skill']}: {t['current_demand']} [{t['trend']}]")
    print(f"Emerging Skills Elevated in Roadmap: {', '.join(results['emerging_skills'])}")

    print("\n--- 4. RECOMMENDED LEARNING PLAN ---")
    if results["llm_reasoning"].get("learning"):
        print(f"\n[L&D ARCHITECT]:\n{results['llm_reasoning']['learning']}\n")
    for step in results["learning_plan"]:
        print(f"  Step {step['step']}: {step['skill']} -> '{step['course_title']}' ({step['platform']}) [{step['priority'].upper()} PRIORITY]")

    print("\n--- 5. OPPORTUNITY MATCHING ---")
    if results["llm_reasoning"].get("opportunity"):
        print(f"\n[TECH RECRUITER]:\n{results['llm_reasoning']['opportunity']}\n")
    for opp in results["matched_opportunities"]:
        print(f"\n  [JOB] {opp['title']} @ {opp['company']}")
        print(f"     Overall Compatibility Score: {opp['compatibility_score']}%")
        print(f"     Breakdown: Skill Match {opp['breakdown']['skill_match']}%, Experience Match {opp['breakdown']['experience_match']}%, Education Match {opp['breakdown']['education_match']}%")
        print(f"     WHY MATCHED: {', '.join(opp['why_matched']) if opp['why_matched'] else 'None'}")
        print(f"     GAPS: {', '.join(opp['gaps']) if opp['gaps'] else 'None'}")

    print("\n--- 6. PROFILE INTELLIGENCE & READINESS ---")
    if results["llm_reasoning"].get("profile_intelligence"):
        print(f"\n[CHIEF STRATEGIST]:\n{results['llm_reasoning']['profile_intelligence']}\n")
    readiness = results["readiness"]
    print(f"Overall Career Readiness Score: {readiness.get('readiness_score', 0)}% ({readiness.get('status', 'Unknown')})")
    print(f"Skill Readiness: {readiness.get('skill_readiness', 0)}%, Project Readiness: {readiness.get('project_readiness', 0)}%")
    
    print("\nGenerated Sequenced Roadmap:")
    for r in results["roadmap"]:
        print(f"  Stage {r['step']}: {r['title']} - {r['action']}")

    print("\n==================================================")
    print("[OK] AI CAREER ENGINE PIPELINE COMPLETED SUCCESSFULLY")
    print("==================================================")



if __name__ == "__main__":
    asyncio.run(main())
