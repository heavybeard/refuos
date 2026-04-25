"""Shared fixtures for the Refuos test suite."""
import os
import pytest
import generate_espanso


@pytest.fixture()
def tmp_dict_dir(tmp_path, monkeypatch):
    """
    Return a helper that writes named .txt files into a temp directory and
    patches generate_espanso.DICT_DIR to point there, so load_words reads
    from the temp files instead of the real dictionaries/ folder.

    Supports subdirectories: use a key like "local/foo.txt" to create
    files under tmp_path/local/.

    Usage:
        def test_something(tmp_dict_dir):
            tmp_dict_dir({"italiano.txt": "ciao\nbello\n"})
            words = generate_espanso.load_words("italiano.txt")

        def test_local(tmp_dict_dir):
            tmp_dict_dir({
                "italiano.txt": "ciao\n",
                "accenti.txt": "",
                "dev.txt": "",
                "local/react.txt": "useState\nuseEffect\n",
            })
            local = generate_espanso.load_local_dictionaries()
    """
    monkeypatch.setattr(generate_espanso, "DICT_DIR", str(tmp_path))

    def _write(files: dict[str, str]):
        for name, content in files.items():
            target = tmp_path / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

    return _write


@pytest.fixture()
def all_dict_paths():
    """Return the absolute paths of the three real dictionary files."""
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_dir = os.path.join(repo, "dictionaries")
    return {
        "italiano": os.path.join(dict_dir, "italiano.txt"),
        "accenti":  os.path.join(dict_dir, "accenti.txt"),
        "dev":      os.path.join(dict_dir, "dev.txt"),
    }


@pytest.fixture()
def isolated_all_words(monkeypatch):
    """
    Patch ALL_WORDS to an empty set so typo-generator tests are deterministic
    and don't accidentally depend on the real dictionary contents.
    """
    monkeypatch.setattr(generate_espanso, "ALL_WORDS", set())
