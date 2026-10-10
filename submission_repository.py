"""Transactional submission results for isolated relational integration tests.

This repository does not switch Flask storage or start a worker.
"""
from copy import deepcopy

from sqlalchemy import select
import migration_schema as schema


class SubmissionRepository:
    def __init__(self, engine):
        self.engine = engine

    def get(self, submission_id):
        with self.engine.connect() as connection:
            row = connection.execute(select(schema.submissions.c.payload).where(
                schema.submissions.c.id == submission_id)).first()
            if row is None:
                raise KeyError(submission_id)
            result = deepcopy(row[0])
            for table, key in ((schema.grades, 'correction'),
                               (schema.plagiarism, 'plagiarism')):
                record = connection.execute(select(table.c.payload).where(
                    table.c.submission_id == submission_id)).first()
                if record is not None:
                    result[key] = record[0]
            return result

    def save_proposal(self, submission_id, proposal):
        """Save an IA draft without replacing a teacher-approved correction."""
        payload = deepcopy(proposal)
        payload['review_status'] = 'pending'
        return self._save(submission_id, schema.grades, payload, protect_approved=True)

    def save_similarity(self, submission_id, result):
        payload = deepcopy(result)
        payload['requires_human_review'] = True
        return self._save(submission_id, schema.plagiarism, payload)

    def _save(self, submission_id, table, payload, protect_approved=False):
        with self.engine.begin() as connection:
            # Serialize concurrent results for this submission in PostgreSQL.
            parent = connection.execute(select(schema.submissions.c.id).where(
                schema.submissions.c.id == submission_id).with_for_update()).first()
            if parent is None:
                raise KeyError(submission_id)
            condition = table.c.submission_id == submission_id
            record = connection.execute(select(table.c.payload).where(condition)).first()
            if protect_approved and record and record[0].get('review_status') == 'approved':
                return False
            if record is None:
                connection.execute(table.insert().values(submission_id=submission_id,
                                                         payload=payload))
            else:
                connection.execute(table.update().where(condition).values(payload=payload))
        return True
