#!/bin/bash
# Refuos — Installer
# Usage: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/heavybeard/refuos/main/install.sh)"
set -e

REPO="https://github.com/heavybeard/refuos.git"
INSTALL_DIR="$HOME/.refuos"

echo ""
echo "🔤 Refuos — Installer"
echo "====================="
echo ""

# 1. Check/install Espanso
if ! command -v espanso &> /dev/null; then
    echo "📦 Installo Espanso..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew non trovato. Installa Homebrew prima: https://brew.sh"
        exit 1
    fi
    brew install espanso
    espanso service register
    espanso start
    echo ""
    echo "⚠️  macOS ti chiederà di abilitare Espanso in:"
    echo "   Impostazioni di Sistema → Privacy e Sicurezza → Accessibilità"
    echo ""
    read -p "Premi Enter dopo aver abilitato il permesso..."
    espanso restart
else
    echo "✅ Espanso già installato"
fi

# 2. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trovato. Installa con: brew install python3"
    exit 1
fi

# 3. Clone/update repo
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Aggiorno Refuos..."
    cd "$INSTALL_DIR"
    git pull --quiet
else
    echo "📥 Scarico Refuos..."
    git clone --quiet "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 4. Generate rules
echo "⚙️  Genero le regole di autocorrezione..."
python3 generate_espanso.py

# 5. Restart Espanso
espanso restart

echo ""
echo "✅ Refuos installato!"
echo "   Prova a scrivere 'perche' in qualsiasi app — diventerà 'perché'"
echo ""
echo "   Per aggiornare: cd ~/.refuos && git pull && python3 generate_espanso.py && espanso restart"
echo ""
