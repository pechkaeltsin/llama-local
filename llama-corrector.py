import json
import requests
import pandas as pd


class BColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
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


def correct_names(data):
    client = LMStudioClient()
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
    """

    for item in data:
        full_text = f"{item['name']} {item['params']}"
        print('---')
        print(full_text)
        attempt_count = 0
        while attempt_count < 3:
            try:
                correct_name = client.ask_question(full_text, system_prompt)
                if correct_name:
                    item['name'], item['params'] = correct_name.split(' ', 1)
                    print(BColors.RED + item['name'] + BColors.ENDC + ' ' +
                          BColors.BLUE + item['params'] + BColors.ENDC)
                break
            except Exception as e:
                attempt_count += 1
                print(f"Ошибка при обработке строки {full_text}. Попытка {attempt_count}. Ошибка: {str(e)}")
                if attempt_count == 3:
                    print("Превышено количество попыток обработки строки.")


def main():
    with open('src/ksr_lemma.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    correct_names(data)
    with open('src/ksr_corrected.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
