#!/bin/bash
# Refuos - Installer (macOS and Linux)
# Usage: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/heavybeard/refuos/main/install.sh)"
set -euo pipefail

REPO="heavybeard/refuos"
BASE_URL="https://github.com/$REPO/releases/latest/download"
PACKAGES=(refuos-italiano.yml refuos-accenti.yml refuos-dev.yml)
OS="$(uname -s)"

echo ""
echo "Refuos - Installer"
echo "=================="
echo ""

# 1. Check/install Espanso
if ! command -v espanso &> /dev/null; then
    if [ "$OS" = "Darwin" ]; then
        echo "Installing Espanso via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "Error: Homebrew not found. Install it first: https://brew.sh"
            exit 1
        fi
        brew install espanso
        espanso service register
        espanso start
        echo ""
        echo "Note: macOS will ask you to enable Espanso in:"
        echo "   System Settings -> Privacy & Security -> Accessibility"
        echo ""
        read -p "Press Enter after enabling the permission..."
        espanso restart
    elif [ "$OS" = "Linux" ]; then
        echo "Error: Espanso not found."
        echo "Download and install Espanso for Linux from: https://espanso.org/install/linux/"
        exit 1
    else
        echo "Error: unsupported operating system. Install Espanso from: https://espanso.org"
        exit 1
    fi
else
    echo "Espanso already installed"
fi

# 2. Find Espanso match directory
MATCH_DIR="$(espanso path config)/match"
mkdir -p "$MATCH_DIR"

# 3. Download pre-built rules (no Python, no Git required)
echo "Downloading Refuos rules..."
echo ""

# Download checksums file for integrity verification
CHECKSUM_FILE="$(mktemp)"
curl -fsSL "$BASE_URL/checksums.sha256" -o "$CHECKSUM_FILE"

for pkg in "${PACKAGES[@]}"; do
    curl -fsSL "$BASE_URL/$pkg" -o "$MATCH_DIR/$pkg"
    # Verify integrity: use shasum on macOS, sha256sum on Linux
    if [ "$OS" = "Darwin" ]; then
        expected=$(grep "$pkg" "$CHECKSUM_FILE" | awk '{print $1}')
        actual=$(shasum -a 256 "$MATCH_DIR/$pkg" | awk '{print $1}')
    else
        expected=$(grep "$pkg" "$CHECKSUM_FILE" | awk '{print $1}')
        actual=$(sha256sum "$MATCH_DIR/$pkg" | awk '{print $1}')
    fi
    if [ "$expected" != "$actual" ]; then
        echo "Error: checksum mismatch for $pkg (expected $expected, got $actual)"
        rm -f "$MATCH_DIR/$pkg"
        rm -f "$CHECKSUM_FILE"
        exit 1
    fi
    echo "  ok  $pkg"
done

rm -f "$CHECKSUM_FILE"

# 4. Restart Espanso
espanso restart

echo ""
echo "Refuos installed. 3 packages:"
echo "   refuos-italiano.yml  - everyday Italian words"
echo "   refuos-accenti.yml   - accents and future tense"
echo "   refuos-dev.yml       - tech/code terms"
echo ""
echo "   Try typing 'perche' in any app - it becomes 'perche''"
echo "   To remove a package: delete its .yml file from:"
echo "   $MATCH_DIR"
echo ""
echo "   To update: re-run this installer at any time"
echo ""
