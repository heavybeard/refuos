"""Integration tests for generate_espanso.py CLI interface."""
import os
import subprocess
import sys
import yaml
import pytest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generate_espanso.py")
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED_PACKAGES = ["refuos-italiano", "refuos-accenti", "refuos-dev"]
EXPECTED_YMLS = [f"{p}.yml" for p in EXPECTED_PACKAGES]
MANIFEST_REQUIRED_KEYS = {"name", "title", "description", "version", "author", "tags"}


def _run(*args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# --check
# ---------------------------------------------------------------------------

class TestCheckMode:
    def test_exits_zero_with_valid_dictionaries(self):
        result = _run("--check")
        assert result.returncode == 0, f"--check failed:\n{result.stdout}\n{result.stderr}"

    def test_stdout_contains_ok_message(self):
        result = _run("--check")
        assert "OK" in result.stdout or "ok" in result.stdout.lower()


# ---------------------------------------------------------------------------
# --output-dir
# ---------------------------------------------------------------------------

class TestOutputDir:
    def test_creates_three_yml_files(self, tmp_path):
        result = _run("--output-dir", str(tmp_path))
        assert result.returncode == 0, f"--output-dir failed:\n{result.stdout}\n{result.stderr}"
        for name in EXPECTED_YMLS:
            assert (tmp_path / name).exists(), f"Missing file: {name}"

    def test_each_yml_is_non_empty(self, tmp_path):
        _run("--output-dir", str(tmp_path))
        for name in EXPECTED_YMLS:
            path = tmp_path / name
            assert path.stat().st_size > 0, f"File is empty: {name}"

    def test_each_yml_is_valid_yaml(self, tmp_path):
        _run("--output-dir", str(tmp_path))
        for name in EXPECTED_YMLS:
            path = tmp_path / name
            with open(path, encoding="utf-8") as f:
                doc = yaml.safe_load(f)
            assert isinstance(doc, dict), f"{name} did not parse as a dict"
            assert "matches" in doc, f"{name} missing 'matches' key"
            assert isinstance(doc["matches"], list), f"{name} 'matches' is not a list"
            assert len(doc["matches"]) > 0, f"{name} 'matches' is empty"

    def test_legacy_monolithic_file_removed(self, tmp_path):
        legacy = tmp_path / "italian-realtime.yml"
        legacy.write_text("# legacy file\n", encoding="utf-8")
        _run("--output-dir", str(tmp_path))
        assert not legacy.exists(), "Legacy file was not removed"

    def test_no_extra_public_yml_files_created_without_locals(self, tmp_path):
        """Without local dicts, only the three public YMLs should be written."""
        local_dir = os.path.join(REPO_DIR, "dictionaries", "local")
        local_txts = (
            [f for f in os.listdir(local_dir) if f.endswith(".txt")]
            if os.path.isdir(local_dir) else []
        )
        if local_txts:
            pytest.skip("Local dictionaries present — exact file count test not applicable")
        _run("--output-dir", str(tmp_path))
        yml_files = sorted(p.name for p in tmp_path.glob("*.yml"))
        assert yml_files == sorted(EXPECTED_YMLS), f"Unexpected files: {yml_files}"


# ---------------------------------------------------------------------------
# Local dictionaries
# ---------------------------------------------------------------------------

class TestLocalDictionaries:
    def _write_local_dict(self, repo_local_dir, name, content):
        """Write a temporary local .txt file for integration tests."""
        os.makedirs(repo_local_dir, exist_ok=True)
        path = os.path.join(repo_local_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    # Words used only in these integration tests: chosen to not appear in any
    # real dictionary (public or local). If validation fails, they may have
    # been added to a dictionary; replace them with other unused tech terms.
    _TEST_WORDS = "# test local dict\nastrojs\nsolidjs\nqwikdev\n"

    def test_local_dict_generates_local_yml(self, tmp_path, tmp_path_factory):
        """A local .txt file produces a refuos-local-<name>.yml in --output-dir."""
        local_dir = os.path.join(REPO_DIR, "dictionaries", "local")
        local_file = os.path.join(local_dir, "_test_integration.txt")
        os.makedirs(local_dir, exist_ok=True)
        try:
            with open(local_file, "w", encoding="utf-8") as f:
                f.write(self._TEST_WORDS)
            result = _run("--output-dir", str(tmp_path))
            assert result.returncode == 0, f"Failed:\n{result.stdout}\n{result.stderr}"
            expected = tmp_path / "refuos-local-_test_integration.yml"
            assert expected.exists(), f"Missing local yml: {expected.name}"
        finally:
            if os.path.exists(local_file):
                os.remove(local_file)

    def test_local_yml_is_valid_yaml(self, tmp_path):
        """The generated local yml must be valid YAML with a matches list."""
        local_dir = os.path.join(REPO_DIR, "dictionaries", "local")
        local_file = os.path.join(local_dir, "_test_valid.txt")
        os.makedirs(local_dir, exist_ok=True)
        try:
            with open(local_file, "w", encoding="utf-8") as f:
                f.write(self._TEST_WORDS)
            _run("--output-dir", str(tmp_path))
            yml_path = tmp_path / "refuos-local-_test_valid.yml"
            if not yml_path.exists():
                pytest.skip("Local yml not generated (possibly 0 typos produced)")
            with open(yml_path, encoding="utf-8") as f:
                doc = yaml.safe_load(f)
            assert "matches" in doc
        finally:
            if os.path.exists(local_file):
                os.remove(local_file)

    def test_espanso_packages_excludes_local_dicts(self, tmp_path):
        """--espanso-packages must only produce the three public packages."""
        local_dir = os.path.join(REPO_DIR, "dictionaries", "local")
        local_file = os.path.join(local_dir, "_test_hub.txt")
        os.makedirs(local_dir, exist_ok=True)
        try:
            with open(local_file, "w", encoding="utf-8") as f:
                f.write(self._TEST_WORDS)
            result = _run("--espanso-packages", str(tmp_path))
            assert result.returncode == 0, f"Failed:\n{result.stdout}\n{result.stderr}"
            top_dirs = {d.name for d in tmp_path.iterdir() if d.is_dir()}
            assert top_dirs == set(EXPECTED_PACKAGES), (
                f"Unexpected dirs in espanso-packages output: {top_dirs}"
            )
        finally:
            if os.path.exists(local_file):
                os.remove(local_file)


# ---------------------------------------------------------------------------
# --espanso-packages
# ---------------------------------------------------------------------------

class TestEspansoPackages:
    def test_exits_zero(self, tmp_path):
        result = _run("--espanso-packages", str(tmp_path))
        assert result.returncode == 0, f"--espanso-packages failed:\n{result.stdout}\n{result.stderr}"

    def test_creates_package_structure(self, tmp_path):
        _run("--espanso-packages", str(tmp_path))
        for pkg in EXPECTED_PACKAGES:
            pkg_dir = tmp_path / pkg
            assert pkg_dir.is_dir(), f"Missing package dir: {pkg}"
            version_dirs = list(pkg_dir.iterdir())
            assert len(version_dirs) == 1, f"Expected exactly one version dir inside {pkg}"
            version_dir = version_dirs[0]
            assert (version_dir / "package.yml").exists(), f"Missing package.yml in {pkg}"
            assert (version_dir / "_manifest.yml").exists(), f"Missing _manifest.yml in {pkg}"
            assert (version_dir / "README.md").exists(), f"Missing README.md in {pkg}"

    def test_manifest_contains_required_keys(self, tmp_path):
        _run("--espanso-packages", str(tmp_path))
        for pkg in EXPECTED_PACKAGES:
            version_dir = next((tmp_path / pkg).iterdir())
            with open(version_dir / "_manifest.yml", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)
            missing = MANIFEST_REQUIRED_KEYS - set(manifest.keys())
            assert missing == set(), f"{pkg}/_manifest.yml missing keys: {missing}"

    def test_manifest_name_matches_package(self, tmp_path):
        _run("--espanso-packages", str(tmp_path))
        for pkg in EXPECTED_PACKAGES:
            version_dir = next((tmp_path / pkg).iterdir())
            with open(version_dir / "_manifest.yml", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)
            assert manifest["name"] == pkg

    def test_package_yml_is_valid_yaml(self, tmp_path):
        _run("--espanso-packages", str(tmp_path))
        for pkg in EXPECTED_PACKAGES:
            version_dir = next((tmp_path / pkg).iterdir())
            with open(version_dir / "package.yml", encoding="utf-8") as f:
                doc = yaml.safe_load(f)
            assert "matches" in doc, f"{pkg}/package.yml missing 'matches'"

    def test_readme_is_non_empty(self, tmp_path):
        _run("--espanso-packages", str(tmp_path))
        for pkg in EXPECTED_PACKAGES:
            version_dir = next((tmp_path / pkg).iterdir())
            readme = (version_dir / "README.md").read_text(encoding="utf-8")
            assert len(readme.strip()) > 0, f"{pkg}/README.md is empty"
