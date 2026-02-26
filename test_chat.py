import requests
import json

s = requests.Session()
# Login
print("Logging in...")
res = s.post("http://127.0.0.1:5000/login", data={"email": "test@test.com", "password": "password"})
print(f"Login status: {res.status_code}")

# Chat
print("Asking chat for TDI10...")
# Needs to be a POST request for /api/chat
res = s.post(
    "http://127.0.0.1:5000/api/chat", 
    json={"message": "Can you check Part Number TDI100010?"}
)
print(f"Chat status: {res.status_code}")

try:
    data = res.json()
    print("Chat Response:")
    print(data.get("reply"))
except Exception as e:
    print(f"Error parsing JSON: {e}")
    print(res.text)
