import requests
from settings import settings

# Register a new user (only needed once)
register_url = f"http://{settings.host}:{settings.port}/register"
register_payload = {
    "username": "testuser",
    "password": "testpassword"
}
register_response = requests.post(register_url, json=register_payload, headers={"Content-Type": "application/json"})
if register_response.status_code == 200:
    print("User registered successfully")
else:
    print("User registration failed or user already exists")

# Login to get JWT token
login_url = f"http://{settings.host}:{settings.port}/login"
login_payload = {
    "username": "testuser",
    "password": "testpassword"
}
login_response = requests.post(login_url, data=login_payload)
try:
    login_data = login_response.json()
    access_token = login_data["access_token"]
    print("Login successful, access token:", access_token)
except requests.exceptions.JSONDecodeError:
    print("Login failed, JSON decode error occurred.")
    access_token = None

# Test the chat endpoint with the JWT token
if access_token:
    chat_url = f"http://{settings.host}:{settings.port}/chat"
    chat_payload = {"input": "kredi nedir"}
    chat_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    chat_response = requests.post(chat_url, json=chat_payload, headers=chat_headers)
    try:
        chat_data = chat_response.json()
        print("Chat response:", chat_data)
    except requests.exceptions.JSONDecodeError:
        print("Chat request failed, JSON decode error occurred.")
else:
    print("No access token, cannot test chat endpoint")
