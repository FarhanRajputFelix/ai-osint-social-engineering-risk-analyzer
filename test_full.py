import requests

try:
    response = requests.post(
        "http://localhost:8000/api/analyze/full",
        data={"username": "johndoe", "bio": "test bio"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
