"""Similarity analysis independent of Flask globals."""
import os
import re
import logging
import requests
from difflib import SequenceMatcher
logger = logging.getLogger(__name__)

_KEYWORDS = frozenset({
    # Python
    'def','class','return','if','else','elif','for','while','in','not','and',
    'or','import','from','as','with','try','except','finally','raise','pass',
    'break','continue','lambda','yield','None','True','False','self','print',
    # C / C++ / Java
    'int','float','double','char','void','bool','long','short','unsigned',
    'signed','const','static','public','private','protected','new','delete',
    'this','super','extends','implements','interface','class','struct','enum',
    'switch','case','default','do','while','goto','sizeof','typedef','return',
    'include','define','ifdef','endif','printf','scanf','cout','cin','endl',
    'string','vector','map','set','list','array','null','true','false',
    # JavaScript
    'var','let','const','function','arrow','console','log','document',
    'window','event','async','await','promise','then','catch',
})

# Regex : identifiants (noms de variables, fonctions, classes)
_IDENT_RE = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]{2,})\b')

# Regex pour supprimer les commentaires multi-lignes /* ... */
_BLOCK_COMMENT_RE = re.compile(r'/\*.*?\*/', re.DOTALL)
# Regex pour supprimer les docstrings Python """ ... """ ou ''' ... '''
_DOCSTRING_RE = re.compile(r'(""".*?"""|\'\'\'.*?\'\'\')', re.DOTALL)
# Regex pour supprimer les littéraux de chaînes (après suppression des commentaires)
_STRING_LITERAL_RE = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'')
# Regex pour remplacer les nombres par un token générique
_NUMBER_RE = re.compile(r'\b\d+(\.\d+)?\b')


def _strip_comments(source: str) -> str:
    """Supprime tous les styles de commentaires d'un code source."""
    # Commentaires bloc /* ... */
    source = _BLOCK_COMMENT_RE.sub(' ', source)
    # Docstrings Python
    source = _DOCSTRING_RE.sub(' ', source)
    # Commentaires ligne // ...
    lines = []
    for line in source.split('\n'):
        if '//' in line:
            line = line[:line.index('//')].rstrip()
        lines.append(line)
    source = '\n'.join(lines)
    # Commentaires Python # ... (pas les directives #include / #define)
    lines = []
    for line in source.split('\n'):
        stripped = line.lstrip()
        if '#' in line and not stripped.startswith('#include') and not stripped.startswith('#define'):
            line = line[:line.index('#')].rstrip()
        lines.append(line)
    return '\n'.join(lines)


def normalize_code_line(line: str) -> str:
    """
    Normalise une ligne de code pour la comparaison de base.
    Supprime les commentaires inline, la casse et les espaces multiples.
    """
    line = line.strip()
    # Commentaire inline //
    if '//' in line:
        line = line[:line.index('//')].strip()
    # Commentaire Python # (sauf #include / #define)
    if '#' in line and not line.lstrip().startswith(('#include', '#define')):
        line = line[:line.index('#')].strip()
    # Espaces multiples
    line = ' '.join(line.split())
    return line.lower()


def _normalize_lines(text: str) -> list:
    """
    Retourne la liste des lignes normalisées non-vides d'un texte.
    Supprime d'abord tous les commentaires bloc.
    """
    clean = _strip_comments(text)
    result = []
    for line in clean.split('\n'):
        norm = normalize_code_line(line)
        if norm:
            result.append(norm)
    return result


def _tokenize_variables(text: str) -> str:
    """
    Remplace les noms de variables / fonctions par des tokens génériques.
    Exemple : 'int compteur = 0;' → 'int VAR_1 = NUM;'

    Résiste aux attaques de renommage de variables.
    """
    clean = _strip_comments(text)
    # Remplacer les chaînes de caractères par STRING
    clean = _STRING_LITERAL_RE.sub('STRING', clean)
    # Remplacer les nombres par NUM
    clean = _NUMBER_RE.sub('NUM', clean)

    # Construire le mapping identifiant → token
    mapping = {}
    counter = [1]  # liste pour mutation dans la closure

    def replace_ident(match):
        name = match.group(1)
        if name in _KEYWORDS or name.isupper():
            return name  # garder les mots-clés et constantes ALL_CAPS
        if name not in mapping:
            mapping[name] = f'VAR_{counter[0]}'
            counter[0] += 1
        return mapping[name]

    tokenized = _IDENT_RE.sub(replace_ident, clean)
    return tokenized


def _sequence_similarity(seq_a: list, seq_b: list) -> float:
    """
    Calcule la similarité entre deux séquences de chaînes via SequenceMatcher.
    Retourne un float entre 0 et 100.
    """
    if not seq_a or not seq_b:
        return 0.0
    matcher = SequenceMatcher(None, seq_a, seq_b, autojunk=False)
    return matcher.ratio() * 100


def _text_to_token_lines(text: str) -> list:
    """Tokenise les variables puis découpe en lignes normalisées."""
    tokenized = _tokenize_variables(text)
    return _normalize_lines(tokenized)


def check_similarity(text, submission_id, submissions, upload_folder, read_document, web_checker=None):
    """
    Détection de plagiat améliorée — 3 niveaux :
      1. Similarité exacte   (SequenceMatcher sur lignes normalisées)
      2. Similarité structurelle (SequenceMatcher après tokenisation variables)
      3. Plagiat web         (Google Custom Search, si clé configurée)

    Retourne un dict :
      { similarity, sources, status, details }
    """
    if not text or not text.strip():
        return {'similarity': 0, 'sources': [], 'status': 'acceptable', 'details': {}}

    # Préparer les représentations du texte à vérifier
    lines_exact = _normalize_lines(text)
    lines_token = _text_to_token_lines(text)

    max_similarity = 0.0
    sources = []  # liste de dict détaillés

    # -------------------------------------------------------
    # Niveau 1 & 2 : comparaison contre toutes les soumissions
    # -------------------------------------------------------
    for sub in submissions:
        if sub['id'] == submission_id:
            continue
        if not sub.get('filename'):
            continue

        try:
            other_text = ''
            if sub.get('code_submission'):
                path = os.path.join(
                    upload_folder, 'code_submissions', sub['filename']
                )
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        other_text = f.read()
            else:
                path = os.path.join(upload_folder, sub['filename'])
                if os.path.exists(path):
                    other_text = read_document(path)

            if not other_text.strip():
                continue

            other_lines_exact = _normalize_lines(other_text)
            other_lines_token = _text_to_token_lines(other_text)

            # Score 1 : comparaison exacte
            sim_exact = _sequence_similarity(lines_exact, other_lines_exact)
            # Score 2 : comparaison structurelle (résiste au renommage)
            sim_struct = _sequence_similarity(lines_token, other_lines_token)

            # On prend le maximum des deux scores pour chaque paire
            sim_pair = max(sim_exact, sim_struct)

            if sim_pair >= 20:
                student_name = users.get(sub.get('student', ''), {}).get('name', sub.get('student', '?'))
                method = 'structurelle' if sim_struct > sim_exact else 'exacte'
                sources.append({
                    'label': (
                        f"Soumission de {student_name} — "
                        f"{sim_pair:.1f}% (similarité {method})"
                    ),
                    'student': sub.get('student', ''),
                    'submission_id': sub['id'],
                    'similarity_exact': round(sim_exact, 1),
                    'similarity_structural': round(sim_struct, 1),
                    'similarity': round(sim_pair, 1),
                })
                max_similarity = max(max_similarity, sim_pair)
                logger.info(
                    f"Plagiat local — sub {submission_id} vs sub {sub['id']}: "
                    f"exact={sim_exact:.1f}% struct={sim_struct:.1f}%"
                )

        except Exception as e:
            logger.warning(f"Erreur comparaison plagiat (sub {sub['id']}): {e}")

    # -------------------------------------------------------
    # Niveau 3 : plagiat web (Google Custom Search)
    # -------------------------------------------------------
    web_score, web_source = (web_checker or check_web_plagiarism)(text)
    if web_score > 0:
        max_similarity = max(max_similarity, web_score)
        sources.append({
            'label': f"Source web détectée — {web_score:.0f}% de similarité ({web_source})",
            'student': None,
            'submission_id': None,
            'similarity': web_score,
            'similarity_exact': web_score,
            'similarity_structural': web_score,
        })
        logger.info(f"Plagiat web — sub {submission_id}: {web_score}% ({web_source})")

    # Trier les sources par similarité décroissante, garder les 5 premières
    sources.sort(key=lambda s: s['similarity'], reverse=True)

    # Déterminer le statut
    sim = round(max_similarity, 1)
    if sim >= 70:
        status = 'suspect'
    elif sim >= 40:
        status = 'attention'
    else:
        status = 'acceptable'

    result = {
        'similarity': sim,
        'sources': [s['label'] for s in sources[:5]],   # labels texte pour l'affichage
        'requires_human_review': True,
        'interpretation': 'La similarité est un indice à examiner, pas une preuve de fraude.',
        'sources_detail': sources[:5],                   # données complètes pour les APIs
        'status': status,
        'details': {
            'checked_submissions': len([s for s in sources if s['student']]),
            'web_checked': web_score > 0 or bool(os.environ.get('GOOGLE_API_KEY')),
        }
    }

    return result


def check_web_plagiarism(text_sample: str) -> tuple:
    """
    Vérifie le plagiat web via Google Custom Search API.

    Retourne un tuple (score: float, source_label: str) :
      - score = 0    → rien trouvé ou API non configurée
      - score = 60   → 1-2 résultats trouvés
      - score = 80   → 3-4 résultats trouvés
      - score = 95   → 5+ résultats trouvés (copie quasi-certaine)
    """
    api_key = os.environ.get('GOOGLE_API_KEY', '').strip()
    search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID', '').strip()

    if not api_key or not search_engine_id:
        return 0, ''

    try:
        # Choisir la phrase la plus significative (>50 chars, sans mots triviaux)
        candidates = re.split(r'[.!?\n]+', text_sample)
        query = ''
        for candidate in candidates:
            candidate = candidate.strip()
            if 60 <= len(candidate) <= 200 and not candidate.startswith(('import ', '#include', '//')):
                query = candidate
                break

        if not query:
            # Fallback : premiers 100 caractères significatifs
            clean = re.sub(r'\s+', ' ', text_sample.strip())
            query = clean[:120]

        if not query:
            return 0, ''

        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': f'"{query}"',
            'num': 10,
        }
        response = requests.get(
            'https://www.googleapis.com/customsearch/v1',
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            logger.warning(f"Google Search API erreur: {response.status_code}")
            return 0, ''

        data = response.json()
        items = data.get('items', [])
        total = data.get('searchInformation', {}).get('totalResults', '0')
        nb_results = len(items)

        if nb_results == 0:
            return 0, ''

        # Premier résultat le plus pertinent
        first_url = items[0].get('link', '') if items else ''
        first_title = items[0].get('title', '') if items else ''

        if nb_results >= 5:
            score = 95
        elif nb_results >= 3:
            score = 80
        else:
            score = 60

        label = f"{first_title} ({first_url})" if first_url else f"{nb_results} résultat(s) trouvé(s)"
        return score, label

    except requests.Timeout:
        logger.warning("Google Search API: timeout")
        return 0, ''
    except Exception as e:
        logger.warning(f"Erreur vérification web: {e}")
        return 0, ''

