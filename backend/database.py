from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime

load_dotenv()

# MongoDB connection
mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
database_name = os.getenv("MONGODB_DATABASE", "recipio")

# Initialize MongoDB client
client = MongoClient(mongodb_url)
db = client[database_name]

# Collections
recipes_collection = db.recipes
users_collection = db.users
profiles_collection = db.profiles

def save_recipe(recipe_data: dict) -> dict:
    """
    Сохраняет рецепт в базу данных MongoDB
    """
    try:
        # Добавляем timestamp
        recipe_data["created_at"] = datetime.utcnow()
        recipe_data["updated_at"] = datetime.utcnow()
        
        # Вставляем документ
        result = recipes_collection.insert_one(recipe_data)
        
        # Получаем созданный документ
        created_recipe = recipes_collection.find_one({"_id": result.inserted_id})
        created_recipe["id"] = str(created_recipe["_id"])
        del created_recipe["_id"]
        
        return created_recipe
    except PyMongoError as e:
        raise Exception(f"Error saving recipe: {str(e)}")

def get_recipe(recipe_id: str) -> dict:
    """
    Получает рецепт по ID
    """
    try:
        # Проверяем, что ID валидный ObjectId
        if not ObjectId.is_valid(recipe_id):
            return None
            
        recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})
        if recipe:
            recipe["id"] = str(recipe["_id"])
            del recipe["_id"]
        return recipe
    except PyMongoError as e:
        raise Exception(f"Error getting recipe: {str(e)}")

def get_user_recipes(user_id: str) -> list:
    """
    Получает все рецепты пользователя
    """
    try:
        recipes = list(recipes_collection.find({"user_id": user_id}))
        
        # Преобразуем ObjectId в строки
        for recipe in recipes:
            recipe["id"] = str(recipe["_id"])
            del recipe["_id"]
            
        return recipes
    except PyMongoError as e:
        raise Exception(f"Error getting user recipes: {str(e)}") 

def update_recipe(recipe_id: str, recipe_data: dict) -> dict:
    """
    Обновляет рецепт
    """
    try:
        if not ObjectId.is_valid(recipe_id):
            raise Exception("Invalid recipe ID")
            
        recipe_data["updated_at"] = datetime.utcnow()
        
        result = recipes_collection.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$set": recipe_data}
        )
        
        if result.modified_count == 0:
            raise Exception("Recipe not found")
            
        # Получаем обновленный документ
        updated_recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})
        updated_recipe["id"] = str(updated_recipe["_id"])
        del updated_recipe["_id"]
        
        return updated_recipe
    except PyMongoError as e:
        raise Exception(f"Error updating recipe: {str(e)}")

def delete_recipe(recipe_id: str) -> bool:
    """
    Удаляет рецепт
    """
    try:
        if not ObjectId.is_valid(recipe_id):
            raise Exception("Invalid recipe ID")
            
        result = recipes_collection.delete_one({"_id": ObjectId(recipe_id)})
        return result.deleted_count > 0
    except PyMongoError as e:
        raise Exception(f"Error deleting recipe: {str(e)}")

def save_user(user_data: dict) -> dict:
    """
    Сохраняет пользователя
    """
    try:
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        
        result = users_collection.insert_one(user_data)
        
        created_user = users_collection.find_one({"_id": result.inserted_id})
        created_user["id"] = str(created_user["_id"])
        del created_user["_id"]
        
        return created_user
    except PyMongoError as e:
        raise Exception(f"Error saving user: {str(e)}")

def get_user(user_id: str) -> dict:
    """
    Получает пользователя по ID
    """
    try:
        user = users_collection.find_one({"id": user_id})
        if user:
            user["id"] = str(user["_id"])
            del user["_id"]
        return user
    except PyMongoError as e:
        raise Exception(f"Error getting user: {str(e)}")

def update_user(user_id: str, user_data: dict) -> dict:
    """
    Обновляет пользователя
    """
    try:
        user_data["updated_at"] = datetime.utcnow()
        
        result = users_collection.update_one(
            {"id": user_id},
            {"$set": user_data}
        )
        
        if result.modified_count == 0:
            raise Exception("User not found")
            
        updated_user = users_collection.find_one({"id": user_id})
        updated_user["id"] = str(updated_user["_id"])
        del updated_user["_id"]
        
        return updated_user
    except PyMongoError as e:
        raise Exception(f"Error updating user: {str(e)}")

# Создание индексов для оптимизации
def create_indexes():
    """
    Создает индексы для оптимизации запросов
    """
    try:
        # Индексы для рецептов
        recipes_collection.create_index("user_id")
        recipes_collection.create_index("created_at")
        recipes_collection.create_index("title")
        
        # Индексы для пользователей
        users_collection.create_index("email", unique=True)
        users_collection.create_index("id")
        
        print("Database indexes created successfully")
    except PyMongoError as e:
        print(f"Error creating indexes: {str(e)}")

# Инициализация индексов при импорте модуля
create_indexes() 