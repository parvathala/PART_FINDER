import requests

s = requests.Session()
# Login
print("Logging in...")
res = s.post("http://127.0.0.1:5000/login", data={"email": "test@test.com", "password": "password"})
print(f"Login status: {res.status_code}")

# Chat
print("Testing Chat API...")
res = s.post("http://127.0.0.1:5000/api/chat", json={"message": "Do you have any parts with legacy number TDI1000106?"})
print(f"Chat status: {res.status_code}")
print(f"Chat response: {res.json()}")
