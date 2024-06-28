import logging
import requests
import json
import asyncio
from urllib.parse import urlencode, quote
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties

# Загрузка конфигурации из файла config.json
with open('config.json', 'r') as config_file:
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
    city_name_encoded = quote(city_name.encode('utf-8'))
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

async def on_shutdown(bot: Bot):
    await bot.session.close()

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(bot)

if __name__ == "__main__":
    asyncio.run(main())
