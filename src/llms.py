import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from dotenv import load_dotenv

load_dotenv()


available_models = [
    "gpt-4o-mini",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "qwen/qwen3-32b",
    "openai/gpt-oss-20b",
    "lm-studio",
]


def get_llm(model: str):
    if model not in available_models:
        raise ValueError(f"Invalid model. Available models: {available_models}")

    if model == "gpt-4o-mini":
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    elif model in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0.0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    elif model == "lm-studio":
        return ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="openai/gpt-oss-20b",
            temperature=0.7,
        )
    elif model in [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "qwen/qwen3-32b",
        "openai/gpt-oss-20b",
    ]:
        return ChatGroq(
            model=model,
            temperature=0.0,
            api_key=os.getenv("GROQ_API_KEY"),
        )


def initialize_llm(model: Optional[str] = None):
    """
    Initialize the LLM by checking for available API keys.
    Tries OpenAI, Groq, and Google Gemini in that order.
    
    Args:
        model: Optional model name. If None, uses environment variables with defaults.
    
    Returns:
        LLM instance (ChatOpenAI, ChatGroq, or ChatGoogleGenerativeAI)
        
    Raises:
        ValueError: If no valid API key is found
    """
    # If model is provided, use it directly
    if model:
        if model not in available_models:
            raise ValueError(f"Invalid model '{model}'. Available models: {available_models}")
        print(f"Using specified model: {model}")
        return get_llm(model)
    
    # Otherwise, check for API keys in order of preference
    # Check for OpenAI API key
    if os.getenv("OPENAI_API_KEY"):
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if model_name in available_models:
            print(f"Using OpenAI model: {model_name}")
            return get_llm(model_name)
        else:
            print(f"Warning: {model_name} not in available_models, using gpt-4o-mini")
            return get_llm("gpt-4o-mini")
    
    # Check for Groq API key
    elif os.getenv("GROQ_API_KEY"):
        model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        if model_name in available_models:
            print(f"Using Groq model: {model_name}")
            return get_llm(model_name)
        else:
            print(f"Warning: {model_name} not in available_models, using llama-3.1-8b-instant")
            return get_llm("llama-3.1-8b-instant")
    
    # Check for Google API key
    elif os.getenv("GOOGLE_API_KEY"):
        model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        if model_name in available_models:
            print(f"Using Google Gemini model: {model_name}")
            return get_llm(model_name)
        else:
            print(f"Warning: {model_name} not in available_models, using gemini-1.5-flash")
            return get_llm("gemini-1.5-flash")
    
    else:
        raise ValueError(
            "No valid API key found. Please set one of: "
            "OPENAI_API_KEY, GROQ_API_KEY, or GOOGLE_API_KEY in your .env file"
        )