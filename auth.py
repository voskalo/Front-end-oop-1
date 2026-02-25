from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import settings
from database import get_db

class AuthService:
    def __init__(self):
        self.password_hash = PasswordHash.recommended()
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")
        self.secret_key = settings.secret_key.get_secret_value()
        self.algorithm = settings.algorithm

    def hash_password(self, password: str) -> str:
        """Хешування пароля."""
        return self.password_hash.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Перевірка пароля."""
        return self.password_hash.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Створення JWT токена."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=settings.access_token_expire_minutes,
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm,
        )
        return encoded_jwt

    def verify_access_token(self, token: str) -> str | None:
        """Перевірка JWT токена та повернення subject (user id)."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"require": ["exp", "sub"]},
            )
            return payload.get("sub")
        except jwt.InvalidTokenError:
            return None

# Створюємо єдиний екземпляр сервісу для всього додатку
auth_service = AuthService()

# Функція-залежність для отримання поточного користувача
async def get_current_user(
    token: Annotated[str, Depends(auth_service.oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> models.User:
    user_id = auth_service.verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError) as exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exception

    result = await db.execute(
        select(models.User).where(models.User.id == user_id_int),
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Тип для зручного використання в роутах
CurrentUser = Annotated[models.User, Depends(get_current_user)]
