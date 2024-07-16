import json
import os
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
from settings import settings
from fastapi.middleware.cors import CORSMiddleware
import openai
import logging
import firebase_admin
from firebase_admin import credentials, firestore

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

cred = credentials.Certificate('firebase_key.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

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
    chat_id: str

class ChatHistory(BaseModel):
    chat_id: str
    history: List[dict]

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(username: str):
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
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
    doc_ref = db.collection('users').document(user.username)
    if doc_ref.get().exists:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    doc_ref.set({"username": user.username, "password": hashed_password})

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

@app.get("/history/{chat_id}")
async def chat_history(chat_id: str, current_user: str = Depends(get_current_user)):
    doc_ref = db.collection('users').document(current_user).collection('chats').document(chat_id)
    doc = doc_ref.get()
    if doc.exists:
        user_history = doc.to_dict().get('history', [])
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

    doc_ref = db.collection('users').document(current_user).collection('chats').document(query.chat_id)
    doc = doc_ref.get()
    if doc.exists:
        history = doc.to_dict().get('history', [])
    else:
        history = []

    history.append(data)
    doc_ref.set({"history": history})

    return {"response": response}

async def process_input(input_text: str) -> str:
    logging.debug(f"Received input: {input_text}")
    
    try:
        response = client.chat.completions.create(
            model=deployment,
            temperature=0.15,
            max_tokens=4096,
            top_p=0.95,
            messages=[
                {
                    "role": "system", "content": "Sen alanında uzman finansal okuryazarlık eğitmenisin. Finansal okuryazarlık dışında bir soru sorulduğunda sadece şu cevabı vermen gerekir: \"Üzgünüm bu konuda bilgim yok. Lütfen başka bir soru sorunuz.\" Sen bir yatırım danışmanı değilsin. Danışmanlık veya tavsiye istenildiğinde şu cevabı vereceksin: \"Üzgünüm yasalar gereği cevap veremiyorum. Lütfen bu konuda bir uzmana danışınız.\" Basit, anlaşılır ve başlangıç seviyesindeki birine hitap edecek şekilde konuş."
                },
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
