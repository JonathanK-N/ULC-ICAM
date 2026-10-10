import pytest
from reportlab.pdfgen import canvas
from document_service import extract_document


def test_pdf_reader_preserves_text_and_enforces_extraction_limit(tmp_path):
    path = tmp_path / 'synthetic.pdf'
    document = canvas.Canvas(str(path))
    document.drawString(40, 700, 'Synthetic academic answer 2026')
    document.save()
    assert 'Synthetic academic answer 2026' in extract_document(path)
    with pytest.raises(ValueError, match='manual review'):
        extract_document(path, max_characters=10)


def test_invalid_pdf_is_not_accepted_as_an_answer(tmp_path):
    path = tmp_path / 'broken.pdf'
    path.write_bytes(b'not a PDF')
    with pytest.raises(Exception):
        extract_document(path)
