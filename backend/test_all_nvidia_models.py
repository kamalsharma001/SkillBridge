import os
import requests

key = os.getenv("NVIDIA_API_KEY", "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")
url = "https://integrate.api.nvidia.com/v1/chat/completions"

models_to_test = [
    "nvidia/llama-3.1-nemotron-70b-instruct",
    "meta/llama3-70b-instruct",
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.2-90b-vision-instruct",
    "meta/llama2-70b",
    "nvidia/mistral-nemo-minitron-8b-8k-instruct",
    "mistralai/mistral-large-2-instruct",
    "google/gemma-2b",
    "google/gemma-3-12b-it",
    "nvidia/nemotron-4-340b-instruct"
]

for model in models_to_test:
    res = requests.post(
        url,
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 10
        }
    )
    
    if res.status_code == 200:
        print(f"[SUCCESS] {model}")
    else:
        print(f"[FAILED] {model} -> {res.status_code} {res.text[:100]}")
