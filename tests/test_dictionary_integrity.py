"""Integrity tests for the real dictionary .txt files in dictionaries/."""
import os
import pytest

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_DIR = os.path.join(REPO_DIR, "dictionaries")

ACCENTED_CHARS = set("àèéìòù")

DICT_FILES = ["italiano.txt", "accenti.txt", "dev.txt"]


def _load_raw_lines(filename: str) -> list[str]:
    """Return all raw lines (including comments/blanks) from a dictionary file."""
    with open(os.path.join(DICT_DIR, filename), encoding="utf-8") as f:
        return f.readlines()


def _load_words(filename: str) -> list[str]:
    """Load meaningful words (skip blanks and # comments, strip whitespace)."""
    return [
        line.strip()
        for line in _load_raw_lines(filename)
        if line.strip() and not line.startswith("#")
    ]


# ---------------------------------------------------------------------------
# Parametrized per-file tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filename", DICT_FILES)
class TestPerFile:
    def test_no_duplicates(self, filename):
        words = _load_words(filename)
        seen: set[str] = set()
        dupes = []
        for w in words:
            if w in seen:
                dupes.append(w)
            seen.add(w)
        assert dupes == [], f"Duplicates in {filename}: {dupes}"

    def test_no_trailing_whitespace(self, filename):
        bad = []
        for raw in _load_raw_lines(filename):
            # rstrip('\n') keeps intentional content, rstrip() removes trailing spaces
            if raw.rstrip("\n") != raw.rstrip():
                bad.append(repr(raw))
        assert bad == [], f"Trailing whitespace found in {filename}:\n" + "\n".join(bad)

    def test_utf8_encoding(self, filename):
        path = os.path.join(DICT_DIR, filename)
        try:
            with open(path, encoding="utf-8", errors="strict") as f:
                f.read()
        except UnicodeDecodeError as exc:
            pytest.fail(f"{filename} is not valid UTF-8: {exc}")

    def test_words_have_min_length_one(self, filename):
        words = _load_words(filename)
        empty = [w for w in words if len(w) == 0]
        assert empty == [], f"Empty words found in {filename}"

    def test_sorted_alphabetically(self, filename):
        words = _load_words(filename)
        # Use locale-agnostic sort; file should be sorted case-insensitively
        expected = sorted(words, key=str.casefold)
        if words != expected:
            # Find first mismatch
            for i, (actual, exp) in enumerate(zip(words, expected)):
                if actual != exp:
                    pytest.fail(
                        f"{filename} is not sorted alphabetically. "
                        f"First mismatch at position {i}: got '{actual}', expected '{exp}'"
                    )
            pytest.fail(f"{filename} is not sorted alphabetically (length mismatch)")


# ---------------------------------------------------------------------------
# Cross-file overlap tests
# ---------------------------------------------------------------------------

class TestCrossFileOverlap:
    def test_no_overlap_italiano_accenti(self):
        it = set(_load_words("italiano.txt"))
        acc = set(_load_words("accenti.txt"))
        overlap = it & acc
        assert overlap == set(), f"Words in both italiano.txt and accenti.txt: {sorted(overlap)}"

    def test_no_overlap_italiano_dev(self):
        it = set(_load_words("italiano.txt"))
        dev = set(_load_words("dev.txt"))
        overlap = it & dev
        assert overlap == set(), f"Words in both italiano.txt and dev.txt: {sorted(overlap)}"

    def test_no_overlap_accenti_dev(self):
        acc = set(_load_words("accenti.txt"))
        dev = set(_load_words("dev.txt"))
        overlap = acc & dev
        assert overlap == set(), f"Words in both accenti.txt and dev.txt: {sorted(overlap)}"


# ---------------------------------------------------------------------------
# Accent placement test
# ---------------------------------------------------------------------------

class TestAccentPlacement:
    def test_accented_words_only_in_accenti(self):
        """Words containing àèéìòù must live in accenti.txt, not italiano or dev."""
        wrong: dict[str, list[str]] = {}
        for fname in ("italiano.txt", "dev.txt"):
            bad = [w for w in _load_words(fname) if any(c in ACCENTED_CHARS for c in w)]
            if bad:
                wrong[fname] = bad
        assert wrong == {}, (
            "Accented words found outside accenti.txt:\n"
            + "\n".join(f"  {f}: {ws}" for f, ws in wrong.items())
        )
