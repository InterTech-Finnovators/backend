from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
from settings import settings
import json
import os
from fastapi.middleware.cors import CORSMiddleware
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chat API",
    description="A simple chat API that reverses input strings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    input: str = Field(..., min_length=1, max_length=100, description="Input string to be processed")

@app.get("/history", summary="Get Chat History", response_description="Returns the chat history")
async def chat_history():
    json_file = settings.json_file

    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            file_data = json.load(file)
    else:
        file_data = []

    return {"history": file_data}

@app.post("/chat", summary="Process Chat Input", response_description="Returns the processed input")
async def get_response(query: Query):
    try:
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

        logger.info(f"Processed input: {query.input} -> {response}")

        return {"response": response}
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

def process_input(input: str) -> str:
    # Example complex processing function
    return input[::-1]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
