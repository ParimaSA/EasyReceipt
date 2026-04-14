from functools import wraps
from typing import List, Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.group_repository import GroupRepository
from app.core.security import decode_token
from app.core.enums import GroupMemberRole
from app.core.exceptions import AuthenticationError, AuthorizationError
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

    # Fetch user from DB
    user_id = payload.get("sub")
    user = await UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    return user


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
        member = await GroupRepository(db).get_member(group_id, current_user.id)
        if not member:
            raise AuthorizationError("You are not a member of this group")
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
        member = await GroupRepository(db).get_member(group_id, current_user.id)
        if not member:
            raise AuthorizationError("You are not a member of this group")
        if member.role == GroupMemberRole.VIEWER:
            raise AuthorizationError("Viewers cannot create or modify records")
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
        member = await GroupRepository(db).get_member(group_id, current_user.id)
        if not member or member.role != GroupMemberRole.LEADER:
            raise AuthorizationError("Only the group leader can perform this action")
        return current_user
    return _check
