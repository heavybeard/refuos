"""Unit tests for validate_dictionaries in generate_espanso."""
import generate_espanso as ge


class TestValidateDictionaries:
    def test_real_dictionaries_have_no_errors(self):
        """Regression: current dictionaries must be clean."""
        errors = ge.validate_dictionaries()
        assert errors == [], f"Unexpected validation errors:\n" + "\n".join(errors)

    def test_duplicate_in_italiano_reported(self, monkeypatch):
        def fake_load(filename):
            if filename == "italiano.txt":
                return ["ciao", "bello", "ciao"]  # duplicate
            if filename == "accenti.txt":
                return ["perché"]
            return ["const"]

        monkeypatch.setattr(ge, "load_words", fake_load)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {})
        errors = ge.validate_dictionaries()
        assert any("Duplicate" in e and "italiano.txt" in e for e in errors)

    def test_duplicate_in_accenti_reported(self, monkeypatch):
        def fake_load(filename):
            if filename == "italiano.txt":
                return ["ciao"]
            if filename == "accenti.txt":
                return ["perché", "così", "perché"]  # duplicate
            return ["const"]

        monkeypatch.setattr(ge, "load_words", fake_load)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {})
        errors = ge.validate_dictionaries()
        assert any("Duplicate" in e and "accenti.txt" in e for e in errors)

    def test_duplicate_in_dev_reported(self, monkeypatch):
        def fake_load(filename):
            if filename == "italiano.txt":
                return ["ciao"]
            if filename == "accenti.txt":
                return ["perché"]
            return ["const", "return", "const"]  # duplicate

        monkeypatch.setattr(ge, "load_words", fake_load)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {})
        errors = ge.validate_dictionaries()
        assert any("Duplicate" in e and "dev.txt" in e for e in errors)

    def test_overlap_italiano_accenti_reported(self, monkeypatch):
        def fake_load(filename):
            if filename == "italiano.txt":
                return ["ciao", "perché"]  # "perché" also in accenti
            if filename == "accenti.txt":
                return ["perché", "così"]
            return ["const"]

        monkeypatch.setattr(ge, "load_words", fake_load)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {})
        errors = ge.validate_dictionaries()
        assert any("italiano.txt" in e and "accenti.txt" in e for e in errors)

    def test_overlap_italiano_dev_reported(self, monkeypatch):
        def fake_load(filename):
            if filename == "italiano.txt":
                return ["ciao", "const"]  # "const" also in dev
            if filename == "accenti.txt":
                return ["perché"]
            return ["const", "return"]

        monkeypatch.setattr(ge, "load_words", fake_load)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {})
        errors = ge.validate_dictionaries()
        assert any("italiano.txt" in e and "dev.txt" in e for e in errors)

    def test_overlap_accenti_dev_reported(self, monkeypatch):
        def fake_load(filename):
            if filename == "italiano.txt":
                return ["ciao"]
            if filename == "accenti.txt":
                return ["perché", "const"]  # "const" also in dev
            return ["const", "return"]

        monkeypatch.setattr(ge, "load_words", fake_load)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {})
        errors = ge.validate_dictionaries()
        assert any("accenti.txt" in e and "dev.txt" in e for e in errors)

    def test_clean_dictionaries_return_empty_list(self, monkeypatch):
        def fake_load(filename):
            if filename == "italiano.txt":
                return ["ciao", "bello"]
            if filename == "accenti.txt":
                return ["perché", "così"]
            return ["const", "return"]

        monkeypatch.setattr(ge, "load_words", fake_load)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {})
        assert ge.validate_dictionaries() == []


class TestValidateLocalDictionaries:
    """Tests for validation of local (private) dictionaries."""

    def _public_stub(self, monkeypatch):
        """Patch load_words to return minimal, non-overlapping public words."""
        def fake_load(filename):
            if filename == "italiano.txt":
                return ["ciao"]
            if filename == "accenti.txt":
                return ["perché"]
            return ["const"]  # dev.txt

        monkeypatch.setattr(ge, "load_words", fake_load)

    def test_clean_local_returns_no_errors(self, monkeypatch):
        self._public_stub(monkeypatch)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {
            "react": ["useState", "useEffect"],
        })
        assert ge.validate_dictionaries() == []

    def test_duplicate_within_local_file_reported(self, monkeypatch):
        self._public_stub(monkeypatch)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {
            "react": ["useState", "useEffect", "useState"],
        })
        errors = ge.validate_dictionaries()
        assert any("Duplicate" in e and "local/react.txt" in e for e in errors)

    def test_overlap_with_public_reported(self, monkeypatch):
        self._public_stub(monkeypatch)
        # "const" is in the fake dev.txt above
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {
            "react": ["useState", "const"],
        })
        errors = ge.validate_dictionaries()
        assert any("local/react.txt" in e and "public dictionary" in e for e in errors)

    def test_overlap_between_local_files_reported(self, monkeypatch):
        self._public_stub(monkeypatch)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {
            "frontend": ["useState", "vitest"],
            "backend": ["nestjs", "vitest"],  # "vitest" in both
        })
        errors = ge.validate_dictionaries()
        assert any(
            "local/frontend.txt" in e and "local/backend.txt" in e
            for e in errors
        )

    def test_no_overlap_between_different_local_files(self, monkeypatch):
        self._public_stub(monkeypatch)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {
            "frontend": ["useState", "vitest"],
            "backend": ["nestjs", "fastify"],
        })
        errors = ge.validate_dictionaries()
        assert not any("local/" in e for e in errors)

    def test_multiple_violations_all_reported(self, monkeypatch):
        self._public_stub(monkeypatch)
        monkeypatch.setattr(ge, "load_local_dictionaries", lambda: {
            # duplicate within file + overlap with public
            "react": ["useState", "useState", "const"],
        })
        errors = ge.validate_dictionaries()
        assert len(errors) >= 2
