# Recipe Collector Backend

Backend часть приложения для сбора и структурирования рецептов из различных источников.

## Требования

- Python 3.8+
- Redis (для Celery)
- Supabase аккаунт
- OpenAI API ключ
- RapidAPI ключ (для Instagram Reels)

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
.\venv\Scripts\activate  # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Скопируйте файл конфигурации:
```bash
cp .env.example .env
```

4. Отредактируйте `.env` файл, добавив необходимые ключи:
- SUPABASE_URL и SUPABASE_KEY из вашего Supabase проекта
- OPENAI_API_KEY из вашего OpenAI аккаунта
- REDIS_URL для подключения к Redis
- RAPIDAPI_KEY для доступа к RapidAPI

**Внимание! Не коммитьте .env в репозиторий.**

## Запуск

1. Запустите Redis сервер (если не запущен)

2. Запустите приложение:
```bash
python run.py
```

Приложение будет доступно по адресу http://localhost:8000

## API Endpoints

- POST /parse - Парсинг рецепта по URL
- GET /recipes - Получение списка рецептов пользователя
- GET /recipes/{id} - Получение детальной информации о рецепте
- POST /recipes/save - Сохранение рецепта

## Разработка

Для запуска в режиме разработки установите DEBUG=True в .env файле.

## Тестирование

```bash
pytest
``` 