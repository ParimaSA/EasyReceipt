from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.core.enums import RecordType
from .auth import UserBrief


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

class CategoryResponse(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: bool
    owner_id: Optional[str] = None

    model_config = {"from_attributes": True}

class OCRResult(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None
    raw_text: str

class RecordCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    type: RecordType
    note: Optional[str] = None
    date: datetime
    category_id: Optional[str] = None
    group_id: Optional[str] = None

class RecordUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[RecordType] = None
    note: Optional[str] = None
    date: Optional[datetime] = None
    category_id: Optional[str] = None

class RecordResponse(BaseModel):
    id: str
    title: str
    amount: float
    type: RecordType
    note: Optional[str] = None
    date: datetime
    receipt_image_url: Optional[str] = None
    is_scanned: bool
    owner_id: str
    group_id: Optional[str] = None
    category_id: Optional[str] = None
    category: Optional[CategoryResponse] = None
    owner: Optional["UserBrief"] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

RecordResponse.model_rebuild()