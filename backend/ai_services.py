import openai
import os
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
import json
import re

# Настройка OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

async def extract_recipe_from_url(url: str) -> Dict[str, Any]:
    """
    Извлекает рецепт из URL с помощью AI
    """
    try:
        # Получаем содержимое страницы
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            html_content = response.text
        
        # Извлекаем текст с помощью BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Получаем текст
        text = soup.get_text()
        
        # Очищаем текст
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Ограничиваем размер текста для GPT
        if len(text) > 4000:
            text = text[:4000]
        
        # Используем GPT для извлечения структурированной информации
        recipe_data = await extract_recipe_with_gpt(text, url)
        
        return recipe_data
        
    except Exception as e:
        print(f"Error extracting recipe from URL: {e}")
        # Возвращаем базовую структуру в случае ошибки
        return {
            "title": "Recipe from URL",
            "description": f"Recipe extracted from {url}",
            "ingredients": [],
            "instructions": [],
            "cooking_time": 30,
            "servings": 2,
            "difficulty": "Easy",
            "cuisine": "International",
            "tags": [],
            "image_url": None,
            "source_url": url
        }

async def extract_recipe_with_gpt(text: str, url: str) -> Dict[str, Any]:
    """
    Использует GPT для извлечения структурированной информации о рецепте
    """
    try:
        system_prompt = """
        Ты - эксперт по извлечению рецептов из текста. Извлеки структурированную информацию о рецепте.
        
        Верни JSON в следующем формате:
        {
            "title": "Название рецепта",
            "description": "Краткое описание рецепта",
            "ingredients": ["ингредиент 1", "ингредиент 2", ...],
            "instructions": ["шаг 1", "шаг 2", ...],
            "cooking_time": 30,
            "servings": 2,
            "difficulty": "Easy/Medium/Hard",
            "cuisine": "Italian/Chinese/Japanese/Indian/Mexican/French/Mediterranean/American/International",
            "tags": ["тег1", "тег2", ...],
            "image_url": "URL изображения или null"
        }
        
        Правила:
        1. Если информация не найдена, используй разумные значения по умолчанию
        2. cooking_time в минутах
        3. servings - количество порций
        4. difficulty: Easy (до 30 мин), Medium (30-60 мин), Hard (более 60 мин)
        5. cuisine: определи по названию или ингредиентам
        6. tags: добавь релевантные теги (например, "вегетарианский", "быстро", "десерт")
        """
        
        user_prompt = f"""
        Извлеки информацию о рецепте из следующего текста:
        
        {text}
        
        URL: {url}
        """
        
        # Используем новый API OpenAI
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Парсим JSON ответ
        content = response.choices[0].message.content
        recipe_data = json.loads(content)
        
        # Добавляем source_url
        recipe_data["source_url"] = url
        
        return recipe_data
        
    except Exception as e:
        print(f"Error with GPT extraction: {e}")
        # Возвращаем базовую структуру в случае ошибки
        return {
            "title": "Recipe from URL",
            "description": f"Recipe extracted from {url}",
            "ingredients": [],
            "instructions": [],
            "cooking_time": 30,
            "servings": 2,
            "difficulty": "Easy",
            "cuisine": "International",
            "tags": [],
            "image_url": None,
            "source_url": url
        }

async def extract_recipe_from_text(text: str) -> Dict[str, Any]:
    """
    Извлекает рецепт из текста с помощью AI
    """
    try:
        system_prompt = """
        Ты - эксперт по извлечению рецептов из текста. Извлеки структурированную информацию о рецепте.
        
        Верни JSON в следующем формате:
        {
            "title": "Название рецепта",
            "description": "Краткое описание рецепта",
            "ingredients": ["ингредиент 1", "ингредиент 2", ...],
            "instructions": ["шаг 1", "шаг 2", ...],
            "cooking_time": 30,
            "servings": 2,
            "difficulty": "Easy/Medium/Hard",
            "cuisine": "Italian/Chinese/Japanese/Indian/Mexican/French/Mediterranean/American/International",
            "tags": ["тег1", "тег2", ...]
        }
        
        Правила:
        1. Если информация не найдена, используй разумные значения по умолчанию
        2. cooking_time в минутах
        3. servings - количество порций
        4. difficulty: Easy (до 30 мин), Medium (30-60 мин), Hard (более 60 мин)
        5. cuisine: определи по названию или ингредиентам
        6. tags: добавь релевантные теги
        """
        
        # Используем новый API OpenAI
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Извлеки информацию о рецепте из следующего текста:\n\n{text}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        recipe_data = json.loads(content)
        
        return recipe_data
        
    except Exception as e:
        print(f"Error extracting recipe from text: {e}")
        return {
            "title": "Recipe",
            "description": "Recipe extracted from text",
            "ingredients": [],
            "instructions": [],
            "cooking_time": 30,
            "servings": 2,
            "difficulty": "Easy",
            "cuisine": "International",
            "tags": []
        }

def parse_ingredients(text: str) -> List[str]:
    """
    Парсит ингредиенты из текста
    """
    ingredients = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line and any(keyword in line.lower() for keyword in ['г', 'кг', 'мл', 'л', 'шт', 'по вкусу', 'щепотка']):
            ingredients.append(line)
    
    return ingredients

def parse_instructions(text: str) -> List[str]:
    """
    Парсит инструкции из текста
    """
    instructions = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line and any(keyword in line.lower() for keyword in ['шаг', 'этап', 'шаг', '1.', '2.', '3.', '4.', '5.']):
            instructions.append(line)
    
    return instructions

def estimate_cooking_time(instructions: List[str]) -> int:
    """
    Оценивает время приготовления на основе количества инструкций
    """
    base_time = 30
    time_per_step = 10
    return base_time + (len(instructions) * time_per_step)

def determine_difficulty(cooking_time: int, ingredients_count: int) -> str:
    """
    Определяет сложность рецепта
    """
    if cooking_time <= 30 and ingredients_count <= 5:
        return "Easy"
    elif cooking_time <= 60 and ingredients_count <= 10:
        return "Medium"
    else:
        return "Hard"

def determine_cuisine(title: str, ingredients: List[str]) -> str:
    """
    Определяет кухню на основе названия и ингредиентов
    """
    title_lower = title.lower()
    ingredients_text = ' '.join(ingredients).lower()
    
    cuisines = {
        'italian': ['паста', 'ризотто', 'пицца', 'базилик', 'оливковое масло'],
        'chinese': ['рис', 'соя', 'имбирь', 'чеснок', 'кунжут'],
        'japanese': ['суши', 'сашими', 'мисо', 'васаби', 'нори'],
        'indian': ['карри', 'куркума', 'имбирь', 'чеснок', 'кориандр'],
        'mexican': ['тако', 'буррито', 'авокадо', 'перец чили', 'лайм'],
        'french': ['вино', 'сыр', 'масло', 'лук', 'чеснок'],
        'mediterranean': ['оливки', 'оливковое масло', 'томаты', 'базилик', 'фета']
    }
    
    for cuisine, keywords in cuisines.items():
        if any(keyword in title_lower for keyword in keywords) or any(keyword in ingredients_text for keyword in keywords):
            return cuisine.capitalize()
    
    return "International"
