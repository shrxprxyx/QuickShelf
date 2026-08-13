"""
QR generation for books.

Hackathon-pragmatic choice: QR images are generated and saved to a local
`static/qr_codes/` folder served by FastAPI's StaticFiles, rather than
uploaded to Supabase Storage. This avoids needing Supabase creds wired up
just to get QR issue/return working. Swap `save_qr_locally` for a Supabase
upload later if you have time — the call site in routers/books.py doesn't
need to change, just what this function returns.
"""
import io
import os
import uuid as uuid_lib

import qrcode

QR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "qr_codes")
os.makedirs(QR_DIR, exist_ok=True)


def generate_book_qr(book_id: uuid_lib.UUID, base_url: str = "http://localhost:8000") -> str:
    """
    Generates a QR code encoding `book:<id>` and saves it as a PNG.
    Returns the URL the frontend can use to display/download it.

    `book:<id>` (not a full URL) is what the scanner reads — keeps the
    payload short and unambiguous to parse in routers/issues.py.
    """
    payload = f"book:{book_id}"

    img = qrcode.make(payload)
    filename = f"{book_id}.png"
    filepath = os.path.join(QR_DIR, filename)
    img.save(filepath)

    return f"{base_url}/static/qr_codes/{filename}"


def delete_book_qr(book_id: uuid_lib.UUID) -> None:
    filepath = os.path.join(QR_DIR, f"{book_id}.png")
    if os.path.exists(filepath):
        os.remove(filepath)