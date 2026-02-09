'''Backend module'''
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Дозволяємо запити з браузера

# Шлях до файлу, куди будемо зберігати дані
DB_FILE = 'users_data.json'

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        # Отримуємо дані від JavaScript
        user_data = request.json

        # Перевіряємо, чи існує файл. Якщо так — зчитуємо старі дані
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
        else:
            data_list = []

        # Додаємо нового користувача до списку
        data_list.append(user_data)

        # Записуємо оновлений список назад у JSON файл
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)

        return jsonify({"status": "success", "message": "Дані збережено!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Сервер запущено! Очікую дані на http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
