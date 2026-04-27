"""Tests for YAML generation functions in generate_espanso."""
import yaml

import generate_espanso as ge

ACCENTED_CHARS = set("àèéìòù")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(content: str) -> dict:
    """Parse YAML content and return the document dict."""
    return yaml.safe_load(content)


# ---------------------------------------------------------------------------
# generate_pack — generic behaviour
# ---------------------------------------------------------------------------

class TestGeneratePack:
    def test_output_is_valid_yaml(self):
        content, _ = ge.generate_pack(["anche", "bello"], "Test", "Test pack")
        doc = _parse(content)
        assert isinstance(doc, dict)

    def test_matches_key_present(self):
        content, _ = ge.generate_pack(["anche", "bello"], "Test", "Test pack")
        doc = _parse(content)
        assert "matches" in doc

    def test_matches_is_non_empty_list(self):
        content, total = ge.generate_pack(["anche", "bello"], "Test", "Test pack")
        doc = _parse(content)
        assert isinstance(doc["matches"], list)
        assert len(doc["matches"]) > 0
        assert total > 0

    def test_every_match_has_triggers_replace_word(self):
        content, _ = ge.generate_pack(["anche", "bello"], "Test", "Test pack")
        doc = _parse(content)
        for match in doc["matches"]:
            assert "triggers" in match, f"Match missing triggers: {match}"
            assert isinstance(match["triggers"], list), f"triggers must be a list: {match}"
            assert len(match["triggers"]) > 0, f"triggers list is empty: {match}"
            assert "replace" in match, f"Match missing replace: {match}"
            assert match.get("word") is True, f"Match missing word:true: {match}"

    def test_propagate_case_only_for_non_accented_words(self):
        # "perché" contains an accent — propagate_case must NOT appear
        # "bello" has no accent — propagate_case should appear
        content, _ = ge.generate_pack(["perché", "bello"], "Test", "Test pack")
        doc = _parse(content)
        for match in doc["matches"]:
            replace = match.get("replace", "")
            has_accent = any(c in ACCENTED_CHARS for c in replace)
            if has_accent:
                assert "propagate_case" not in match, (
                    f"propagate_case present for accented word '{replace}'"
                )
            else:
                assert match.get("propagate_case") is True, (
                    f"propagate_case missing for non-accented word '{replace}'"
                )

    def test_header_contains_refuos_and_url(self):
        content, _ = ge.generate_pack(["anche"], "Test", "Test pack")
        assert "Refuos" in content
        assert "https://github.com/heavybeard/refuos" in content

    def test_empty_word_list_returns_zero_total(self):
        content, total = ge.generate_pack([], "Test", "Empty pack")
        assert total == 0

    def test_short_words_below_3_chars_are_skipped(self):
        # "ab" has len 2 — must be silently ignored
        content, total = ge.generate_pack(["ab"], "Test", "Short words")
        assert total == 0

    def test_total_matches_actual_rules_count(self):
        # total counts individual triggers across all match blocks;
        # len(matches) counts word groups (one per word with at least one typo)
        words = ["anche", "bello", "comunque"]
        content, total = ge.generate_pack(words, "Test", "Count check")
        doc = _parse(content)
        trigger_count = sum(len(m["triggers"]) for m in doc["matches"])
        assert trigger_count == total


# ---------------------------------------------------------------------------
# generate_accenti_pack — specific behaviour
# ---------------------------------------------------------------------------

class TestGenerateAccentiPack:
    def test_output_is_valid_yaml(self):
        content, _ = ge.generate_accenti_pack()
        _parse(content)  # must not raise

    def test_matches_non_empty(self):
        content, total = ge.generate_accenti_pack()
        assert total > 0

    def test_no_regex_rules(self):
        content, _ = ge.generate_accenti_pack()
        assert "regex:" not in content

    def test_contains_trigger_rules(self):
        content, _ = ge.generate_accenti_pack()
        assert "triggers:" in content

    def test_hardcoded_short_word_rules_present(self):
        content, _ = ge.generate_accenti_pack()
        for trigger in ("e'", "e1", "si'", "si1", "la'", "la1", "li'", "li1"):
            assert trigger in content, f"Missing hardcoded trigger: {trigger!r}"

    def test_hardcoded_rules_included_in_total(self):
        _, total = ge.generate_accenti_pack()
        # 8 hardcoded short-word rules = 8 minimum
        assert total >= 8


# ---------------------------------------------------------------------------
# generate_dev_pack — specific behaviour
# ---------------------------------------------------------------------------

class TestGenerateDevPack:
    def test_output_is_valid_yaml(self):
        content, _ = ge.generate_dev_pack()
        _parse(content)

    def test_matches_non_empty(self):
        _, total = ge.generate_dev_pack()
        assert total > 0

    def test_no_accent_variants_in_triggers(self):
        content, _ = ge.generate_dev_pack()
        doc = _parse(content)
        for match in doc["matches"]:
            for trigger in match.get("triggers", []):
                for ch in ACCENTED_CHARS:
                    assert ch not in trigger, (
                        f"Accented char '{ch}' found in dev trigger '{trigger}'"
                    )


# ---------------------------------------------------------------------------
# generate_local_pack — private local dictionaries
# ---------------------------------------------------------------------------

class TestGenerateLocalPack:
    def test_output_is_valid_yaml(self):
        content, _ = ge.generate_local_pack("react", ["vitest", "playwright", "turborepo"])
        doc = _parse(content)
        assert isinstance(doc, dict)
        assert "matches" in doc

    def test_pack_name_appears_in_header(self):
        content, _ = ge.generate_local_pack("mypkg", ["vitest"])
        assert "mypkg" in content

    def test_matches_non_empty_for_typo_prone_words(self):
        _, total = ge.generate_local_pack("react", ["vitest", "playwright"])
        assert total > 0

    def test_empty_word_list_returns_zero_total(self):
        _, total = ge.generate_local_pack("empty", [])
        assert total == 0

    def test_no_accent_variants_in_triggers(self):
        content, _ = ge.generate_local_pack("local", ["playwright", "turborepo"])
        doc = _parse(content)
        for match in doc.get("matches") or []:
            for trigger in match.get("triggers", []):
                for ch in ACCENTED_CHARS:
                    assert ch not in trigger, (
                        f"Accented char '{ch}' found in local trigger '{trigger}'"
                    )
