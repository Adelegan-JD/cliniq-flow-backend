from pathlib import Path
from uuid import uuid4

UPLOAD_DIR = Path('backend/uploads')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_file(filename: str, content: bytes) -> str:
    safe_name = f"{uuid4()}-{filename}"
    target = UPLOAD_DIR / safe_name
    target.write_bytes(content)
    return f"/uploads/{safe_name}"
