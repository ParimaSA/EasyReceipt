from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.repositories.category_repository import CategoryRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import AuthenticationError, ConflictError
from app.schemas.auth import UserRegister, UserLogin, Token, UserBase


class AuthService:
    """Business logic for user authentication and registration."""

    def __init__(self, db: AsyncSession):
        """Initialize and connect to Persistence layer."""
        self._user_repo = UserRepository(db)
        self._cat_repo = CategoryRepository(db)

    async def register(self, data: UserRegister) -> Token:
        """Register a new user and return auth tokens."""
        if await self._user_repo.get_by_email(data.email):
            raise ConflictError("Email already registered")
        if await self._user_repo.get_by_username(data.username):
            raise ConflictError("Username already taken")

        user = await self._user_repo.create(data)
        return self._build_token(user.id)

    async def login(self, data: UserLogin) -> Token:
        """Authenticate user and return auth tokens."""
        user = await self._user_repo.get_by_email(data.email)

        # verify the password and check if user is active
        if not user or not verify_password(data.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")
        return self._build_token(user.id)

    async def refresh(self, refresh_token: str) -> Token:
        """Validate refresh token and return new auth tokens."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")
        user_id = payload.get("sub")
        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        return self._build_token(user.id)
    
    async def validate_user_access(self, user_id: str) -> UserBase:
        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        return user

    def _build_token(self, user_id: str) -> Token:
        """Helper to create access and refresh tokens for a user."""
        return Token(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
