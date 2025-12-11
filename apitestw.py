import requests

API_KEY = "sk-KkPONG8A1lC2Kp_ucS0dgg"  # твой ключ

r = requests.post(
    "https://api.openai.com/v1/chat/completions",
    json={
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello!"}]
    },
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
)

print(r.status_code, r.text)
