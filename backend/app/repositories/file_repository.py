from pathlib import Path
import uuid

class FileRepository:
    """Persistence layer for handling file operations."""

    def __init__(self, upload_dir: str):
        """Initialize with an injected storage path."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, content: bytes, extension: str) -> str:
        unique_name = f"{uuid.uuid4()}{extension}"
        dest = self.upload_dir / unique_name
        dest.write_bytes(content)
        return f"/uploads/{unique_name}"

    async def get_file(self, relative_path: str) -> bytes | None:
        filename = relative_path.split("/")[-1]
        file_path = self.upload_dir / filename
        if not file_path.exists():
            return None
        return file_path.read_bytes()