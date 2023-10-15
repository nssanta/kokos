import json
import logging
import os
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ru_core_news_sm


'''
Класс TextAnalyst предназначен для анализа текстовых данных, включая их обработку, векторизацию и классификацию.

Методы:
- __init__(json_file_path): инициализирует класс, загружает данные из JSON-файла, подготавливает тексты для обучения векторизатора и обучает векторизатор на униграммах.
- load_data(json_file_path): загружает данные из JSON-файла.
- prepare_data(): подготавливает данные для обработки.
- train_vectorizer(documents): обучает векторизатор на униграммах.
- tokenize_text(input_text): токенизирует входной текст.
- get_text_theme(input_text): классифицирует входной текст и определяет категорию и тему, которой он наиболее соответствует.
- clean_text(doc): очищает текст от местоимений, стоп-слов, чисел и пунктуации, лемматизирует слова и приводит их к нижнему регистру.

Логирование:
- Ошибки записываются в файл 'erroranalyzertext.log'. Если файл не существует, он будет создан при инициализации класса.

Вывод:
- Вывод будет иметь такой вид
        { "category": "Категория",
        "theme": "Тема" }

Пример использования:

# Создаем экземпляр класса TextAnalyst
analyzer = TextAnalyst('data.json')

# Классифицируем входной текст
input_text = "Пример входного текста для классификации."
theme_info = analyzer.get_text_theme(input_text)
print(f"Результат классификации: {theme_info}")

# Токенизируем входной текст
tokenized_text = analyzer.tokenize_text(input_text)
print(f"Токенизированный текст: {tokenized_text}")
'''
class TextAnalyst:
    def __init__(self, json_file_path):
        '''
        Инициализирует логгер для записи ошибок в файл 'erroranalyzertext.log'.
        Если файл лога не существует, он будет создан.
            __logger - объект логгера, используемый для записи сообщений об ошибках в файл.
        '''
        # Путь к файлу журнала ошибок
        log_file = 'erroranalyzertext.log'
        # Создаем логгер
        self.__logger = logging.getLogger('Analyst')
        self.__logger.setLevel(logging.ERROR)
        # Проверяем, существует ли файл лога, и создаем файловый хендлер при необходимости
        if not os.path.exists(log_file):
            # Создаем пустой файл, если он не существует
            with open(log_file, 'w') as f:
                pass
        # Проверяем, не добавлен ли уже файловый хендлер
        if not self.__logger.handlers:
            # Создаем файловый хендлер для записи в файл
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.ERROR)
            # Создаем форматтер для сообщений
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            # Добавляем файловый хендлер к логгеру
            self.__logger.addHandler(file_handler)
        self.nlp = ru_core_news_sm.load()
        self.data = self.load_data(json_file_path)
        self.categories = list(self.data.keys())
        self.vectorizer = TfidfVectorizer()

        # Загружаем данные из JSON-файла
        self.data = self.load_data(json_file_path)  # Загрузка данных
        # Инициализируем категории на основе загруженных данных
        self.categories = list(self.data.keys())
        # Инициализируем векторизатор
        self.vectorizer = TfidfVectorizer()
        # Подготавливаем униграммы для обучения векторизатора
        documents = self.prepare_data()  # Подготовка униграмм
        # Обучаем векторизатор на подготовленных данных
        self.train_vectorizer(documents)

    '''
    Загружает данные из JSON-файла.
        :param json_file_path: Путь к JSON-файлу.
        :return: Словарь данных из JSON-файла или None в случае ошибки.
    '''
    def load_data(self, json_file_path):
        try:
            # Открываем JSON-файл для чтения
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                # Загружаем данные из JSON-файла в словарь
                data = json.load(json_file)
            # Возвращаем загруженные данные
            return data
        except FileNotFoundError as e:
            # Логируем ошибку, если файл не найден
            self.__logger.error(f"Файл '{json_file_path}' не найден: {e}")
            # Возвращаем None, чтобы указать на ошибку
            return None
        except json.JSONDecodeError as e:
            # Логируем ошибку, если возникает ошибка при декодировании JSON
            self.__logger.error(f"Ошибка при декодировании JSON: {e}")
            # Возвращаем None, чтобы указать на ошибку
            return None
        except Exception as e:
            # Логируем общую ошибку
            self.__logger.error(f"Произошла ошибка: {e}")
            # Возвращаем None, чтобы указать на ошибку
            return None

    '''
    Подготавливает данные для обработки.
        :return: Список униграмм для всех н-грамм в данных или None в случае ошибки.
    '''
    def prepare_data(self):
        try:
            documents = []  # Список для хранения униграмм
            # Перебираем категории данных
            for category in self.categories:
                # Перебираем темы в каждой категории
                for theme in self.data[category]:
                    # Получаем н-граммы для текущей категории и темы
                    category_phrases = self.data[category][theme]
                    # Перебираем н-граммы
                    for n_gram in category_phrases:
                        # Токенизация н-граммы
                        n_gram_tokens = word_tokenize(n_gram)
                        # Преобразование токенов в строку с униграммами, разделенными пробелами
                        n_gram_unigrams = ' '.join(n_gram_tokens)
                        # Добавляем униграммы как одну строку в список документов
                        documents.append(n_gram_unigrams)
            # Возвращаем список униграмм для всех н-грамм в данных
            return documents
        except Exception as e:
            # Логируем ошибку и возвращаем None, чтобы указать на ошибку
            self.__logger.error(f"Произошла ошибка при подготовке данных: {e}")
            return None

    '''
    Обучает векторизатор на униграммах.
        :param documents: Список униграмм для обучения векторизатора.
    '''
    def train_vectorizer(self, documents):
        try:
            if not documents:
                raise ValueError("Список униграмм пуст.")
            # Обучение векторизатора на униграммах
            self.vectorizer.fit_transform(documents)
        except Exception as e:
            self.__logger.error(f"Произошла ошибка при обучении векторизатора: {e}")

    '''
    Токенизирует входной текст.
        :param input_text: Входной текст для токенизации.
        :return: Токенизированный текст как одну строку.
    '''
    def tokenize_text(self, input_text):
        try:
            if not input_text:
                raise ValueError("Входной текст пуст.")
            # Токенизация входного текста
            tokens = word_tokenize(input_text)
            # Возвращаем токенизированный текст как одну строку
            return ' '.join(tokens)
        except Exception as e:
            self.__logger.error(f"Произошла ошибка при токенизации текста: {e}")
            return None

    '''
    Классифицирует входной текст и определяет категорию и тему, которой он наиболее соответствует.
        :param input_text: Входной текст для классификации.
        :return: JSON-строка с информацией о категории и теме, которой соответствует входной текст.
    '''
    def get_text_theme(self, input_text):
        try:
            # Очищаем входной текст от лишних символов и форматируем его
            clean_text = self.clean_text(input_text)
            # Токенизируем очищенный текст
            tokenized_text = self.tokenize_text(clean_text)
            # Преобразуем текст в токены и затем в TF-IDF вектор
            input_vector = self.vectorizer.transform([tokenized_text])
            # Вычисляем косинусную близость между входным текстом и каждой тематикой
            '''Этот блок кода выполняет процесс классификации входного текста, сравнивая его с каждой темой в заданных 
            категориях. Для каждой темы текст объединяется в один текст и преобразуется в вектор с использованием 
            векторизации TF-IDF. Затем получается косинусная близость между входным текстом и каждой темой'''
            max_category_similarity = 0
            selected_category = ""
            selected_theme = ""
            for category in self.categories:
                for theme in self.data[category]:
                    # Объединяем фразы в каждой теме в один текст для сравнения
                    category_phrases = self.data[category][theme]
                    category_text = ' '.join(category_phrases)
                    category_vector = self.vectorizer.transform([category_text])
                    # Вычисляем косинусную близость между входным текстом и текущей тематикой
                    similarity = cosine_similarity(input_vector, category_vector)[0][0]
                    # Обновляем наиболее подходящую категорию и тему, если находим более высокую близость
                    if similarity > max_category_similarity:
                        max_category_similarity = similarity
                        selected_category = category
                        selected_theme = theme
            # Возвращаем результат в формате JSON
            result = {
                "category": selected_category,
                "theme": selected_theme
            }
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            # Логируем ошибку и возвращаем JSON с информацией об ошибке
            self.__logger.error(f"Произошла ошибка при классификации текста: {e}")
            return json.dumps({"error": "Произошла ошибка при классификации текста."})

    '''
    Очищает документ от местоимений, стоп-слов, чисел и пунктуации.
    лемматизирует слова и приводит их к нижнему регистру.
        :param doc: Входной текст для очистки.
        :return: Очищенный текст в виде строки.
    '''
    def clean_text(self, doc):
        try:
            doc = self.nlp(doc)
            tokens = []
            exclusion_list = ["nan"]
            for token in doc:
                # Пропускаем стоп-слова, пунктуацию, числа и определенные слова из исключительного списка
                if token.is_stop or token.is_punct or token.text.isnumeric() or (
                        token.text.isalnum() == False) or token.text in exclusion_list:
                    continue
                # Лемматизируем слово и приводим его к нижнему регистру, затем добавляем в список токенов
                token = str(token.lemma_.lower().strip())
                tokens.append(token)
            # Объединяем токены в одну строку и возвращаем очищенный текст
            return " ".join(tokens)
        except Exception as e:
            # Логируем ошибку и возвращаем пустую строку в случае ошибки
            self.__logger.error(f"Произошла ошибка при очистке текста: {e}")
            return ""