import requests
import json
import csv

ollama_url = "http://10.0.50.2:11434"
model_name = "llama3.1:70b"
system_prompt = """
Входные данные - строка, которая содержит наименование товара и его параметры.
Наименование товара - первое слое слово в строке.

Проверь строку: если в строке наименование не является первым словом, переставь так, чтобы наименование товара стало первым, и следом за ним шли его параметры.

Пример:
ВВОД: 'лестничный марш железобетонный 1лм 30.12.15-4 бетон в22,5 объём 0,68 м3 расход арматура 18,31 кг'
ВЫВОД: 'марш лестничный железобетонный 1лм 30.12.15-4 бетон в22,5 объём 0,68 м3 расход арматура 18,31 кг'
ВВОД: 'лист хризотилцементный волнистый профиль 40/150 7-волновой толщина 5,2 мм'
ВЫВОД: 'лист хризотилцементный волнистый профиль 40/150 7-волновой толщина 5,2 мм'

Важно: 
- Вноси необходимые корректиры ТОЛЬКО ЕСЛИ наименование товара во входной строке не является первым словом.
- Если входная строка не нуждается в обработке, в качестве вывода используй входную строку
- В качестве вывода - ТОЛЬКО ВЫВОД (например: 'лист хризотилцементный волнистый профиль 40/150 7-волновой толщина 5,2 мм')
- Не выводи ничего кроме строки
- Используй ТОЛЬКО входную строку
- Используй ВСЮ строку ЦЕЛИКОМ
- НЕ добавляй новых слов
- Сохрани ВСЕ значения строки
- Строго следуй инструкциям
"""  # Системный промпт


def process_csv(csv_file, output_file):
    """
    Обрабатывает цсв файл, отправляя данные в модель оллама и сохраняя результаты в жисон файл.
    :param csv_file: Путь к цсв файлу
    :param output_file: Путь к выходному жисон файлу
    :return:
    """

    results = []

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            prompt = f"{system_prompt}\n\nДанные:\n{json.dumps(row, ensure_ascii=False)}"
            response = get_ollama_response(prompt)
            results.append({
                "input": row,
                "output": response
            })

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)


def get_ollama_response(prompt):
    """
    Отправляет запрос к модели Ollama и возвращает ответ.
    :param prompt: Запрос к модели
    :return: Ответ модели.
    """

    headers = {'Content-Type': 'application/json'}
    data = {"model": model_name, "prompt": prompt}

    response = requests.post(f"{ollama_url}/api/generate", headers=headers, json=data)
    response.raise_for_status()
    return response.json()['response']


csv_file = "src/ksr.csv"
output_file = "output.json"
process_csv(csv_file, output_file)

