import requests
from settings import settings

# Register a new user
register_url = f"http://{settings.host}:{settings.port}/register"
register_payload = {
    "username": "testuser2",
    "password": "testpassword"
}
register_headers = {"Content-Type": "application/json"}

register_response = requests.post(register_url, json=register_payload, headers=register_headers)
print(f"Register Status Code: {register_response.status_code}")
print(f"Register Response: {register_response.json()}")

# Obtain a token
token_url = f"http://{settings.host}:{settings.port}/token"
token_payload = {
    "username": "testuser2",
    "password": "testpassword"
}
token_headers = {"Content-Type": "application/x-www-form-urlencoded"}

token_response = requests.post(token_url, data=token_payload, headers=token_headers)

if token_response.status_code != 200:
    print(f"Failed to obtain token: {token_response.status_code}")
    print(token_response.text)
    exit()

token = token_response.json().get("access_token")
if not token:
    print("Token not found in the response.")
    exit()

# Chat endpoint'ine istek gönderelim
chat_url = f"http://{settings.host}:{settings.port}/chat"
chat_payload = {"input": "nasılsın"}
chat_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

chat_response = requests.post(chat_url, json=chat_payload, headers=chat_headers)

print(f"Chat Status Code: {chat_response.status_code}")

try:
    print(chat_response.json())
except requests.exceptions.JSONDecodeError:
    print("JSON decode error occurred.")

# Get chat history
history_url = f"http://{settings.host}:{settings.port}/history"
history_headers = {
    "Authorization": f"Bearer {token}"
}

history_response = requests.get(history_url, headers=history_headers)

print(f"History Status Code: {history_response.status_code}")

try:
    print(history_response.json())
except requests.exceptions.JSONDecodeError:
    print("JSON decode error occurred.")
