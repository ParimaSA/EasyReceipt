from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.services.category_service import CategoryService
from app.middleware.auth import get_current_user
from app.repositories.category_repository import CategoryRepository
from app.schemas.record import CategoryCreate, CategoryResponse
from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.models import User

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all available categories (defaults and user-created)."""
    return await CategoryService(db).get_categories(current_user)


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new custom category for the user."""
    return await CategoryService(db).create_category(current_user, data)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user-created category."""
    await CategoryService(db).remove_category(current_user, category_id)
