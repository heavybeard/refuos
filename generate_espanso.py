#!/usr/bin/env python3
"""
Refuos - Espanso rule generator
https://github.com/heavybeard/refuos

Generates modular YAML files for Espanso. Each package is independent:
  - refuos-italiano.yml  -> everyday Italian words
  - refuos-accenti.yml   -> accents, future-tense verbs, -ita' nouns
  - refuos-dev.yml       -> tech/code terms (cross-stack, framework-agnostic)

Private local dictionaries are also supported. Any .txt file placed in
dictionaries/local/ generates a private refuos-local-<name>.yml package.
Local files are gitignored and excluded from --espanso-packages output.

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
    'à': ['a', "a'", 'a1'], 'è': ['e', "e'", 'e1'], 'é': ['e', "e'", 'e1'],
    'ì': ['i', "i'", 'i1'], 'ò': ['o', "o'", 'o1'], 'ù': ['u', "u'", 'u1'],
}

# Common English words that would be generated as typo triggers for dev terms,
# causing false positives. These are excluded from all generated trigger lists.
FALSE_POSITIVE_BLOCKLIST: frozenset[str] = frozenset({
    # High-risk: everyday words
    "asset", "cost", "cone", "filer", "fronted", "gird", "mere", "neural",
    "reactor", "sash", "sate", "sinner", "sting", "tale", "thee",
    # Medium-risk: less common but real English words
    "bade", "borer", "brach", "deign", "lading", "outlie", "sider", "sprit", "tost",
})

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


def load_local_dictionaries() -> dict[str, list[str]]:
    """
    Scan dictionaries/local/ for *.txt files and return a dict mapping
    the stem name (without .txt) to the list of words.

    Returns an empty dict if the folder does not exist or contains no .txt files.
    Resolves LOCAL_DIR at call time so that tests can patch DICT_DIR.
    """
    local_dir = os.path.join(DICT_DIR, "local")
    if not os.path.isdir(local_dir):
        return {}
    result = {}
    for entry in sorted(os.listdir(local_dir)):
        if not entry.endswith(".txt"):
            continue
        name = entry[:-4]  # strip .txt
        path = os.path.join(local_dir, entry)
        with open(path, encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        result[name] = words
    return result


ITALIANO_WORDS = load_words("italiano.txt")
ACCENTI_WORDS = load_words("accenti.txt")
DEV_WORDS = load_words("dev.txt")
LOCAL_DICTS: dict[str, list[str]] = load_local_dictionaries()

ALL_WORDS = (
    set(ITALIANO_WORDS)
    | set(ACCENTI_WORDS)
    | set(DEV_WORDS)
    | {w for words in LOCAL_DICTS.values() for w in words}
)


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
    typos -= FALSE_POSITIVE_BLOCKLIST
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
        typos = sorted(t for t in generate_all_typos(word, include_accents) if t not in seen)
        if not typos:
            continue
        seen.update(typos)
        lines.append("  - triggers:")
        for typo in typos:
            lines.append(f'    - {esc(typo)}')
        lines.append(f"    replace: {esc(word)}")
        if not any(c in word for c in 'àèéìòù'):
            lines.append("    propagate_case: true")
        lines.append("    word: true")
        lines.append("")
        total += len(typos)
    return '\n'.join(lines), total


def generate_accenti_pack():
    content, total = generate_pack(
        ACCENTI_WORDS, "Accenti",
        "Missing accents, future tense verbs, -ità nouns"
    )
    short_groups = [
        (["e'", "e1"], "è"),
        (["si'", "si1"], "sì"),
        (["la'", "la1"], "là"),
        (["li'", "li1"], "lì"),
    ]
    short_lines = [
        "  # Short accented words (too short for the auto-generator)",
    ]
    for triggers, replace in short_groups:
        short_lines.append("  - triggers:")
        for t in triggers:
            short_lines.append(f'    - {esc(t)}')
        short_lines.append(f"    replace: {esc(replace)}")
        short_lines.append("    word: true")
        short_lines.append("")
        total += len(triggers)
    return content + '\n' + '\n'.join(short_lines), total


def generate_dev_pack():
    content, total = generate_pack(
        DEV_WORDS, "Dev",
        "Tech and code terms: HTML, CSS, patterns, paradigms, Git, DevOps, Python and more",
        include_accents=False
    )
    return content, total


def generate_local_pack(name: str, words: list[str]):
    """Generate a private local pack for a given local dictionary."""
    content, total = generate_pack(
        words,
        f"Local – {name}",
        f"Private local dictionary: {name}",
        include_accents=False,
    )
    return content, total


# ===================================================================
# Validation
# ===================================================================
def validate_dictionaries() -> list[str]:
    """Return a list of error messages (empty means OK)."""
    errors = []

    # Check for duplicates within each public file
    for fname in ("italiano.txt", "accenti.txt", "dev.txt"):
        words = load_words(fname)
        seen: set[str] = set()
        for w in words:
            if w in seen:
                errors.append(f"Duplicate in {fname}: '{w}'")
            seen.add(w)

    # Check for overlaps between public files
    it = set(load_words("italiano.txt"))
    acc = set(load_words("accenti.txt"))
    dev = set(load_words("dev.txt"))
    for w in sorted(it & acc):
        errors.append(f"Word appears in both italiano.txt and accenti.txt: '{w}'")
    for w in sorted(it & dev):
        errors.append(f"Word appears in both italiano.txt and dev.txt: '{w}'")
    for w in sorted(acc & dev):
        errors.append(f"Word appears in both accenti.txt and dev.txt: '{w}'")

    # Validate local dictionaries
    local = load_local_dictionaries()
    public_all = it | acc | dev
    local_names = sorted(local.keys())

    for name, words in local.items():
        fname = f"local/{name}.txt"
        seen_local: set[str] = set()
        for w in words:
            # Duplicates within the same local file
            if w in seen_local:
                errors.append(f"Duplicate in {fname}: '{w}'")
            seen_local.add(w)
            # Overlap with any public dictionary
            if w in public_all:
                errors.append(f"Word in {fname} already exists in a public dictionary: '{w}'")

    # Overlap between local files
    for i, name_a in enumerate(local_names):
        for name_b in local_names[i + 1:]:
            overlap = set(local[name_a]) & set(local[name_b])
            for w in sorted(overlap):
                errors.append(
                    f"Word appears in both local/{name_a}.txt and local/{name_b}.txt: '{w}'"
                )

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
    print(f"  ok  {filename:<35} {total:>5,} rules  ({size:.0f} KB)")
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
        "tags": ["italian", "autocorrect", "typo", "italiano", "languages", "spell-correction", "typofixer"],
        "readme": textwrap.dedent("""\
            # Refuos Italiano

            Real-time autocorrection for everyday Italian words, powered by [Espanso](https://espanso.org).

            ## What it fixes

            Transpositions, missing double letters, and dropped characters — for example:

            | You type   | Corrected to |
            |------------|--------------|
            | `acnhe`    | `anche`      |
            | `comunqeu` | `comunque`   |
            | `probelma` | `problema`   |

            ~2,500 rules in total.

            ## Source

            <https://github.com/heavybeard/refuos>
        """),
    },
    "refuos-accenti": {
        "title": "Refuos Accenti",
        "description": "Autocorrection for Italian accents, future-tense verbs and -ità nouns. Fixes perche→perché, aggiungero→aggiungerò.",
        "tags": ["italian", "autocorrect", "accents", "accenti", "italiano", "languages", "spell-correction", "typofixer"],
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

            ~4,700 rules.

            ## Source

            <https://github.com/heavybeard/refuos>
        """),
    },
    "refuos-dev": {
        "title": "Refuos Dev",
        "description": "Autocorrection for tech and code terms: HTML, CSS, patterns, paradigms, Git, DevOps, Python and more. Fixes cosnt→const, reutrn→return.",
        "tags": ["dev", "autocorrect", "code", "html", "css", "git", "devops", "python", "patterns", "architecture", "spell-correction", "typofixer"],
        "readme": textwrap.dedent("""\
            # Refuos Dev

            Real-time autocorrection for tech and code terms, powered by [Espanso](https://espanso.org).

            ## What it fixes

            Common typos in language keywords, HTML, CSS, design patterns, paradigms,
            Git, DevOps tools, Python, and infrastructure — for example:

            | You type       | Corrected to   |
            |----------------|----------------|
            | `cosnt`        | `const`        |
            | `reutrn`       | `return`       |
            | `ipmort`       | `import`       |
            | `dockerfiel`   | `dockerfile`   |
            | `migraiton`    | `migration`    |
            | `Kuberentes`   | `Kubernetes`   |

            Framework-agnostic: works for JavaScript, TypeScript, Python, Go, Java,
            and any other stack. For framework-specific terms (React hooks, Vue
            Composition API, NestJS decorators, Django ORM, etc.) use a local
            dictionary — see the [project repository](https://github.com/heavybeard/refuos)
            for documentation on local dictionaries.

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

        print(f"  ok  {pkg_name:<35} {total:>5,} rules  -> {pkg_dir}")


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

    public_packs = [
        ("refuos-italiano", it_content, it_total),
        ("refuos-accenti",  acc_content, acc_total),
        ("refuos-dev",      dev_content, dev_total),
    ]

    # --- Mode: Espanso Hub package structure (public packs only) ---
    if args.espanso_packages:
        version = get_version()
        grand_total = it_total + acc_total + dev_total
        print(f"  Generating Espanso Hub packages (version {version})...\n")
        write_espanso_packages(args.espanso_packages, public_packs, version)
        print(f"\n  Total: {grand_total:,} rules across {len(public_packs)} packages")
        print(f"  Package dir: {os.path.abspath(args.espanso_packages)}")
        print(f"\n  Note: local dictionaries are excluded from Hub packages.")
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

    grand_total = it_total + acc_total + dev_total

    # Generate local packs
    if LOCAL_DICTS:
        print()
        for name, words in sorted(LOCAL_DICTS.items()):
            local_content, local_total = generate_local_pack(name, words)
            filename = f"refuos-local-{name}.yml"
            write_pack(match_dir, filename, local_content, local_total)
            grand_total += local_total

    total_packs = len(public_packs) + len(LOCAL_DICTS)
    print(f"\n  Total: {grand_total:,} rules across {total_packs} packages")
    print(f"\n  Restart Espanso: espanso restart")
    print(f"  To remove a package: delete the corresponding .yml file")
