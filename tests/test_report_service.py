import pytest
from report_service import assignment_report


def test_report_is_owned_and_spreadsheet_cells_cannot_execute_formulas():
    data = {'users': {'t': {'role': 'teacher'}, 'other': {'role': 'teacher'}, 's': {'role': 'student'}},
            'assignments': [{'id': 1, 'teacher': 't'}],
            'submissions': [{'id': 1, 'assignment_id': 1, 'student': '=EXTERNAL()',
                             'correction': {'score': 80, 'max_score': 100, 'review_status': 'pending'}}]}
    assert "'=EXTERNAL()" in assignment_report(data, 1, 't')
    for user in ('other', 's'):
        with pytest.raises(PermissionError):
            assignment_report(data, 1, user)
