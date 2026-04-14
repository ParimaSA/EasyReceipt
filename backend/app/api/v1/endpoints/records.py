from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.middleware.auth import get_current_user, require_group_member
from app.services.record_service import RecordService
from app.services.ocr_service import OCRService
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse, OCRResult
from app.schemas.dashboard import DashboardResponse
from app.core.enums import RecordType
from app.models.models import User

router = APIRouter(prefix="/records", tags=["records"])
_ocr = OCRService()


@router.get("/personal", response_model=dict)
async def list_personal_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    group_id: Optional[str] = None,
    type: Optional[RecordType] = None,
    category_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List personal records for the authenticated user."""
    records, total = await RecordService(db).get_personal_records(
        current_user, skip=skip, limit=limit,
        group_id=group_id, record_type=type, category_id=category_id,
        date_from=date_from, date_to=date_to,
    )
    return {
        "items": [RecordResponse.model_validate(r) for r in records],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/personal/dashboard", response_model=DashboardResponse)
async def personal_dashboard(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard statistics for personal account."""
    return await RecordService(db).get_personal_dashboard(current_user, date_from, date_to)


@router.get("/group/{group_id}", response_model=dict)
async def list_group_records(
    group_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    member_id: Optional[str] = None,
    category_id: Optional[str] = None,
    type: Optional[RecordType] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(require_group_member()),
    db: AsyncSession = Depends(get_db),
):
    """List group records. Accessible by all group members including viewers."""
    records, total = await RecordService(db).get_group_records(
        group_id, current_user, skip=skip, limit=limit,
        member_id=member_id, category_id=category_id, 
        record_type=type, date_from=date_from, date_to=date_to,
    )
    return {
        "items": [RecordResponse.model_validate(r) for r in records],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/group/{group_id}/dashboard", response_model=DashboardResponse)
async def group_dashboard(
    group_id: str,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(require_group_member()),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard statistics for a group. Accessible by all members."""
    return await RecordService(db).get_group_dashboard(group_id, current_user, date_from, date_to)


@router.post("/", response_model=RecordResponse, status_code=201)
async def create_record(
    data: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a record (personal or group).
    For group records: only LEADER and MEMBER are allowed (enforced in service).
    """
    return await RecordService(db).create_record(current_user, data)


@router.put("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: str,
    data: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a record. Only the owner or group leader can update."""
    return await RecordService(db).update_record(record_id, current_user, data)


@router.delete("/{record_id}", status_code=204)
async def delete_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a record. Only the owner or group leader can delete."""
    await RecordService(db).delete_record(record_id, current_user)


@router.post("/scan", response_model=OCRResult)
async def scan_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a receipt image for OCR extraction.
    Returns extracted title, amount, and date to pre-fill the form.
    """
    contents = await file.read()
    return await _ocr.extract_from_image(contents)


@router.post("/scan-and-save", response_model=RecordResponse, status_code=201)
async def scan_and_save_receipt(
    data: RecordCreate = Depends(),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a receipt image, run OCR, and immediately save the record."""
    contents = await file.read()
    receipt_url = await _ocr.save_image(contents, file.filename)
    return await RecordService(db).create_record(
        current_user, data, receipt_url=receipt_url, is_scanned=True
    )
