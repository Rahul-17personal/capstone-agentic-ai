"""Provider adapter used by LangGraph agents."""
from typing import TypeVar

from google import genai
from google.genai import types
from openai import OpenAI
from pydantic import BaseModel

from app.config import settings

T = TypeVar("T", bound=BaseModel)


def generate_structured(
    provider: str,
    schema: type[T],
    system_prompt: str,
    user_prompt: str,
) -> T:
    selected = provider.lower().strip()

    if selected == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not configured")
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            instructions=system_prompt,
            input=user_prompt,
            text={"format": {"type": "json_object"}},
        )
        if not response.output_text:
            raise ValueError("OpenAI returned an empty agent response")
        return schema.model_validate_json(response.output_text)

    if selected == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key is not configured")
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=system_prompt + "\n\n" + user_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        if not response.text:
            raise ValueError("Gemini returned an empty agent response")
        return schema.model_validate_json(response.text)

    raise ValueError("Unsupported AI provider. Choose openai or gemini.")
