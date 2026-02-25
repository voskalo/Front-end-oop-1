from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Вхідні схеми (frontend → backend) ──────────────

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)

class UserCreate(UserBase):
    password: str = Field(min_length=8)


# ── Вихідні схеми (backend → frontend) ─────────────

class Token(BaseModel):
    access_token: str
    token_type: str

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


# ── Схеми для фільмів ───────────────────────────────

# Те що frontend надсилає при лайку (choose.html → POST /movies/like-movie)
class MoviePublic(BaseModel):
    id: int
    movie_name: str
    poster_path:  Optional[str] = None
    poster_url:   Optional[str] = None   # повний URL картинки
    overview:     Optional[str] = None   # опис
    release_date: Optional[str] = None   # "2024-11-26"
    vote_average: Optional[float] = None # рейтинг 0.0–10.0

# Те що backend повертає з бази (GET /movies/{id}/liked)
class MovieInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    movie_name:   str
    poster_path:  Optional[str] = None
    poster_url:   Optional[str] = None
    overview:     Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
