import csv
import json
import chatgpt
from tqdm import tqdm

with open('src/ksr.csv', mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    ksr_data = list(reader)

with open('src/extracted.csv', mode='w', newline='', encoding='utf-8') as file:
    fieldnames = ['name', 'params', 'code', 'uint']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for row in tqdm(ksr_data, desc="Processing rows"):
        result = json.loads(chatgpt.ask(row['name']))
        filtered_result = {key: result[key] for key in fieldnames if key in result}
        writer.writerow(filtered_result)
