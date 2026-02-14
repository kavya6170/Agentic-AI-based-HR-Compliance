import requests
import json

url = "http://127.0.0.1:8000/ask"
data = {
    "question": "How many employees are there in the company?",
    "user": {
        "name": "Test Admin",
        "role": "admin"
    }
}
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
