import requests

res = requests.post("http://localhost:8000/api/upload-resume", files={"file": ("test.pdf", b"%PDF-1.4 test", "application/pdf")})
print(res.status_code, res.text)
