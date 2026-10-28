import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import LLMService
from api.resume_parser import parse_resume_to_profile
import api.resume_parser

async def mock_extract(file_path):
    return "Aditya Jha\nMachine Learning Engineer\nBengaluru, India\n\nExperience:\n- Data Scientist at TechCorp (2 years)\n\nProjects:\n- AI Recommendation Engine using Python and SQL\n- NLP Chatbot using PyTorch\n\nEducation:\n- B.Tech in Computer Science, IIT"

api.resume_parser.extract_text_from_file = mock_extract

async def main():
    service = LLMService()
    profile = await parse_resume_to_profile("fake_resume.pdf", service)
    import json
    print(json.dumps(profile, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
