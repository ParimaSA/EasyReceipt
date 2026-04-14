from pydantic import BaseModel
from typing import Optional, List
from .records import RecordResponse


class PeriodSummary(BaseModel):
    total_income: float
    total_expense: float
    net: float
    record_count: int

class CategoryBreakdown(BaseModel):
    category_id: Optional[str]
    category_name: str
    total: float
    count: int
    percentage: float

class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: float
    expense: float
    net: float

class DashboardResponse(BaseModel):
    period_summary: PeriodSummary
    category_breakdown: List[CategoryBreakdown]
    monthly_trends: List[MonthlyTrend]
    recent_records: List[RecordResponse]
