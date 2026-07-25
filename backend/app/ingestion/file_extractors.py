import io

from pypdf import PdfReader


def extract_text(filename: str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        return _extract_pdf(content)
    return content.decode("utf-8", errors="replace")


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()
