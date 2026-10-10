from academic_cache import cached_summary


def test_cache_is_scoped_and_invalidated_on_grade_publication():
    class Cache:
        def __init__(self):
            self.items = {}
        def get(self, key):
            return self.items.get(key)
        def setex(self, key, ttl, value):
            self.items[key] = value
    data = {'users': {'s': {'role': 'student'}, 'other': {'role': 'student'}, 't': {'role': 'teacher'}},
            'assignments': [{'id': 1, 'teacher': 't', 'course_id': 1}],
            'course_enrollments': {'1': ['s', 'other']},
            'submissions': [{'id': 1, 'assignment_id': 1, 'student': 's', 'results_available': False,
                             'correction': {'score': 80, 'max_score': 100, 'review_status': 'approved'}}]}
    cache = Cache()
    assert cached_summary(data, 's', cache)['average'] is None
    assert cached_summary(data, 'other', cache)['submissions'] == 0
    data['submissions'][0]['results_available'] = True
    assert cached_summary(data, 's', cache)['average'] == 80
    assert cached_summary(data, 'other', cache)['average'] is None
