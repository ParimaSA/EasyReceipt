from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta
from app.models.models import Group, GroupMember, GroupInvitation
from app.schemas.group import GroupCreate, GroupUpdate, InvitationCreate
from app.core.enums import GroupMemberRole
import uuid, secrets


class GroupRepository:
    """Persistence layer for Group, GroupMember, GroupInvitation."""

    def __init__(self, db: AsyncSession):
        """Initialize with async database session."""
        self._db = db

    async def get_by_id(self, group_id: str) -> Optional[Group]:
        """Get group by ID with members and leader preloaded."""
        result = await self._db.execute(
            select(Group)
            .options(
                selectinload(Group.members).selectinload(GroupMember.user),
                selectinload(Group.leader),
            )
            .where(Group.id == group_id)
        )
        return result.scalar_one_or_none()

    async def get_user_groups(self, user_id: str) -> List[Group]:
        """Get all active groups the user is a member of, with members and leader preloaded."""
        q = (
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .options(selectinload(Group.members).selectinload(GroupMember.user))
            .where(and_(GroupMember.user_id == user_id, Group.is_active == True))
        )
        return list((await self._db.execute(q)).scalars().all())

    async def create(self, leader_id: str, data: GroupCreate) -> Group:
        """Create a new group with the specified leader."""
        # Create new group
        group = Group(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            icon=data.icon,
            leader_id=leader_id,
        )
        self._db.add(group)
        await self._db.flush()

        # Add leader as member in GroupMember
        member = GroupMember(
            id=str(uuid.uuid4()),
            group_id=group.id,
            user_id=leader_id,
            role=GroupMemberRole.LEADER,
        )
        self._db.add(member)
        await self._db.flush()
        await self._db.refresh(group)
        return group

    async def update(self, group: Group, data: GroupUpdate) -> Group:
        """Update group details."""
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(group, k, v)
        await self._db.flush()
        return group

    async def delete(self, group: Group) -> None:
        """Delete the group."""
        await self._db.delete(group)
        await self._db.flush()

    async def get_member(self, group_id: str, user_id: str) -> Optional[GroupMember]:
        """Get a specific group member."""
        result = await self._db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def add_member(self, group_id: str, user_id: str, role: GroupMemberRole) -> GroupMember:
        """Add a new member to the group with the specified role."""
        member = GroupMember(
            id=str(uuid.uuid4()),
            group_id=group_id,
            user_id=user_id,
            role=role,
        )
        self._db.add(member)
        await self._db.flush()
        await self._db.refresh(member)
        return member

    async def update_member_role(self, member: GroupMember, role: GroupMemberRole) -> GroupMember:
        """Update a member's role in the group."""
        member.role = role
        await self._db.flush()
        return member

    async def remove_member(self, member: GroupMember) -> None:
        """Remove a member from the group."""
        await self._db.delete(member)
        await self._db.flush()

    async def create_invitation(self, group_id: str, data: InvitationCreate) -> GroupInvitation:
        """Create a new invitation for the group."""
        # Generate a random token for the invitation
        token = secrets.token_urlsafe(32)
        expires_at = None
        if data.expires_hours:
            expires_at = datetime.utcnow() + timedelta(hours=data.expires_hours)

        # Add new invitation to GroupInvitation
        invitation = GroupInvitation(
            id=str(uuid.uuid4()),
            group_id=group_id,
            token=token,
            invited_role=data.invited_role,
            max_uses=data.max_uses,
            expires_at=expires_at,
        )
        self._db.add(invitation)
        await self._db.flush()
        await self._db.refresh(invitation)
        return invitation

    async def get_invitation_by_token(self, token: str) -> Optional[GroupInvitation]:
        """Get an invitation by its token."""
        result = await self._db.execute(
            select(GroupInvitation)
            .options(selectinload(GroupInvitation.group))
            .where(GroupInvitation.token == token)
        )
        return result.scalar_one_or_none()

    async def get_group_invitations(self, group_id: str) -> List[GroupInvitation]:
        """Get all invitations for a specific group."""
        result = await self._db.execute(
            select(GroupInvitation).where(GroupInvitation.group_id == group_id)
        )
        return list(result.scalars().all())

    async def increment_invitation_use(self, invitation: GroupInvitation) -> GroupInvitation:
        """Increment the use count of an invitation."""
        invitation.use_count += 1

        # Deactivate the invitation if it has reached its max uses
        if invitation.max_uses and invitation.use_count >= invitation.max_uses:
            invitation.is_active = False
        await self._db.flush()
        return invitation

    async def deactivate_invitation(self, invitation: GroupInvitation) -> GroupInvitation:
        """Manually deactivate an invitation."""
        invitation.is_active = False
        await self._db.flush()
        return invitation
