from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from auth import auth_service, CurrentUser
from database import get_db
from schemas import Token, UserCreate, UserPublic
from services.user_service import UserService, FriendshipService

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


# ══════════════════════════════════════════════
#  ПОРЯДОК ВАЖЛИВИЙ:
#  конкретні шляхи (/me, /search, /friends/...)
#  стоять ВИЩЕ динамічного (/{user_id})
# ══════════════════════════════════════════════


# POST /users/registration
# signup.html надсилає JSON: { "username": "...", "password": "..." }
@router.post("/registration", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: DB):
    service = UserService(db)
    return await service.register(user_data)


# POST /users/login
# login.html надсилає form-data: username=...&password=...  (НЕ JSON)
@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DB,
):
    service = UserService(db)
    user = await service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_service.create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# GET /users/me
# Повертає профіль залогіненого юзера. Потрібен токен.
@router.get("/me", response_model=UserPublic)
async def get_me(current_user: CurrentUser):
    return current_user


# GET /users/search?query=Tom
# search_friends.html використовує цей ендпоінт.
# СТОЇТЬ ВИЩЕ /{user_id} — інакше слово "search" трактується як user_id
@router.get("/search", response_model=list[UserPublic])
async def search_users(
    query: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.User)
        .where(models.User.username.ilike(f"%{query}%"))
        .limit(20)
    )
    return result.scalars().all()


# GET /users/friends/my
# profile.html — список моїх друзів. Потрібен токен.
@router.get("/friends/my", response_model=list[UserPublic])
async def get_my_friends(db: DB, current_user: CurrentUser):
    service = FriendshipService(db)
    return await service.get_friends(current_user.id)


# GET /users/friends/requests/incoming
# Вхідні запити дружби. Потрібен токен.
@router.get("/friends/requests/incoming", response_model=list[UserPublic])
async def get_incoming_requests(db: DB, current_user: CurrentUser):
    service = FriendshipService(db)
    return await service.get_incoming(current_user.id)


# POST /users/friends/request/{friend_id}
# search_friends.html — кнопка "Add". Потрібен токен.
@router.post("/friends/request/{friend_id}", status_code=status.HTTP_201_CREATED)
async def send_friend_request(friend_id: int, db: DB, current_user: CurrentUser):
    service = FriendshipService(db)
    return await service.send_request(current_user.id, friend_id)


# POST /users/friends/accept/{sender_id}
# Прийняти запит дружби. Потрібен токен.
@router.post("/friends/accept/{sender_id}")
async def accept_friend_request(sender_id: int, db: DB, current_user: CurrentUser):
    service = FriendshipService(db)
    return await service.accept_request(current_user.id, sender_id)


# DELETE /users/friends/{user_id}
# Видалити друга або відхилити запит. Потрібен токен.
@router.delete("/friends/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(user_id: int, db: DB, current_user: CurrentUser):
    service = FriendshipService(db)
    await service.remove_friendship(current_user.id, user_id)


# GET /users/{user_id}  ← ЗАВЖДИ ОСТАННІЙ з GET
# Публічний профіль. Токен не потрібен.
@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: DB):
    service = UserService(db)
    return await service.get_by_id(user_id)


# DELETE /users/{user_id}
# Видалити свій акаунт. Потрібен токен.
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DB, current_user: CurrentUser):
    service = UserService(db)
    await service.delete_user(user_id, current_user.id)
