import requests

try:
    response = requests.post(
        "http://localhost:8000/api/analyze/username",
        data={"username": "johndoe"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
