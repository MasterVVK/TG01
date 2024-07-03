import time

def fetch_data_sync(name):
    print(f"Начало запроса данных {name}...")
    time.sleep(2)  # Симуляция длительной операции
    print(f"Данные {name} получены")
    return f"Данные {name}"

def main_sync():
    start_time = time.time()

    data1 = fetch_data_sync("1")
    data2 = fetch_data_sync("2")

    print(f"Результаты: {data1}, {data2}")
    print(f"Время выполнения: {time.time() - start_time} секунд")

# Запуск программы
if __name__ == "__main__":
    main_sync()
