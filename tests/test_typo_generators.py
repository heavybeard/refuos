"""Unit tests for the typo-generator functions in generate_espanso."""
import pytest

import generate_espanso as ge

# ---------------------------------------------------------------------------
# generate_transpositions
# ---------------------------------------------------------------------------

class TestGenerateTranspositions:
    def test_anche_contains_expected_swaps(self):
        result = ge.generate_transpositions("anche")
        assert "acnhe" in result
        assert "anhce" in result

    def test_result_never_contains_original_word(self):
        for word in ("anche", "bello", "ciao", "comunque"):
            result = ge.generate_transpositions(word)
            assert word not in result, f"'{word}' should not appear in its own transpositions"

    def test_identical_chars_produces_empty(self):
        assert ge.generate_transpositions("aaa") == set()

    def test_two_chars_produces_single_swap(self):
        result = ge.generate_transpositions("ab")
        assert result == {"ba"}

    def test_all_results_are_same_length_as_input(self):
        word = "esempio"
        for typo in ge.generate_transpositions(word):
            assert len(typo) == len(word)


# ---------------------------------------------------------------------------
# generate_missing_double
# ---------------------------------------------------------------------------

class TestGenerateMissingDouble:
    def test_bello_produces_belo(self):
        assert "belo" in ge.generate_missing_double("bello")

    def test_appuntamento_produces_apuntamento(self):
        assert "apuntamento" in ge.generate_missing_double("appuntamento")

    def test_word_without_doubles_returns_empty(self):
        assert ge.generate_missing_double("ciao") == set()

    def test_short_result_excluded(self):
        # "aab" -> dropping one 'a' gives "ab" (len 2), should be excluded
        result = ge.generate_missing_double("aab")
        assert "ab" not in result

    def test_multiple_doubles(self):
        # "abbcc" has two pairs
        result = ge.generate_missing_double("abbcc")
        assert "abcc" in result
        assert "abbc" in result

    def test_original_not_in_result(self):
        result = ge.generate_missing_double("bello")
        assert "bello" not in result


# ---------------------------------------------------------------------------
# generate_missing_char
# ---------------------------------------------------------------------------

class TestGenerateMissingChar:
    def test_short_word_returns_empty(self):
        # "ciao" has 4 chars — below threshold of 5
        assert ge.generate_missing_char("ciao") == set()

    def test_five_char_word_is_active(self):
        result = ge.generate_missing_char("anche")
        assert len(result) > 0

    def test_first_and_last_char_not_removed(self):
        # Removing first or last char is not in scope (range(1, len-1))
        word = "anche"
        result = ge.generate_missing_char(word)
        # Removing first char: "nche"
        assert "nche" not in result
        # Removing last char: "anch"
        assert "anch" not in result

    def test_internal_chars_are_removed(self):
        # "anche" -> remove index 1 ('n') -> "ache"
        result = ge.generate_missing_char("anche")
        assert "ache" in result

    def test_results_have_min_length_3(self):
        for typo in ge.generate_missing_char("anche"):
            assert len(typo) >= 3

    def test_results_shorter_than_input(self):
        word = "example"
        for typo in ge.generate_missing_char(word):
            assert len(typo) == len(word) - 1


# ---------------------------------------------------------------------------
# generate_accent_variants
# ---------------------------------------------------------------------------

class TestGenerateAccentVariants:
    def test_perche_produces_all_variants(self):
        result = ge.generate_accent_variants("perché")
        assert "perche" in result
        assert "perche'" in result
        assert "perche1" in result

    def test_word_without_accent_returns_empty(self):
        assert ge.generate_accent_variants("ciao") == set()
        assert ge.generate_accent_variants("bello") == set()

    def test_original_not_in_result(self):
        result = ge.generate_accent_variants("così")
        assert "così" not in result

    def test_multiple_accented_chars(self):
        # "è" maps to 'e', "e'", "e1"
        result = ge.generate_accent_variants("è")
        assert "e" in result
        assert "e'" in result

    def test_accent_replace_map_coverage(self):
        expected = {"à", "è", "é", "ì", "ò", "ù"}
        actual_keys = set(ge.ACCENT_REPLACE_MAP.keys())
        assert expected == actual_keys


# ---------------------------------------------------------------------------
# generate_all_typos
# ---------------------------------------------------------------------------

class TestGenerateAllTypos:
    def test_result_never_contains_original(self, isolated_all_words):
        for word in ("anche", "bello", "comunque", "perché"):
            typos = ge.generate_all_typos(word)
            assert word not in typos, f"'{word}' found in its own typos"

    def test_all_typos_have_min_length_2(self, isolated_all_words):
        for word in ("anche", "bello", "perché", "sviluppo"):
            for typo in ge.generate_all_typos(word):
                assert len(typo) >= 2, f"Short typo '{typo}' found for '{word}'"

    def test_include_accents_false_excludes_accent_variants(self, isolated_all_words):
        typos = ge.generate_all_typos("perché", include_accents=False)
        for typo in typos:
            assert "'" not in typo, f"Accent variant '{typo}' found with include_accents=False"
            assert "1" not in typo

    def test_include_accents_true_includes_accent_variants(self, isolated_all_words):
        typos = ge.generate_all_typos("perché", include_accents=True)
        assert "perche" in typos

    def test_all_words_exclusion(self, monkeypatch):
        # If a generated typo happens to be a real word, it must be excluded
        monkeypatch.setattr(ge, "ALL_WORDS", {"acnhe"})
        typos = ge.generate_all_typos("anche")
        assert "acnhe" not in typos

    def test_original_excluded_even_if_in_all_words(self, monkeypatch):
        monkeypatch.setattr(ge, "ALL_WORDS", {"anche"})
        typos = ge.generate_all_typos("anche")
        assert "anche" not in typos


# ---------------------------------------------------------------------------
# Regression pairs — must match the README table
# ---------------------------------------------------------------------------

class TestRegressionPairs:
    """Ensure documented examples still work end-to-end."""

    def test_acnhe_for_anche(self):
        assert "acnhe" in ge.generate_all_typos("anche")

    def test_comunqeu_for_comunque(self):
        assert "comunqeu" in ge.generate_all_typos("comunque")

    def test_cosnt_for_const(self):
        assert "cosnt" in ge.generate_all_typos("const")

    def test_reutrn_for_return(self):
        assert "reutrn" in ge.generate_all_typos("return")


# ---------------------------------------------------------------------------
# Blocklist regressions — valid Italian words must never be used as triggers
# ---------------------------------------------------------------------------

# These tests intentionally use the real ALL_WORDS (no isolated_all_words
# fixture) because the whole point is to verify that words added to the
# dictionaries are actually loaded at runtime and excluded from typo generation.
@pytest.mark.parametrize(
    ("trigger", "source"),
    [
        # Transpositions of common Italian words
        ("mare", "madre"),
        ("vero", "verso"),
        ("lago", "largo"),
        ("lato", "alto"),
        ("vano", "vanno"),
        ("temo", "tempo"),
        ("moto", "molto"),
        ("sena", "senza"),
        # Missing-double variants
        ("fato", "fatto"),
        ("fano", "fanno"),
        ("tropo", "troppo"),
        ("tuto", "tutto"),
        # Missing-char variants (including one from dev.txt)
        ("sete", "siete"),
        ("site", "siete"),
        # Accent (missing-accent) variants
        ("faro", "farò"),
        ("pero", "però"),
        ("sara", "sarà"),
    ],
)
def test_blocklisted_word_not_generated_as_typo(trigger, source):
    assert trigger not in ge.generate_all_typos(source)
