from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DB_FILE = 'users_data.json'

# Змінено відповідно до твоєї схеми
@app.route('/user/registration', methods=['POST'])
def register_user():
    try:
        user_data = request.json
        # Очікуємо username та password згідно зі схемою
        username = user_data.get('username')
        password = user_data.get('password')

        if not username or not password:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
        else:
            data_list = []

        data_list.append({
            "username": username,
            "password": password
        })

        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)

        return jsonify({"status": "success", "message": "User registered"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
