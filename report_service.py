"""Credential-free report generation for dedicated workers."""
import csv
import io
import uuid
from pathlib import Path


def csv_cell(value):
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value


def assignment_report(snapshot, assignment_id, actor):
    user = snapshot['users'].get(actor, {})
    assignment = next((item for item in snapshot['assignments'] if item['id'] == assignment_id), None)
    if user.get('disabled') or not assignment or not (user.get('role') == 'admin' or
            (user.get('role') == 'teacher' and assignment.get('teacher') == actor)):
        raise PermissionError('Report access denied')
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Étudiant', 'Déposé le', 'Note', 'Maximum', 'Validation', 'Publié'])
    for submission in snapshot['submissions']:
        if submission['assignment_id'] != assignment_id:
            continue
        correction = submission.get('correction', {})
        writer.writerow([csv_cell(submission['student']), csv_cell(submission.get('submitted_at', '')),
                         correction.get('score'), correction.get('max_score'),
                         correction.get('review_status', ''), bool(submission.get('results_available'))])
    return output.getvalue()


def store_assignment_report(repository, upload_folder, assignment_id, actor):
    with repository.transaction() as connection:
        data = repository.load(connection)
    content = assignment_report(data, assignment_id, actor)
    identifier = uuid.uuid4().hex
    folder = Path(upload_folder).resolve() / 'reports'
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / (identifier + '.csv')
    with destination.open('x', encoding='utf-8', newline='') as stream:
        stream.write(content)
    destination.chmod(0o600)
    with repository.transaction() as connection:
        current = repository.load(connection)
        # Recheck permission if a course was reassigned during generation.
        assignment_report(current, assignment_id, actor)
        current.setdefault('generated_reports', []).append({'id': identifier, 'username': actor,
                                                           'assignment_id': assignment_id,
                                                           'filename': identifier + '.csv'})
        current.setdefault('notifications', []).append({'id': uuid.uuid4().hex, 'username': actor,
                                                       'message': 'Votre rapport est prêt.', 'read': False,
                                                       'url': '/reports/generated/' + identifier})
        repository.save(connection, current)
    return {'id': identifier, 'url': '/reports/generated/' + identifier}
