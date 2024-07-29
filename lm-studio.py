import csv
import json
import requests


class LMStudioClient:
    def __init__(self, server_url="http://localhost:1234"):
        """
        Инициализирует клиента API для взаимодействия с сервером LMStudio.
        :param server_url: Базовый URL сервера для отправки запросов.
        """
        self.server_url = server_url
        self.model_endpoint = f"{self.server_url}/v1/chat/completions"

    def set_system_prompt(self, system_prompt):
        """
        Устанавливает системный запрос (инструкцию), который будет использоваться в диалогах.
        :param system_prompt: Системный запрос для модели.
        """
        self.system_prompt = system_prompt

    def ask_question(self, question):
        """
        Отправляет вопрос модели и возвращает ответ.
        :param Вопрос, который нужно задать модели.
        :return: Ответ модели в формате JSON.
        """
        headers = {'Content-Type': 'application/json'}
        payload = {
            "model": "SanctumAI/Meta-Llama-3-8B-Instruct-GGUF/meta-llama-3-8b-instruct.f16.gguf",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]
        }
        response = requests.post(self.model_endpoint, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Failed to get response from model: {response.status_code}, {response.text}")


class NameSynthesizer:
    def __init__(self, lm_client):
        """
        Инициализирует объект, который использует LMStudioClient для генерации синонимов.
        :param lm_client (LMStudioClient): Экземпляр клиента для отправки запросов к модели.
        """
        self.lm_client = lm_client
        system_prompt = """Задача: Сгенерировать список синонимов для заданной строки name, которая обозначает термин или наименование в контексте строительных материалов из строки params.
         
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
        - JSON должен иметь правильную структуру"""
        self.lm_client.set_system_prompt(system_prompt)

    def generate_synonyms(self, name, params):
        """
        Генерирует синонимы для указанного наименования с учетом параметров.
        :param name: Наименование, для которого нужно сгенерировать синонимы.
        :param params: Параметры, уточняющие наименование.
        :return: Список синонимов для наименования.
        """
        question = '{ "name": "' + name + '", "params": "' + params + '" }'
        response = self.lm_client.ask_question(question)
        return json.loads(response)['syn_names'] if response else []


class NameExtractor:
    def __init__(self, lm_client):
        """
        Инициализирует объект для извлечения наименования и параметров из строки.
        :param lm_client (LMStudioClient): Экземпляр клиента для отправки запросов к модели.
        """
        self.lm_client = lm_client
        system_prompt = """Задача: Разделить строку на наименование и параметры товара.

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
                { "name": "соль", "params": "Натриевая 2-метил 4-хлорфенокси-уксусной кислоты (2м-4х)" }
                Входная строка: "Листы хризотилцементные плоские прессованные, толщина 8 мм"
                Ожидаемый вывод: 
                { "name": "лист", "params": "хризотилцементный плоский прессованный, толщина 8 мм" }

                Требования:
                - Строго следовать инструкциям для извлечения наименования и параметров.
                - Результаты должны быть точно сформированы в JSON формате.
                - Обработка должна быть корректной для строк с разной структурой и длиной параметров.
                - В качестве ответа ТОЛЬКО JSON.
                - JSON в ТОЛЬКО В ОДНУ строку
                - JSON должен иметь правильную структуру"""
        self.lm_client.set_system_prompt(system_prompt)

    def extract_name(self, string):
        """
        Извлекает наименование и параметры из строки
        :param string: Строка для обработки
        :return: Наименование и параметры товара
        """
        response = self.lm_client.ask_question(string)
        return json.loads(response)['name'], json.loads(response)['params'] if response else ('', '')


def name_extractor(agent):
    """
    Обрабатывает CSV файл, извлекает из каждой строки наименование и параметры товара,
    и сохраняет результаты в новый CSV файл.
    :param agent: Экземпляр класса NameExtractor
    """
    with open('ksr.csv', 'r', newline='', encoding='utf-8') as file:
        reader = list(csv.DictReader(file))
        total_rows = len(reader)
        with open('extracted.csv', 'w', newline='', encoding='utf-8') as extracted_file:
            extracted_writer = csv.DictWriter(extracted_file, fieldnames=['name', 'params'])
            extracted_writer.writeheader()
            for index, row in enumerate(reader):
                name, params = agent.extract_name(row['name'].lower())
                extracted_writer.writerow({'name': name, 'params': params})
                print(f"Extracted {index + 1}/{total_rows} rows")
                # print(f'name: {name}\nparams: {params}')


def name_synthesizer(agent):
    """
    Читает файл с извлеченными наименованиями и параметрами, генерирует синонимы,
    и сохраняет их в другой CSV файл.
    :param agent: Экземпляр класса NameSynthesizer
    """
    with open('extracted.csv', 'r', newline='', encoding='utf-8') as extracted_file:
        extracted_reader = list(csv.DictReader(extracted_file))
        total_rows = len(extracted_reader)
        with open('dictionary.csv', 'w', newline='', encoding='utf-8') as dict_file:
            dict_writer = csv.DictWriter(dict_file, fieldnames=['name', 'syns'])
            dict_writer.writeheader()
            dictionary = {}
            for index, row in enumerate(extracted_reader):
                name = row['name']
                synonyms = agent.generate_synonyms(name, row['params'])
                if name in dictionary:
                    dictionary[name].update(synonyms)
                else:
                    dictionary[name] = set(synonyms)
                dict_writer.writerow({'name': name, 'syns': ','.join(dictionary[name])})
                print(f"Updated {index + 1}/{total_rows} rows in dictionary")


if __name__ == "__main__":
    client = LMStudioClient()
    client_ = LMStudioClient()

    extractor = NameExtractor(client_)
    synthesizer = NameSynthesizer(client)

    name_extractor(extractor)
    name_synthesizer(synthesizer)
