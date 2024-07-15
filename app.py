import os  
from fastapi import FastAPI, Depends, HTTPException  
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel, Field  
from fastapi_jwt_auth import AuthJWT  
from fastapi_jwt_auth.exceptions import AuthJWTException  
from fastapi.responses import JSONResponse  
from passlib.context import CryptContext  
import json  
import logging  
import openai  
from settings import settings  
  
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
  
# Password hashing context  
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  
  
# JWT settings  
class KeySettings(BaseModel):  
    authjwt_secret_key: str = Field("secret", min_length=1, strip_whitespace=True)  
  
@AuthJWT.load_config  
def get_config():  
    return KeySettings()  
  
@app.exception_handler(AuthJWTException)  
async def authjwt_exception_handler(request, exc):  
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})  
  
# User schema  
class UserCreate(BaseModel):  
    username: str  
    password: str  
  
class User(BaseModel):  
    username: str  
  
class Query(BaseModel):  
    input: str  
  
# JSON file paths  
users_file = "users.json"  
history_file = "history.json"  
  
# Initialize JSON files if they don't exist  
if not os.path.exists(users_file):  
    with open(users_file, "w") as file:  
        json.dump([], file)  
  
if not os.path.exists(history_file):  
    with open(history_file, "w") as file:  
        json.dump([], file)  
  
def read_json(file_path):  
    with open(file_path, "r") as file:  
        return json.load(file)  
  
def write_json(file_path, data):  
    with open(file_path, "w") as file:  
        json.dump(data, file, indent=4)  
  
@app.post("/register", response_model=User)  
def register(user: UserCreate):  
    users = read_json(users_file)  
    if any(u['username'] == user.username for u in users):  
        raise HTTPException(status_code=400, detail="Username already registered")  
      
    hashed_password = pwd_context.hash(user.password)  
    users.append({"username": user.username, "hashed_password": hashed_password})  
    write_json(users_file, users)  
    return {"username": user.username}  
  
@app.post("/login")  
def login(form_data: OAuth2PasswordRequestForm = Depends(), Authorize: AuthJWT = Depends()):  
    users = read_json(users_file)  
    user = next((u for u in users if u["username"] == form_data.username), None)  
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):  
        raise HTTPException(status_code=400, detail="Incorrect username or password")  
      
    access_token = Authorize.create_access_token(subject=user["username"])  
    return {"access_token": access_token, "token_type": "bearer"}  
  
@app.get("/history")  
async def chat_history(Authorize: AuthJWT = Depends()):  
    Authorize.jwt_required()  
    current_user = Authorize.get_jwt_subject()  
    history = read_json(history_file)  
    user_history = [h for h in history if h["username"] == current_user]  
    return {"history": user_history}  
  
@app.post("/chat")  
async def get_response(query: Query, Authorize: AuthJWT = Depends()):  
    Authorize.jwt_required()  
    current_user = Authorize.get_jwt_subject()  
      
    response = await process_input(query.input)  
    data = {  
        "username": current_user,  
        "input": query.input,  
        "response": response  
    }  
    history = read_json(history_file)  
    history.append(data)  
    write_json(history_file, history)  
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