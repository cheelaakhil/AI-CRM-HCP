"""
LLM configuration — Groq with Gemma 2 9B IT via LangChain.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def get_llm(temperature: float = 0.1) -> ChatGroq:
    """Get a configured ChatGroq instance with Gemma 2 9B IT."""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=temperature,
        max_tokens=2048,
    )
