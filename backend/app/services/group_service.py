"""
Group Service — business logic only. Calls GroupRepository.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from app.repositories.group_repository import GroupRepository
from app.repositories.user_repository import UserRepository
from app.models.models import Group, GroupInvitation, User
from app.schemas.group import GroupCreate, GroupUpdate, InvitationCreate
from app.core.enums import GroupMemberRole
from app.core.exceptions import NotFoundError, AuthorizationError, ConflictError, InvitationError


class GroupService:
    """Business logic for managing groups, invitations, and memberships."""

    def __init__(self, db: AsyncSession):
        """Initialize and connect to Persistence layer."""
        self._group_repo = GroupRepository(db)
        self._user_repo = UserRepository(db)

    async def get_user_groups(self, user: User) -> List[Group]:
        """Get all groups the user is a member of."""
        return await self._group_repo.get_user_groups(user.id)

    async def get_group(self, group_id: str, current_user: User) -> Group:
        """Get group details if user is a member."""
        group = await self._group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundError("Group not found")
        
        # raise error if user is not a member of the group
        member = await self._group_repo.get_member(group_id, current_user.id)
        if not member:
            raise AuthorizationError("You are not a member of this group")
        return group

    async def create_group(self, current_user: User, data: GroupCreate) -> Group:
        """Create a new group with the current user as leader."""
        group = await self._group_repo.create(current_user.id, data)
        return await self._group_repo.get_by_id(group.id)

    async def update_group(self, group_id: str, current_user: User, data: GroupUpdate) -> Group:
        """Update group details. Only leader can update."""
        group = await self._get_leader_group(group_id, current_user)
        return await self._group_repo.update(group, data)

    async def delete_group(self, group_id: str, current_user: User) -> None:
        """Delete a group. Only leader can delete."""
        group = await self._get_leader_group(group_id, current_user)
        await self._group_repo.delete(group)

    async def create_invitation(self, group_id: str, current_user: User, data: InvitationCreate) -> GroupInvitation:
        """Create a new invitation for the group. Only leader can create."""
        await self._get_leader_group(group_id, current_user)
        return await self._group_repo.create_invitation(group_id, data)

    async def get_invitations(self, group_id: str, current_user: User) -> List[GroupInvitation]:
        """Get all invitations for the group. Only leader can view."""
        await self._get_leader_group(group_id, current_user)
        return await self._group_repo.get_group_invitations(group_id)

    async def revoke_invitation(self, group_id: str, invitation_id: str, current_user: User) -> None:
        """Revoke an existing invitation. Only leader can revoke."""
        await self._get_leader_group(group_id, current_user)
        invitations = await self._group_repo.get_group_invitations(group_id)
        invitation = next((i for i in invitations if i.id == invitation_id), None)
        if not invitation:
            raise NotFoundError("Invitation not found")
        await self._group_repo.deactivate_invitation(invitation)

    async def join_group(self, token: str, current_user: User) -> Group:
        """Join a group using an invitation token."""
        invitation = await self._group_repo.get_invitation_by_token(token)
        if not invitation:
            raise InvitationError("Invitation not found")
        if not invitation.is_active:
            raise InvitationError("Invitation is no longer active")
        if invitation.expires_at and invitation.expires_at < datetime.utcnow():
            raise InvitationError("Invitation has expired")

        existing = await self._group_repo.get_member(invitation.group_id, current_user.id)
        if existing:
            raise ConflictError("You are already a member of this group")

        # Assign role based on invitation
        join_role = invitation.invited_role
        await self._group_repo.add_member(invitation.group_id, current_user.id, join_role)

        await self._group_repo.increment_invitation_use(invitation)
        return await self._group_repo.get_by_id(invitation.group_id)

    async def remove_member(self, group_id: str, member_user_id: str, current_user: User) -> None:
        """Remove a member from the group. Only leader can remove members."""
        await self._get_leader_group(group_id, current_user) # verify current user is leader
        if member_user_id == current_user.id:
            raise AuthorizationError("Leader cannot remove themselves")
        
        member = await self._group_repo.get_member(group_id, member_user_id)
        if not member:
            raise NotFoundError("Member not found")
        await self._group_repo.remove_member(member)

    async def update_member_role(
        self, group_id: str, member_user_id: str,
        new_role: GroupMemberRole, current_user: User
    ) -> None:
        """Update a member's role in the group. Only leader can update roles."""
        await self._get_leader_group(group_id, current_user) # verify current user is leader
        member = await self._group_repo.get_member(group_id, member_user_id)
        
        if not member:
            raise NotFoundError("Member not found")
        await self._group_repo.update_member_role(member, new_role)

    async def _get_leader_group(self, group_id: str, user: User) -> Group:
        """Helper to get group and verify user is the leader."""
        group = await self._group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundError("Group not found")
        if group.leader_id != user.id:
            raise AuthorizationError("Only the group leader can perform this action")
        return group