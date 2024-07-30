import json
import os
from fastapi import FastAPI, HTTPException, Depends, status, Body, Response, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, List
import firebase_admin
from firebase_admin import auth, firestore, credentials
from google.cloud.firestore_v1.base_query import FieldFilter
from settings import settings
import openai
import logging
import re
import azure.cognitiveservices.speech as speechsdk
import traceback
import bcrypt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class User(BaseModel):
    username: str
    password: str
    email: str
   
class Token(BaseModel):
    username: str
    password: str
   
class Query(BaseModel):
    input: str
    chat_id: str

class ChatHistory(BaseModel):
    chat_id: str
    history: List[dict]

class PasswordReset(BaseModel):
    email: str
    new_password: str


def verify_password(pass1, pass2):
    return pass1 == pass2

def get_user(username: str):
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def create_access_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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
    try:
        return verify_token(token, credentials_exception)
    except Exception as e:
        logging.error(f"Token verification failed: {e}")
        raise credentials_exception

def remove_doc_references(text):
    return re.sub(r'\[doc\d+\]', '', text)

@app.post("/synthesize")
def synthesize_endpoint(payload: dict = Body(...)):
    try:
        text = payload.get("text")
        if not text:
            raise HTTPException(status_code=400, detail="Text field is required")
        audio_filepath = synthesize_speech(text)
        return {"audio_filepath": audio_filepath}
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

speech_key = "38ab1d115cbd4020af61b1662c543641"
service_region = "eastus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "tr-TR-EmelNeural"

"""def synthesize_speech(text: str) -> str:
    audio_filename = "response.wav"
    audio_output = speechsdk.audio.AudioOutputConfig(filename=audio_filename)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("hello")
        return audio_filename
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logging.error(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            logging.error(f"Error details: {cancellation_details.error_details}")
        raise HTTPException(status_code=500, detail="Speech synthesis failed")
"""
request_counter = 0
def synthesize_speech(text: str, output_dir: str = "frontend/gpt-client-frontend") -> str:
    global request_counter

    audio_filename = f"response_{request_counter}.wav"  # Benzersiz dosya adı
    audio_output_path = os.path.join(output_dir, audio_filename) 

    # Ses çıkış dizininin kontrolü ve gerekirse oluşturulması
    os.makedirs(output_dir, exist_ok=True)

    audio_output = speechsdk.audio.AudioOutputConfig(filename=audio_output_path)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return audio_output_path  # Tam dosya yolunu döndür
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logging.error(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            logging.error(f"Error details: {cancellation_details.error_details}")
        raise HTTPException(status_code=500, detail="Speech synthesis failed")

@app.post("/register")
async def register(user: User):
    try:
        # Hash the password
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        # Create user in Firebase Authentication
        user_record = firebase_admin.auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.username
        )
        firebase_admin.auth.generate_email_verification_link(user.email)

        # Store user in Firestore with username as document ID
        db.collection('users').document(user.username).set({
            "username": user.username,
            "email": user.email,
            "password": user.password,  # Store hashed password
            "uid": user_record.uid  # Store UID for reference
        })
       
       
        return {"msg": "User registered successfully", "success": "True"}
    except firebase_admin.auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except firebase_admin.auth.UidAlreadyExistsError:  
        raise HTTPException(status_code=400, detail="Username already registered")
    except Exception as e:
        logging.error(f"An error occurred during registration: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An error occurred during registration")



@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):  
    """Authenticates the user and returns a Firebase ID token."""
    current_user = get_user(form_data.username)
    user = firebase_admin.auth.get_user_by_email(current_user["email"])
    if not user or not verify_password(form_data.password, current_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/history")
async def chat_history(current_user: str = Depends(get_current_user)):
    user_ref = db.collection('users').document(current_user)
    chats_ref = user_ref.collection('chats')
   
    all_chats = []
    for chat_doc in chats_ref.stream():
        chat_data = chat_doc.to_dict()
        chat_id = chat_doc.id
        chat_history = chat_data.get('history', [])
        all_chats.append({"chat_id": chat_id, "history": chat_history})
   
    return {"chats": all_chats}

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

@app.post("/reset-password")
async def reset_password(password_reset: PasswordReset):
    try:
        user_ref = db.collection('users').where('email', '==', password_reset.email).limit(1).stream()
        user_doc = next(user_ref, None)

        if user_doc:
            user_id = user_doc.id
            db.collection('users').document(user_id).update({
                "password": password_reset.new_password
            })
            return {"msg": "Password reset successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_input(input_text: str) -> str:
    logging.debug(f"Received input: {input_text}")
   
    try:
        response = client.chat.completions.create(
            model=deployment,
            temperature=0.15,
            max_tokens=2048,
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

        return remove_doc_references(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=8181)