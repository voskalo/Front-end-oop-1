from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from get_movie_info import client
import models
from schemas import MoviePublic


class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── GET /movies/ ────────────────────────────────
    async def get_all_movies(self, name: Optional[str], year: Optional[int], page: int):
        return client.get_movies(name=name, year=year, page=page)

    # ── POST /movies/like-movie ──────────────────────
    async def like_movie(self, movie_data: MoviePublic, current_user: models.User):

        # 1. Шукаємо фільм в нашій БД
        result = await self.db.execute(
            select(models.Movie).where(models.Movie.id == movie_data.id)
        )
        movie = result.scalars().first()

        if not movie:
            # Фільму ще немає — створюємо з усіма полями
            movie = models.Movie(
                id           = movie_data.id,
                movie_name   = movie_data.movie_name,
                poster_path  = movie_data.poster_path,
                poster_url   = movie_data.poster_url,
                overview     = movie_data.overview,
                release_date = movie_data.release_date,
                vote_average = movie_data.vote_average,
            )
            self.db.add(movie)
            await self.db.flush()
        else:
            # Фільм вже є — оновлюємо поля якщо вони були порожні
            # (могли бути збережені раніше без нових полів)
            if not movie.poster_url   and movie_data.poster_url:
                movie.poster_url   = movie_data.poster_url
            if not movie.overview     and movie_data.overview:
                movie.overview     = movie_data.overview
            if not movie.release_date and movie_data.release_date:
                movie.release_date = movie_data.release_date
            if not movie.vote_average and movie_data.vote_average:
                movie.vote_average = movie_data.vote_average

        # 2. Завантажуємо поточного юзера з його лайками
        result = await self.db.execute(
            select(models.User)
            .options(selectinload(models.User.liked_movies))
            .where(models.User.id == current_user.id)
        )
        user = result.scalars().first()

        # 3. Додаємо лайк якщо ще немає
        if movie not in user.liked_movies:
            user.liked_movies.append(movie)
            await self.db.commit()
            return {"message": "Movie added to favorites"}

        return {"message": "Movie already in favorites"}

    # ── GET /movies/{user_id}/liked ──────────────────
    async def get_user_liked_movies(self, user_id: int):
        result = await self.db.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        await self.db.refresh(user, ["liked_movies"])
        return user.liked_movies

    # ── GET /movies/common/{friend_id} ──────────────
    async def get_common_movies(self, current_user: models.User, friend_id: int):
        # Лайки поточного юзера
        await self.db.refresh(current_user, ["liked_movies"])
        my_ids = {movie.id for movie in current_user.liked_movies}

        # Лайки друга
        result = await self.db.execute(
            select(models.User).where(models.User.id == friend_id)
        )
        friend = result.scalars().first()

        if not friend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend not found"
            )

        await self.db.refresh(friend, ["liked_movies"])

        # Перетин
        return [m for m in friend.liked_movies if m.id in my_ids]
