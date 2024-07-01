from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import sqlite3

# Создание маршрутизатора
router = Router()

# Настройка базы данных
conn = sqlite3.connect('school_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        grade TEXT
    )
''')
conn.commit()

# Состояния для регистрации студента
class StudentRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_grade = State()

# Команда /register
@router.message(Command("register"))
async def register_student(message: Message, state: FSMContext):
    await message.reply("Введите имя студента:")
    await state.set_state(StudentRegistration.waiting_for_name)

# Обработчик имени студента
@router.message(StudentRegistration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Введите возраст студента:")
    await state.set_state(StudentRegistration.waiting_for_age)

# Обработчик возраста студента
@router.message(StudentRegistration.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Введите класс студента:")
    await state.set_state(StudentRegistration.waiting_for_grade)

# Обработчик класса студента
@router.message(StudentRegistration.waiting_for_grade)
async def process_grade(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data['name']
    age = user_data['age']
    grade = message.text

    cursor.execute('INSERT INTO students (name, age, grade) VALUES (?, ?, ?)', (name, age, grade))
    conn.commit()

    await message.reply(f"Студент {name}, возраст {age}, класс {grade} был успешно зарегистрирован!")
    await state.clear()
