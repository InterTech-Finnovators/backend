import requests
from settings import settings

url = f"http://{settings.host}:{settings.port}/chat"
payload = {"input": "My Name is Atakan"
           }
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")

try:
    print(response.json())
except requests.exceptions.JSONDecodeError:
    print("JSON decode error occurred.")