"""Optional Redis cache for role-scoped academic summaries."""
import hashlib
import json
import math
import os


def academic_summary(data, actor):
    user = data['users'].get(actor, {})
    if user.get('disabled') or user.get('role') not in ('student', 'teacher', 'admin'):
        raise PermissionError('Summary access denied')
    role = user['role']
    assignments = [a for a in data['assignments'] if role == 'admin' or
                   (role == 'teacher' and a.get('teacher') == actor) or
                   (role == 'student' and actor in data.get('course_enrollments', {}).get(str(a.get('course_id')), []))]
    identifiers = {a['id'] for a in assignments}
    submissions = [s for s in data['submissions'] if s['assignment_id'] in identifiers and
                   (role != 'student' or s.get('student') == actor)]
    percentages = []
    pending = 0
    for submission in submissions:
        correction = submission.get('correction', {})
        if correction.get('review_status') == 'pending':
            pending += 1
        score, maximum = correction.get('score'), correction.get('max_score')
        if correction.get('review_status') != 'approved' or (role == 'student' and not submission.get('results_available')):
            continue
        if isinstance(score, (int, float)) and isinstance(maximum, (int, float)) and maximum > 0 and math.isfinite(score):
            percentages.append(score / maximum * 100)
    return {'assignments': len(assignments), 'submissions': len(submissions),
            'pending': pending if role != 'student' else None,
            'average': round(sum(percentages) / len(percentages), 1) if percentages else None}


def cached_summary(data, actor, client=None):
    user = data['users'].get(actor, {})
    if user.get('disabled') or user.get('role') not in ('student', 'teacher', 'admin'):
        raise PermissionError('Summary access denied')
    # Fingerprint only relevant state; credentials and contact details are excluded.
    signature = {'users': {key: {'role': value.get('role'), 'disabled': value.get('disabled', False)}
                           for key, value in data['users'].items()},
                 'assignments': [(a['id'], a.get('teacher'), a.get('course_id')) for a in data['assignments']],
                 'enrollments': data.get('course_enrollments', {}),
                 'submissions': [(s['id'], s['assignment_id'], s.get('student'),
                                  s.get('results_available'), s.get('correction', {}).get('score'),
                                  s.get('correction', {}).get('max_score'),
                                  s.get('correction', {}).get('review_status')) for s in data['submissions']]}
    key = 'cognito:summary:' + hashlib.sha256((actor + json.dumps(signature, sort_keys=True)).encode()).hexdigest()
    if client is None and os.environ.get('REDIS_URL'):
        import redis
        client = redis.Redis.from_url(os.environ['REDIS_URL'], socket_connect_timeout=1, socket_timeout=1)
    try:
        cached = client.get(key) if client else None
        if cached:
            return json.loads(cached)
    except Exception:
        pass
    result = academic_summary(data, actor)
    if client:
        try:
            client.setex(key, 60, json.dumps(result))
        except Exception:
            pass
    return result
