"""
OCR Service — receipt scanning logic.
Uses Pillow + pytesseract to extract text, then parses amounts/dates.
"""
import re
import os
import uuid
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

from app.schemas.record import OCRResult
from app.core.config import settings
from app.repositories.file_repository import FileRepository



class OCRService:
    """Business logic for OCR operations."""

    def __init__(self):
        """Initialize and connect to Persistence layer."""
        self.file_repo = FileRepository(upload_dir=settings.UPLOAD_DIR)


    async def save_image(self, image_bytes: bytes, filename: str):
        """Save image and extracted OCR data."""
        ext = Path(filename).suffix.lower() or ".jpg"
        file_path = await self.file_repo.save_file(image_bytes, ext)
        
        ocr_results = await self.extract_from_image(image_bytes)
        return {"url": file_path, "data": ocr_results}

    async def extract_from_image(self, image_bytes: bytes) -> OCRResult:
        """Run OCR on image bytes and return structured result."""
        try:
            import pytesseract
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(image_bytes))
            raw_text = pytesseract.image_to_string(image)
        except ImportError:
            raw_text = ""
        except Exception:
            raw_text = ""

        title = self._extract_title(raw_text)
        amount = self._extract_amount(raw_text)
        date = self._extract_date(raw_text)

        return OCRResult(title=title, amount=amount, date=date, raw_text=raw_text)

    def _extract_amount(self, text: str) -> Optional[float]:
        """Find the largest currency amount in text (likely the total)."""
        patterns = [
            r"total[:\s]*[\$฿£€]?\s*([\d,]+\.?\d*)",
            r"amount[:\s]*[\$฿£€]?\s*([\d,]+\.?\d*)",
            r"[\$฿£€]\s*([\d,]+\.\d{2})",
            r"([\d,]+\.\d{2})",
        ]
        candidates = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    val = float(match.group(1).replace(",", ""))
                    candidates.append(val)
                except ValueError:
                    continue
        return max(candidates) if candidates else None

    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from receipt text."""
        patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})",
            r"(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})",
        ]
        formats = [
            "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
            "%d-%m-%Y", "%m-%d-%Y", "%Y-%m-%d",
            "%d %B %Y", "%d %b %Y",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
        return None

    def _extract_title(self, text: str) -> Optional[str]:
        """Use first non-empty line as title (typically merchant name)."""
        for line in text.splitlines():
            clean = line.strip()
            if clean and len(clean) > 2:
                return clean[:100]
        return None
