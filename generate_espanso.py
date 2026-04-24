#!/usr/bin/env python3
"""
Refuos — Generatore regole Espanso
https://github.com/heavybeard/refuos
Genera tutte le varianti typo plausibili per parole italiane + termini tech.
"""
import os, subprocess

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

# -------------------------------------------------------------------
# DIZIONARIO ITALIANO — Aggiungi parole qui e rigenera
# -------------------------------------------------------------------
ITALIAN_WORDS = """
il lo la i gli le un uno una
di a da in con su per tra fra
e o ma anche però quindi perché quando come dove
che chi cosa quale quanto
non più molto poco tutto tanto troppo sempre mai ancora già
io tu lui lei noi voi loro
mi ti ci si vi ne lo la li le
essere avere fare dire andare venire potere volere dovere sapere
stare dare vedere sentire trovare pensare credere mettere prendere portare
sono sei è siamo siete sono
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
qui qua là lì sopra sotto dentro fuori vicino lontano
oggi domani ieri adesso ora poi prima dopo subito
sì no forse
acqua casa anno tempo giorno vita uomo donna bambino ragazzo
lavoro scuola città paese mondo parte modo punto fatto cosa
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
comunque tuttavia inoltre infatti perciò dunque
attraverso durante senza contro verso secondo
insieme davvero proprio appena quasi almeno
settimana mese anno minuto secondo ora
lunedì martedì mercoledì giovedì venerdì sabato domenica
gennaio febbraio marzo aprile maggio giugno
luglio agosto settembre ottobre novembre dicembre
perché poiché affinché benché sebbene nonostante
veloce velocemente possibile impossibile
sicuro sicuramente probabilmente certamente
problema problemi soluzione soluzioni
messaggio informazione comunicazione
attenzione esperienza conoscenza
sviluppo aggiornamento miglioramento cambiamento
appuntamento disponibile disponibilità
funzionare funziona funzionamento
organizzare organizzazione collaborare collaborazione
presentazione documentazione
psicoterapia psicoterapeuta terapeuta terapia
nutrizione nutrizionista alimentazione
medicina medico paziente benessere salute mentale
percorso sessione consulenza prenotazione prenotare
piattaforma applicazione
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
già più giù può ciò così però perciò cioè
affinché giacché allorché purché finché cosicché
attività capacità possibilità disponibilità responsabilità qualità
quantità identità realtà libertà difficoltà facilità utilità necessità
università curiosità creatività sensibilità vulnerabilità
""".split()

# -------------------------------------------------------------------
# DIZIONARIO TECH — Aggiungi termini qui e rigenera
# -------------------------------------------------------------------
TECH_WORDS = """
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

# -------------------------------------------------------------------
# Generatori di typo
# -------------------------------------------------------------------
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

def generate_all_typos(word, is_tech=False):
    typos = set()
    typos |= generate_transpositions(word)
    typos |= generate_missing_double(word)
    if not is_tech:
        typos |= generate_accent_variants(word)
    if len(word) >= 5:
        typos |= generate_missing_char(word)
    all_valid = set(ITALIAN_WORDS) | set(TECH_WORDS)
    typos -= all_valid
    typos.discard(word)
    return {t for t in typos if len(t) >= 2}

def esc(s):
    return f'"{s}"'

# -------------------------------------------------------------------
# Generatore YAML
# -------------------------------------------------------------------
def generate_yaml():
    lines = [
        "# Refuos — Autocorrezione real-time",
        "# https://github.com/heavybeard/refuos",
        "# File auto-generato — rigenera con: python3 generate_espanso.py",
        "", "matches:", "",
        "  # ITALIANO — Parole ad alta frequenza",
    ]
    total = 0
    seen = set()

    for word in sorted(set(ITALIAN_WORDS)):
        if len(word) < 3: continue
        for typo in sorted(generate_all_typos(word)):
            if typo in seen: continue
            seen.add(typo)
            lines.append(f"  - trigger: {esc(typo)}")
            lines.append(f"    replace: {esc(word)}")
            if not any(c in word for c in 'àèéìòù'):
                lines.append("    propagate_case: true")
            lines.append("    word: true")
            lines.append("")
            total += 1

    lines.append("  # TECH — Termini inglesi comuni")
    for word in sorted(set(TECH_WORDS)):
        if len(word) < 3: continue
        for typo in sorted(generate_all_typos(word, is_tech=True)):
            if typo in seen: continue
            seen.add(typo)
            lines.append(f"  - trigger: {esc(typo)}")
            lines.append(f"    replace: {esc(word)}")
            lines.append("    word: true")
            lines.append("")
            total += 1

    # Regex catch-all per accenti
    lines.append("  # REGEX — Pattern accenti (catch-all)")
    for pattern, repl, comment in [
        ("(?P<stem>[a-z]{6,})ero$", "{{stem}}erò", "Futuro 1p -erò"),
        ("(?P<stem>[a-z]{6,})era$", "{{stem}}erà", "Futuro 3p -erà"),
        ("(?P<stem>[a-z]{6,})iro$", "{{stem}}irò", "Futuro 1p -irò"),
        ("(?P<stem>[a-z]{6,})ira$", "{{stem}}irà", "Futuro 3p -irà"),
        ("(?P<stem>[a-z]{8,})ita$", "{{stem}}ità", "Sostantivi -ità"),
    ]:
        lines.append(f"  # {comment}")
        lines.append(f"  - regex: {esc(pattern)}")
        lines.append(f"    replace: {esc(repl)}")
        lines.append("    word: true")
        lines.append("")
        total += 1

    return '\n'.join(lines), total

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def get_espanso_config_path():
    """Rileva automaticamente il percorso config di Espanso."""
    try:
        result = subprocess.run(
            ["espanso", "path", "config"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    # Fallback macOS
    fallback = os.path.expanduser(
        "~/Library/Application Support/espanso"
    )
    if os.path.isdir(fallback):
        return fallback
    return None

if __name__ == "__main__":
    print("🔤 Refuos — Generatore regole Espanso")
    print("=" * 45)
    words = len(set(ITALIAN_WORDS)) + len(set(TECH_WORDS))
    print(f"📖 Dizionario: {words} parole")
    print("⚙️  Generazione typo in corso...")

    yaml_content, total = generate_yaml()

    config_path = get_espanso_config_path()
    if config_path:
        match_dir = os.path.join(config_path, "match")
        os.makedirs(match_dir, exist_ok=True)
        out = os.path.join(match_dir, "italian-realtime.yml")
        with open(out, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        size_kb = os.path.getsize(out) / 1024
        print(f"")
        print(f"✅ {total:,} regole scritte ({size_kb:.0f} KB)")
        print(f"📂 {out}")
        print(f"")
        print(f"Riavvia Espanso: espanso restart")
    else:
        out = "italian-realtime.yml"
        with open(out, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        print(f"")
        print(f"✅ {total:,} regole generate in {out}")
        print(f"⚠️  Espanso non trovato.")
        print(f'   Copia il file manualmente:')
        print(f'   cp {out} "$(espanso path config)/match/"')
