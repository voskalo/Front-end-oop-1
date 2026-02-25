from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from fastapi import HTTPException, status
import models
from auth import auth_service

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db


    # ---------------- registration ----------------

    async def register(self, user_data):
        result = await self.db.execute(select(models.User).where(models.User.username == user_data.username))
        if result.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        new_user = models.User(username=user_data.username, password_hash=auth_service.hash_password(user_data.password))
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user



    # ---------------- login ----------------

    async def authenticate(self, username, password):
        result = await self.db.execute(select(models.User).where(func.lower(models.User.username) == username.lower()))
        user = result.scalars().first()
        if not user or not auth_service.verify_password(password, user.password_hash):
            return None
        return user



    # ---------------- get_user ----------------

    async def get_by_id(self, user_id: int):
        result = await self.db.execute(select(models.User).where(models.User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id doesn't exists")
        return user



    # ---------------- delete_user ----------------

    async def delete_user(self, target_id: int, current_user_id: int):
        if target_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
        user = await self.get_by_id(target_id)
        await self.db.delete(user)
        await self.db.commit()






class FriendshipService:
    def __init__(self, db: AsyncSession):
        self.db = db



    # ---------------- send_friend_request ----------------

    async def send_request(self, user_id: int, friend_id: int):
        if user_id == friend_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot add yourself as a friend")
        result = await self.db.execute(select(models.Friendship).where(
            or_(
                and_(models.Friendship.user_id == user_id, models.Friendship.friend_id == friend_id),
                and_(models.Friendship.user_id == friend_id, models.Friendship.friend_id == user_id)
            )
        ))
        existing = result.scalars().first()
        if existing:
            massage = "already friends" if existing.is_accepted else "request already pending"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Relationship exists: {massage}")
        new_request = models.Friendship(user_id=user_id, friend_id=friend_id)
        self.db.add(new_request)
        await self.db.commit()
        return {"message": "Friend request sent"}



    # ---------------- accept_friend_request ----------------

    async def accept_request(self, user_id: int, sender_id: int):
        result = await self.db.execute(select(models.Friendship).where(
            and_(models.Friendship.user_id == sender_id, models.Friendship.friend_id == user_id, models.Friendship.is_accepted == False)
        ))
        request = result.scalars().first()
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending request not found")
        request.is_accepted = True
        await self.db.commit()
        return {"message": "Friend request accepted"}



    # ---------------- get_my_friends ----------------

    async def get_friends(self, user_id: int):
        result = await self.db.execute(select(models.Friendship).where(
            and_(models.Friendship.is_accepted == True, or_(models.Friendship.user_id == user_id, models.Friendship.friend_id == user_id))
        ))
        friendships = result.scalars().all()
        ids = [friendship.friend_id if friendship.user_id == user_id else friendship.user_id for friendship in friendships]
        if not ids:
            return []
        users_result = await self.db.execute(select(models.User).where(models.User.id.in_(ids)))
        return users_result.scalars().all()



    # ---------------- get_incoming_requests ----------------

    async def get_incoming(self, user_id: int):
        result = await self.db.execute(
            select(models.User).join(models.Friendship, models.User.id == models.Friendship.user_id)
            .where(and_(models.Friendship.friend_id == user_id, models.Friendship.is_accepted == False))
        )
        return result.scalars().all()



    # ---------------- remove_friendship ----------------

    async def remove_friendship(self, user_id: int, friend_id: int):
        result = await self.db.execute(select(models.Friendship).where(
            or_(
                and_(models.Friendship.user_id == user_id, models.Friendship.friend_id == friend_id),
                and_(models.Friendship.user_id == friend_id, models.Friendship.friend_id == user_id)
            )
        ))
        friendship = result.scalars().first()
        if not friendship:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")
        await self.db.delete(friendship)
        await self.db.commit()
