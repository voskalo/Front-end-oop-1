# Backend API Technical Documentation

It describes how the backend works, how the database is structured, and provides detailed instructions (contracts) for interacting with the server via HTTP requests.

The project is built on the **FastAPI** framework using the **Service Layer** architectural pattern. The database is **SQLite** + **SQLAlchemy** (asynchronous).



---

## Section 1: Architecture and File Structure

### 1. Entry Point & Configuration
* **`main.py` (Reception)**: The main entry point of the application. It creates the app instance, connects the databases, and configures **CORS** (which allows browsers to make requests to the backend from other addresses, like `localhost:3000`). It also includes all the route prefixes (`/users`, `/movies`).
* **`.env` and `config.py` (The Safe)**: The `.env` file stores secret keys (e.g., for encrypting tokens and accessing the external TMDB movie database). `config.py` safely reads and provides these keys to the code.

### 2. Data & Validation
* **`models.py` (Database Blueprint)**: Describes the structure of the database tables.
  * `User`: Users (id, username, password_hash).
  * `Movie`: Movies (id, poster, title).
  * `Friendship`: Friends (who added whom, and the request acceptance status).
  * `likes`: A hidden pivot table that stores information about "which user liked which movie".
* **`schemas.py` (Face Control)**: The frontend sends data in JSON format. `schemas.py` strictly validates this data. If the frontend sends a password that is too short, the server will automatically throw a 422 error. It also describes output "filters" (to ensure we don't accidentally send passwords to the frontend).



### 3. Business Logic (Services)
The data processing logic is separated into dedicated Service classes:
* **`user_service.py`**: Handles registration, login, and the friendship system (sending, accepting requests, deleting).
* **`movie_service.py`**: Handles liking movies and finding "common" movies between friends.
* **`get_movie_info.py` (External Agent)**: Makes requests to the global external movie database (TMDB), filters the results, generates image links, and returns ready-to-use data to the frontend.

---

## Section 2: Security (Authentication)

The **`auth.py`** file handles security. The project uses **JWT (JSON Web Tokens)**.



1. **How it works**: When a user enters the correct username and password, the backend generates a long string (token) that is valid for 30 minutes.
2. **Frontend Action**: The frontend must save this token (e.g., in `localStorage`).
3. **Protected Routes**: For actions that require authentication, the frontend must pass this token in the headers of every request:
   `Authorization: Bearer <YOUR_TOKEN>`
4. **401 Error**: If the backend returns a **401 Unauthorized** status, the token has expired or is invalid. The user should be redirected to the login page.

---

## Section 3: Routes (Endpoints)

Base URL: `http://127.0.0.1:8000` (for local development).

### Users & Authorization (`/users`)

#### 1. Registration
* **Method**: `POST` `/users/registration`
* **Body (JSON)**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
* **Response (201)**: `{"id": 1, "username": "Ivan"}`

#### 2. Login
* **Method**: `POST` `/users/login`
* **Body (Form-Data)**: `username`, `password` *(Note: this is `x-www-form-urlencoded` format, NOT JSON!)*
* **Response (200)**:
  ```json
  {
    "access_token": "eyJhbG...",
    "token_type": "bearer"
  }
  ```

#### 3. Get Profile
* **Method**: `GET` `/users/{user_id}` (Public profile of another user)
* **Method**: `GET` `/users/me` (My profile, requires `Authorization: Bearer <token>`)

#### 4. Delete Account
* **Method**: `DELETE` `/users/{user_id}`
* **Headers**: `Authorization: Bearer <token>`
* **Response (204)**: Empty body (success).

---

### Friends (`/users/friends`)
*All routes below require the header: `Authorization: Bearer <token>`*

* **Send Request**: `POST` `/users/friends/request/{friend_id}`
* **Accept Request**: `POST` `/users/friends/accept/{sender_id}`
* **My Friends List**: `GET` `/users/friends/my`
  * *Example response*: `[{"id": 2, "username": "Anna"}]`
* **Incoming Requests**: `GET` `/users/friends/requests/incoming`
* **Remove Friend / Reject Request**: `DELETE` `/users/friends/{user_id}`

---

### 🎬 Movies (`/movies`)

#### 1. Search Movies (Catalog)
* **Method**: `GET` `/movies/`
* **Query Params** (all optional): `?name=Matrix&year=1999&page=1`
* **Response (200)**: A large JSON object with a `"results"` array. The server automatically adds convenient `"poster_url"` and `"genres_str"` fields. *(No token required)*.

#### 2. Like a Movie
* **Method**: `POST` `/movies/like-movie`
* **Headers**: `Authorization: Bearer <token>`
* **Body (JSON)**:
  ```json
  {
    "id": 603,
    "poster_path": "/abc.jpg",
    "movie_name": "The Matrix"
  }
  ```
* **Response (200)**: `{"message": "Movie added to favorites"}`

#### 3. User's Liked Movies
* **Method**: `GET` `/movies/{user_id}/liked`
* **Response (200)**: An array of movies liked by this user. *(No token required)*.

#### 4. Common Movies with a Friend
* **Method**: `GET` `/movies/common/{friend_id}`
* **Headers**: `Authorization: Bearer <token>`
* **Response (200)**: An array of common movies. If there are no common movies, it returns `[]`.
