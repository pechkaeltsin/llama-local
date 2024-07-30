import csv
import json


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


def process_csv(file_path, json_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            code, name, uint = row
            name_ = name.split(' ', 1)[0]
            params = name.split(' ', 1)[1] if ' ' in name else ''
            data.append({
                'code': code,
                'name': name_,
                'params': params,
                'uint': uint
            })
            print(name)
            print(BColors.RED + name_ + BColors.ENDC + ' ' + BColors.BLUE + params + BColors.ENDC)

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main():
    csv_file_path = 'src/ksr_lemma.csv'
    json_file_path = 'src/ksr_lemma.json'
    process_csv(csv_file_path, json_file_path)


if __name__ == "__main__":
    main()
