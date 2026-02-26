# MovieMatch - Backend API

This is the backend service for a social movie-tracking application. It handles user authentication, movie data retrieval via external APIs, and social interactions between users.

## Core Capabilities

### 1. User Management & Security
* **Authentication**: Uses JWT (JSON Web Tokens) for secure session management.
* **Password Security**: Implements Argon2id hashing for storing user credentials safely.
* **Profile Management**: Support for user registration, public profile retrieval, and account deletion.
* **User Search**: An endpoint to find other registered users by their username using case-insensitive partial matching.

### 2. Movie Integration
* **TMDB Client**: A custom client that communicates with The Movie Database (TMDB) API to fetch popular movies or search for specific titles by name and year.
* **Local Persistence**: When a user "likes" a movie, its basic metadata (ID, name, poster path) is stored in the local database to ensure data consistency even if external API data changes.
* **User Favorites**: Allows users to maintain a personal list of "liked" movies.

### 3. Social Engine
* **Friendship System**: A full request-response cycle for managing friends (sending requests, accepting, or removing friendships).
* **Common Interests**: Logic to compare two users' "liked" lists and return a list of movies they both enjoy.

## Technical Architecture

* **Framework**: Built with **FastAPI**, utilizing asynchronous endpoints for better performance.
* **Database**: Uses **SQLite** with **SQLAlchemy 2.0** (Async engine). The schema includes tables for users, movies, and association tables for likes and friendships.
* **Data Validation**: **Pydantic** models (schemas) are used to validate all incoming request bodies and define outgoing response structures.
* **Configuration**: Managed via **Pydantic Settings**, loading sensitive keys (like API tokens and secrets) from a `.env` file.

## Setup & Running

### Requirements
The service requires Python 3.10+ and the following main dependencies:
* `fastapi`, `uvicorn`, `sqlalchemy`, `aiosqlite`, `python-jose`, `pwdlib[argon2]`, `requests`, `pydantic-settings`.

### Installation
1.  **Environment Setup**:
    Create a `.env` file in the root directory with the following variables:
    ```env
    SECRET_KEY=your_jwt_secret
    TMDB_API_KEY=your_tmdb_key
    ```
2.  **Database**:
    The database (`blog.db`) and its tables are automatically initialized during the application startup via the lifespan context manager.

### Execution
Run the server using Uvicorn:
```bash
uvicorn main:app --reload
```
