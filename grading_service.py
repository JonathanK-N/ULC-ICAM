"""Draft evaluation rules; an unavailable evaluator must never invent a grade."""
import math
import re


def parse_ai_response(response_text, max_score):
    if not isinstance(response_text, str):
        return None, ['Évaluation indisponible : correction manuelle requise.']
    match = re.search(r'^\s*NOTE:\s*(-?\d+(?:[.,]\d+)?)\s*/\s*(\d+(?:[.,]\d+)?)', response_text, re.I | re.M)
    feedback = [line.strip()[1:].strip() for line in response_text.splitlines() if line.strip().startswith('-')][:5]
    if match:
        score, denominator = (float(value.replace(',', '.')) for value in match.groups())
        if math.isfinite(score) and 0 <= score <= max_score and denominator == max_score:
            return score, feedback or ['Proposition à vérifier par le professeur.']
    return None, feedback or ['Note IA non valide : correction manuelle requise.']


def requires_review(correction):
    return correction.get('review_status') == 'pending'
