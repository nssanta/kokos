import json
from flask import Flask, request, jsonify, Response
from WebParserS import WebParser
from TextAnalyst import TextAnalyst
import nltk
from flask_cors import CORS

#nltk.download('punkt')

# Создаем объект приложения Flask
app = Flask(__name__)
CORS(app, resources={r"/check_url": {"origins": "null"}})
# Создаем объекты парсера веб-страниц и текстового анализатора
parser = WebParser()
analyzer = TextAnalyst('nT.json')

# Активируем обработчик маршрута "/check_url" для методов GET и POST
@app.route('/check_url', methods=['GET', 'POST'])
def check_url():
    # Проверяем метод запроса
    if request.method == 'GET':
        # Получаем URL из параметра запроса
        url = request.args.get('url')
    elif request.method == 'POST':
        # Получаем URL из данных формы
        url = request.form.get('url')
        # Если URL не был получен из формы, пробуем получить его из JSON-данных
        if url is None:
            data = request.get_json()
            if data and 'url' in data:
                url = data['url']
    else:
        # В случае неверного метода запроса возвращаем ошибку
        return jsonify({'error': 'Неверный метод запроса'}), 400
    # Проверяем наличие URL
    if url:
        # Получаем контент страницы, делаем запрос к веб-парсеру
        #!!! Можете использовать любые методы парсера или совмещать их
        #!!! как title+" "+meta итд. Здесь используем только метатеги
        #page_content = parser.get_html_title(url)
        #page_content = parser.get_html_meta_tags(url)
        page_content = parser.get_title_and_meta(url)
        #page_content = parser.get_text_from_url(url)
        print(f'Полученый текст с сайта :{page_content}')


        # Проанализируем контент страницы и определим тематику с использованием текстового анализатора
        report = analyzer.get_text_theme(page_content)
        # Создаем ответ в формате JSON
        response = Response(json.dumps(report, ensure_ascii=False), mimetype='application/json')
        return response
    else:
        # Если URL отсутствует, возвращаем ошибку
        return jsonify({'error': 'Неверный или отсутствующий параметр URL'}), 400

# Активируем приложение Flask
if __name__ == '__main__':
    app.debug = True # Дебаг включен, в релизи отключить
    app.run(host='0.0.0.0', port=5000)
