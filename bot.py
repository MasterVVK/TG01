import logging
import requests
import json
import os
import asyncio
from urllib.parse import quote
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from student_registration import router as student_router  # Импорт маршрутизатора
from translator_handler import router as translator_router  # Импорт маршрутизатора для перевода
import aiohttp  # Импорт aiohttp для асинхронных запросов

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

# Создание диспетчера и состояния
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(student_router)  # Включение маршрутизатора
dp.include_router(translator_router)  # Включение маршрутизатора для перевода

class VoiceState(StatesGroup):
    waiting_for_voice = State()

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
    await message.reply(
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Получить помощь\n"
        "/weather &lt;город&gt; - Получить прогноз погоды для указанного города\n"
        "/voice - Записать и отправить голосовое сообщение\n"
        "/register - Зарегистрировать нового студента\n"  # Добавлена команда /register
        "Просто отправьте текстовое сообщение, чтобы перевести его на английский язык.\n"
        "Отправьте фотографию, чтобы сохранить ее на сервере."
    )

# Обработчик текста "что такое ИИ?"
@dp.message(F.text == "что такое ИИ?")
async def aitext(message: Message):
    await message.answer(
        'Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека; наука и технология создания интеллектуальных машин, особенно интеллектуальных компьютерных программ'
    )

# Функция для получения прогноза погоды
async def get_weather(city_name):
    city_name_encoded = quote(city_name, safe='')
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city_name_encoded}&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            logging.debug(f"Запрос к WeatherAPI: {response.url}")
            if response.status == 200:
                data = await response.json()
                logging.debug(f"Ответ от WeatherAPI: {data}")
                if 'current' in data:
                    weather_description = data['current']['condition']['text']
                    temperature = data['current']['temp_c']
                    humidity = data['current']['humidity']
                    icon_url = "http:" + data['current']['condition']['icon']
                    return f"Погода в {city_name}:\nТемпература: {temperature}°C\nОписание: {weather_description}\nВлажность: {humidity}%", icon_url
            else:
                logging.error(f"Ошибка при запросе к WeatherAPI: {response.status} {await response.text()}")
                return None, None

# Команда /weather
@dp.message(Command("weather"))
async def send_weather(message: Message):
    logging.info("Получена команда /weather")
    args = message.text.split(' ', 1)
    city_name = args[1] if len(args) > 1 else DEFAULT_CITY_NAME

    weather, icon_url = await get_weather(city_name)
    if weather and icon_url:
        logging.info(f"Отправка прогноза погоды: {weather}")
        await message.answer_photo(photo=icon_url, caption=weather)
    else:
        logging.warning(f"Не удалось получить данные о погоде для города: {city_name}")
        await message.reply("Не удалось получить данные о погоде. Попробуйте позже.")

# Команда /voice
@dp.message(Command("voice"))
async def send_voice_prompt(message: Message, state: FSMContext):
    logging.info("Получена команда /voice")
    await message.reply("Пожалуйста, запишите и отправьте голосовое сообщение.")
    await state.set_state(VoiceState.waiting_for_voice)

# Обработчик голосовых сообщений
@dp.message(F.voice, StateFilter(VoiceState.waiting_for_voice))
async def handle_voice(message: Message, state: FSMContext):
    logging.info("Получено голосовое сообщение")
    file_info = await bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    file_name = os.path.join("voice", file_info.file_unique_id + ".ogg")
    os.makedirs("voice", exist_ok=True)
    await bot.download_file(file_path, file_name)
    await message.reply_voice(message.voice.file_id)
    await state.clear()



async def on_shutdown(bot: Bot):
    await bot.session.close()

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(bot)

if __name__ == "__main__":
    asyncio.run(main())
