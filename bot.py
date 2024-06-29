import logging
import requests
import json
import os
import asyncio
from urllib.parse import quote
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from googletrans import Translator

# Загрузка конфигурации из файла config.json с явным указанием кодировки utf-8
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

API_TOKEN = config['API_TOKEN']
WEATHER_API_KEY = config['WEATHER_API_KEY']
DEFAULT_CITY_NAME = config['DEFAULT_CITY_NAME']

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Установите уровень DEBUG для подробного логирования
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Создание объекта бота с кастомной сессией и настройками
session = AiohttpSession()
bot = Bot(
    token=API_TOKEN,
    session=session,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Создание диспетчера
dp = Dispatcher()

# Папка для сохранения изображений
IMG_DIR = "img"
os.makedirs(IMG_DIR, exist_ok=True)

# Обработчик фотографий
@dp.message(F.photo)
async def handle_photos(message: Message):
    logging.info("Получена фотография")
    for photo in message.photo:
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        file_name = os.path.join(IMG_DIR, file_info.file_unique_id + ".jpg")
        await bot.download_file(file_path, file_name)
        await message.reply(f"Фото сохранено как {file_name}")

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    logging.info("Получена команда /start")
    await message.reply("Привет! Я бот, созданный с помощью Aiogram. Используйте команду /weather &lt;город&gt; для получения прогноза погоды.")

# Команда /help
@dp.message(Command("help"))
async def send_help(message: Message):
    logging.info("Получена команда /help")
    await message.reply("Доступные команды:\n/start - Начать работу с ботом\n/help - Получить помощь\n/weather &lt;город&gt; - Получить прогноз погоды для указанного города")

# Обработчик текста "что такое ИИ?"
@dp.message(F.text == "что такое ИИ?")
async def aitext(message: Message):
    await message.answer(
        'Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека; наука и технология создания интеллектуальных машин, особенно интеллектуальных компьютерных программ'
    )

# Команда /weather
@dp.message(Command("weather"))
async def send_weather(message: Message):
    logging.info("Получена команда /weather")
    args = message.text.split(' ', 1)
    city_name = args[1] if len(args) > 1 else DEFAULT_CITY_NAME

    weather = get_weather(city_name)
    if weather:
        logging.info(f"Отправка прогноза погоды: {weather}")
        await message.reply(weather)
    else:
        logging.warning(f"Не удалось получить данные о погоде для города: {city_name}")
        await message.reply("Не удалось получить данные о погоде. Попробуйте позже.")

# Функция для получения прогноза погоды
def get_weather(city_name):
    city_name_encoded = quote(city_name, safe='')
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city_name_encoded}&lang=ru"
    response = requests.get(url)
    logging.debug(f"Запрос к WeatherAPI: {response.url}")
    if response.status_code == 200:
        data = response.json()
        logging.debug(f"Ответ от WeatherAPI: {data}")
        if 'current' in data:
            weather_description = data['current']['condition']['text']
            temperature = data['current']['temp_c']
            return f"Погода в {city_name}:\nТемпература: {temperature}°C\nОписание: {weather_description}"
    else:
        logging.error(f"Ошибка при запросе к WeatherAPI: {response.status_code} {response.text}")
        return None

# Команда /voice
@dp.message(Command("voice"))
async def send_voice_prompt(message: Message):
    logging.info("Получена команда /voice")
    await message.reply("Пожалуйста, запишите и отправьте голосовое сообщение.")

# Обработчик голосовых сообщений
@dp.message(F.voice)
async def handle_voice(message: Message):
    logging.info("Получено голосовое сообщение")
    file_info = await bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    file_name = os.path.join("voice", file_info.file_unique_id + ".ogg")
    os.makedirs("voice", exist_ok=True)
    await bot.download_file(file_path, file_name)
    await message.reply_voice(message.voice.file_id)

# Перевод текста на английский язык
translator = Translator()

@dp.message(F.text)
async def translate_to_english(message: Message):
    logging.info("Получено текстовое сообщение для перевода")
    try:
        translation = translator.translate(message.text, dest='en')
        await message.reply(translation.text)
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        await message.reply("Ошибка перевода. Попробуйте позже.")

async def on_shutdown(bot: Bot):
    await bot.session.close()

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(bot)

if __name__ == "__main__":
    asyncio.run(main())
