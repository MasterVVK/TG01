import asyncio
import time

async def fetch_data_async(name):
    print(f"Начало запроса данных {name}...")
    await asyncio.sleep(2)  # Симуляция длительной операции
    print(f"Данные {name} получены")
    return f"Данные {name}"

async def main_async():
    start_time = time.time()

    task1 = asyncio.create_task(fetch_data_async("1"))
    task2 = asyncio.create_task(fetch_data_async("2"))

    data1 = await task1
    data2 = await task2

    print(f"Результаты: {data1}, {data2}")
    print(f"Время выполнения: {time.time() - start_time} секунд")

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main_async())
