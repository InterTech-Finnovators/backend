import json
import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from settings import settings
from fastapi.middleware.cors import CORSMiddleware
import openai
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

endpoint = os.getenv("AZURE_OAI_ENDPOINT")
api_key = os.getenv("AZURE_OAI_KEY")
deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "https://rgacademy8srch.search.windows.net")
search_key = os.getenv("AZURE_SEARCH_KEY")
search_index = os.getenv("AZURE_SEARCH_INDEX", "omerindex")

# Initialize OpenAI client
client = openai.AzureOpenAI(
    base_url=f"{endpoint}/openai/deployments/{deployment}/extensions",
    api_key=api_key,
    api_version="2023-08-01-preview"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

class Query(BaseModel):
    input: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(username: str):
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            users = json.load(file)
        if username in users:
            return users[username]
    return None

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

@app.post("/register")
async def register(user: User):
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            users = json.load(file)
    else:
        users = {}

    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    users[user.username] = {"username": user.username, "password": hashed_password}

    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

    return {"msg": "User registered successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/history")
async def chat_history(current_user: str = Depends(get_current_user)):
    if os.path.exists("history.json"):
        with open("history.json", "r") as file:
            history = json.load(file)
        user_history = history.get(current_user, [])
    else:
        user_history = []

    return {"history": user_history}

@app.post("/chat")
async def get_response(query: Query, current_user: str = Depends(get_current_user)):
    response = await process_input(query.input)

    data = {
        "input": query.input,
        "response": response
    }

    if os.path.exists("history.json"):
        with open("history.json", "r") as file:
            history = json.load(file)
    else:
        history = {}

    if current_user not in history:
        history[current_user] = []

    history[current_user].append(data)

    with open("history.json", "w") as file:
        json.dump(history, file, indent=4)

    return {"response": response}

async def process_input(input_text: str) -> str:
    logging.debug(f"Received input: {input_text}")
    
    try:
        response = client.chat.completions.create(
            model=deployment,
            temperature=0.7,
            max_tokens=4096,
            top_p=0.95,
            messages=[
                {
                    "role": "user",
                    "content": input_text
                },
            ],
            extra_body={
                "dataSources": [
                    {
                        "type": "AzureCognitiveSearch",
                        "parameters": {
                            "endpoint": search_endpoint,
                            "key": search_key,
                            "indexName": search_index,
                            "query_type": "semantic",
                            "semanticConfiguration": "default"
                        },
                    }
                ]
            },
        )

        logging.debug(f"OpenAI response: {response}")

        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
