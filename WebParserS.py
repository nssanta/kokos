import csv
import json
import logging
import os
from urllib.parse import urljoin
import openpyxl
import requests
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

'''
Класс WebParser предназначен для парсинга веб-страниц. Он позволяет извлекать текст и мета-теги с веб-страниц.

Методы:
- get_html_title(url): извлекает текст из тега <title> веб-страницы по указанному URL-адресу.
- get_html_meta_tags(url): извлекает текст из тегов <meta>, связанных с ключевыми словами и описанием веб-страницы по указанному URL-адресу.
- get_title_and_meta(url): возвращает строку, содержащую текст из тега <title> и текст из тегов <meta> веб-страницы по указанному URL-адресу.
- get_text_from_url(url): получает текст из одного URL-адреса веб-страницы.
- get_text_from_urls_in_file(file_path): получает тексты с нескольких URL-адресов, указанных в файле.

Логирование:
- Ошибки записываются в файл 'errorparser.log'. Если файл не существует, он будет создан при инициализации класса.

Пример использования:

# Создаем экземпляр класса WebParser
parser = WebParser()

# Получаем заголовок веб-страницы по указанному URL
url = "https://kokoc.com/"
title = parser.get_html_title(url)
print(f"Заголовок: {title}")

# Получаем текст из тегов <meta> веб-страницы по указанному URL
meta_tags = parser.get_html_meta_tags(url)
print(f"Мета-теги: {meta_tags}")

# Получаем текст из тега <title> и текст из тегов <meta> веб-страницы по указанному URL
title_and_meta = parser.get_title_and_meta(url)
print(f"Заголовок и мета-теги: {title_and_meta}")

# Получаем текст с одного URL-адреса веб-страницы
text_url = "https://kokoc.com/uslugi/"
text = parser.get_text_from_url(text_url)
print(f"Текст с веб-страницы: {text}")

# Получаем тексты с нескольких URL-адресов, указанных в файле
# форматы должны быть такие '.txt', '.csv', '.xlsx', '.json'
file_path = "urls.txt"
texts_from_file = parser.get_text_from_urls_in_file(file_path)
for url, text in texts_from_file.items():
    print(f"URL: {url}")
    print(f"Текст: {text}")
'''
class WebParser:
    # TODO Разработка регламента обхода ограничений, таких как CAPTCHA и ограничений скорости.

    def __init__(self):
        '''
        Инициализирует логгер для записи ошибок в файл 'errorparser.log'.
        Если файл лога не существует, он будет создан.
        __logger - объект логгера, используемый для записи сообщений об ошибках в файл.
        '''
        # Путь к файлу журнала ошибок
        log_file = 'errorparser.log'
        # Создаем логгер
        self.__logger = logging.getLogger('Parser')
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
            # Устанавливаем пользовательский User-Agent, чтобы имитировать запрос от браузера Chrome
            #!!!
            # headers=headers - это добавить к запросам чтобы отправлять User-Agent.!!! В данном коде не используется User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    '''
    Функция check_scraping_permission принимает URL-адрес веб-страницы в качестве параметра и проверяет, 
    разрешено ли сканирование этой страницы в соответствии с правилами файла robots.txt на данном сайте. 
    Если сканирование разрешено, функция возвращает True, в противном случае возвращает False.
        :param url: URL-адрес веб-страницы для проверки разрешения на сканирование.
        :return: True, если сканирование разрешено, иначе False.
    '''
    def check_scraping_permission(self, url):
        try:
            # Получаем базовый URL из переданного URL
            base_url = urljoin(url, '/robots.txt')
            # Отправляем запрос на файл robots.txt
            response = requests.get(base_url)
            # Проверяем успешность запроса; если код ответа не 2xx, будем считать, что сканирование разрешено
            response.raise_for_status()
            # Используем BeautifulSoup для парсинга robots.txt файла
            try:
                soup = BeautifulSoup(response.text, 'lxml')
            except MarkupResemblesLocatorWarning:
                # В случае возникновения предупреждения попробуем другой парсер
                soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем директиву User-Agent, которая соответствует нашему User-Agent (пока будем использовать "User-agent: *")
            user_agent_directive = soup.find('user-agent: *')
            # Если директива найдена, проверяем, разрешено ли сканирование для данного User-Agent
            if user_agent_directive:
                disallow_directives = user_agent_directive.find_all('disallow')
                for directive in disallow_directives:
                    # Проверяем, соответствует ли текущий URL запрещенному пути
                    if directive.text == '/' or url.startswith(urljoin(base_url, directive.text)):
                        self.__logger.error(f"Сканирование для {url} запрещено в robots.txt.")
                        return False
            # Если директива не найдена или URL не соответствует запрещенным путям, сканирование разрешено
            return True
        except Exception as e:
            # Логируем ошибку и считаем, что сканирование разрешено
            self.__logger.error(f"Ошибка при проверке разрешения на сканирование(Возможно файл не найден): {e}")
            return True  # Возвращаем True, чтобы не блокировать сканирование в случае ошибки

    '''Возвращает текст из тега <title> веб-страницы
        :param url: URL-адрес веб-страницы.
        :return: текст из тега <title> или пустая строка.
    '''
    def get_html_title(self, url):
        try:
            # Проверяем разрешение на сканирование
            if not self.check_scraping_permission(url):
                self.__logger.error(f"Сканирование для {url} запрещено.")
                return  # Прекращаем выполнение функции здесь
            # Отправляем GET-запрос на указанный URL
            response = requests.get(url)
            # Проверяем успешность запроса; если код ответа не 2xx, будет вызвано исключение HTTPError
            response.raise_for_status()
            # Используем BeautifulSoup для парсинга HTML-контента страницы и находим тег <title>
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            # Проверяем, найден ли тег <title>
            if title_tag:
                # Если тег <title> найден, извлекаем текст, убираем лишние пробелы и переводы строк и возвращаем заголовок
                title = title_tag.text
                return title.strip()
            else:
                # Если тег <title> не найден, возвращаем ""
                return ""
        # Обрабатываем возможные исключения, которые могут возникнуть при выполнении запроса или парсинге страницы
        except Exception as e:
            # Логируем ошибку с указанием деталей исключения
            self.__logger.error(f"Произошла ошибка при получении заголовка: {e}")
            # Возвращаем пустую строку в случае ошибки
            return ""

    '''Возвращает текст из тегов <meta>, связанных с ключевыми словами и описанием веб-страницы
        :param url: URL-адрес веб-страницы.
        :return: текст из тегов <meta> или пустая строка.
    '''
    def get_html_meta_tags(self, url):
        try:
            # Проверяем разрешение на сканирование
            if not self.check_scraping_permission(url):
                self.__logger.error(f"Сканирование для {url} запрещено.")
                return  # Прекращаем выполнение функции здесь
            # Отправляем GET-запрос на указанный URL с заданными заголовками
            response = requests.get(url)
            # Проверяем успешность запроса; если код ответа не 2xx, будет вызвано исключение HTTPError
            response.raise_for_status()
            # Используем BeautifulSoup для парсинга HTML-контента страницы
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)
            # Ищем все теги <meta>, имеющие атрибуты 'name' и 'content', где 'name' - 'keywords' или 'description'
            tags = soup.find_all(lambda tag: (tag.name == "meta") and
                                             tag.has_attr('name') and
                                             tag.has_attr('content') and
                                             tag['name'].lower() in ['keywords', 'description'])
            # Извлекаем содержимое этих тегов и убираем лишние пробелы, затем объединяем их в одну строку
            content = [tag["content"].strip() for tag in tags if tag["content"].strip()]
            meta = ' '.join(content)
            # Возвращаем текст из тегов <meta>
            return meta
        # Обрабатываем возможные исключения, которые могут возникнуть при выполнении запроса или парсинге страницы
        except Exception as e:
            # Логируем ошибку с указанием деталей исключения
            self.__logger.error(f"Произошла ошибка при получении мета-тегов: {e}")
            # Возвращаем пустую строку в случае ошибки
            return ""

    '''Возвращает строку, содержащую текст из тега <title> и текст из тегов <meta> веб-страницы
        :param url: URL-адрес веб-страницы.
        :return: текст из тега <title> и текст из тегов <meta> или пустая строка.
    '''
    def get_title_and_meta(self, url):
        try:
            # Получаем текст из тега <title>
            title = self.get_html_title(url)
            # Получаем текст из тегов <meta>
            meta = self.get_html_meta_tags(url)
            # Возвращаем объединенный текст из тега <title> и <meta>
            return title + " " + meta
        except Exception as e:
            self.__logger.error(f"Произошла ошибка при получении заголовка и мета-тегов: {e}")
            # Возвращаем пустую строку в случае ошибки
            return ""

    '''Получает текст из URL-адреса
        :param url: URL-адрес веб-страницы.
        :return: Текст с веб-страницы или пустая строка.
    '''
    def get_text_from_url(self, url):
        try:
            # Проверяем разрешение на сканирование
            if not self.check_scraping_permission(url):
                self.__logger.error(f"Сканирование для {url} запрещено.")
                return  # Прекращаем выполнение функции здесь
            # Отправляем GET-запрос на указанный URL
            response = requests.get(url)
            # Проверяем успешность запроса; если код ответа не 2xx, будет вызвано исключение HTTPError
            response.raise_for_status()
            # Используем BeautifulSoup для парсинга HTML-контента страницы и извлекаем текст
            soup = BeautifulSoup(response.text, 'html.parser')
            # Извлекаем текст из HTML-контента, удаляем лишние пробелы и переводы строк, затем объединяем текст в одну строку
            text = ' '.join(soup.stripped_strings)
            # Возвращаем полученный текст
            return text
        # Обрабатываем возможные исключения, которые могут возникнуть при выполнении запроса или парсинге страницы
        except requests.exceptions.RequestException as e:
            # Логируем ошибку с указанием деталей исключения
            self.__logger.error(f"Произошла ошибка при получении текста из {url}: {e}")
            # Возвращаем сообщение об ошибке в случае проблем с соединением
            return "Ошибка соединения"
        except ValueError as e:
            # Логируем ошибку с указанием деталей исключения
            self.__logger.error(f"Произошла ошибка при получении текста из {url}: {e}")
            # Возвращаем пустую строку в случае ошибки
            return ""

    '''Получает текст из URL-адресов, указанных в файле
        :param file_path: Путь к файлу с URL-адресами.
        :return: словарь с URL-адресами в качестве ключей и текстами веб-страниц в качестве значений
        или сообщение об ошибке, если файл не найден или имеет неподдерживаемый формат.
    '''
    def get_text_from_urls_in_file(self, file_path):
        '''Получаем текст из URL-адресов, указанных в файле'''
        _, file_extension = os.path.splitext(file_path)
        # Проверяем расширение файла
        if file_extension.lower() not in ['.txt', '.csv', '.xlsx', '.json']:
            raise ValueError("Файл должен иметь расширение .txt, .csv, .xlsx или .json")
        url_to_text = {}
        try:
            # Обработка файла .txt
            if file_extension.lower() == '.txt':
                with open(file_path, 'r') as file:
                    urls = file.readlines()
                    for url in urls:
                        url = url.strip()
                        text = self.get_text_from_url(url)
                        url_to_text[url] = text
            # Обработка файла .csv
            elif file_extension.lower() == '.csv':
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        url = row[0].strip()
                        text = self.get_text_from_url(url)
                        url_to_text[url] = text
            # Обработка файла .xlsx
            elif file_extension.lower() == '.xlsx':
                workbook = openpyxl.load_workbook(file_path)
                sheet = workbook.active
                for row in sheet.iter_rows(values_only=True):
                    url = row[0].strip()
                    text = self.get_text_from_url(url)
                    url_to_text[url] = text
            # Обработка файла .json
            elif file_extension.lower() == '.json':
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    for item in data:
                        # Используем ключи "url" или "domain" из JSON объекта
                        url = item.get('url', item.get('domain', '')).strip()
                        text = self.get_text_from_url(url)
                        url_to_text[url] = text
        except FileNotFoundError as e:
            # Логируем ошибку, если файл не найден
            self.__logger.error(f"Файл не найден: {e}")
            raise
        # Возвращаем словарь с URL-адресами и текстом
        return url_to_text