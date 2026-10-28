import os
from openai import OpenAI
from dotenv import load_dotenv
import threading

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=5.0
)

models = client.models.list()
available = [m.id for m in models.data if "instruct" in m.id.lower() or "llama" in m.id.lower()]

print(f"Testing {len(available)} models...")

working_models = []

for m in available:
    try:
        completion = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        print(f"[SUCCESS] {m}")
        working_models.append(m)
        break  # We only need one!
    except Exception as e:
        pass

if working_models:
    print(f"\nFOUND WORKING MODEL: {working_models[0]}")
else:
    print("\nNO WORKING MODELS FOUND.")
