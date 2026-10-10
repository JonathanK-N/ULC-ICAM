from types import SimpleNamespace
from plagiarism_service import check_web_plagiarism


def test_search_hit_count_is_not_a_fraud_score(monkeypatch):
    import plagiarism_service
    monkeypatch.setenv('GOOGLE_API_KEY', 'isolated-test-only')
    monkeypatch.setenv('GOOGLE_SEARCH_ENGINE_ID', 'isolated-test-only')
    monkeypatch.setattr(plagiarism_service.requests, 'get', lambda *args, **kwargs:
        SimpleNamespace(status_code=200, json=lambda: {'items': [
            {'title': 'Candidate', 'link': 'https://example.test', 'snippet': ''} for _ in range(10)]}))
    score, label = check_web_plagiarism('A sufficiently long academic statement with a detailed reasoning and explanation for this exercise')
    assert score == 0 and 'examiner' in label
