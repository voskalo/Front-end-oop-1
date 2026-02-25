import streamlit as st
import requests

# streamlit run front_test.py

BASE_URL = "http://127.0.0.1:8000"

# зберігаємо токен між запитами
if "token" not in st.session_state:
    st.session_state.token = None

if "movies_list" not in st.session_state:
    st.session_state.movies_list = []

if "movie_index" not in st.session_state:
    st.session_state.movie_index = 0


# ---------------- REGISTRATION ----------------
st.header("Registration")

reg_username = st.text_input("Username", key="reg_username")
reg_password = st.text_input("Password", type="password", key="reg_password")

if st.button("Register"):
    r = requests.post(
        f"{BASE_URL}/users/registration",
        json={"username": reg_username, "password": reg_password},
        timeout=5,
    )

    if r.status_code == 201:
        st.success("User created!")
        st.json(r.json())
    else:
        st.error(r.text)


# ---------------- LOGIN ----------------
st.header("Login")

login_username = st.text_input("Username", key="login_username")
login_password = st.text_input("Password", type="password", key="login_password")

if st.button("Login"):
    r = requests.post(
        f"{BASE_URL}/users/login",
        data={"username": login_username, "password": login_password},
        timeout=5,
    )

    if r.status_code == 200:
        token = r.json()["access_token"]
        st.session_state.token = token
        st.success("Logged in!")
        st.write(token)
    else:
        st.error(r.text)


# ---------------- ME ----------------
st.header("Current user (/me)")

if st.button("Get me"):
    if not st.session_state.token:
        st.warning("Login first")
    else:
        r = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        st.write(r.status_code)
        st.json(r.json())


# ---------------- GET BY ID ----------------
st.header("Get user by ID")

user_id = st.text_input("User ID")

if st.button("Get user"):
    r = requests.get(f"{BASE_URL}/users/{user_id}")
    st.write(r.status_code)
    st.text(r.text)


# ---------------- DELETE ----------------
st.header("Delete myself")

delete_id = st.text_input("ID to delete")

if st.button("Delete"):
    if not st.session_state.token:
        st.warning("Login first")
    else:
        r = requests.delete(
            f"{BASE_URL}/users/{delete_id}",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        st.write(r.status_code)
        if r.status_code == 204:
            st.success("Deleted!")


# ---------------- FRIENDS SECTION ----------------
st.divider()
st.header("🤝 Friends Management")

if not st.session_state.token:
    st.info("Увійдіть в систему, щоб керувати друзями.")
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # 1. Надсилання запиту
    st.subheader("Send Friend Request")
    target_friend_id = st.number_input("Enter User ID to add", min_value=1, step=1, key="send_req_id")
    if st.button("Send Request", key="send_req_btn"):
        r = requests.post(f"{BASE_URL}/users/friends/request/{target_friend_id}", headers=headers)
        if r.status_code == 201:
            st.success("Request sent!")
        else:
            st.error(f"Error: {r.json().get('detail')}")

    # 2. Вхідні запити
    st.subheader("Incoming Requests")
    # Використовуємо контейнер, щоб дані оновлювалися
    incoming_container = st.container()

    # Робимо запит одразу, без кнопки "Check", щоб бачити актуальний стан
    r_inc = requests.get(f"{BASE_URL}/users/friends/requests/incoming", headers=headers)
    if r_inc.status_code == 200:
        incoming = r_inc.json()
        if not incoming:
            st.write("No pending requests.")
        else:
            for req_user in incoming:
                with st.expander(f"Request from {req_user['username']} (ID: {req_user['id']})", expanded=True):
                    col1, col2 = st.columns(2)
                    # Додаємо унікальні ключі для кнопок
                    if col1.button(f"✅ Accept {req_user['id']}", key=f"acc_{req_user['id']}"):
                        acc_r = requests.post(f"{BASE_URL}/users/friends/accept/{req_user['id']}", headers=headers)
                        if acc_r.status_code == 200:
                            st.toast(f"Accepted {req_user['username']}!")
                            st.rerun()

                    if col2.button(f"❌ Reject {req_user['id']}", key=f"rej_{req_user['id']}"):
                        rej_r = requests.delete(f"{BASE_URL}/users/friends/{req_user['id']}", headers=headers)
                        if rej_r.status_code == 204:
                            st.toast(f"Rejected {req_user['username']}")
                            st.rerun()

    # 3. Мій список друзів
    st.subheader("My Friends List")
    r_friends = requests.get(f"{BASE_URL}/users/friends/my", headers=headers)
    if r_friends.status_code == 200:
        friends = r_friends.json()
        if not friends:
            st.write("You have no friends yet.")
        else:
            for friend in friends:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {friend['username']} (ID: {friend['id']})")
                if col2.button(f"🗑️ Unfriend", key=f"unf_{friend['id']}"):
                    del_r = requests.delete(f"{BASE_URL}/users/friends/{friend['id']}", headers=headers)
                    if del_r.status_code == 204:
                        st.toast(f"Removed {friend['username']}")
                        st.rerun()



# ---------------- MOVIES EXPLORER & LIKE ----------------
st.header("🎬 Movie Explorer")

col_search1, col_search2, col_search3 = st.columns([3, 1, 1])
with col_search1:
    name = st.text_input("Назва фільму", placeholder="Наприклад: Inception")
with col_search2:
    year = st.number_input("Рік", value=None, step=1)
with col_search3:
    page = st.number_input("Сторінка", min_value=1, value=1)

if st.button("🔍 Пошук", use_container_width=True):
    params = {"name": name, "year": year, "page": page}
    params = {k: v for k, v in params.items() if v}
    try:
        response = requests.get(f"{BASE_URL}/movies/", params=params)
        if response.status_code == 200:
            st.session_state.movies_list = response.json().get("results", [])
            st.session_state.movie_index = 0
            st.rerun()
    except Exception as e:
        st.error(f"Помилка підключення: {e}")

if st.session_state.movies_list:
    movie = st.session_state.movies_list[st.session_state.movie_index]

    st.divider()
    col_poster, col_info = st.columns([1, 2])

    with col_poster:
        # TMDB повертає poster_url, але в базу ми збережемо poster_path (відносний шлях)
        poster_url = movie.get("poster_url")
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.info("Постер відсутній")

    with col_info:
        st.title(movie.get("title", "Unknown"))
        st.write(f"⭐ Рейтинг: {movie.get('vote_average')}")
        st.write(f"🎭 Жанри: {', '.join(movie.get('genres_str', [])) if movie.get('genres_str') else 'N/A'}")
        st.write(f"📝 {movie.get('overview', 'No description available.')}")

        if st.session_state.token:
            # На бекенді твій MoviePublic очікує: id, poster_path, movie_name
            if st.button("❤️ Like", use_container_width=True):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                movie_payload = {
                    "id": movie["id"],
                    "poster_path": movie.get("poster_path") or "",
                    "movie_name": movie.get("title") or "Unknown"
                }

                # ЗМІНИ ЦЕЙ РЯДОК: з requests.get на requests.post
                response = requests.post(f"{BASE_URL}/movies/like-movie", json=movie_payload, headers=headers)

                if response.status_code == 200:
                    st.toast(response.json().get("message"))
                elif response.status_code == 401:
                    st.error("Будь ласка, спочатку авторизуйтесь.")
                else:
                    st.error(f"Помилка: {response.status_code}")

    # Навігація
    n_col1, n_col2, n_col3 = st.columns([1,1,1])
    with n_col1:
        if st.button("⬅️ Назад") and st.session_state.movie_index > 0:
            st.session_state.movie_index -= 1
            st.rerun()
    with n_col3:
        if st.button("Вперед ➡️") and st.session_state.movie_index < len(st.session_state.movies_list) - 1:
            st.session_state.movie_index += 1
            st.rerun()

# ---------------- LIKED MOVIES SECTION ----------------
st.divider()
st.header("📂 Community & Matches")

tab1, tab2 = st.tabs(["My & Others Favorites", "🍿 Match with Friend"])

with tab1:
    u_id = st.number_input("Чиї вподобання показати? (Введіть ID)", min_value=1, step=1)
    if st.button("Показати фільми"):
        r = requests.get(f"{BASE_URL}/movies/{u_id}/liked")
        if r.status_code == 200:
            liked_data = r.json()
            if not liked_data:
                st.info("Список порожній")
            for m in liked_data:
                with st.expander(f"🎬 {m['movie_name']}"):
                    if m['poster_path']:
                        st.image(f"https://image.tmdb.org/t/p/w200{m['poster_path']}")
                    st.write(f"ID фільму в TMDB: {m['id']}")
        else:
            st.error("Користувача не знайдено")

with tab2:
    f_id = st.number_input("ID друга для пошуку спільних фільмів", min_value=1, step=1, key="match_id")
    if st.button("Find Common Movies"):
        if not st.session_state.token:
            st.warning("Спочатку увійдіть в систему!")
        else:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            r = requests.get(f"{BASE_URL}/movies/common/{f_id}", headers=headers)
            if r.status_code == 200:
                common = r.json()
                if common:
                    st.success(f"У вас {len(common)} спільних фільмів!")
                    for m in common:
                        st.write(f"🌟 **{m['movie_name']}**")
                else:
                    st.info("Спільних фільмів поки немає.")
