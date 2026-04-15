from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, extract
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime
from app.models.models import Record, Category
from app.schemas.record import RecordCreate, RecordUpdate
from app.core.enums import RecordType
import uuid


class RecordRepository:
    """Persistence layer for Record."""

    def __init__(self, db: AsyncSession):
        """Initialize with async database session."""
        self._db = db

    async def get_by_id(self, record_id: str) -> Optional[Record]:
        """Get a record by its ID, with category and owner preloaded."""
        result = await self._db.execute(
            select(Record)
            .options(selectinload(Record.category), selectinload(Record.owner))
            .where(Record.id == record_id)
        )
        return result.scalar_one_or_none()

    async def get_personal_records(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 50,
        category_id: Optional[str] = None,
        record_type: Optional[RecordType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Tuple[List[Record], int]:
        """Get personal records for a user, with optional filtering and pagination."""
        conditions = [Record.owner_id == owner_id, Record.group_id == None]
        if category_id:
            conditions.append(Record.category_id == category_id)
        if record_type:
            conditions.append(Record.type == record_type)
        if date_from:
            conditions.append(Record.date >= date_from)
        if date_to:
            conditions.append(Record.date <= date_to)

        # Count the filtered records for pagination
        count_q = select(func.count(Record.id)).where(and_(*conditions))
        total = (await self._db.execute(count_q)).scalar()

        # Filter the records
        q = (
            select(Record)
            .options(selectinload(Record.category), selectinload(Record.owner))
            .where(and_(*conditions))
            .order_by(Record.date.desc())
            .offset(skip)
            .limit(limit)
        )
        records = (await self._db.execute(q)).scalars().all()
        return list(records), total

    async def get_group_records(
        self,
        group_id: str,
        skip: int = 0,
        limit: int = 50,
        member_id: Optional[str] = None,
        category_id: Optional[str] = None,
        record_type: Optional[RecordType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Tuple[List[Record], int]:
        """Get records for a group, with optional filtering and pagination."""
        conditions = [Record.group_id == group_id]
        if member_id:
            conditions.append(Record.owner_id == member_id)
        if category_id:
            conditions.append(Record.category_id == category_id)
        if record_type:
            conditions.append(Record.type == record_type)
        if date_from:
            conditions.append(Record.date >= date_from)
        if date_to:
            conditions.append(Record.date <= date_to)

        # Count the filtered records for pagination
        count_q = select(func.count(Record.id)).where(and_(*conditions))
        total = (await self._db.execute(count_q)).scalar()

        # Filter the records
        q = (
            select(Record)
            .options(selectinload(Record.category), selectinload(Record.owner))
            .where(and_(*conditions))
            .order_by(Record.date.desc())
            .offset(skip)
            .limit(limit)
        )
        records = (await self._db.execute(q)).scalars().all()
        return list(records), total

    async def create(self, owner_id: str, data: RecordCreate, receipt_url: Optional[str] = None, is_scanned: bool = False) -> Record:
        """Create a new record for the user."""
        record = Record(
            id=str(uuid.uuid4()),
            owner_id=owner_id,
            group_id=data.group_id,
            title=data.title,
            amount=data.amount,
            type=data.type,
            note=data.note,
            date=data.date,
            category_id=data.category_id,
            receipt_image_url=receipt_url,
            is_scanned=is_scanned,
        )
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def update(self, record: Record, data: RecordUpdate) -> Record:
        """Update an existing record."""
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(record, k, v)
        await self._db.flush()
        await self._db.refresh(record)
        return record

    async def delete(self, record: Record) -> None:
        """Delete a record."""
        await self._db.delete(record)
        await self._db.flush()

    async def get_summary(
        self,
        owner_id: Optional[str] = None,
        group_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Get summary of income, expenses, and net total for a user or group within a date range."""
        conditions = []
        if owner_id and not group_id:
            conditions.append(Record.owner_id == owner_id)
            conditions.append(Record.group_id == None)
        elif group_id:
            conditions.append(Record.group_id == group_id)
        if date_from:
            conditions.append(Record.date >= date_from)
        if date_to:
            conditions.append(Record.date <= date_to)

        where = and_(*conditions) if conditions else True

        # Calculate total income, total expenses, and count of records
        income_q = select(func.sum(Record.amount)).where(and_(where, Record.type == "income"))
        expense_q = select(func.sum(Record.amount)).where(and_(where, Record.type == "expense"))
        count_q = select(func.count(Record.id)).where(where)

        total_income = (await self._db.execute(income_q)).scalar() or 0.0
        total_expense = (await self._db.execute(expense_q)).scalar() or 0.0
        record_count = (await self._db.execute(count_q)).scalar() or 0

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net": total_income - total_expense,
            "record_count": record_count,
        }

    async def get_monthly_trends(
        self,
        owner_id: Optional[str] = None,
        group_id: Optional[str] = None,
        months: int = 6,
    ) -> List[dict]:
        """Get monthly trends of income and expenses for a user or group over the past N months."""
        conditions = []
        if owner_id and not group_id:
            conditions.append(Record.owner_id == owner_id)
            conditions.append(Record.group_id == None)
        elif group_id:
            conditions.append(Record.group_id == group_id)

        where = and_(*conditions) if conditions else True

        # Filter records and extract year/month from date
        q = (
            select(
                extract("year", Record.date).label("year"),
                extract("month", Record.date).label("month"),
                Record.type,
                func.sum(Record.amount).label("total"),
            )
            .where(where)
            .group_by("year", "month", Record.type)
            .order_by("year", "month")
        )
        rows = (await self._db.execute(q)).all()

        # Aggregate income and expenses by year and month
        trends: dict = {}
        for row in rows:
            key = (int(row.year), int(row.month))
            if key not in trends:
                # Create empty income/expense entry for this month
                trends[key] = {"year": int(row.year), "month": int(row.month), "income": 0.0, "expense": 0.0}
            if row.type == "income":
                trends[key]["income"] = float(row.total)
            else:
                trends[key]["expense"] = float(row.total)

        # Calculate net again from the income/expense
        result = []
        for k in sorted(trends.keys())[-months:]:
            t = trends[k]
            t["net"] = t["income"] - t["expense"]
            result.append(t)
        return result

    async def get_category_breakdown(
        self,
        owner_id: Optional[str] = None,
        group_id: Optional[str] = None,
        record_type: RecordType = RecordType.EXPENSE,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """Get breakdown of expenses by category for a user or group within a date range."""
        conditions = [Record.type == record_type]
        if owner_id and not group_id:
            conditions.append(Record.owner_id == owner_id)
            conditions.append(Record.group_id == None)
        elif group_id:
            conditions.append(Record.group_id == group_id)
        if date_from:
            conditions.append(Record.date >= date_from)
        if date_to:
            conditions.append(Record.date <= date_to)

        # Filter records, join with category, and group by category
        q = (
            select(
                Record.category_id,
                Category.name.label("category_name"),
                func.sum(Record.amount).label("total"),
                func.count(Record.id).label("count"),
            )
            .outerjoin(Category, Record.category_id == Category.id)
            .where(and_(*conditions))
            .group_by(Record.category_id, Category.name)
            .order_by(func.sum(Record.amount).desc())
        )
        rows = (await self._db.execute(q)).all()

        # Calculate grand total for percentage calculation
        grand_total = sum(float(r.total) for r in rows) or 1 # summation = 1 if no records to avoid division by zero

        # Format the result with percentage of total for each category
        return [
            {
                "category_id": r.category_id,
                "category_name": r.category_name or "Uncategorized",
                "total": float(r.total),
                "count": r.count,
                "percentage": round(float(r.total) / grand_total * 100, 1),
            }
            for r in rows
        ]
