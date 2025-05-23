import yt_dlp
import os
import re
from typing import Dict, Any, Optional
import tempfile
from ai_services import transcribe_audio, extract_recipe_from_text
from dotenv import load_dotenv
import requests
from moviepy.editor import VideoFileClip

load_dotenv()

def extract_instagram_shortcode(url: str) -> str:
    match = re.search(r'instagram\.com/(?:p|reel)/([\w-]+)', url)
    if not match:
        raise Exception("Не удалось извлечь shortcode из URL")
    return match.group(1)

def download_instagram_reel_by_shortcode(shortcode: str) -> dict:
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    rapidapi_host = os.getenv("RAPIDAPI_HOST")
    if not rapidapi_key or not rapidapi_host:
        raise Exception("RapidAPI ключи не заданы в .env")

    url = "https://instagram-scrapper-posts-reels-stories-downloader.p.rapidapi.com/reel_by_shortcode"
    querystring = {"shortcode": shortcode}
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": rapidapi_host
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code != 200:
        raise Exception(f"Ошибка RapidAPI: {response.text}")
    return response.json()

class MediaProcessor:
    def is_instagram_url(self, url: str) -> bool:
        """Проверяет, является ли URL ссылкой на Instagram."""
        return bool(re.match(r'https?://(?:www\.)?instagram\.com/(?:p|reel)/[\w-]+/?', url))

    async def process_instagram_url(self, url: str) -> Dict[str, Any]:
        """Обрабатывает URL Instagram и извлекает данные поста через RapidAPI."""
        try:
            print(f"[LOG] Получена ссылка: {url}")
            shortcode = extract_instagram_shortcode(url)
            print(f"[LOG] Извлечён shortcode: {shortcode}")
            data = download_instagram_reel_by_shortcode(shortcode)
            print(f"[LOG] Данные с RapidAPI: {data}")
            video_url = data.get("video_url") or data.get("video_versions", [{}])[0].get("url")
            # Получаем картинку (thumbnail)
            image_url = None
            if 'image_versions2' in data and 'candidates' in data['image_versions2']:
                image_url = data['image_versions2']['candidates'][0].get('url')
            elif 'thumbnail' in data:
                image_url = data['thumbnail']
            description = data.get("caption") or data.get("description")
            if isinstance(description, dict):
                description = description.get('text', '')
            print(f"[LOG] Описание: {description}")
            if not video_url:
                print("[ERROR] Не удалось получить ссылку на видео!")
                raise Exception("Не удалось получить ссылку на видео!")
            with tempfile.TemporaryDirectory() as temp_dir:
                video_path = os.path.join(temp_dir, "video.mp4")
                print(f"[LOG] Скачиваем видео по ссылке: {video_url}")
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': video_path,
                    'quiet': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                print(f"[LOG] Видео скачано: {video_path}")
                audio_path = os.path.join(temp_dir, "audio.wav")
                print(f"[LOG] Извлекаем аудио из видео...")
                try:
                    clip = VideoFileClip(video_path)
                    clip.audio.write_audiofile(audio_path, logger=None)
                    print(f"[LOG] Аудио извлечено: {audio_path}")
                except Exception as e:
                    print(f"[ERROR] Ошибка при извлечении аудио: {e}")
                    raise Exception(f"Ошибка при извлечении аудио: {e}")
                print(f"[LOG] Транскрибируем аудио...")
                transcript = await transcribe_audio(audio_path)
                print(f"[LOG] Транскрипция: {transcript}")
                text_for_gpt = ""
                if description:
                    text_for_gpt += description + "\n"
                if transcript:
                    text_for_gpt += transcript
                print(f"[LOG] Текст для GPT:\n{text_for_gpt}")
                if not text_for_gpt.strip():
                    print("[ERROR] Нет текста для анализа (ни описания, ни аудио)")
                    raise Exception("Нет текста для анализа (ни описания, ни аудио)")
                print(f"[LOG] Отправляем текст в GPT...")
                recipe = await extract_recipe_from_text(text_for_gpt)
                recipe['description'] = description or ""
                recipe['source_url'] = url
                recipe['image_url'] = image_url or ""
                print(f"[LOG] Ответ от GPT: {recipe}")
                return recipe
        except Exception as e:
            print(f"[ERROR] Ошибка при обработке Instagram URL: {e}")
            raise Exception(f"Error extracting recipe: {e}")

    async def process_tiktok(self, url: str) -> Dict[str, Any]:
        """
        Обрабатывает TikTok видео и извлекает рецепт
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                video_path = os.path.join(temp_dir, 'video.mp4')
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': video_path,
                    'quiet': True,
                    'writethumbnail': True,
                    'writeinfojson': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                # Получаем thumbnail
                image_url = info.get('thumbnail', "")
                description = info.get('description', "")
                print(f"[LOG] Описание TikTok: {description}")
                audio_path = os.path.join(temp_dir, "audio.wav")
                print(f"[LOG] Извлекаем аудио из видео TikTok...")
                try:
                    clip = VideoFileClip(video_path)
                    clip.audio.write_audiofile(audio_path, logger=None)
                    print(f"[LOG] Аудио TikTok извлечено: {audio_path}")
                except Exception as e:
                    print(f"[ERROR] Ошибка при извлечении аудио TikTok: {e}")
                    raise Exception(f"Ошибка при извлечении аудио TikTok: {e}")
                print(f"[LOG] Транскрибируем аудио TikTok...")
                transcript = await transcribe_audio(audio_path)
                print(f"[LOG] Транскрипция TikTok: {transcript}")
                text_for_gpt = ""
                if description:
                    text_for_gpt += description + "\n"
                if transcript:
                    text_for_gpt += transcript
                print(f"[LOG] Текст для GPT TikTok:\n{text_for_gpt}")
                if not text_for_gpt.strip():
                    print("[ERROR] Нет текста для анализа TikTok (ни описания, ни аудио)")
                    raise Exception("Нет текста для анализа TikTok (ни описания, ни аудио)")
                print(f"[LOG] Отправляем текст в GPT TikTok...")
                recipe = await extract_recipe_from_text(text_for_gpt)
                recipe['description'] = description or ""
                recipe['source_url'] = url
                recipe['image_url'] = image_url or ""
                print(f"[LOG] Ответ от GPT TikTok: {recipe}")
                return recipe
        except Exception as e:
            print(f"[ERROR] Ошибка при обработке TikTok: {e}")
            raise Exception(f"Error processing TikTok: {str(e)}")

    async def process_web_page(self, url: str) -> Dict[str, Any]:
        """
        Обрабатывает веб-страницу и извлекает рецепт
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            import json as pyjson
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Ищем og:image
            image_url = ""
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_url = og_image['content']
            else:
                # fallback: ищем самое большое изображение
                images = soup.find_all('img')
                max_area = 0
                for img in images:
                    try:
                        width = int(img.get('width', 0))
                        height = int(img.get('height', 0))
                        area = width * height
                        if area > max_area and img.get('src'):
                            image_url = img['src']
                            max_area = area
                    except Exception:
                        continue
            # 1. Пробуем найти JSON-LD с рецептом
            recipe_text = ""
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = pyjson.loads(script.string)
                    if isinstance(data, list):
                        for entry in data:
                            if entry.get('@type') == 'Recipe':
                                recipe_text = pyjson.dumps(entry, ensure_ascii=False)
                                break
                    elif data.get('@type') == 'Recipe':
                        recipe_text = pyjson.dumps(data, ensure_ascii=False)
                        break
                except Exception:
                    continue
            # 2. Если не нашли — ищем блоки с классами recipe, ingredients, instructions, steps
            if not recipe_text:
                keywords = ['recipe', 'ingredients', 'instruction', 'step']
                found_blocks = []
                for kw in keywords:
                    found_blocks += soup.find_all(class_=lambda c: c and kw in c.lower())
                texts = [b.get_text(separator=" ", strip=True) for b in found_blocks if b]
                recipe_text = "\n".join(texts)
            # 3. Если не нашли — ищем большие списки и параграфы подряд
            if not recipe_text:
                blocks = []
                for tag in soup.find_all(['ul', 'ol', 'p']):
                    text = tag.get_text(separator=" ", strip=True)
                    if len(text) > 30:
                        blocks.append(text)
                recipe_text = "\n".join(blocks)
            # 4. Если ничего не нашли — fallback: первые 1000 символов текста страницы
            if not recipe_text:
                recipe_text = soup.get_text(separator=" ", strip=True)[:1000]
            print(f"[LOG] Извлечён текст рецепта для GPT: {recipe_text[:500]}...")
            recipe = await extract_recipe_from_text(recipe_text)
            recipe['description'] = recipe_text[:500] or ""
            recipe['source_url'] = url
            recipe['image_url'] = image_url or ""
            print(f"[LOG] Ответ от GPT Web: {recipe}")
            return recipe
        except Exception as e:
            print(f"[ERROR] Ошибка при обработке web page: {e}")
            raise Exception(f"Error processing web page: {str(e)}")

    async def process_url(self, url: str) -> Dict[str, Any]:
        """Обрабатывает URL и возвращает данные рецепта."""
        if self.is_instagram_url(url):
            return await self.process_instagram_url(url)
        elif "tiktok.com" in url:
            return await self.process_tiktok(url)
        else:
            return await self.process_web_page(url) 