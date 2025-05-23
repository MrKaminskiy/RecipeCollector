from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

supabase = create_client(supabase_url, supabase_key)

def save_recipe(recipe_data: dict) -> dict:
    """
    Сохраняет рецепт в базу данных
    """
    try:
        response = supabase.table("recipes").insert(recipe_data).execute()
        return response.data[0]
    except Exception as e:
        raise Exception(f"Error saving recipe: {str(e)}")

def get_recipe(recipe_id: str) -> dict:
    """
    Получает рецепт по ID
    """
    try:
        response = supabase.table("recipes").select("*").eq("id", recipe_id).execute()
        if not response.data:
            return None
        return response.data[0]
    except Exception as e:
        raise Exception(f"Error getting recipe: {str(e)}")

def get_user_recipes(user_id: str) -> list:
    """
    Получает все рецепты пользователя
    """
    try:
        response = supabase.table("recipes").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        raise Exception(f"Error getting user recipes: {str(e)}") 