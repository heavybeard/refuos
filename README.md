# Refuos 🔤

> *refuos* — come scriveresti "refuso" di fretta. Ed è esattamente il problema che risolve.

Autocorrezione real-time per macOS. **9.000+ regole** che correggono typo mentre scrivi — lettere invertite, accenti mancanti, doppie saltate — ovunque: Slack, browser, terminale, qualsiasi app.

Zero latenza, tutto offline, nessun account richiesto.

Usa [Espanso](https://espanso.org), un text expander open-source.

## Esempi

| Scrivi | Diventa |
|---|---|
| `perche` | perché |
| `aggiungero` | aggiungerò |
| `acnhe` | anche |
| `possibilita` | possibilità |
| `cosnt` | const |
| `reutrn` | return |
| `comunqeu` | comunque |
| `velcoemente` | velocemente |

## Installazione (2 minuti)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/heavybeard/refuos/main/install.sh)"
```

### Cosa fa

Un generatore Python analizza ~850 parole italiane ad alta frequenza + 112 termini tech e produce **tutte le varianti typo plausibili**: trasposizioni, doppie mancanti, accenti sbagliati, lettere mancanti. Il risultato è un file di configurazione Espanso che corregge in tempo reale.

Include anche regole regex catch-all per i verbi al futuro (`aggiungero` → `aggiungerò`) e i sostantivi in `-ità` (`possibilita` → `possibilità`).

### Installazione manuale

Se preferisci fare tutto a mano:

```bash
# 1. Installa Espanso (se non ce l'hai)
brew install espanso
espanso service register
espanso start
# ⚠️ macOS chiederà il permesso Accessibilità: accetta in
# Impostazioni di Sistema → Privacy e Sicurezza → Accessibilità

# 2. Clona il repo e genera le regole
git clone https://github.com/heavybeard/refuos.git
cd refuos
python3 generate_espanso.py

# 3. Riavvia Espanso
espanso restart
```

## Aggiungere parole

Apri `generate_espanso.py`, aggiungi le parole nella lista `ITALIAN_WORDS` o `TECH_WORDS`, e rigenera:

```bash
python3 generate_espanso.py
espanso restart
```

Oppure apri una [issue](https://github.com/heavybeard/refuos/issues) e le aggiungo io.

## Aggiornamento

```bash
cd ~/.refuos
git pull
python3 generate_espanso.py
espanso restart
```

## Come funziona

Espanso gira in background e monitora la tastiera. Quando finisci di scrivere una parola che matcha un typo nel dizionario, la sostituisce istantaneamente. Non serve fare niente: scrivi e basta.

## Requisiti

- macOS (testato su Sonoma/Sequoia)
- Python 3
- [Homebrew](https://brew.sh)

## License

MIT — Andrea Cognini
