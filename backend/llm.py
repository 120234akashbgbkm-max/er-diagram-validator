"""llm.py - one place that talks to Gemini, with retries and model fallback."""

import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def _extract_json(text):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return json.loads(text)


def generate_json(system_prompt: str, user_message: str = "", file_bytes: bytes = None,
                  mime_type: str = None, temperature: float = None, contents=None):
    """Ask Gemini for JSON and return it parsed.

    Tries GEMINI_MODEL first, then each model in GEMINI_FALLBACK_MODELS.
    503 (overloaded) errors are retried with a short wait; any other error
    moves on to the next model.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Check your .env file.")

    primary = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    fallbacks = [m.strip() for m in os.getenv("GEMINI_FALLBACK_MODELS", "").split(",") if m.strip()]
    models = [primary] + fallbacks

    client = genai.Client(api_key=api_key)
    last_error = None

    # 'contents' lets a caller send several parts at once (text plus many images)
    if contents is None:
        contents = user_message
        if file_bytes is not None:
            contents = [types.Part.from_bytes(data=file_bytes, mime_type=mime_type), user_message]

    config_args = {"system_instruction": system_prompt, "response_mime_type": "application/json"}
    if temperature is not None:
        config_args["temperature"] = temperature

    for model in models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(**config_args),
                )
                return _extract_json(response.text)
            except Exception as e:  # noqa: BLE001
                last_error = e
                text = str(e)
                if "503" in text or "UNAVAILABLE" in text:
                    time.sleep(2 * (attempt + 1))
                    continue
                break  # wrong model name / quota / bad JSON: try the next model

    raise last_error
