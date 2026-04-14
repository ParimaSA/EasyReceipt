from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.middleware.auth import get_current_user, require_group_member, require_group_leader
from app.services.group_service import GroupService
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse,
    InvitationCreate, InvitationResponse, JoinGroupRequest,
)
from app.core.config import settings
from app.core.enums import GroupMemberRole
from app.models.models import User

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=List[GroupResponse])
async def list_my_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all groups the current user belongs to."""
    return await GroupService(db).get_user_groups(current_user)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_group(
    data: GroupCreate,
    # Any authenticated user can create a group
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a group. Caller becomes the group LEADER."""
    return await GroupService(db).create_group(current_user, data)


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    current_user: User = Depends(require_group_member()),
    db: AsyncSession = Depends(get_db),
):
    """Get group details. Any member can view."""
    return await GroupService(db).get_group(group_id, current_user)


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    data: GroupUpdate,
    current_user: User = Depends(require_group_leader()),
    db: AsyncSession = Depends(get_db),
):
    """Update group info. LEADER only."""
    return await GroupService(db).update_group(group_id, current_user, data)


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: str,
    current_user: User = Depends(require_group_leader()),
    db: AsyncSession = Depends(get_db),
):
    """Delete the group. LEADER only."""
    await GroupService(db).delete_group(group_id, current_user)


@router.post("/{group_id}/invitations", response_model=InvitationResponse, status_code=201)
async def create_invitation(
    group_id: str,
    data: InvitationCreate,
    current_user: User = Depends(require_group_leader()),
    db: AsyncSession = Depends(get_db),
):
    """Create an invite link. LEADER only."""
    invitation = await GroupService(db).create_invitation(group_id, current_user, data)
    invite_url = f"{settings.CORS_ORIGINS[0]}/join/{invitation.token}"
    return InvitationResponse.model_validate(invitation).model_copy(
        update={"invite_url": invite_url}
    )


@router.get("/{group_id}/invitations", response_model=List[InvitationResponse])
async def list_invitations(
    group_id: str,
    current_user: User = Depends(require_group_leader()),
    db: AsyncSession = Depends(get_db),
):
    """List all invite links for the group. LEADER only."""
    return await GroupService(db).get_invitations(group_id, current_user)


@router.delete("/{group_id}/invitations/{invitation_id}", status_code=204)
async def revoke_invitation(
    group_id: str,
    invitation_id: str,
    current_user: User = Depends(require_group_leader()),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an invite link. LEADER only."""
    await GroupService(db).revoke_invitation(group_id, invitation_id, current_user)


@router.post("/join", response_model=GroupResponse)
async def join_group(
    data: JoinGroupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a group using an invite token."""
    return await GroupService(db).join_group(data.token, current_user)


@router.delete("/{group_id}/members/{member_user_id}", status_code=204)
async def remove_member(
    group_id: str,
    member_user_id: str,
    current_user: User = Depends(require_group_leader()),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from the group. LEADER only."""
    await GroupService(db).remove_member(group_id, member_user_id, current_user)


@router.patch("/{group_id}/members/{member_user_id}/role", status_code=204)
async def update_member_role(
    group_id: str,
    member_user_id: str,
    new_role: GroupMemberRole,
    current_user: User = Depends(require_group_leader()),
    db: AsyncSession = Depends(get_db),
):
    """Change a member's role. LEADER only."""
    await GroupService(db).update_member_role(group_id, member_user_id, new_role, current_user)
