# Alternative installation methods

The [README](README.md) covers the recommended installation method. This page documents the alternatives — pick the one that fits you best.

---

## Method 1 — Download ZIP (no terminal needed)

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

---

## Method 2 — One-liner (terminal)

The scripts download the pre-built rules directly from the latest release — no Python or Git required.

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

> **Note:** The Windows instructions (PowerShell installer, winget) have not been tested directly by the maintainer. If you run into any issues, please [open an issue](https://github.com/heavybeard/refuos/issues/new) — feedback is very welcome.
