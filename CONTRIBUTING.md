# Contributing to Refuos

Thanks for taking the time to contribute! Every word counts.

---

## Table of contents

- [Add a word to an existing dictionary](#add-a-word-to-an-existing-dictionary)
- [Propose a new dictionary](#propose-a-new-dictionary)
- [Report a wrong correction](#report-a-wrong-correction)
- [Request a feature](#request-a-feature)
- [Development setup](#development-setup)
- [Style guide](#style-guide)
- [Commit conventions](#commit-conventions)

---

## Add a word to an existing dictionary

This is the most common contribution and requires no coding.

1. **Fork** the repository and create a branch: `git checkout -b add-word/yourword`
2. Open the right file in `dictionaries/`:
   - `italiano.txt` — everyday Italian words
   - `accenti.txt` — accented words, future-tense verbs, nouns ending in `-ità`
   - `dev.txt` — tech/code terms (JS, React, CSS, Git, ...)
3. Add the word on its own line. Keep the file sorted alphabetically.
4. Regenerate and verify:

   ```bash
   python3 generate_espanso.py --check   # validate, no files written
   python3 generate_espanso.py --output-dir /tmp/refuos-out  # inspect output
   ```

5. Open a Pull Request. The CI will run the same validation automatically.

> **Not sure which file to edit?** Just pick the closest one and mention it in the PR — the maintainer will move it if needed.

---

## Propose a new dictionary

Want to add a whole new language or domain (e.g. Spanish, French, medical terms)?

1. Open an **Issue** using the [New dictionary](.github/ISSUE_TEMPLATE/new-dictionary.yml) template.
2. Include a sample list of at least 20 words so the maintainer can gauge quality and scope.
3. If approved, open a PR that:
   - Adds `dictionaries/<name>.txt` with the word list
   - Adds a generation block in `generate_espanso.py` (follow the existing pattern)
   - Updates `README.md` to document the new package

---

## Report a wrong correction

If Refuos corrects a word you didn't want corrected, open a **Bug report** issue.

Please include:

- What you typed
- What it was corrected to
- What you expected
- Your OS and Espanso version

---

## Request a feature

Open a **Feature request** issue. Describe the problem you're trying to solve, not just the solution.

---

## Development setup

```bash
# Clone the repo
git clone https://github.com/heavybeard/refuos.git
cd refuos

# Edit a dictionary
nano dictionaries/italiano.txt

# Validate (no Espanso needed)
python3 generate_espanso.py --check

# Generate to a temp dir for inspection
python3 generate_espanso.py --output-dir /tmp/refuos-out

# Generate to your actual Espanso config (requires Espanso installed)
python3 generate_espanso.py
espanso restart
```

**Requirements:** Python 3.9+. No external dependencies.

---

## Style guide

- Words must be **lowercase** (the generator handles `propagate_case` automatically for ASCII words).
- One word per line.
- Lines starting with `#` are comments — use them to group related words.
- **No duplicates** within a file or across files. The generator will reject duplicates.
- Keep words **sorted alphabetically** within each logical group.
- Minimum word length is 3 characters (shorter words are skipped by the generator).

---

## Commit conventions

Use short, imperative commit messages:

```text
add: parola to italiano
fix: remove duplicate 'esempio'
feat: add French dictionary
docs: update CONTRIBUTING.md
```

---

## License

By contributing you agree that your changes will be released under the [MIT License](LICENSE).
