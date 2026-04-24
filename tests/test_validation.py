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
        assert ge.validate_dictionaries() == []
