from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from app.models.models import Category
from app.schemas.record import CategoryCreate
import uuid


class CategoryRepository:
    """Persistence layer for Category."""

    def __init__(self, db: AsyncSession):
        """Initialize with async database session."""
        self._db = db

    async def get_available(self, user_id: str) -> List[Category]:
        """Get default and user's own categories."""
        q = select(Category).where(
            or_(Category.is_default == True, Category.owner_id == user_id)
        ).order_by(Category.is_default.desc(), Category.name)
        return list((await self._db.execute(q)).scalars().all())

    async def get_by_id(self, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        result = await self._db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(self, owner_id: str, data: CategoryCreate) -> Category:
        """Create a new category for the user."""
        cat = Category(
            id=str(uuid.uuid4()),
            name=data.name,
            icon=data.icon,
            color=data.color,
            owner_id=owner_id,
            is_default=False,
        )
        self._db.add(cat)
        await self._db.flush()
        await self._db.refresh(cat)
        return cat

    async def delete(self, category: Category) -> None:
        """Delete a category."""
        await self._db.delete(category)
        await self._db.flush()

    async def seed_defaults(self) -> None:
        """Insert default categories if not present."""
        defaults = [
            {"name": "Food & Dining", "icon": "🍽️", "color": "#FF6B6B"},
            {"name": "Transportation", "icon": "🚗", "color": "#4ECDC4"},
            {"name": "Shopping", "icon": "🛍️", "color": "#45B7D1"},
            {"name": "Entertainment", "icon": "🎬", "color": "#96CEB4"},
            {"name": "Health", "icon": "💊", "color": "#FFEAA7"},
            {"name": "Utilities", "icon": "⚡", "color": "#DDA0DD"},
            {"name": "Salary", "icon": "💰", "color": "#98FB98"},
            {"name": "Freelance", "icon": "💻", "color": "#87CEEB"},
            {"name": "Investment", "icon": "📈", "color": "#FAE849"},
            {"name": "Other", "icon": "📦", "color": "#D3D3D3"},
        ]

        # Check which default categories already exist
        existing = (await self._db.execute(
            select(Category).where(Category.is_default == True)
        )).scalars().all()
        existing_names = {c.name for c in existing}

        # Seed missing default categories
        for d in defaults:
            if d["name"] not in existing_names:
                self._db.add(Category(
                    id=str(uuid.uuid4()),
                    name=d["name"], icon=d["icon"], color=d["color"],
                    is_default=True
                ))
        await self._db.flush()
