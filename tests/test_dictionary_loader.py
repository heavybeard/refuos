"""Unit tests for load_words in generate_espanso."""
import generate_espanso as ge


class TestLoadWords:
    def test_basic_words_are_loaded(self, tmp_dict_dir):
        tmp_dict_dir({"test.txt": "ciao\nbello\nmondo\n"})
        words = ge.load_words("test.txt")
        assert words == ["ciao", "bello", "mondo"]

    def test_blank_lines_are_ignored(self, tmp_dict_dir):
        tmp_dict_dir({"test.txt": "ciao\n\nbello\n\n"})
        words = ge.load_words("test.txt")
        assert words == ["ciao", "bello"]

    def test_hash_comments_at_column_zero_ignored(self, tmp_dict_dir):
        tmp_dict_dir({"test.txt": "# commento\nciao\n# altro commento\nbello\n"})
        words = ge.load_words("test.txt")
        assert words == ["ciao", "bello"]

    def test_indented_comment_not_ignored(self, tmp_dict_dir):
        # load_words uses line.startswith("#") without strip, so "  # note"
        # is NOT treated as a comment — it becomes a word (after strip).
        # This test documents the current behaviour.
        tmp_dict_dir({"test.txt": "  # nota\nciao\n"})
        words = ge.load_words("test.txt")
        assert "# nota" in words  # stripped value of "  # nota"

    def test_leading_trailing_whitespace_stripped(self, tmp_dict_dir):
        tmp_dict_dir({"test.txt": "  ciao  \n  bello\n"})
        words = ge.load_words("test.txt")
        assert words == ["ciao", "bello"]

    def test_order_is_preserved(self, tmp_dict_dir):
        tmp_dict_dir({"test.txt": "zebra\nalfa\nmedio\n"})
        words = ge.load_words("test.txt")
        assert words == ["zebra", "alfa", "medio"]

    def test_file_with_only_comments_and_blanks_returns_empty(self, tmp_dict_dir):
        tmp_dict_dir({"test.txt": "# commento\n\n# altro\n\n"})
        words = ge.load_words("test.txt")
        assert words == []

    def test_single_word_no_newline(self, tmp_dict_dir):
        tmp_dict_dir({"test.txt": "ciao"})
        words = ge.load_words("test.txt")
        assert words == ["ciao"]

    def test_real_italiano_file_is_not_empty(self):
        words = ge.load_words("italiano.txt")
        assert len(words) > 0

    def test_real_accenti_file_is_not_empty(self):
        words = ge.load_words("accenti.txt")
        assert len(words) > 0

    def test_real_dev_file_is_not_empty(self):
        words = ge.load_words("dev.txt")
        assert len(words) > 0


class TestLoadLocalDictionaries:
    def test_returns_empty_dict_when_folder_absent(self, tmp_dict_dir):
        tmp_dict_dir({})  # no local/ subfolder
        result = ge.load_local_dictionaries()
        assert result == {}

    def test_returns_empty_dict_when_folder_has_no_txt(self, tmp_dict_dir):
        tmp_dict_dir({"local/README.md": "# docs\n"})
        result = ge.load_local_dictionaries()
        assert result == {}

    def test_loads_single_txt_file(self, tmp_dict_dir):
        tmp_dict_dir({"local/react.txt": "useState\nuseEffect\n"})
        result = ge.load_local_dictionaries()
        assert "react" in result
        assert result["react"] == ["useState", "useEffect"]

    def test_loads_multiple_txt_files(self, tmp_dict_dir):
        tmp_dict_dir({
            "local/frontend.txt": "nextjs\nvitest\n",
            "local/backend.txt": "nestjs\nfastify\n",
        })
        result = ge.load_local_dictionaries()
        assert set(result.keys()) == {"frontend", "backend"}
        assert result["frontend"] == ["nextjs", "vitest"]
        assert result["backend"] == ["nestjs", "fastify"]

    def test_ignores_non_txt_files(self, tmp_dict_dir):
        tmp_dict_dir({
            "local/react.txt": "useState\n",
            "local/README.md": "# docs\n",
            "local/notes.json": "{}",
        })
        result = ge.load_local_dictionaries()
        assert set(result.keys()) == {"react"}

    def test_strips_blank_lines_and_comments(self, tmp_dict_dir):
        tmp_dict_dir({"local/test.txt": "# comment\nuseState\n\nuseEffect\n"})
        result = ge.load_local_dictionaries()
        assert result["test"] == ["useState", "useEffect"]

    def test_files_are_returned_in_sorted_order(self, tmp_dict_dir):
        tmp_dict_dir({
            "local/zebra.txt": "zoo\n",
            "local/alpha.txt": "ant\n",
            "local/middle.txt": "mid\n",
        })
        result = ge.load_local_dictionaries()
        assert list(result.keys()) == ["alpha", "middle", "zebra"]
