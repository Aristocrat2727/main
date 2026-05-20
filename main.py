from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # разрешаем запросы с любых доменов

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    # DuckDuckGo Instant Answer API
    url = 'https://api.duckduckgo.com/'
    params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return jsonify({'error': 'DuckDuckGo API error'}), 500
        
        data = resp.json()
        answer = data.get('AbstractText', '')
        if not answer:
            # Если нет прямого ответа, ищем среди RelatedTopics
            results = data.get('RelatedTopics', [])
            for topic in results:
                if 'Text' in topic:
                    answer = topic['Text']
                    break
            if not answer:
                answer = 'Ничего не найдено. Попробуй уточнить запрос.'
        
        return jsonify({'answer': answer, 'source': 'DuckDuckGo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)