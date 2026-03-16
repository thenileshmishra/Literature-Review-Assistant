"""User database operations"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.db.models import UserORM


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, email: str, password: str, full_name: str | None = None) -> UserORM:
        user = UserORM(
            email=email.lower().strip(),
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_email(self, email: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.email == email.lower().strip())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> UserORM | None:
        try:
            uid = UUID(str(user_id))
        except ValueError:
            return None
        stmt = select(UserORM).where(UserORM.id == uid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
