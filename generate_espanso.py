#!/usr/bin/env python3
"""
Refuos — Generatore regole Espanso
https://github.com/heavybeard/refuos

Genera file YAML modulari per Espanso. Ogni pacchetto è indipendente:
  - refuos-italiano.yml  → parole italiane quotidiane
  - refuos-accenti.yml   → accenti, verbi futuri, sostantivi -ità
  - refuos-dev.yml       → termini tech/codice
"""
import os, subprocess

# -------------------------------------------------------------------
# Utils
# -------------------------------------------------------------------
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

# ===================================================================
# 📦 PACCHETTO 1: ITALIANO — Parole quotidiane
# ===================================================================
ITALIANO_WORDS = """
il lo la i gli le un uno una
di a da in con su per tra fra
e o ma anche quindi quando come dove
che chi cosa quale quanto
non molto poco tutto tanto troppo sempre mai ancora
io tu lui lei noi voi loro
mi ti ci si vi ne lo la li le
essere avere fare dire andare venire potere volere dovere sapere
stare dare vedere sentire trovare pensare credere mettere prendere portare
sono sei siamo siete
ho hai ha abbiamo avete hanno
ero eri era eravamo eravate erano
faccio fai fa facciamo fate fanno
dico dici dice diciamo dite dicono
vado vai va andiamo andate vanno
questo questa questi queste quello quella quelli quelle
mio mia miei mie tuo tua tuoi tue suo sua suoi sue
nostro nostra nostri nostre vostro vostra vostri vostre loro
primo prima secondo seconda terzo terza ultimo ultima
buono buona cattivo cattiva grande piccolo bello bella brutto brutta
nuovo nuova vecchio vecchia giovane alto bassa lungo corto largo stretto
caro cara facile difficile possibile impossibile necessario importante
bene male meglio peggio
qui qua sopra sotto dentro fuori vicino lontano
oggi domani ieri adesso ora poi prima dopo subito
forse
acqua casa anno tempo giorno vita uomo donna bambino ragazzo
lavoro scuola paese mondo parte modo punto fatto cosa
mano testa occhio bocca cuore corpo
amico famiglia padre madre figlio figlia fratello sorella
numero nome parola storia problema esempio caso tipo
grazie prego scusa ciao buongiorno buonasera arrivederci
capire parlare leggere scrivere lavorare giocare mangiare bere dormire
aprire chiudere iniziare finire provare usare cambiare aiutare
chiamare aspettare tornare restare lasciare tenere
momento risultato progetto servizio sistema processo obiettivo
domanda risposta soluzione decisione situazione condizione
qualcosa qualcuno nessuno ognuno ciascuno
comunque tuttavia inoltre infatti dunque
attraverso durante senza contro verso secondo
insieme davvero proprio appena quasi almeno
settimana mese anno minuto secondo ora
messaggio informazione comunicazione
attenzione esperienza conoscenza
sviluppo aggiornamento miglioramento cambiamento
appuntamento disponibile
funzionare funziona funzionamento
organizzare organizzazione collaborare collaborazione
presentazione documentazione
problema problemi soluzione soluzioni
""".split()

# ===================================================================
# 📦 PACCHETTO 2: ACCENTI — Accenti, futuri, -ità
# ===================================================================
ACCENTI_WORDS = """
è già più giù può ciò così però perciò cioè sì là lì
perché poiché affinché benché sebbene nonostante
giacché allorché purché finché cosicché
città disponibilità
attività capacità possibilità responsabilità qualità
quantità identità realtà libertà difficoltà facilità utilità necessità
università curiosità creatività sensibilità vulnerabilità
veloce velocemente sicuro sicuramente probabilmente certamente
lunedì martedì mercoledì giovedì venerdì
andrò andrai andrà andremo andranno
farò farai farà faremo faranno
sarò sarai sarà saremo saranno
avrò avrai avrà avremo avranno
dirò dirai dirà diremo diranno
verrò verrai verrà verremo verranno
potrò potrai potrà potremo potranno
vorrò vorrai vorrà vorremo vorranno
dovrò dovrai dovrà dovremo dovranno
saprò saprai saprà sapremo sapranno
starò starai starà staremo staranno
darò darai darà daremo daranno
terrò terrai terrà terremo terranno
rimarrò rimarrai rimarrà rimarremo rimarranno
prenderò prenderai prenderà prenderemo prenderanno
metterò metterai metterà metteremo metteranno
parlerò parlerai parlerà parleremo parleranno
lavorerò lavorerai lavorerà lavoreremo lavoreranno
chiamerò chiamerai chiamerà chiameremo chiameranno
troverò troverai troverà troveremo troveranno
piacerà piacerò piaceranno
proverò proverai proverà proveremo proveranno
userò userai userà useremo useranno
cambierò cambierai cambierà cambieremo cambieranno
aiuterò aiuterai aiuterà aiuteremo aiuteranno
aggiungerò aggiungerai aggiungerà aggiungeremo aggiungeranno
manderò manderai manderà manderemo manderanno
invierò invierai invierà invieremo invieranno
creerò creerai creerà creeremo creeranno
finirò finirai finirà finiremo finiranno
capirò capirai capirà capiremo capiranno
inserirò inserirai inserirà inseriremo inseriranno
correggerò correggerai correggerà correggeremo correggeranno
scriverò scriverai scriverà scriveremo scriveranno
leggerò leggerai leggerà leggeremo leggeranno
vedrò vedrai vedrà vedremo vedranno
sentirò sentirai sentirà sentiremo sentiranno
resterò resterai resterà resteremo resteranno
aspetterò aspetterai aspetterà aspetteremo aspetteranno
tornerò tornerai tornerà torneremo torneranno
preparerò preparerai preparerà prepareremo prepareranno
pubblicherò pubblicherai pubblicherà pubblicheremo pubblicheranno
risolverò risolverai risolverà risolveremo risolveranno
mangerò mangerai mangerà mangeremo mangeranno
arriverò arriverai arriverà arriveremo arriveranno
chiederò chiederai chiederà chiederemo chiederanno
risponderò risponderai risponderà risponderemo risponderanno
spiegherò spiegherai spiegherà spiegheremo spiegheranno
verificherò verificherai verificherà verificheremo verificheranno
confermerò confermerai confermerà confermeremo confermeranno
organizzerò organizzerai organizzerà organizzeremo organizzeranno
aggiornerò aggionerai aggiornerà aggiorneremo aggiorneranno
implementerò implementerai implementerà implementeremo implementeranno
comunicherò comunicherai comunicherà comunicheremo comunicheranno
inizierò inizierai inizierà inizieremo inizieranno
passerò passerai passerà passeremo passeranno
riceverò riceverai riceverà riceveremo riceveranno
condividerò condividerai condividerà condivideremo condivideranno
completerò completerai completerà completeremo completeranno
""".split()

# ===================================================================
# 📦 PACCHETTO 3: DEV — Termini tech/codice
# ===================================================================
DEV_WORDS = """
component components import export default function return const let var
string number boolean null undefined async await promise
useState useEffect useRef useCallback useMemo useContext
interface type props state children className style onClick onChange
fetch request response error status loading data
deploy build test merge commit push pull branch
review issue ticket sprint backlog milestone
button input select modal dialog toast checkbox radio
header footer sidebar navigation layout container wrapper
padding margin border radius shadow opacity
primary secondary accent neutral background foreground
token theme color font spacing typography
design system library package module
storybook figma sketch prototype wireframe
dashboard settings profile notification
search filter sort pagination scroll
table list grid card badge avatar
""".split()

# ===================================================================
# Generatori di typo
# ===================================================================
ALL_WORDS = set(ITALIANO_WORDS) | set(ACCENTI_WORDS) | set(DEV_WORDS)

def generate_transpositions(word):
    typos = set()
    for i in range(len(word) - 1):
        chars = list(word)
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
        typo = ''.join(chars)
        if typo != word: typos.add(typo)
    return typos

def generate_missing_double(word):
    typos = set()
    i = 0
    while i < len(word) - 1:
        if word[i] == word[i + 1]:
            typo = word[:i] + word[i + 1:]
            if len(typo) >= 3: typos.add(typo)
        i += 1
    return typos

def generate_missing_char(word):
    typos = set()
    if len(word) >= 5:
        for i in range(1, len(word) - 1):
            typo = word[:i] + word[i + 1:]
            if len(typo) >= 3: typos.add(typo)
    return typos

def generate_accent_variants(word):
    typos = set()
    for i, char in enumerate(word):
        if char in ACCENT_REPLACE_MAP:
            for r in ACCENT_REPLACE_MAP[char]:
                typo = word[:i] + r + word[i + 1:]
                if typo != word: typos.add(typo)
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
# Generazione multi-file
# ===================================================================
def make_header(title, desc):
    return [
        f"# Refuos — {title}",
        f"# {desc}",
        "# https://github.com/heavybeard/refuos",
        "# Auto-generato — rigenera con: python3 generate_espanso.py",
        "", "matches:", "",
    ]

def generate_pack(words, title, desc, include_accents=True):
    lines = make_header(title, desc)
    total = 0
    seen = set()
    for word in sorted(set(words)):
        if len(word) < 3: continue
        for typo in sorted(generate_all_typos(word, include_accents)):
            if typo in seen: continue
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
        "Accenti mancanti, verbi futuri, sostantivi in -ità"
    )
    # Append regex catch-all
    regex_lines = [
        "  # REGEX — Pattern catch-all per accenti",
    ]
    for pattern, repl, comment in [
        ("(?P<stem>[a-z]{6,})ero$", "{{stem}}erò", "Futuro 1p -erò"),
        ("(?P<stem>[a-z]{6,})era$", "{{stem}}erà", "Futuro 3p -erà"),
        ("(?P<stem>[a-z]{6,})iro$", "{{stem}}irò", "Futuro 1p -irò"),
        ("(?P<stem>[a-z]{6,})ira$", "{{stem}}irà", "Futuro 3p -irà"),
        ("(?P<stem>[a-z]{8,})ita$", "{{stem}}ità", "Sostantivi -ità"),
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
        "Termini tech e codice (JS, React, CSS, Git...)",
        include_accents=False
    )
    return content, total

# ===================================================================
# Main
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
    fallback = os.path.expanduser("~/Library/Application Support/espanso")
    if os.path.isdir(fallback):
        return fallback
    return None

def write_pack(match_dir, filename, content, total):
    path = os.path.join(match_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    size = os.path.getsize(path) / 1024
    print(f"  ✅ {filename:<25} {total:>5,} regole  ({size:.0f} KB)")
    return total

if __name__ == "__main__":
    print("🔤 Refuos — Generatore regole Espanso")
    print("=" * 45)

    config_path = get_espanso_config_path()
    if not config_path:
        print("⚠️  Espanso non trovato. Genera i file nella cartella corrente.")
        config_path = "."

    match_dir = os.path.join(config_path, "match")
    os.makedirs(match_dir, exist_ok=True)

    # Rimuovi il vecchio file monolitico se esiste
    old_file = os.path.join(match_dir, "italian-realtime.yml")
    if os.path.exists(old_file):
        os.remove(old_file)
        print(f"  🗑  Rimosso vecchio file: italian-realtime.yml")

    print(f"  📂 {match_dir}\n")

    grand_total = 0

    # Pack 1: Italiano
    it_content, it_total = generate_pack(
        ITALIANO_WORDS, "Italiano",
        "Parole italiane quotidiane"
    )
    grand_total += write_pack(match_dir, "refuos-italiano.yml", it_content, it_total)

    # Pack 2: Accenti
    acc_content, acc_total = generate_accenti_pack()
    grand_total += write_pack(match_dir, "refuos-accenti.yml", acc_content, acc_total)

    # Pack 3: Dev
    dev_content, dev_total = generate_dev_pack()
    grand_total += write_pack(match_dir, "refuos-dev.yml", dev_content, dev_total)

    print(f"\n  📊 Totale: {grand_total:,} regole in 3 pacchetti")
    print(f"\n  Riavvia Espanso: espanso restart")
    print(f"  Per rimuovere un pacchetto: elimina il file .yml corrispondente")
