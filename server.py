from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import datetime

app = FastAPI()

# Налаштування CORS: дозволяє запити з будь-якого джерела (важливо для розробки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Шлях для реєстрації (як у вашому JS: /user/registration)
@app.post("/user/registration")
async def register_user(request: Request):
    try:
        # Отримуємо дані з JSON-тіла запиту
        data = await request.json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Missing username or password")

        # Формуємо запис
        log_entry = {
            "timestamp": str(datetime.datetime.now()),
            "username": username,
            "password": password
        }

        # Зберігаємо в файл (режим "a" - додавання в кінець)
        with open("data/database.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"DEBUG: New user registered: {username}")

        return {"status": "success", "message": f"User {username} saved!"}

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    # Запускаємо на порту 5000, як вказано у вашому JS
    uvicorn.run(app, host="127.0.0.1", port=5000)
