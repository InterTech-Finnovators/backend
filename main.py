from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from settings import settings
import json
import os
from fastapi.middleware.cors import CORSMiddleware
import openai
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Debug seviyesinde loglama yapalım
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
    response = await process_input(query.input)

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
