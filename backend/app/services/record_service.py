"""
Record Service — business logic layer.
Delegates data access to RecordRepository and GroupRepository.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from datetime import datetime

from app.repositories.record_repository import RecordRepository
from app.repositories.group_repository import GroupRepository
from app.models.models import Record, User
from app.schemas.record import RecordCreate, RecordUpdate
from app.schemas.dashboard import DashboardResponse, PeriodSummary, CategoryBreakdown, MonthlyTrend
from app.core.enums import RecordType, GroupMemberRole
from app.core.exceptions import NotFoundError, AuthorizationError


class RecordService:
    """Business logic for managing records."""

    def __init__(self, db: AsyncSession):
        """Initialize and connect to Persistence layer."""
        self._record_repo = RecordRepository(db)
        self._group_repo = GroupRepository(db)

    async def get_personal_records(
        self, current_user: User, skip: int = 0, limit: int = 50,
        group_id: Optional[str] = None,
        record_type: Optional[RecordType] = None,
        category_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Tuple[List[Record], int]:
        """Get personal records with optional filtering and pagination."""
        return await self._record_repo.get_personal_records(
            owner_id=current_user.id, skip=skip, limit=limit,
            group_id=group_id, record_type=record_type, 
            category_id=category_id, date_from=date_from, date_to=date_to,
        )

    async def get_group_records(
        self, group_id: str, current_user: User,
        skip: int = 0, limit: int = 50,
        member_id: Optional[str] = None,
        category_id: Optional[str] = None,
        record_type: Optional[RecordType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Tuple[List[Record], int]:
        """Get group records with optional filtering and pagination. User must be a member/leader."""
        await self._assert_group_member(group_id, current_user.id)
        return await self._record_repo.get_group_records(
            group_id=group_id, skip=skip, limit=limit,
            member_id=member_id, category_id=category_id,
            record_type=record_type, date_from=date_from, date_to=date_to,
        )

    async def create_record(
        self, current_user: User, data: RecordCreate,
        receipt_url: Optional[str] = None, is_scanned: bool = False,
    ) -> Record:
        """Create a new record. If group_id is provided, user must not be a viewer."""
        if data.group_id:
            member = await self._group_repo.get_member(data.group_id, current_user.id)
            if not member:
                raise AuthorizationError("You are not a member of this group")
            if member.role == GroupMemberRole.VIEWER:
                raise AuthorizationError("Viewers cannot create records")

        record = await self._record_repo.create(current_user.id, data, receipt_url, is_scanned)
        return await self._record_repo.get_by_id(record.id)

    async def update_record(self, record_id: str, current_user: User, data: RecordUpdate) -> Record:
        """Update a record. User must be the owner or group leader."""
        record = await self._get_owned_record(record_id, current_user)
        updated = await self._record_repo.update(record, data)
        return await self._record_repo.get_by_id(updated.id)

    async def delete_record(self, record_id: str, current_user: User) -> None:
        """Delete a record. User must be the owner or group leader."""
        record = await self._get_owned_record(record_id, current_user)
        await self._record_repo.delete(record)

    async def get_personal_dashboard(
        self, current_user: User,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> DashboardResponse:
        """Get personal dashboard data for the specified period."""
        summary = await self._record_repo.get_summary(owner_id=current_user.id, date_from=date_from, date_to=date_to)
        categories = await self._record_repo.get_category_breakdown(owner_id=current_user.id, date_from=date_from, date_to=date_to)
        trends = await self._record_repo.get_monthly_trends(owner_id=current_user.id)
        recent, _ = await self._record_repo.get_personal_records(owner_id=current_user.id, limit=5)
        return self._build_dashboard(summary, categories, trends, recent)

    async def get_group_dashboard(
        self, group_id: str, current_user: User,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> DashboardResponse:
        """Get group dashboard data for the specified period."""
        await self._assert_group_member(group_id, current_user.id) # check if user is a member
        summary = await self._record_repo.get_summary(group_id=group_id, date_from=date_from, date_to=date_to)
        categories = await self._record_repo.get_category_breakdown(group_id=group_id, date_from=date_from, date_to=date_to)
        trends = await self._record_repo.get_monthly_trends(group_id=group_id)
        recent, _ = await self._record_repo.get_group_records(group_id=group_id, limit=5)
        return self._build_dashboard(summary, categories, trends, recent)

    async def _get_owned_record(self, record_id: str, user: User) -> Record:
        """Helper to fetch a record and check if the user is the owner or group leader."""
        record = await self._record_repo.get_by_id(record_id)
        if not record:
            raise NotFoundError("Record not found")
        if record.owner_id != user.id:
            # Group leader can also edit group records
            if record.group_id:
                member = await self._group_repo.get_member(record.group_id, user.id)
                if member and member.role == GroupMemberRole.LEADER:
                    return record
            raise AuthorizationError("You don't own this record")
        return record

    async def _assert_group_member(self, group_id: str, user_id: str):
        """Helper to check if a user is a member of a group."""
        member = await self._group_repo.get_member(group_id, user_id)
        if not member:
            raise AuthorizationError("You are not a member of this group")

    def _build_dashboard(self, summary, categories, trends, recent) -> DashboardResponse:
        """Helper to construct DashboardResponse from raw data."""
        from app.schemas.record import RecordResponse
        return DashboardResponse(
            period_summary=PeriodSummary(**summary),
            category_breakdown=[CategoryBreakdown(**c) for c in categories],
            monthly_trends=[MonthlyTrend(**t) for t in trends],
            recent_records=[RecordResponse.model_validate(r) for r in recent],
        )
