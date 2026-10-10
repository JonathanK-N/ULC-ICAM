"""Durable processing queue stored with submissions; no Flask or JSON writes."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid
from ai_service import propose_correction, manual_proposal
from document_service import extract_document
from plagiarism_service import check_similarity


def due_for_processing(submission):
    status = submission.get('processing_status')
    if status == 'pending':
        return True
    if status == 'running':
        try:
            lease = datetime.fromisoformat(submission['processing_started'])
            return datetime.now(timezone.utc) - lease > timedelta(minutes=10)
        except (KeyError, ValueError, TypeError):
            return True
    return False


class SubmissionProcessor:
    def __init__(self, repository, upload_folder, grader=propose_correction):
        self.repository = repository
        self.upload_folder = Path(upload_folder).resolve()
        self.grader = grader

    def process(self, submission_id):
        token = uuid.uuid4().hex
        with self.repository.transaction() as connection:
            data = self.repository.load(connection)
            submission = next((s for s in data['submissions'] if s['id'] == submission_id), None)
            if submission is None:
                raise KeyError(submission_id)
            if not due_for_processing(submission):
                return {'status': 'already_processed'}
            submission.update(processing_status='running', processing_token=token,
                              processing_started=datetime.now(timezone.utc).isoformat())
            assignment = next(a for a in data['assignments'] if a['id'] == submission['assignment_id'])
            self.repository.save(connection, data)
        correction = similarity = None
        failed = False
        try:
            path = (self.upload_folder / submission['filename']).resolve()
            if not path.is_relative_to(self.upload_folder):
                raise ValueError('Unsafe upload path')
            text = extract_document(path)
            if assignment.get('auto_correct'):
                correction = self.grader(text, assignment)
            if assignment.get('plagiarism_check'):
                peers = [s for s in data['submissions'] if s['assignment_id'] == assignment['id']]
                similarity = check_similarity(text, submission_id, peers,
                                              str(self.upload_folder), extract_document)
        except Exception:
            failed = True
            correction = manual_proposal(assignment, 'Traitement interrompu. Vérification manuelle requise.')
        with self.repository.transaction() as connection:
            current = self.repository.load(connection)
            target = next((s for s in current['submissions'] if s['id'] == submission_id), None)
            if target is None or target.get('processing_token') != token:
                return {'status': 'superseded'}
            if correction and target.get('correction', {}).get('review_status') != 'approved':
                correction['review_status'] = 'pending'
                target['correction'] = correction
            if similarity is not None:
                target['plagiarism'] = similarity
            target['processing_status'] = 'needs_review' if failed else 'completed'
            target.pop('processing_token', None)
            current.setdefault('notifications', []).append({
                'id': uuid.uuid4().hex, 'username': assignment['teacher'],
                'message': 'Une soumission est prête à être examinée.',
                'url': '/teacher/assignment_results/' + str(assignment['id']),
                'read': False, 'created_at': datetime.now(timezone.utc).isoformat()})
            current.setdefault('audit_logs', []).append({
                'id': uuid.uuid4().hex, 'username': assignment['teacher'],
                'event': 'submission_processed', 'submission_id': submission_id,
                'created_at': datetime.now(timezone.utc).isoformat()})
            self.repository.save(connection, current)
        return {'status': target['processing_status']}
