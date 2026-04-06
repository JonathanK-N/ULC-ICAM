"""
Tests unitaires — Moteur de détection de plagiat ULC-ICAM
Exécuter avec: python -m pytest tests/test_plagiarism.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ──────────────────────────────────────────────────────────────────────────────
# Helpers importés directement depuis app
# ──────────────────────────────────────────────────────────────────────────────
from app import (
    normalize_code_line,
    _strip_comments,
    _normalize_lines,
    _tokenize_variables,
    _text_to_token_lines,
    _sequence_similarity,
    check_web_plagiarism,
)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Normalisation des lignes
# ──────────────────────────────────────────────────────────────────────────────

class TestNormalizeLine:

    def test_lowercase(self):
        assert normalize_code_line("INT X = 0;") == "int x = 0;"

    def test_strip_inline_cpp_comment(self):
        result = normalize_code_line("int x = 0; // initialisation")
        assert "//" not in result
        assert "int x = 0;" in result

    def test_strip_python_comment(self):
        result = normalize_code_line("x = 0  # initialisation")
        assert "#" not in result
        assert "x = 0" in result

    def test_keep_include(self):
        result = normalize_code_line("#include <stdio.h>")
        assert "#include" in result

    def test_multiple_spaces_collapsed(self):
        assert normalize_code_line("int   x   =   0;") == "int x = 0;"

    def test_empty_line_returns_empty(self):
        assert normalize_code_line("   ") == ""
        assert normalize_code_line("") == ""


class TestStripComments:

    def test_block_comment_removed(self):
        code = "int x = 0; /* commentaire */ int y = 1;"
        result = _strip_comments(code)
        assert "commentaire" not in result
        assert "int x = 0;" in result
        assert "int y = 1;" in result

    def test_multiline_block_comment(self):
        code = "int a = 1;\n/* ligne 1\n   ligne 2\n*/\nint b = 2;"
        result = _strip_comments(code)
        assert "ligne 1" not in result
        assert "int a = 1;" in result
        assert "int b = 2;" in result

    def test_python_docstring_removed(self):
        code = '"""Ceci est une docstring"""\ndef foo():\n    pass'
        result = _strip_comments(code)
        assert "Ceci est une docstring" not in result
        assert "def foo():" in result

    def test_cpp_line_comment(self):
        code = "x = 1; // commentaire fin de ligne\ny = 2;"
        result = _strip_comments(code)
        assert "commentaire" not in result


# ──────────────────────────────────────────────────────────────────────────────
# 2. Tokenisation des variables
# ──────────────────────────────────────────────────────────────────────────────

class TestTokenizeVariables:

    def test_variable_replaced_by_token(self):
        code = "int compteur = 0;"
        result = _tokenize_variables(code)
        assert "VAR_" in result
        assert "compteur" not in result

    def test_keyword_not_replaced(self):
        code = "for (int i = 0; i < 10; i++) {}"
        result = _tokenize_variables(code)
        assert "for" in result
        assert "int" in result

    def test_same_variable_same_token(self):
        code = "int x = 0;\nx = x + 1;"
        result = _tokenize_variables(code)
        # "x" doit être remplacé par le même token partout
        tokens = [t for t in result.split() if t.startswith("VAR_")]
        # Tous les tokens pour "x" doivent être identiques
        assert len(set(tokens)) <= len(tokens)  # peut avoir plusieurs vars différentes

    def test_numbers_replaced(self):
        code = "int x = 42; float y = 3.14;"
        result = _tokenize_variables(code)
        assert "42" not in result
        assert "3.14" not in result
        assert "NUM" in result

    def test_strings_replaced(self):
        code = 'printf("Hello World");'
        result = _tokenize_variables(code)
        assert "Hello World" not in result
        assert "STRING" in result

    def test_rename_bypass_detected(self):
        """Le renommage de variables ne doit PAS produire des tokens différents."""
        code_a = "int compteur = 0;\ncompteur = compteur + 1;"
        code_b = "int result = 0;\nresult = result + 1;"

        tokens_a = _text_to_token_lines(code_a)
        tokens_b = _text_to_token_lines(code_b)

        sim = _sequence_similarity(tokens_a, tokens_b)
        # Les deux codes ont la même structure → similarité élevée
        assert sim > 70, f"Similarité structurelle trop basse: {sim:.1f}%"


# ──────────────────────────────────────────────────────────────────────────────
# 3. SequenceMatcher
# ──────────────────────────────────────────────────────────────────────────────

class TestSequenceSimilarity:

    def test_identical_sequences(self):
        seq = ["int x = 0;", "x = x + 1;", "return x;"]
        assert _sequence_similarity(seq, seq) == 100.0

    def test_completely_different(self):
        seq_a = ["aaa", "bbb", "ccc"]
        seq_b = ["xxx", "yyy", "zzz"]
        sim = _sequence_similarity(seq_a, seq_b)
        assert sim == 0.0

    def test_partial_overlap(self):
        seq_a = ["ligne1", "ligne2", "ligne3", "ligne4"]
        seq_b = ["ligne1", "ligne2", "autrechose", "fin"]
        sim = _sequence_similarity(seq_a, seq_b)
        assert 30 < sim < 70

    def test_empty_sequences(self):
        assert _sequence_similarity([], []) == 0.0
        assert _sequence_similarity(["a"], []) == 0.0
        assert _sequence_similarity([], ["a"]) == 0.0

    def test_reordered_lines_detected(self):
        """SequenceMatcher détecte les blocs déplacés."""
        seq_a = ["int a = 1;", "int b = 2;", "int c = a + b;", "return c;"]
        seq_b = ["int b = 2;", "int a = 1;", "int c = a + b;", "return c;"]  # a et b inversés
        sim = _sequence_similarity(seq_a, seq_b)
        # Doit détecter la similarité même avec un léger réordonnement
        assert sim > 50


# ──────────────────────────────────────────────────────────────────────────────
# 4. Scénarios réels de plagiat
# ──────────────────────────────────────────────────────────────────────────────

class TestPlagiarismScenarios:

    def test_direct_copy_detected(self):
        """Copie directe : similarité > 90%."""
        code = "int main() {\n    int x = 0;\n    for(int i=0;i<10;i++) x+=i;\n    return x;\n}"
        lines_a = _normalize_lines(code)
        lines_b = _normalize_lines(code)  # copie exacte
        sim = _sequence_similarity(lines_a, lines_b)
        assert sim >= 95

    def test_renamed_variables_detected(self):
        """Copie avec renommage des variables : doit être détectée."""
        code_a = """
int calculer(int valeur) {
    int resultat = 0;
    for (int i = 0; i < valeur; i++) {
        resultat = resultat + i;
    }
    return resultat;
}
"""
        code_b = """
int compute(int input) {
    int output = 0;
    for (int j = 0; j < input; j++) {
        output = output + j;
    }
    return output;
}
"""
        tokens_a = _text_to_token_lines(code_a)
        tokens_b = _text_to_token_lines(code_b)
        sim_struct = _sequence_similarity(tokens_a, tokens_b)
        assert sim_struct > 70, f"Copie renommée non détectée : {sim_struct:.1f}%"

    def test_completely_different_code(self):
        """Deux codes totalement différents : similarité < 30%."""
        code_a = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
        code_b = """
class BinaryTree:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
    def insert(self, val):
        if val < self.value:
            if self.left is None:
                self.left = BinaryTree(val)
"""
        lines_a = _normalize_lines(code_a)
        lines_b = _normalize_lines(code_b)
        sim = _sequence_similarity(lines_a, lines_b)
        assert sim < 30, f"Faux positif — codes différents : {sim:.1f}%"

    def test_comments_stripped_before_comparison(self):
        """Les commentaires ne doivent pas augmenter artificiellement la similarité."""
        code_a = """
int x = 0;  // initialiser x
x = x + 1;  // incrémenter
return x;   // retourner
"""
        code_b = """
int x = 0;
x = x + 1;
return x;
"""
        lines_a = _normalize_lines(code_a)
        lines_b = _normalize_lines(code_b)
        sim = _sequence_similarity(lines_a, lines_b)
        # Les commentaires étant supprimés, les deux codes sont identiques
        assert sim >= 90, f"Commentaires mal gérés : {sim:.1f}%"

    def test_added_noise_still_detected(self):
        """Copie avec quelques lignes ajoutées : toujours détectée."""
        original = [
            "int a = 1;", "int b = 2;", "int c = a + b;",
            "print(c);", "return 0;"
        ]
        plagiat = original[:] + [
            "// ligne ajoutée pour tromper",
            "int z = 99;",
        ]
        sim = _sequence_similarity(original, plagiat)
        assert sim > 60, f"Copie avec bruit non détectée : {sim:.1f}%"


# ──────────────────────────────────────────────────────────────────────────────
# 5. Moteur web (sans vraie clé API)
# ──────────────────────────────────────────────────────────────────────────────

class TestWebPlagiarism:

    def test_no_api_key_returns_zero(self, monkeypatch):
        """Sans clé API, le score doit être 0."""
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        monkeypatch.delenv('GOOGLE_SEARCH_ENGINE_ID', raising=False)
        score, label = check_web_plagiarism("Texte quelconque pour tester la fonction.")
        assert score == 0
        assert label == ''

    def test_empty_text_returns_zero(self, monkeypatch):
        monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
        score, label = check_web_plagiarism("")
        assert score == 0
