from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json
import os
from datetime import datetime
import uuid

# Импортируем функции для работы с MongoDB
from database import (
    save_recipe, get_recipe, get_user_recipes, update_recipe, 
    delete_recipe, save_user, get_user, update_user
)

app = FastAPI(title="Recipio API", version="1.0.0")

# Настройка CORS для iOS приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class RecipeCreate(BaseModel):
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    cooking_time: int
    servings: int
    difficulty: str
    cuisine: str
    tags: List[str]
    image_url: Optional[str] = None
    source_url: Optional[str] = None

class RecipeResponse(BaseModel):
    id: str
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    cooking_time: int
    servings: int
    difficulty: str
    cuisine: str
    tags: List[str]
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    is_favorite: bool = False
    created_at: str
    updated_at: str

class APIResponse(BaseModel):
    success: bool
    data: Optional[RecipeResponse] = None
    message: Optional[str] = None

class ExtractRecipeRequest(BaseModel):
    url: str

# Безопасность
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Извлекает user_id из JWT токена"""
    try:
        # Здесь должна быть валидация JWT токена
        # Пока что просто извлекаем user_id из токена
        token = credentials.credentials
        # В реальном приложении декодируйте JWT и извлеките user_id
        # Пока что используем простую логику
        return "user_" + str(hash(token) % 1000)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@app.get("/")
async def root():
    return {"message": "Recipio API is running!"}

@app.get("/api/recipes", response_model=List[RecipeResponse])
async def get_recipes(user_id: str = Depends(get_current_user_id)):
    """Получить все рецепты пользователя"""
    try:
        user_recipes = get_user_recipes(user_id)
    return user_recipes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recipes", response_model=APIResponse, status_code=201)
async def create_recipe(
    recipe: RecipeCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Создать новый рецепт"""
    try:
    recipe_data = {
        "user_id": user_id,
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "cooking_time": recipe.cooking_time,
        "servings": recipe.servings,
        "difficulty": recipe.difficulty,
        "cuisine": recipe.cuisine,
        "tags": recipe.tags,
        "image_url": recipe.image_url,
        "source_url": recipe.source_url,
            "is_favorite": False
    }
    
        saved_recipe = save_recipe(recipe_data)
    
    return APIResponse(
        success=True,
            data=RecipeResponse(**saved_recipe),
        message="Recipe created successfully"
    )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recipes/{recipe_id}", response_model=APIResponse)
async def get_recipe(
    recipe_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Получить конкретный рецепт"""
    try:
        recipe = get_recipe(recipe_id)
        if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if recipe.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return APIResponse(
        success=True,
        data=RecipeResponse(**recipe)
    )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/recipes/{recipe_id}", response_model=APIResponse)
async def update_recipe(
    recipe_id: str,
    recipe: RecipeCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Обновить рецепт"""
    try:
        # Сначала проверяем существование рецепта
        existing_recipe = get_recipe(recipe_id)
        if not existing_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if existing_recipe.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    recipe_data = {
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "cooking_time": recipe.cooking_time,
        "servings": recipe.servings,
        "difficulty": recipe.difficulty,
        "cuisine": recipe.cuisine,
        "tags": recipe.tags,
        "image_url": recipe.image_url,
        "source_url": recipe.source_url,
            "is_favorite": existing_recipe.get("is_favorite", False)
    }
    
        updated_recipe = update_recipe(recipe_id, recipe_data)
    
    return APIResponse(
        success=True,
            data=RecipeResponse(**updated_recipe),
        message="Recipe updated successfully"
    )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/recipes/{recipe_id}")
async def delete_recipe(
    recipe_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Удалить рецепт"""
    try:
        # Сначала проверяем существование рецепта
        existing_recipe = get_recipe(recipe_id)
        if not existing_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
        if existing_recipe.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
        success = delete_recipe(recipe_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete recipe")
        
    return {"message": "Recipe deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract-recipe", response_model=APIResponse)
async def extract_recipe(
    request: ExtractRecipeRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Извлечь рецепт из URL"""
    try:
        # Используем существующий сервис для извлечения рецепта
        from ai_services import extract_recipe_from_url
        
        recipe_data = await extract_recipe_from_url(request.url)
        
        # Создаем рецепт в базе данных
        recipe = {
            "user_id": user_id,
            "title": recipe_data.get("title", "Extracted Recipe"),
            "description": recipe_data.get("description", ""),
            "ingredients": recipe_data.get("ingredients", []),
            "instructions": recipe_data.get("instructions", []),
            "cooking_time": recipe_data.get("cooking_time", 30),
            "servings": recipe_data.get("servings", 2),
            "difficulty": recipe_data.get("difficulty", "Easy"),
            "cuisine": recipe_data.get("cuisine", "International"),
            "tags": recipe_data.get("tags", []),
            "image_url": recipe_data.get("image_url"),
            "source_url": request.url,
            "is_favorite": False
        }
        
        saved_recipe = save_recipe(recipe)
        
        return APIResponse(
            success=True,
            data=RecipeResponse(**saved_recipe),
            message="Recipe extracted and saved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract recipe: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": "MongoDB"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 