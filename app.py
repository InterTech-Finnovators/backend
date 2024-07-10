from fastapi import FastAPI  
from pydantic import BaseModel  
from settings import settings  
import json  
import os  
from fastapi.middleware.cors import CORSMiddleware
  
app = FastAPI()  
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{settings.host}:{settings.port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
  
class Query(BaseModel):  
    input: str  

@app.get("/history")  
async def chat_history():  
    json_file = settings.json_file  

    if os.path.exists(json_file):  
        with open(json_file, "r") as file:  
            file_data = json.load(file)  
    else:  
        file_data = []  
  
    return {"history": file_data}  
  
@app.post("/chat")  
async def get_response(query: Query):  
    response = process_input(query.input) 
  
    data = {  
        "input": query.input,  
        "response": response  
    }  
    json_file = settings.json_file
   
    if os.path.exists(json_file):  
        with open(json_file, "r") as file:  
            file_data = json.load(file)  
    else:  
        file_data = []  

    file_data.append(data)  
    
    with open(json_file, "w") as file:  
        json.dump(file_data, file, indent=4)  
      
    return {"response": response}  

def process_input(input: str) -> str:
    response = input[::-1]
    return response

if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(app, host=settings.host, port=settings.port)  
