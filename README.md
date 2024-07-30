# 1. Предобработка в начальную форму

`lemma.py` выполняет предобработку текстовых данных из CSV файла, преобразуя их к лемматизированной форме без стоп-слов и знаков пунктуации, и сохраняет результат в новый CSV файл. Вот структурированное описание работы программы:

1. **Импорт библиотек**:
   - Используются библиотеки `pandas` для работы с данными в табличном формате.
   - `pymorphy3` для морфологического анализа и лемматизации слов русского языка.
   - `nltk` для токенизации текста и работы со стоп-словами.

2. **Загрузка необходимых ресурсов NLTK**:
   - Загружаются модули `punkt` для токенизации слов и `stopwords` для фильтрации стоп-слов.

3. **Определение функции для предобработки текста (`preprocess`)**:
   - **Токенизация**: Разбиение текста на слова.
   - **Фильтрация**: Удаление знаков пунктуации и стоп-слов.
   - **Лемматизация**: Преобразование слов к их начальной форме.
   - **Объединение обработанных слов**: Склеивание слов в строку для дальнейшего сохранения.
   - **Печать лемм**: Вывод каждой обработанной леммы в консоль для контроля.

4. **Настройка параметров обработки**:
   - Определение списка знаков пунктуации и списка стоп-слов.
   - Создание экземпляра морфологического анализатора.

5. **Чтение исходных данных**:
   - Загрузка данных из CSV файла `ksr.csv`.
   - Использование разделителя `,` для правильного считывания полей.

6. **Применение функции предобработки**:
   - Применение функции `preprocess` к каждому элементу столбца `name` в DataFrame. Результат заменяет исходные данные в столбце `name`.

7. **Сохранение обработанных данных**:
   - Данные сохраняются в новый CSV файл `ksr_lemma.csv` без индексов и с выбранными столбцами `code`, `name`, `uint`.

# 2. Выделение наименование как первое слово 

`separation.py` выполняет преобразование данных из CSV файла в JSON формат, проводя при этом некоторую предварительную обработку данных. Вот подробное описание работы программы:

1. **Импорт библиотек**: Программа использует модули `csv` для работы с CSV-файлами и `json` для сериализации данных в JSON формат.

2. **Определение класса для цветного вывода текста**:
   - `BColors` определяет ANSI escape-коды для вывода цветного текста в консоль, что позволяет более наглядно представить результаты обработки данных.

3. **Функция обработки CSV (`process_csv`)**:
   - **Чтение CSV файла**: Функция принимает путь к CSV файлу и путь, куда будет сохранён JSON файл. Далее, она открывает CSV файл и считывает его содержимое.
   - **Пропуск заголовка**: Первая строка в CSV файле, содержащая заголовки столбцов, пропускается.
   - **Обработка строк**: Для каждой строки извлекаются значения столбцов `code`, `name`, и `uint`. Поле `name` разделяется на две части: первое слово (`name_`) и остальная часть строки (`params`).
   - **Формирование данных**: Создаётся словарь с ключами `code`, `name` (для первого слова из поля `name`), `params` (для оставшейся части строки) и `uint`. Этот словарь добавляется в список `data`.
   - **Вывод обработанных данных**: В консоль выводятся обработанные данные с использованием цветового оформления, чтобы подчеркнуть разделение `name` на `name_` и `params`.

4. **Сохранение в JSON**:
   - После обработки всех строк данные записываются в JSON файл с помощью функции `json.dump`, гарантируя читаемый формат с отступами.

5. **Основная функция (`main`)**:
   - Определяются пути к исходному CSV файлу и целевому JSON файлу.
   - Вызывается функция `process_csv` для выполнения всей работы по преобразованию данных.

6. **Запуск программы**:
   - Если скрипт запущен как основная программа, вызывается функция `main`.

# 3. Обработка llamой для случаев, где наименование не первое слово 



# 4. Создание таблицы для БД 

