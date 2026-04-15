from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.repositories.category_repository import CategoryRepository
from app.schemas.record import CategoryCreate
from app.models.models import Category, User
from app.core.exceptions import NotFoundError, AuthorizationError


class CategoryService:
    """Business logic for category management."""

    def __init__(self, db: AsyncSession):
        """Initialize and connect to Persistence layer."""
        self._cat_repo = CategoryRepository(db)

    async def get_categories(self, user: User) -> List[Category]:
        """Get all available categories for the user."""
        return await self._cat_repo.get_available(user.id)

    async def create_category(self, owner: User, data: CategoryCreate) -> Category:
        """Create a new category for the user."""
        return await self._cat_repo.create(owner.id, data)
    
    async def remove_category(self, user: User, category_id: str) -> None:
        """Remove a category."""
        cat = await self._cat_repo.get_by_id(category_id)
        if not cat:
            raise NotFoundError("Category not found")
        if cat.owner_id != user.id:
            raise AuthorizationError("Cannot delete this category")
        if cat.is_default:
            raise AuthorizationError("Cannot delete default categories")
        await self._cat_repo.delete(cat)
