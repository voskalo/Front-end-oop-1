#!/bin/bash

# ──────────────────────────────────────────────
#  MovieMatch — start.sh
#  Перевіряє залежності, запускає бекенд,
#  відкриває index.html у браузері
#  Використання: ./start.sh
# ──────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${GREEN}🎬  MovieMatch — Starting...${NC}"
echo ""

# ════════════════════════════════════════════════
# 1. Перевірка: чи є main.py поруч
# ════════════════════════════════════════════════
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌  Error: main.py not found.${NC}"
    echo "    Run this script from the project root folder:"
    echo "    cd UCU-Stydents-Industries && ./start.sh"
    exit 1
fi

# ════════════════════════════════════════════════
# 2. Перевірка: чи є .env файл
# ════════════════════════════════════════════════
if [ ! -f ".env" ]; then
    echo -e "${RED}❌  Error: .env file not found.${NC}"
    echo ""
    echo "    Create a .env file in the project root with:"
    echo ""
    echo "      SECRET_KEY=any_long_random_string_here"
    echo "      ALGORITHM=HS256"
    echo "      ACCESS_TOKEN_EXPIRE_MINUTES=30"
    echo "      TMDB_API_KEY=your_tmdb_api_key_here"
    echo ""
    echo "    Get TMDB key at: https://www.themoviedb.org/settings/api"
    exit 1
fi

# ════════════════════════════════════════════════
# 3. Перевірка: чи є Python
# ════════════════════════════════════════════════
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌  Python3 not found.${NC}"
    echo "    Install it from https://www.python.org/downloads/"
    exit 1
fi

PYTHON=$(command -v python3)
PY_VERSION=$($PYTHON --version 2>&1)
echo -e "${BLUE}🐍  $PY_VERSION${NC}"

# ════════════════════════════════════════════════
# 4. Перевірка: чи є pip
# ════════════════════════════════════════════════
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo -e "${RED}❌  pip not found.${NC}"
    echo "    Install pip: https://pip.pypa.io/en/stable/installation/"
    exit 1
fi

PIP=$(command -v pip3 || command -v pip)

# ════════════════════════════════════════════════
# 5. Перевірка і встановлення бібліотек
# ════════════════════════════════════════════════

# Всі потрібні пакети (назва для import : назва для pip install)
declare -A PACKAGES=(
    ["fastapi"]="fastapi==0.128.0"
    ["uvicorn"]="uvicorn==0.40.0"
    ["sqlalchemy"]="sqlalchemy==2.0.46"
    ["aiosqlite"]="aiosqlite==0.22.1"
    ["pydantic"]="pydantic==2.12.5"
    ["pwdlib"]="pwdlib[argon2]==0.3.0"
    ["jwt"]="PyJWT==2.11.0"
    ["pydantic_settings"]="pydantic_settings==2.12.0"
    ["multipart"]="python-multipart==0.0.9"
    ["requests"]="requests==2.32.5"
    ["greenlet"]="greenlet"
)

echo ""
echo -e "${BLUE}📦  Checking dependencies...${NC}"
echo ""

MISSING=()

for import_name in "${!PACKAGES[@]}"; do
    pip_name="${PACKAGES[$import_name]}"

    # Перевіряємо чи можна імпортувати пакет
    if $PYTHON -c "import $import_name" &> /dev/null; then
        echo -e "   ${GREEN}✓${NC}  $import_name"
    else
        echo -e "   ${RED}✗${NC}  $import_name  ${YELLOW}(missing)${NC}"
        MISSING+=("$pip_name")
    fi
done

# ── Якщо є відсутні пакети — встановлюємо їх ──
if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⬇️   Installing missing packages...${NC}"
    echo ""

    for pkg in "${MISSING[@]}"; do
        echo -e "   Installing ${BLUE}$pkg${NC}..."
        $PIP install "$pkg" --quiet

        if [ $? -eq 0 ]; then
            echo -e "   ${GREEN}✓  $pkg installed${NC}"
        else
            echo -e "   ${RED}❌  Failed to install $pkg${NC}"
            echo "       Try manually: pip install $pkg"
            exit 1
        fi
    done

    echo ""
    echo -e "${GREEN}✓  All dependencies installed!${NC}"
else
    echo ""
    echo -e "${GREEN}✓  All dependencies are present!${NC}"
fi

# ════════════════════════════════════════════════
# 6. Знаходимо index.html
# ════════════════════════════════════════════════
INDEX_PATH=""
for path in "web/index.html" "templates/index.html" "index.html"; do
    if [ -f "$path" ]; then
        INDEX_PATH="$(pwd)/$path"
        break
    fi
done

if [ -z "$INDEX_PATH" ]; then
    echo -e "${YELLOW}⚠️   index.html not found — server will still start.${NC}"
fi

# ════════════════════════════════════════════════
# 7. Запускаємо uvicorn у фоні
# ════════════════════════════════════════════════
echo ""
echo -e "${GREEN}🚀  Starting backend on http://127.0.0.1:8000${NC}"
echo ""

uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
SERVER_PID=$!

# ════════════════════════════════════════════════
# 8. Чекаємо поки сервер реально відповідає
# ════════════════════════════════════════════════
echo -n "   Waiting for server"
READY=false

for i in {1..20}; do
    sleep 1
    echo -n "."

    if curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
        READY=true
        break
    fi

    # Перевіряємо чи процес ще живий
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo ""
        echo -e "${RED}❌  Server crashed on startup.${NC}"
        echo "    Check your code for errors and try again."
        exit 1
    fi
done

echo ""

if [ "$READY" = false ]; then
    echo -e "${YELLOW}⚠️   Server is taking longer than usual. Opening browser anyway...${NC}"
fi

echo -e "${GREEN}   ✓  Server is ready!${NC}"

# ════════════════════════════════════════════════
# 9. Відкриваємо браузер
# ════════════════════════════════════════════════
if [ -n "$INDEX_PATH" ]; then
    echo ""
    echo -e "${GREEN}🌐  Opening browser...${NC}"

    case "$(uname -s)" in
        Darwin)            open "file://$INDEX_PATH" ;;
        Linux)             xdg-open "file://$INDEX_PATH" 2>/dev/null || \
                           sensible-browser "file://$INDEX_PATH" 2>/dev/null ;;
        MINGW*|CYGWIN*)    start "$INDEX_PATH" ;;
    esac
fi

# ════════════════════════════════════════════════
# 10. Фінальний вивід
# ════════════════════════════════════════════════
echo ""
echo -e "${GREEN}────────────────────────────────────────${NC}"
echo -e "${GREEN}  ✓  MovieMatch is running!${NC}"
echo -e "${GREEN}────────────────────────────────────────${NC}"
echo -e "  Backend  : ${BLUE}http://127.0.0.1:8000${NC}"
echo -e "  API docs : ${BLUE}http://127.0.0.1:8000/docs${NC}"
[ -n "$INDEX_PATH" ] && \
echo -e "  Frontend : ${BLUE}file://$INDEX_PATH${NC}"
echo -e "${GREEN}────────────────────────────────────────${NC}"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

# ════════════════════════════════════════════════
# 11. Ctrl+C — зупиняємо сервер коректно
# ════════════════════════════════════════════════
trap "
    echo ''
    echo -e '${RED}🛑  Stopping server...${NC}'
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    echo -e '${GREEN}✓   Server stopped. Bye!${NC}'
    echo ''
    exit 0
" INT

wait $SERVER_PID
