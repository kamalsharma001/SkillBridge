import asyncio
from orchestrator.agent_orchestrator import AgentOrchestrator
from services.llm_service import LLMService

async def main():
    try:
        orchestrator = AgentOrchestrator(llm_service=LLMService())
        context = {
            "candidate": {"candidate_id": "test", "skills": []},
            "target_role": {"name": "Software Engineer"}
        }
        res = await orchestrator.run_career_pipeline_async(context)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
