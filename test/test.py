import requests
import json
import csv


class LMStudioClient:
    def __init__(self, server_url="http://localhost:1234"):
        self.server_url = server_url
        self.model_endpoint = f"{self.server_url}/v1/chat/completions"

    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt

    def ask_question(self, question):
        headers = {'Content-Type': 'application/json'}
        payload = {
            "model": "SanctumAI/Meta-Llama-3-8B-Instruct-GGUF/meta-llama-3-8b-instruct.f16.gguf",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]
        }
        response = requests.post(self.model_endpoint, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else None


class NameSynthesizer:
    def __init__(self, lm_client):
        self.lm_client = lm_client
        self.lm_client.set_system_prompt("""Задача: Сгенерировать список синонимов для заданной строки name, которая обозначает термин или наименование в контексте строительных материалов из строки params.
         
        Шаги выполнения:
         
        1. Прочитать входную строку
        2. Анализ входной строки params для определения контекста (строительные материалы, инструменты, технологии).
        3. Поиск в базах данных и открытых источниках для сбора информации о возможных синонимах и аналогах входной строки.
        4. Анализ собранной информации для формирования списка релевантных синонимов для строки name.
        5. Проверка каждого синонима для строки name на уникальность и отсутствие повторов в списке.
        6. Формирование итогового массива синонимов для строки name в формате json в ОДНУ СТРОКУ без переносов.
         
        Формат вывода: JSON массив со строками syn_names:
        { "name": "наименование_с_параметрами", "syn_names": ["синоним1", "синоним2", ...] }
         
        Пример работы:
        Входная строка: наименование и параметры
        { "name": "Фанера", "params": "ламинированная ФОБ (FOB) F/F 1220х2440х12 мм" }
         
        Ожидаемый вывод: наименование и массив синонимов
        { "name": "Фанера", "syn_names": [ "Фанерный лист", "Шпон", "Листовой материал", "Многослойный материал", "Слоистый древесный материал", "Облицовочный материал", "Склеенный древесный лист" ] }
         
        Требования:
        - Строго следовать инструкциям для извлечения наименования и параметров.
        - Результаты должны быть точно сформированы в JSON формате.
        - Обработка должна быть корректной для строк с разной структурой и длиной параметров.
        - В качестве ответа ТОЛЬКО JSON.
        - JSON в ТОЛЬКО В ОДНУ строку
        - JSON должен иметь правильную структуру""")

    def generate_synonyms(self, name, params):
        question = '{ "name": "' + name + '", "params": "' + params + '" }'
        response = self.lm_client.ask_question(question)
        return json.loads(response)['syn_names'] if response else []


class NameExtractor:
    def __init__(self, lm_client):
        self.lm_client = lm_client
        self.lm_client.set_system_prompt("""Задача: Разделить строку на наименование и параметры товара.

        Шаги выполнения:
        
        1. Определить наименование товара:
           - Наименование определяется как первое существительное в строке, которое является самостоятельным и может описывать товар без дополнительных уточнений.
           - Наименование не должно содержать прилагательные или другие модификаторы, которые уточняют его свойства (например, материал, цвет, размер).
           - Пропустить любые слова, являющиеся прилагательными или частями сложных наименований, если они не представляют собой наиболее общее описание товара.
        
        2. Определить параметры товара:
           - После выделения наименования, все остальное в строке рассматривается как параметры товара.
           - Параметры могут включать прилагательные, типы, размеры, материалы и другие характеристики товара.
        
        Формат вывода: JSON объект с двумя ключами в ОДНУ СТРОКУ без переносов:
        - "name": одно слово.
        - "params": строка с параметрами товара.
        
        Пример работы:
        Входная строка: "Натриевая соль 2-метил 4-хлорфенокси-уксусной кислоты (2м-4х)"
        Ожидаемый вывод: 
        { "name": "соль", "params": "Натриевая 2-метил 4-хлорфенокси-уксусной кислоты (2м-4х)" }
        Входная строка: "Листы хризотилцементные плоские прессованные, толщина 8 мм"
        Ожидаемый вывод: 
        { "name": "листы", "params": "хризотилцементные плоские прессованные, толщина 8 мм" }
        
        Требования:
        - Строго следовать инструкциям для извлечения наименования и параметров.
        - Результаты должны быть точно сформированы в JSON формате.
        - Обработка должна быть корректной для строк с разной структурой и длиной параметров.
        - В качестве ответа ТОЛЬКО JSON.
        - JSON в ТОЛЬКО В ОДНУ строку
        - JSON должен иметь правильную структуру""")

    def extract_name(self, string):
        response = self.lm_client.ask_question(string)
        return json.loads(response)['name'], json.loads(response)['params'] if response else ('', '')


if __name__ == "__main__":
    client = LMStudioClient()
    client_ = LMStudioClient()
    synthesizer = NameSynthesizer(client)
    extractor = NameExtractor(client_)
    start_row = 100

    with open('ksr.csv', 'r', newline='', encoding='utf-8') as file, open('dictionary.csv', 'r+', newline='',
                                                                          encoding='utf-8') as dict_file:
        reader = csv.DictReader(file)
        dict_reader = csv.DictReader(dict_file)
        dict_writer = csv.DictWriter(dict_file, fieldnames=dict_reader.fieldnames)

        existing_data = {row['name']: row['syns'].split(',') for row in dict_reader}
        dict_file.seek(0)
        dict_writer.writeheader()

        for i, row in enumerate(reader, start=1):
            if i < start_row:
                continue
            name, params = extractor.extract_name(row['name'])
            synonyms = synthesizer.generate_synonyms(name, params)
            if name in existing_data:
                existing_data[name].extend(x for x in synonyms if x not in existing_data[name])
            else:
                existing_data[name] = synonyms
            dict_writer.writerow({'name': name, 'syns': ','.join(set(existing_data[name]))})
            print(f"Processed {i}/{start_row - 1 + len(list(reader))}")
