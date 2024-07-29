import requests
import json
import csv


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LMStudioClient:
    def __init__(self, server_url="http://localhost:1234"):
        self.server_url = server_url
        self.model_endpoint = f"{self.server_url}/v1/chat/completions"

    def ask_question(self, question, system_prompt):
        headers = {'Content-Type': 'application/json'}
        payload = {
            "model": "SanctumAI/Meta-Llama-3-8B-Instruct-GGUF/meta-llama-3-8b-instruct.f16.gguf",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        }
        response = requests.post(self.model_endpoint, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else None


def extract_name(client, line):
    system_prompt = """Задача: Разделить строку на наименование и параметры товара. Создать ТОЛЬКО json ТОЛЬКО в одну строку.

                    Шаги выполнения:

                    1. Определить наименование товара:
                       - Наименование определяется как первое существительное в строке, которое является самостоятельным и может описывать товар без дополнительных уточнений.
                       - Наименование не должно содержать прилагательные или другие модификаторы, которые уточняют его свойства (например, материал, цвет, размер).
                       - Пропустить любые слова, являющиеся прилагательными или частями сложных наименований, если они не представляют собой наиболее общее описание товара.
                       - Привести наименование из name к единственному числу (например: "листы" ПРИВЕСТИ К "лист")

                    2. Определить параметры товара:
                       - После выделения наименования, все остальное в строке рассматривается как параметры товара.
                       - Параметры могут включать прилагательные, типы, размеры, материалы и другие характеристики товара.
                       - Привести параметры из params к единственному числу (например: "хризотилцементные плоские прессованные, толщина 8 мм" ПРИВЕСТИ К "хризотилцементный плоский прессованный, толщина 8 мм")


                    Формат вывода: JSON объект с двумя ключами в ОДНУ СТРОКУ без переносов:
                    - "name": одно слово в единственном числе.
                    - "params": строка с параметрами товара в единственном числе.

                    Пример работы:
                    Входная строка: "Натриевая соль 2-метил 4-хлорфенокси-уксусной кислоты (2м-4х)"
                    Ожидаемый вывод: 
                    {"name": "соль", "params": "Натриевая 2-метил 4-хлорфенокси-уксусной кислоты (2м-4х)"}
                    Входная строка: "Листы хризотилцементные плоские прессованные, толщина 8 мм"
                    Ожидаемый вывод: 
                    {"name": "лист", "params": "хризотилцементный плоский прессованный, толщина 8 мм"}

                    Требования:
                    - Строго следовать инструкциям для извлечения наименования и параметров.
                    - Результаты должны быть точно сформированы в JSON формате.
                    - Обработка должна быть корректной для строк с разной структурой и длиной параметров.
                    - В качестве ответа ТОЛЬКО JSON.
                    - JSON в ТОЛЬКО В ОДНУ строку
                    - JSON должен иметь правильную структуру"""
    response = client.ask_question(line.lower(), system_prompt)
    response_data = json.loads(response)
    return response_data['name'], response_data['params']


def generate_synonyms(client, name, params):
    system_prompt = """Задача: Сгенерировать только json в одну строку, содержащий список синонимов для заданной строки name, которая обозначает термин или наименование в контексте строительных материалов из строки params. Создать ТОЛЬКО json ТОЛЬКО в одну строку.

            Шаги выполнения:

            1. Прочитать входную строку
            2. Анализ входной строки params для определения контекста (строительные материалы, инструменты, технологии).
            3. Поиск в базах данных и открытых источниках для сбора информации о возможных синонимах и аналогах входной строки.
            4. Анализ собранной информации для формирования списка релевантных синонимов для строки name.
            5. Проверка каждого синонима для строки name на уникальность и отсутствие повторов в списке.
            6. Формирование итогового массива синонимов для строки name в формате json в ОДНУ СТРОКУ без переносов.

            Формат вывода: JSON массив со строками syn_names:
            {"name": "наименование_с_параметрами", "syn_names": ["синоним1", "синоним2", ...]}

            Пример работы:
            Входная строка: наименование и параметры
            {"name": "Фанера", "params": "ламинированная ФОБ (FOB) F/F 1220х2440х12 мм"}

            Ожидаемый вывод: наименование и массив синонимов
            {"name": "Фанера", "syn_names": [ "Фанерный лист", "Шпон", "Листовой материал", "Многослойный материал", "Слоистый древесный материал", "Облицовочный материал", "Склеенный древесный лист" ]}

            Требования:
            - Строго следовать инструкциям для извлечения наименования и параметров.
            - Результаты должны быть точно сформированы в JSON формате.
            - Обработка должна быть корректной для строк с разной структурой и длиной параметров.
            - В качестве ответа ТОЛЬКО JSON.
            - JSON в ТОЛЬКО В ОДНУ строку
            - JSON должен иметь правильную структуру"""
    question = json.dumps({"name": name, "params": params})
    response = client.ask_question(question, system_prompt)
    response_data = json.loads(response)
    return response_data['syn_names'] if response else []


def process_files():
    client = LMStudioClient()

    with open('src/ksr.csv', 'r', newline='', encoding='utf-8') as infile, \
            open('src/extracted.csv', 'w', newline='', encoding='utf-8') as extracted_file, \
            open('src/dictionary.csv', 'w', newline='', encoding='utf-8') as dict_file:

        reader = list(csv.DictReader(infile))
        total = len(reader)
        extracted_writer = csv.DictWriter(extracted_file, fieldnames=['name', 'params'])
        dict_writer = csv.DictWriter(dict_file, fieldnames=['name', 'syns'])
        extracted_writer.writeheader()
        dict_writer.writeheader()
        dictionary = {}

        for i, row in enumerate(reader, 1):
            print(bcolors.UNDERLINE + row['name'] + bcolors.ENDC)
            name, params = extract_name(client, row['name'])
            print('name: ' + bcolors.OKBLUE + name + bcolors.ENDC)
            print('params: ' + bcolors.OKCYAN + params + bcolors.ENDC)
            synonyms = generate_synonyms(client, name, params)
            print('syns: ' + bcolors.OKGREEN + str(synonyms) + bcolors.ENDC)
            extracted_writer.writerow({'name': name, 'params': params})
            if name in dictionary:
                dictionary[name].update(set(synonyms))
            else:
                dictionary[name] = set(synonyms)
            dict_writer.writerow({'name': name, 'syns': ','.join(dictionary[name])})
            print(f"Processed {i}/{total} rows")


if __name__ == "__main__":
    process_files()
