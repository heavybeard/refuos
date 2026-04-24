#!/usr/bin/env python3
"""
Refuos - Espanso rule generator
https://github.com/heavybeard/refuos

Generates modular YAML files for Espanso. Each package is independent:
  - refuos-italiano.yml  -> everyday Italian words
  - refuos-accenti.yml   -> accents, future-tense verbs, -ita' nouns
  - refuos-dev.yml       -> tech/code terms

Words are loaded from the dictionaries/ folder. To add a word, edit the
corresponding .txt file and re-run this script.

Usage:
  python3 generate_espanso.py                      # writes to Espanso config dir
  python3 generate_espanso.py --check              # validate only, no files written
  python3 generate_espanso.py --output-dir DIR     # write YAML files to DIR
  python3 generate_espanso.py --espanso-packages DIR  # generate Espanso Hub package structure in DIR
"""
import argparse
import os
import platform
import subprocess
import textwrap

# ===================================================================
# Utils
# ===================================================================
QWERTY_NEIGHBORS = {
    'q': 'wa', 'w': 'qeas', 'e': 'wrds', 'r': 'etdf', 't': 'ryfg',
    'y': 'tugh', 'u': 'yijh', 'i': 'uokj', 'o': 'iplk', 'p': 'ol',
    'a': 'qwsz', 's': 'awedxz', 'd': 'serfcx', 'f': 'drtgvc',
    'g': 'ftyhbv', 'h': 'gyujnb', 'j': 'huikmn', 'k': 'jiolm',
    'l': 'kop', 'z': 'asx', 'x': 'zsdc', 'c': 'xdfv',
    'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk',
}
ACCENT_REPLACE_MAP = {
    'à': ['a', "a'"], 'è': ['e', "e'", 'e1'], 'é': ['e', "e'", 'e1'],
    'ì': ['i', "i'"], 'ò': ['o', "o'"], 'ù': ['u', "u'"],
}

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_DIR = os.path.join(REPO_DIR, "dictionaries")


# ===================================================================
# Dictionary loader
# ===================================================================
def load_words(filename: str) -> list[str]:
    """Load words from a dictionary file. Ignores blank lines and # comments."""
    path = os.path.join(DICT_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


ITALIANO_WORDS = load_words("italiano.txt")
ACCENTI_WORDS = load_words("accenti.txt")
DEV_WORDS = load_words("dev.txt")

ALL_WORDS = set(ITALIANO_WORDS) | set(ACCENTI_WORDS) | set(DEV_WORDS)


# ===================================================================
# Typo generators
# ===================================================================
def generate_transpositions(word):
    typos = set()
    for i in range(len(word) - 1):
        chars = list(word)
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
        typo = ''.join(chars)
        if typo != word:
            typos.add(typo)
    return typos


def generate_missing_double(word):
    typos = set()
    i = 0
    while i < len(word) - 1:
        if word[i] == word[i + 1]:
            typo = word[:i] + word[i + 1:]
            if len(typo) >= 3:
                typos.add(typo)
        i += 1
    return typos


def generate_missing_char(word):
    typos = set()
    if len(word) >= 5:
        for i in range(1, len(word) - 1):
            typo = word[:i] + word[i + 1:]
            if len(typo) >= 3:
                typos.add(typo)
    return typos


def generate_accent_variants(word):
    typos = set()
    for i, char in enumerate(word):
        if char in ACCENT_REPLACE_MAP:
            for r in ACCENT_REPLACE_MAP[char]:
                typo = word[:i] + r + word[i + 1:]
                if typo != word:
                    typos.add(typo)
    return typos


def generate_all_typos(word, include_accents=True):
    typos = set()
    typos |= generate_transpositions(word)
    typos |= generate_missing_double(word)
    if include_accents:
        typos |= generate_accent_variants(word)
    if len(word) >= 5:
        typos |= generate_missing_char(word)
    typos -= ALL_WORDS
    typos.discard(word)
    return {t for t in typos if len(t) >= 2}


def esc(s):
    return f'"{s}"'


# ===================================================================
# Multi-file generation
# ===================================================================
def make_header(title, desc):
    return [
        f"# Refuos - {title}",
        f"# {desc}",
        "# https://github.com/heavybeard/refuos",
        "# Auto-generated - regenerate with: python3 generate_espanso.py",
        "", "matches:", "",
    ]


def generate_pack(words, title, desc, include_accents=True):
    lines = make_header(title, desc)
    total = 0
    seen = set()
    for word in sorted(set(words)):
        if len(word) < 3:
            continue
        for typo in sorted(generate_all_typos(word, include_accents)):
            if typo in seen:
                continue
            seen.add(typo)
            lines.append(f"  - trigger: {esc(typo)}")
            lines.append(f"    replace: {esc(word)}")
            if not any(c in word for c in 'àèéìòù'):
                lines.append("    propagate_case: true")
            lines.append("    word: true")
            lines.append("")
            total += 1
    return '\n'.join(lines), total


def generate_accenti_pack():
    content, total = generate_pack(
        ACCENTI_WORDS, "Accenti",
        "Missing accents, future tense verbs, -ità nouns"
    )
    regex_lines = [
        "  # REGEX — Accent catch-all patterns",
    ]
    for pattern, repl, comment in [
        ("(?P<stem>[a-z]{6,})ero$", "{{stem}}erò", "Future 1st person -erò"),
        ("(?P<stem>[a-z]{6,})era$", "{{stem}}erà", "Future 3rd person -erà"),
        ("(?P<stem>[a-z]{6,})iro$", "{{stem}}irò", "Future 1st person -irò"),
        ("(?P<stem>[a-z]{6,})ira$", "{{stem}}irà", "Future 3rd person -irà"),
        ("(?P<stem>[a-z]{8,})ita$", "{{stem}}ità", "Nouns in -ità"),
    ]:
        regex_lines.append(f"  # {comment}")
        regex_lines.append(f"  - regex: {esc(pattern)}")
        regex_lines.append(f"    replace: {esc(repl)}")
        regex_lines.append("    word: true")
        regex_lines.append("")
        total += 1
    return content + '\n' + '\n'.join(regex_lines), total


def generate_dev_pack():
    content, total = generate_pack(
        DEV_WORDS, "Dev",
        "Tech and code terms (JS, React, CSS, Git...)",
        include_accents=False
    )
    return content, total


# ===================================================================
# Validation
# ===================================================================
def validate_dictionaries() -> list[str]:
    """Return a list of error messages (empty means OK)."""
    errors = []

    # Check for duplicates within each file
    for fname in ("italiano.txt", "accenti.txt", "dev.txt"):
        words = load_words(fname)
        seen: set[str] = set()
        for w in words:
            if w in seen:
                errors.append(f"Duplicate in {fname}: '{w}'")
            seen.add(w)

    # Check for words that appear in multiple packs (warn only, not an error)
    it = set(load_words("italiano.txt"))
    acc = set(load_words("accenti.txt"))
    dev = set(load_words("dev.txt"))
    overlap_it_acc = it & acc
    overlap_it_dev = it & dev
    overlap_acc_dev = acc & dev
    for w in sorted(overlap_it_acc):
        errors.append(f"Word appears in both italiano.txt and accenti.txt: '{w}'")
    for w in sorted(overlap_it_dev):
        errors.append(f"Word appears in both italiano.txt and dev.txt: '{w}'")
    for w in sorted(overlap_acc_dev):
        errors.append(f"Word appears in both accenti.txt and dev.txt: '{w}'")

    return errors


# ===================================================================
# Main entry point
# ===================================================================
def get_espanso_config_path():
    try:
        result = subprocess.run(
            ["espanso", "path", "config"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    system = platform.system()
    candidates = []
    if system == "Darwin":
        candidates.append(os.path.expanduser("~/Library/Application Support/espanso"))
    elif system == "Linux":
        candidates.append(os.path.expanduser("~/.config/espanso"))
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            candidates.append(os.path.join(appdata, "espanso"))

    for path in candidates:
        if os.path.isdir(path):
            return path
    return None


def write_pack(match_dir, filename, content, total):
    path = os.path.join(match_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    size = os.path.getsize(path) / 1024
    print(f"  ok  {filename:<25} {total:>5,} rules  ({size:.0f} KB)")
    return total


def get_version() -> str:
    """Return the current version from the latest git tag, or '0.1.0' as fallback."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, timeout=5,
            cwd=REPO_DIR,
        )
        if result.returncode == 0:
            tag = result.stdout.strip().lstrip("v")
            if tag:
                return tag
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "0.1.0"


PACKAGE_META = {
    "refuos-italiano": {
        "title": "Refuos Italiano",
        "description": "Real-time autocorrection for everyday Italian words. Fixes typos like acnhe→anche, comunqeu→comunque.",
        "tags": ["italian", "autocorrect", "typo", "italiano"],
        "readme": textwrap.dedent("""\
            # Refuos Italiano

            Real-time autocorrection for everyday Italian words, powered by [Espanso](https://espanso.org).

            ## What it fixes

            Transpositions, missing double letters, and dropped characters — for example:

            | You type   | Corrected to |
            |------------|--------------|
            | `acnhe`    | `anche`      |
            | `comunqeu` | `comunque`   |
            | `perche`   | `perché`     |

            ~2,500 rules in total.

            ## Source

            <https://github.com/heavybeard/refuos>
        """),
    },
    "refuos-accenti": {
        "title": "Refuos Accenti",
        "description": "Autocorrection for Italian accents, future-tense verbs and -ità nouns. Fixes perche→perché, aggiungero→aggiungerò.",
        "tags": ["italian", "autocorrect", "accents", "accenti", "italiano"],
        "readme": textwrap.dedent("""\
            # Refuos Accenti

            Real-time autocorrection for Italian accented words and future-tense verbs, powered by [Espanso](https://espanso.org).

            ## What it fixes

            Missing accents, future-tense verbs (1st and 3rd person) and nouns ending in *-ità* — for example:

            | You type      | Corrected to   |
            |---------------|----------------|
            | `perche`      | `perché`       |
            | `aggiungero`  | `aggiungerò`   |
            | `disponibilita` | `disponibilità` |

            ~4,700 rules plus regex catch-all patterns.

            ## Source

            <https://github.com/heavybeard/refuos>
        """),
    },
    "refuos-dev": {
        "title": "Refuos Dev",
        "description": "Autocorrection for tech and code terms: JS, React, CSS, Git and more. Fixes cosnt→const, reutrn→return.",
        "tags": ["dev", "autocorrect", "code", "javascript", "react", "git"],
        "readme": textwrap.dedent("""\
            # Refuos Dev

            Real-time autocorrection for tech and code terms, powered by [Espanso](https://espanso.org).

            ## What it fixes

            Common typos in JavaScript, React, CSS, Git keywords and more — for example:

            | You type  | Corrected to |
            |-----------|--------------|
            | `cosnt`   | `const`      |
            | `reutrn`  | `return`     |
            | `ipmort`  | `import`     |

            ~1,100 rules in total.

            ## Source

            <https://github.com/heavybeard/refuos>
        """),
    },
}


def write_espanso_packages(base_dir: str, packs: list[tuple[str, str, int]], version: str) -> None:
    """Write Espanso Hub-compatible package structure under base_dir."""
    for pkg_name, content, total in packs:
        meta = PACKAGE_META[pkg_name]
        pkg_dir = os.path.join(base_dir, pkg_name, version)
        os.makedirs(pkg_dir, exist_ok=True)

        # package.yml — the actual rules
        pkg_yml = os.path.join(pkg_dir, "package.yml")
        with open(pkg_yml, "w", encoding="utf-8") as f:
            f.write(content)

        # _manifest.yml
        tags_yaml = ", ".join(f'"{t}"' for t in meta["tags"])
        manifest = textwrap.dedent(f"""\
            name: "{pkg_name}"
            title: "{meta['title']}"
            description: "{meta['description']}"
            version: "{version}"
            author: "Andrea Cognini"
            tags: [{tags_yaml}]
            homepage: "https://github.com/heavybeard/refuos"
        """)
        with open(os.path.join(pkg_dir, "_manifest.yml"), "w", encoding="utf-8") as f:
            f.write(manifest)

        # README.md
        with open(os.path.join(pkg_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(meta["readme"])

        print(f"  ok  {pkg_name:<25} {total:>5,} rules  -> {pkg_dir}")


def parse_args():
    parser = argparse.ArgumentParser(description="Refuos - Espanso rule generator")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate dictionaries only; do not write any files",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        help="Write generated YAML files to this directory instead of the Espanso config dir",
    )
    parser.add_argument(
        "--espanso-packages",
        metavar="DIR",
        help="Generate Espanso Hub package structure (manifest + package.yml + README) under DIR",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print("Refuos - Espanso rule generator")
    print("=" * 45)

    # Always validate first
    errors = validate_dictionaries()
    if errors:
        print("\n  Validation errors:")
        for e in errors:
            print(f"  ✗ {e}")
        raise SystemExit(1)

    if args.check:
        print("  Dictionaries OK — no errors found.")
        raise SystemExit(0)

    # Generate all pack contents (needed for both modes)
    it_content, it_total = generate_pack(
        ITALIANO_WORDS, "Italiano",
        "Everyday Italian words"
    )
    acc_content, acc_total = generate_accenti_pack()
    dev_content, dev_total = generate_dev_pack()
    grand_total = it_total + acc_total + dev_total

    packs = [
        ("refuos-italiano", it_content, it_total),
        ("refuos-accenti",  acc_content, acc_total),
        ("refuos-dev",      dev_content, dev_total),
    ]

    # --- Mode: Espanso Hub package structure ---
    if args.espanso_packages:
        version = get_version()
        print(f"  Generating Espanso Hub packages (version {version})...\n")
        write_espanso_packages(args.espanso_packages, packs, version)
        print(f"\n  Total: {grand_total:,} rules across {len(packs)} packages")
        print(f"  Package dir: {os.path.abspath(args.espanso_packages)}")
        raise SystemExit(0)

    # --- Mode: write YAML files (default or --output-dir) ---
    if args.output_dir:
        match_dir = args.output_dir
    else:
        config_path = get_espanso_config_path()
        if not config_path:
            print("Warning: Espanso not found. Generating files in the current directory.")
            config_path = "."
        match_dir = os.path.join(config_path, "match")

    os.makedirs(match_dir, exist_ok=True)

    # Remove legacy monolithic file if it exists
    old_file = os.path.join(match_dir, "italian-realtime.yml")
    if os.path.exists(old_file):
        os.remove(old_file)
        print(f"  Removed old file: italian-realtime.yml")

    print(f"  Directory: {match_dir}\n")

    write_pack(match_dir, "refuos-italiano.yml", it_content, it_total)
    write_pack(match_dir, "refuos-accenti.yml",  acc_content, acc_total)
    write_pack(match_dir, "refuos-dev.yml",      dev_content, dev_total)

    print(f"\n  Total: {grand_total:,} rules across 3 packages")
    print(f"\n  Restart Espanso: espanso restart")
    print(f"  To remove a package: delete the corresponding .yml file")
