"""Bounded document extraction shared by web and worker processes."""
from pathlib import Path


def extract_document(path, max_characters=100000):
    path = Path(path)
    if path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError('Document too large for automatic processing')
    if path.suffix.lower() == '.pdf':
        from pypdf import PdfReader
        text = '\n'.join(page.extract_text() or '' for page in PdfReader(path).pages)
    elif path.suffix.lower() == '.docx':
        import docx2txt
        text = docx2txt.process(str(path))
    else:
        text = path.read_text(encoding='utf-8', errors='replace')
    if len(text) > max_characters:
        raise ValueError('Document requires manual review; automatic processing limit exceeded')
    return text
