import os
import dotenv

dotenv.load_dotenv()

class Settings:
    host: str = os.getenv("HOST", "localhost")
    port: int = int(os.getenv("PORT", 8000))
    json_file: str = os.getenv("JSON_FILE", "chat_history.json")
    azure_oai_endpoint: str = os.getenv("AZURE_OAI_ENDPOINT")
    azure_oai_key: str = os.getenv("AZURE_OAI_KEY")
    azure_oai_deployment: str = os.getenv("AZURE_OAI_DEPLOYMENT")
    azure_search_endpoint: str = os.getenv("AZURE_SEARCH_ENDPOINT", "https://rgacademy8srch.search.windows.net")
    azure_search_key: str = os.getenv("AZURE_SEARCH_KEY")
    azure_search_index: str = os.getenv("AZURE_SEARCH_INDEX", "omerindex")

settings = Settings()