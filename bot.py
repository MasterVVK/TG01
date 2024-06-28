import logging
import requests
import json
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode

# Загрузка конфигурации из файла config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

API_TOKEN = config['API_TOKEN']
WEATHER_API_KEY = config['WEATHER_API_KEY']
CITY_NAME = config['CITY_NAME']

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объекта бота
bot = Bot(token=API_TOKEN)
# Создание диспетчера
dp = Dispatcher(bot)

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, созданный с помощью Aiogram. Используйте команду /weather для получения прогноза погоды.")

# Команда /help
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply("Доступные команды:\n/start - Начать работу с ботом\n/help - Получить помощь\n/weather - Получить прогноз погоды")

# Команда /weather
@dp.message_handler(commands=['weather'])
async def send_weather(message: types.Message):
    weather = get_weather(CITY_NAME)
    if weather:
        await message.reply(weather, parse_mode=ParseMode.HTML)
    else:
        await message.reply("Не удалось получить данные о погоде. Попробуйте позже.")

# Функция для получения прогноза погоды
def get_weather(city_name):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city_name}&lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'current' in data:
            weather_description = data['current']['condition']['text']
            temperature = data['current']['temp_c']
            return f"Погода в {city_name}:\nТемпература: {temperature}°C\nОписание: {weather_description}"
    else:
        return None

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
