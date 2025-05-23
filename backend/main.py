from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from database import save_recipe as db_save_recipe, get_recipe as db_get_recipe, get_user_recipes
from media_processor import MediaProcessor
from ai_services import extract_recipe_from_text

load_dotenv()

app = FastAPI(title="Recipe Collector API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL frontend приложения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация MediaProcessor
media_processor = MediaProcessor()

class Ingredient(BaseModel):
    name: str
    amount: str
    unit: str

class RecipeCard(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    title: str
    ingredients: List[Ingredient]
    steps: List[str]
    image_url: str
    source_url: str
    language: str
    estimated_time_min: int
    calories: int
    categories: List[str]
    created_at: Optional[str] = None

class URLInput(BaseModel):
    url: str

@app.post("/parse")
async def parse_recipe(url_input: URLInput) -> Dict[str, Any]:
    try:
        # Получаем базовые данные из поста
        recipe_data = await media_processor.process_url(url_input.url)
        
        # Используем GPT для извлечения структурированной информации
        structured_recipe = await extract_recipe_from_text(recipe_data["description"])
        
        # Объединяем данные
        recipe_data.update(structured_recipe)
        
        return recipe_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recipes")
async def get_recipes(user_id: str) -> List[RecipeCard]:
    """
    Возвращает список рецептов пользователя
    """
    try:
        recipes = get_user_recipes(user_id)
        return [RecipeCard(**recipe) for recipe in recipes]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str) -> RecipeCard:
    """
    Возвращает детальную информацию о рецепте
    """
    try:
        recipe = db_get_recipe(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return RecipeCard(**recipe)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/recipes/save")
async def save_recipe(recipe: Dict[str, Any]):
    """
    Сохраняет рецепт в базу данных
    """
    try:
        saved_recipe = db_save_recipe(recipe)
        return saved_recipe
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 