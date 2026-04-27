# Refuos

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Validate](https://github.com/heavybeard/refuos/actions/workflows/validate.yml/badge.svg)](https://github.com/heavybeard/refuos/actions/workflows/validate.yml)
[![Release](https://github.com/heavybeard/refuos/actions/workflows/release.yml/badge.svg)](https://github.com/heavybeard/refuos/releases/latest)
[![Rules](https://img.shields.io/badge/rules-10%2C500%2B-blue)](#packages)
[![Available on Espanso Hub](https://img.shields.io/badge/espanso_hub-available-blue)](https://hub.espanso.org/search?q=refuos)

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

**10,500+ rules** in total, zero latency, fully offline.

## Packages

Three independent files. Install all of them or only the ones you need.

| Package      | File                  | Rules  | What it fixes                                                       |
| ------------ | --------------------- | ------ | ------------------------------------------------------------------- |
| **Italiano** | `refuos-italiano.yml` | ~2,600 | Everyday words: `acnhe` -> anche, `comunqeu` -> comunque            |
| **Accenti**  | `refuos-accenti.yml`  | ~4,800 | Accents & futures: `perche` -> perche', `aggiungero` -> aggiungero' |
| **Dev**      | `refuos-dev.yml`      | ~3,200 | Tech terms: `cosnt` -> const, `reutrn` -> return                    |

To remove a package, simply delete the corresponding `.yml` file from the Espanso folder.

## Installation

1. Install [Espanso](https://espanso.org) from its website
2. Run:

   ```bash
   espanso install refuos-italiano
   espanso install refuos-accenti
   espanso install refuos-dev
   ```

3. Restart Espanso if it doesn't pick up the new rules automatically.

To install only specific packages, just run the corresponding command above.

> **Tip:** Hub packages are updated manually and may lag behind the latest release. To install directly from GitHub (always up to date), use the `--git` flag:
>
> ```bash
> espanso install refuos-italiano --git https://github.com/heavybeard/refuos --git-branch pkg/refuos-italiano --external
> espanso install refuos-accenti  --git https://github.com/heavybeard/refuos --git-branch pkg/refuos-accenti  --external
> espanso install refuos-dev      --git https://github.com/heavybeard/refuos --git-branch pkg/refuos-dev      --external
> ```

For alternative methods (ZIP download, one-liner scripts for macOS, Linux and Windows) see [INSTALL.md](INSTALL.md).

## Adding words

Words live in plain text files inside the `dictionaries/` folder — one word per line:

| File                        | What to put there                              |
| --------------------------- | ---------------------------------------------- |
| `dictionaries/italiano.txt` | Everyday Italian words                         |
| `dictionaries/accenti.txt`  | Accented words, future-tense verbs, -ità nouns |
| `dictionaries/dev.txt`      | Tech and code terms                            |

For personal or stack-specific words that you don't want to submit upstream, use `dictionaries/local/` — any `.txt` file placed there generates a private `refuos-local-<name>.yml` package that is gitignored and excluded from releases. See [`dictionaries/local/README.md`](dictionaries/local/README.md) for details.

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

- **Espanso Hub:** `espanso update` (updates when a new Hub version is published)
- **GitHub (--git):** re-run the same `espanso install ... --external` commands (always gets the latest release)
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

## Support

If you find Refuos useful, consider supporting its development:

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink?logo=github)](https://github.com/sponsors/heavybeard)
[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=F2MP7WP47RQ5U)

## License

MIT - [Andrea Cognini](https://github.com/heavybeard)
