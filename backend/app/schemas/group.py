from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.core.enums import GroupMemberRole
from .auth import UserBrief


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None

class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    
class GroupMemberResponse(BaseModel):
    id: str
    user_id: str
    group_id: str
    role: GroupMemberRole
    joined_at: datetime
    user: Optional[UserBrief] = None

    model_config = {"from_attributes": True}

class GroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    leader_id: str
    is_active: bool
    created_at: datetime
    members: List[GroupMemberResponse] = []

    model_config = {"from_attributes": True}

class InvitationCreate(BaseModel):
    invited_role: GroupMemberRole = GroupMemberRole.MEMBER
    max_uses: Optional[int] = Field(None, gt=0)
    expires_hours: Optional[int] = Field(None, gt=0)

class InvitationResponse(BaseModel):
    id: str
    group_id: str
    token: str
    invited_role: GroupMemberRole
    is_active: bool
    max_uses: Optional[int]
    use_count: int
    expires_at: Optional[datetime]
    created_at: datetime
    invite_url: Optional[str] = None

    model_config = {"from_attributes": True}

class JoinGroupRequest(BaseModel):
    token: str
