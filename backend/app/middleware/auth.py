from functools import wraps
from typing import List, Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from backend.app.services.auth_service import AuthService
from backend.app.services.group_service import GroupService
from app.core.security import decode_token
from app.core.enums import GroupMemberRole
from app.core.exceptions import AuthenticationError
from app.models.models import User


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT token from Authorization header, then fetch the user."""
    # Check for JWT token in header
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid Authorization header")

    # Extract token and decode
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise AuthenticationError("Invalid or expired token")

    # Validate user access and return user object
    user_id = payload.get("sub")
    auth_service = AuthService(db)
    return await auth_service.validate_user_access(user_id)


def require_group_member(group_id_param: str = "group_id"):
    """
    Ensures the current user is any member of the given group.
    Injects `group_id` from the path parameter named `group_id_param`.
    """
    async def _check(
        group_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        service = GroupService(db)
        await service.validate_membership(group_id, current_user.id)
        return current_user
    return _check


def require_group_recorder(group_id_param: str = "group_id"):
    """
    Ensures user is a LEADER or MEMBER of the group (can create/edit records).
    VIEWER is denied.
    """
    async def _check(
        group_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        service = GroupService(db)
        await service.validate_membership(group_id, current_user.id, required_role="recorder")
        return current_user
    return _check


def require_group_leader(group_id_param: str = "group_id"):
    """
    Ensures user is the LEADER of the group.
    """
    async def _check(
        group_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        service = GroupService(db)
        await service.validate_membership(group_id, current_user.id, required_role=GroupMemberRole.LEADER)
        return current_user
    return _check
