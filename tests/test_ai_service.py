import json
from types import SimpleNamespace
import pytest
from ai_service import assessment_rubric, parse_rubric_response, propose_correction


def response_data():
    return {'criteria': [{'id': item['id'], 'score': item['points'] / 2,
                          'justification': 'Argument observé dans le travail.'}
                         for item in assessment_rubric({'max_score': 100})],
            'feedback': ['Développez la justification de votre solution.']}


def test_rubric_computes_score_and_requires_review():
    result = parse_rubric_response(json.dumps(response_data()), {'max_score': 100})
    assert result['score'] == 50 and result['review_status'] == 'pending'
    assert len(result['criteria']) == 4


@pytest.mark.parametrize('change', ['over', 'duplicate', 'missing', 'nan', 'no_reason'])
def test_invalid_criterion_cannot_generate_grade(change):
    data = response_data()
    if change == 'over':
        data['criteria'][0]['score'] = 500
    elif change == 'duplicate':
        data['criteria'][1]['id'] = data['criteria'][0]['id']
    elif change == 'missing':
        data['criteria'].pop()
    elif change == 'nan':
        data['criteria'][0]['score'] = float('nan')
    else:
        data['criteria'][0]['justification'] = ''
    with pytest.raises(ValueError):
        parse_rubric_response(json.dumps(data), {'max_score': 100})


def test_invalid_rubric_is_rejected():
    with pytest.raises(ValueError):
        assessment_rubric({'max_score': 100, 'rubric': [{'id': 'one', 'label': 'One', 'points': 10}]})


def test_api_contract_with_fake_client_and_no_paid_call(monkeypatch):
    monkeypatch.setenv('OPENAI_MODEL', 'isolated-model')
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
            content=json.dumps(response_data())))])
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    assert propose_correction('Student work', {'max_score': 100}, client)['score'] == 50
    assert calls[0]['response_format'] == {'type': 'json_object'}
    assert calls[0]['messages'][0]['role'] == 'system'
    assert propose_correction('x' * 16001, {'max_score': 100}, client)['score'] is None
    assert len(calls) == 1
