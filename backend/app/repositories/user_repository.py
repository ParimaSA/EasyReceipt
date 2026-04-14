from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.models import User
from app.core.security import get_password_hash
from app.schemas.auth import UserRegister
import uuid


class UserRepository:
    """Persistence layer for User model."""

    def __init__(self, db: AsyncSession):
        """Initialize with async database session."""
        self._db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their unique ID."""
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address."""
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        result = await self._db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, data: UserRegister) -> User:
        """Create a new user with the provided registration data."""
        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
        )
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user
