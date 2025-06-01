import os
import logging
from crewai import LLM

# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemma-3n-e4b-it")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_crew_llm():
    return LLM(
        model=f'gemini/{GEMINI_MODEL}',
        provider='google',
        api_key=os.getenv("GOOGLE_API_KEY", ""),
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
