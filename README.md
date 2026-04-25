# Refuos

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Validate](https://github.com/heavybeard/refuos/actions/workflows/validate.yml/badge.svg)](https://github.com/heavybeard/refuos/actions/workflows/validate.yml)
[![Release](https://github.com/heavybeard/refuos/actions/workflows/release.yml/badge.svg)](https://github.com/heavybeard/refuos/releases/latest)
[![Rules](https://img.shields.io/badge/rules-8%2C000%2B-blue)](#packages)

_refuos_ - how you'd type "refuso" (typo) in a hurry. And that's exactly the problem it solves.

Real-time autocorrection for macOS, Linux and Windows. As you type, typos are fixed automatically in any application: Slack, browser, terminal, editor, anywhere.

## How it works

Refuos uses [Espanso](https://espanso.org), a free open-source text expander that intercepts what you type and replaces it instantly — no internet connection, no account required.

A Python generator reads words from the included dictionaries and automatically produces all plausible typo variants: adjacent-key transpositions, missing double letters, wrong accents, dropped characters. The output is a set of YAML files that Espanso loads and uses to correct text in real time.

Future-tense verbs and nouns ending in `-ità` are covered by explicit entries in the accent dictionary.

## Examples

| You type     | Corrected to  |
| ------------ | ------------- |
| `acnhe`      | `anche`       |
| `comunqeu`   | `comunque`    |
| `perche`     | `perche'`     |
| `aggiungero` | `aggiungero'` |
| `cosnt`      | `const`       |
| `reutrn`     | `return`      |

**8,000+ rules** in total, zero latency, fully offline.

## Packages

Three independent files. Install all of them or only the ones you need.

| Package      | File                  | Rules  | What it fixes                                                       |
| ------------ | --------------------- | ------ | ------------------------------------------------------------------- |
| **Italiano** | `refuos-italiano.yml` | ~2,500 | Everyday words: `acnhe` -> anche, `comunqeu` -> comunque            |
| **Accenti**  | `refuos-accenti.yml`  | ~4,700 | Accents & futures: `perche` -> perche', `aggiungero` -> aggiungero' |
| **Dev**      | `refuos-dev.yml`      | ~1,100 | Tech terms: `cosnt` -> const, `reutrn` -> return                    |

To remove a package, simply delete the corresponding `.yml` file from the Espanso folder.

## Installation

Three methods, from simplest to most technical. Pick the one that fits you.

### Method 1 — Espanso Hub (recommended, no terminal needed)

> Available once the package is approved on the Espanso Hub.

Install [Espanso](https://espanso.org) from its website (standard graphical installer), then run:

```bash
espanso install refuos-italiano
espanso install refuos-accenti
espanso install refuos-dev
```

Or search for `refuos` directly inside the Espanso GUI.

### Method 2 — Download ZIP (no terminal needed)

1. Install [Espanso](https://espanso.org) from its website
2. Download **[refuos-rules.zip](https://github.com/heavybeard/refuos/releases/latest/download/refuos-rules.zip)** from the latest release
3. Open the Espanso config folder:
   - **macOS / Linux:** in the Espanso menu choose _Open config folder_, or navigate to `~/Library/Application Support/espanso` (macOS) / `~/.config/espanso` (Linux)
   - **Windows:** in the Espanso tray icon choose _Open config folder_, or navigate to `%APPDATA%\espanso`
4. Copy the three `.yml` files into the `match/` subfolder
5. Restart Espanso

To install only specific packages, download the individual files instead:
[`refuos-italiano.yml`](https://github.com/heavybeard/refuos/releases/latest/download/refuos-italiano.yml) &middot;
[`refuos-accenti.yml`](https://github.com/heavybeard/refuos/releases/latest/download/refuos-accenti.yml) &middot;
[`refuos-dev.yml`](https://github.com/heavybeard/refuos/releases/latest/download/refuos-dev.yml)

### Method 3 — One-liner (terminal)

**macOS** (installs Espanso via Homebrew if needed):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/heavybeard/refuos/main/install.sh)"
```

**Linux** (requires Espanso already installed):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/heavybeard/refuos/main/install.sh)"
```

**Windows** — PowerShell (installs Espanso via `winget` if needed):

```powershell
irm https://raw.githubusercontent.com/heavybeard/refuos/main/install.ps1 | iex
```

The scripts download the pre-built rules directly from the latest release — no Python or Git required.

## Adding words

Words live in plain text files inside the `dictionaries/` folder — one word per line:

| File                        | What to put there                              |
| --------------------------- | ---------------------------------------------- |
| `dictionaries/italiano.txt` | Everyday Italian words                         |
| `dictionaries/accenti.txt`  | Accented words, future-tense verbs, -ità nouns |
| `dictionaries/dev.txt`      | Tech and code terms                            |

To add a word, edit the right file and regenerate:

```bash
cd ~/.refuos
echo "nuovaparola" >> dictionaries/italiano.txt
python3 generate_espanso.py
espanso restart
```

Or [open an issue](https://github.com/heavybeard/refuos/issues/new/choose) — the maintainer will add it.

## Updating

Re-run whichever installation method you used:

- **Espanso Hub:** `espanso update`
- **ZIP / individual files:** download the new files from [Releases](https://github.com/heavybeard/refuos/releases/latest) and replace the old ones
- **One-liner:** re-run the same curl/PowerShell command

## Requirements

**To install:**

- macOS, Linux or Windows
- [Espanso](https://espanso.org) (free, open-source)
- macOS one-liner: [Homebrew](https://brew.sh)
- Windows one-liner: [winget](https://learn.microsoft.com/windows/package-manager/winget/) (included in Windows 10/11)

**To contribute or build from source:**

- Python 3.9+
- Git

## Contributing

Contributions of any size are welcome — from a single word to a whole new dictionary.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started. The short version:

1. Edit the right file in `dictionaries/`
2. Run `python3 generate_espanso.py --check`
3. Open a Pull Request

## Roadmap

Ideas and planned improvements are tracked as [GitHub Issues](https://github.com/heavybeard/refuos/issues). Contributions towards any of them are especially welcome.

Some ideas under consideration:

- Additional language dictionaries (Spanish, French, ...)
- Domain-specific word lists (medical, legal, academic, ...)
- A `--dry-run` mode that prints stats without writing files

## Support

If you find Refuos useful, consider supporting its development:

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink?logo=github)](https://github.com/sponsors/heavybeard)
[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=F2MP7WP47RQ5U)

## License

MIT - [Andrea Cognini](https://github.com/heavybeard)
