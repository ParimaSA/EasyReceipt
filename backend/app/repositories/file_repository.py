from pathlib import Path
import uuid

class FileRepository:
    """Persistence layer for handling file operations."""

    def __init__(self, upload_dir: str):
        """Initialize with the file storage (Local Folder)."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, content: bytes, extension: str) -> str:
        """Save file content and return relative URL."""
        unique_name = f"{uuid.uuid4()}{extension}"
        dest = self.upload_dir / unique_name
        dest.write_bytes(content)
        return f"/uploads/{unique_name}"
    