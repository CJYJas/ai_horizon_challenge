import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from backend.database import get_session

# Try to load from backend/.env explicitly
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. The API requires a real LLM API key.")
    # Initialize the real LLM as requested by the user
    if api_key.startswith("sk-or"):
        # Configure for OpenRouter if using an OpenRouter key
        return ChatOpenAI(
            model="openai/gpt-4o",
            temperature=0,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            max_tokens=1500
        )
    
    return ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=1500)
