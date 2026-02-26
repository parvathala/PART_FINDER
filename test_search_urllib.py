import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

# Setup cookie jar
cookie_jar = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

# Login
login_url = "http://127.0.0.1:5000/login"
data = urllib.parse.urlencode({"email": "test@test.com", "password": "password"}).encode('utf-8')
try:
    req = urllib.request.Request(login_url, data=data)
    res = urllib.request.urlopen(req)
    print("Login successful")
except Exception as e:
    print(f"Login failed: {e}")

# Search
search_url = "http://127.0.0.1:5000/api/search?q=1000"
try:
    req = urllib.request.Request(search_url)
    res = urllib.request.urlopen(req)
    print("Search successful:")
    print(res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"Search failed with code: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Search failed error: {e}")
