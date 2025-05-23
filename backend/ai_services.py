import openai
import os
from dotenv import load_dotenv
from typing import Dict, Any
import json
import re

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY must be set in .env file")

async def extract_recipe_from_text(text: str) -> Dict[str, Any]:
    """
    Извлекает структурированный рецепт из текста с помощью GPT
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """
You will extract a cooking recipe from the given transcript and/or description.
The text may be in different languages (e.g., Russian, English).
If the text is not in English, please first translate it to English.

Then extract the following structured recipe format:

{
  title: \"Short title of the recipe\",
  ingredients: ["list of ingredients with amounts if mentioned"],
  steps: ["step-by-step instructions"],
  total_time: "estimated time if possible",
  calories: "estimated or leave blank",
  categories: ["e.g. salad, snack, tiktok trend"],
  language: "original language of the transcript"
}

Only respond with valid JSON. If you cannot extract something, leave the field empty.
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        result = response.choices[0].message.content
        print("GPT сырой ответ:", repr(result))
        try:
            return json.loads(result)
        except Exception as e:
            print(f"[ERROR] Не удалось распарсить JSON напрямую: {e}")
            # Пытаемся найти JSON в тексте с помощью регулярки
            match = re.search(r'\{[\s\S]*\}', result)
            if match:
                json_str = match.group(0)
                try:
                    return json.loads(json_str)
                except Exception as e2:
                    print(f"[ERROR] Не удалось распарсить найденный JSON: {e2}")
            # Если не удалось — возвращаем информативную ошибку
            raise Exception(f"GPT вернул невалидный JSON. Сырой ответ: {result}")
    except Exception as e:
        raise Exception(f"Error extracting recipe: {str(e)}")

async def transcribe_audio(audio_path: str) -> str:
    """
    Транскрибирует аудиофайл с помощью OpenAI Whisper (новый синтаксис openai>=1.0.0)
    """
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        raise Exception(f"Error transcribing audio: {e}") 