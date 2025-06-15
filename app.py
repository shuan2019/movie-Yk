from flask import Flask, jsonify, send_from_directory
from scraper import scrape_youku_movies, save_to_json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/movies.json')
def get_movies():
    return send_from_directory('.', 'movies.json')

@app.route('/refresh', methods=['POST'])
def refresh_data():
    try:
        # 运行爬虫获取新数据
        movies = scrape_youku_movies()
        # 保存到 JSON 文件
        save_to_json(movies)
        return jsonify({'status': 'success', 'message': '数据刷新成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # 确保 movies.json 文件存在
    if not os.path.exists('movies.json'):
        movies = scrape_youku_movies()
        save_to_json(movies)
    
    app.run(host='0.0.0.0', port=5000, debug=True) 