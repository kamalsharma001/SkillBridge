import asyncio
from services.llm_service import LLMService

async def main():
    s = LLMService()
    try:
        res = await s.generate_reasoning_async("system", "user", model="nvidia/llama-3.1-nemotron-70b-instruct")
        print("RESULT:", res)
    except Exception as e:
        print("EXCEPTION:", str(e))

if __name__ == '__main__':
    asyncio.run(main())
