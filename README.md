# Refuos 🔤

> *refuos* — come scriveresti "refuso" di fretta. Ed è esattamente il problema che risolve.

Autocorrezione real-time per macOS. **8.000+ regole** che correggono typo mentre scrivi — lettere invertite, accenti mancanti, doppie saltate — ovunque: Slack, browser, terminale, qualsiasi app.

Zero latenza, tutto offline, nessun account richiesto. Usa [Espanso](https://espanso.org).

## Pacchetti

Tre file indipendenti. Installa tutti o solo quelli che ti servono.

| Pacchetto | File | Regole | Cosa corregge |
|---|---|---|---|
| **Italiano** | `refuos-italiano.yml` | ~2.500 | Parole quotidiane: `acnhe` → anche, `comunqeu` → comunque |
| **Accenti** | `refuos-accenti.yml` | ~4.700 | Accenti e futuri: `perche` → perché, `aggiungero` → aggiungerò |
| **Dev** | `refuos-dev.yml` | ~1.100 | Termini tech: `cosnt` → const, `reutrn` → return |

Per rimuovere un pacchetto basta eliminare il file `.yml` corrispondente dalla cartella di Espanso.

## Installazione (2 minuti)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/heavybeard/refuos/main/install.sh)"
```

### Manuale

```bash
# 1. Installa Espanso (se non ce l'hai)
brew install espanso
espanso service register
espanso start
# ⚠️ macOS chiederà il permesso Accessibilità — accetta

# 2. Clona e genera
git clone https://github.com/heavybeard/refuos.git ~/.refuos
cd ~/.refuos
python3 generate_espanso.py

# 3. Riavvia
espanso restart
```

## Aggiungere parole

Apri `generate_espanso.py`, aggiungi le parole nella lista giusta (`ITALIANO_WORDS`, `ACCENTI_WORDS` o `DEV_WORDS`), e rigenera:

```bash
cd ~/.refuos && python3 generate_espanso.py && espanso restart
```

Oppure apri una [issue](https://github.com/heavybeard/refuos/issues).

## Aggiornamento

```bash
cd ~/.refuos && git pull && python3 generate_espanso.py && espanso restart
```

## Come funziona

Un generatore Python prende le parole dai tre dizionari e produce automaticamente tutte le varianti typo plausibili: trasposizioni di lettere adiacenti, doppie mancanti, accenti sbagliati, lettere saltate. Il risultato sono file YAML che Espanso usa per correggere in tempo reale.

Include anche regole regex catch-all per i pattern che non si possono enumerare (verbi al futuro, sostantivi in `-ità`).

## Requisiti

- macOS (testato su Sonoma/Sequoia)
- Python 3
- [Homebrew](https://brew.sh)

## License

MIT — [Andrea Cognini](https://github.com/heavybeard)
