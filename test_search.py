import requests

s = requests.Session()
# Login
print("Logging in...")
res = s.post("http://127.0.0.1:5000/login", data={"email": "test@test.com", "password": "password"})
print(f"Login status: {res.status_code}")

# Search
print("Searching for TDI1000106...")
res = s.get("http://127.0.0.1:5000/api/search?q=TDI1000106")
print(f"Search status: {res.status_code}")
print(f"Search response: {res.text}")
