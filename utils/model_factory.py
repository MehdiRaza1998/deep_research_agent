from agents import AsyncOpenAI, OpenAIChatCompletionsModel
from config import GEMINI_KEY, MODEL, MODEL_LITE

def get_model():
    """Create and return the main model instance"""
    provider = AsyncOpenAI(
        api_key=GEMINI_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model=MODEL,
        openai_client=provider,
    )
    return model

def get_model_lite():
    """Create and return the lite model instance for faster processing"""
    provider = AsyncOpenAI(
        api_key=GEMINI_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = OpenAIChatCompletionsModel(
        model=MODEL_LITE,
        openai_client=provider,
    )
    return model
