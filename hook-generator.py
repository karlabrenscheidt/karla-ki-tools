import streamlit as st
import anthropic
import re
import base64
from pathlib import Path

# ─── Konfiguration ───────────────────────────────────────────────
API_KEY_FILE  = Path("/Users/admin/Desktop/Claude Code Mastery/.env")
PHOTO_FILE    = Path(__file__).parent / "karla-photo-small.jpg"
ACCESS_CODE   = "KARLA2026"

def load_api_key():
    # Streamlit Cloud: secrets
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    # Lokal: .env Datei
    try:
        for line in API_KEY_FILE.read_text().splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def get_photo_b64():
    try:
        return base64.b64encode(PHOTO_FILE.read_bytes()).decode()
    except:
        return None

# ─── Page Setup ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Hook-Generator | Karla Brenscheidt",
    page_icon="🪝",
    layout="centered"
)

# ─── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── WARM CREAM — Karla's Landing Page ── */
    .stApp { background: #FAF0D4 !important; }
    .main  { background: transparent !important; }

    /* ── WHITE CARD CONTAINER ── */
    .block-container {
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 820px !important;
        background: white !important;
        border-radius: 28px !important;
        box-shadow: 0 12px 60px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.06) !important;
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
    }

    /* ── MAGENTA HEADER BLOCK ── */
    .header-box {
        background: #FF08C0;
        padding: 2.5rem 2rem 3.8rem 2rem;
        text-align: center;
        margin: 0 -2rem 2rem -2rem;
        position: relative;
        overflow: hidden;
        border-radius: 28px 28px 0 0;
    }
    /* Curved white bottom edge */
    .header-box::before {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 40px;
        background: white;
        border-radius: 50% 50% 0 0 / 40px 40px 0 0;
        z-index: 2;
    }
    /* Decorative star */
    .header-box::after {
        content: '✦';
        position: absolute;
        font-size: 14rem;
        color: rgba(255,255,255,0.06);
        bottom: -40px;
        right: -10px;
        line-height: 1;
        pointer-events: none;
        z-index: 1;
    }
    .header-pill {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        border: 1.5px solid rgba(255,255,255,0.4);
        color: white;
        border-radius: 50px;
        padding: 0.25rem 1rem;
        font-size: 0.62rem;
        font-weight: 800;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .header-box h1 {
        font-size: 3.8rem;
        font-weight: 900;
        margin: 0;
        line-height: 0.95;
        letter-spacing: -0.03em;
        text-transform: uppercase;
        color: white;
    }
    .header-box p {
        font-size: 0.85rem;
        font-weight: 600;
        color: rgba(255,255,255,0.75);
        margin-top: 1rem;
        letter-spacing: 0.03em;
    }
    .accent-line {
        width: 44px;
        height: 3px;
        background: rgba(255,255,255,0.5);
        border-radius: 2px;
        margin: 0 auto 1rem auto;
    }

    /* ── HOOK CARDS ── */
    .hook-box {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    }
    .hook-label { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 0.5rem; color: #FF08C0; }
    .hook-text  { font-size: 1.05rem; line-height: 1.6; color: #1a1a1a; font-weight: 700; }
    .hook-type-badge {
        display: inline-block;
        background: #FF08C0;
        color: white;
        border-radius: 50px;
        padding: 0.2rem 0.8rem;
        font-size: 0.62rem;
        font-weight: 800;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }

    /* ── INFO PILL ── */
    .info-pill {
        background: white;
        border: 2px solid rgba(255,8,192,0.15);
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        font-size: 0.85rem;
        color: #333;
        margin-bottom: 1.5rem;
    }

    /* ── FOOTER BADGE ── */
    .karla-badge {
        text-align: center;
        font-size: 0.75rem;
        color: rgba(0,0,0,0.4);
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(0,0,0,0.08);
        letter-spacing: 0.05em;
    }

    /* ── BUTTON — pill like landing page ── */
    .stButton > button {
        background: #FF08C0 !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 1rem 2rem !important;
        font-size: 0.9rem !important;
        font-weight: 800 !important;
        width: 100% !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        box-shadow: 0 6px 28px rgba(255,8,192,0.35) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #CC0099 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 36px rgba(255,8,192,0.5) !important;
    }

    /* ── INPUTS ── */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        border: 2px solid rgba(255,8,192,0.15) !important;
        border-radius: 12px !important;
        background: white !important;
        color: #1a1a1a !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {
        color: rgba(0,0,0,0.28) !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #FF08C0 !important;
        box-shadow: 0 0 0 3px rgba(255,8,192,0.1) !important;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSelectbox"] label {
        color: #FF08C0 !important;
        font-size: 0.74rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stSelectbox"] > div > div {
        background: white !important;
        border: 2px solid rgba(255,8,192,0.15) !important;
        border-radius: 12px !important;
        color: #1a1a1a !important;
    }

    /* ── TYPOGRAPHY ── */
    p, .stMarkdown p { color: #333 !important; }
    h1, h2, h3 { color: #FF08C0 !important; }
    h3 {
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        color: #1a1a1a !important;
        font-weight: 800 !important;
    }
    .stCaption { color: rgba(0,0,0,0.4) !important; font-size: 0.78rem !important; }

    /* ── MISC ── */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        background: rgba(255,8,192,0.05) !important;
        border: 1.5px solid rgba(255,8,192,0.2) !important;
    }
    div[data-testid="stExpander"] {
        background: white !important;
        border: 2px solid rgba(255,8,192,0.15) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] summary { color: #1a1a1a !important; }
    div[data-testid="stCode"] {
        background: rgba(255,8,192,0.04) !important;
        border: 1px solid rgba(255,8,192,0.12) !important;
        border-radius: 8px !important;
    }
    hr { border-color: rgba(0,0,0,0.07) !important; }
</style>
""", unsafe_allow_html=True)

# ─── Access Gate ─────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _photo = get_photo_b64()
    _img = f'<img src="data:image/jpeg;base64,{_photo}" style="width:92px;height:92px;border-radius:50%;object-fit:cover;object-position:center top;border:3px solid white;box-shadow:0 6px 20px rgba(0,0,0,0.3);">' if _photo else ""
    st.markdown(f"""
    <div class="header-box">
      <div style="position:relative;z-index:3;text-align:center;">
        <div style="margin-bottom:0.75rem;">{_img}</div>
        <div class="header-pill">✦ KI-Powered Tool</div>
        <div style="font-size:3rem;font-weight:900;color:white;line-height:0.92;
                    letter-spacing:-0.02em;text-transform:uppercase;margin:0.5rem 0 0.25rem;">
          Instagram<br>Hook-Generator
        </div>
        <div style="font-size:0.76rem;color:rgba(255,255,255,0.65);letter-spacing:0.1em;
                    text-transform:uppercase;margin-bottom:1.1rem;">by Karla Brenscheidt</div>
        <div style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;">
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                       color:white;border-radius:50px;padding:0.22rem 0.8rem;
                       font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ 5 Hook-Varianten</span>
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                       color:white;border-radius:50px;padding:0.22rem 0.8rem;
                       font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Psychologie-Analyse</span>
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                       color:white;border-radius:50px;padding:0.22rem 0.8rem;
                       font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Caption-Hook</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Bitte gib deinen Zugangscode ein")
    code = st.text_input("Zugangscode", type="password", placeholder="Dein Code aus der DM")

    if st.button("Zugang freischalten"):
        if code.strip().upper() == ACCESS_CODE:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Falscher Code. Hast du den Hook-Generator bereits gekauft? Schreib mir auf Instagram @karla.brenscheidt 👋")

    st.markdown("""
    <div class="karla-badge">
        Noch kein Zugang? <strong>7€</strong> — oder hol dir beide Generatoren im Bundle für <strong>9€</strong>.<br>
        👉 @karla.brenscheidt auf Instagram
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Hauptanwendung ──────────────────────────────────────────────
_photo = get_photo_b64()
_img = f'<img src="data:image/jpeg;base64,{_photo}" style="width:92px;height:92px;border-radius:50%;object-fit:cover;object-position:center top;border:3px solid white;box-shadow:0 6px 20px rgba(0,0,0,0.3);">' if _photo else ""
st.markdown(f"""
<div class="header-box">
  <div style="position:relative;z-index:3;text-align:center;">
    <div style="margin-bottom:0.75rem;">{_img}</div>
    <div class="header-pill">✦ KI-Powered Tool</div>
    <div style="font-size:3rem;font-weight:900;color:white;line-height:0.92;
                letter-spacing:-0.02em;text-transform:uppercase;margin:0.5rem 0 0.25rem;">
      Instagram<br>Hook-Generator
    </div>
    <div style="font-size:0.76rem;color:rgba(255,255,255,0.65);letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:1.1rem;">by Karla Brenscheidt</div>
    <div style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;">
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ 5 Hook-Varianten</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Psychologie-Analyse</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Caption-Hook</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-pill">
💡 <strong>So funktioniert's:</strong> Beschreib deinen Inhalt kurz — und bekomme 5 Hook-Varianten, die stoppen, fesseln und zum Weiterschauen zwingen.
</div>
""", unsafe_allow_html=True)

st.markdown("### Dein Reel — kurz beschrieben")

col1, col2 = st.columns(2)

with col1:
    thema = st.text_input("Worum geht es in deinem Reel?", placeholder="z.B. Wie ich in 3 Minuten einen Reel-Hook mit Claude schreibe")
    zielgruppe = st.text_input("Deine Zielgruppe", placeholder="z.B. Frauen, die ein Online-Business aufbauen wollen")
    nische = st.text_input("Deine Nische", placeholder="z.B. KI / Claude Code für Instagram-Starter")

with col2:
    ergebnis = st.text_input("Was ist das Ergebnis / die Transformation?", placeholder="z.B. Hooks in 3 Minuten statt 1 Stunde")
    problem = st.text_input("Welches Problem löst du?", placeholder="z.B. Kein Reel performt, weil der Hook schwach ist")
    format_typ = st.selectbox(
        "Format",
        ["Talking Head (Reel gesprochen)", "B-Roll (Text over Video)", "Beitrag (Feed-Post)"]
    )

social_proof = st.text_area(
    "✨ Deine echten Ergebnisse / Social Proof (optional — aber macht deine Hooks 10x stärker)",
    placeholder="z.B. Ich habe in 10 Minuten meinen ersten KI-Agenten gebaut. Mein letzter Reel hatte 44.000 Views bei 220 Followern. 3 Kundinnen in einer Woche gewonnen.",
    height=80
)

st.markdown("---")

if st.button("🪝 5 Hooks generieren"):
    if not thema or not zielgruppe or not ergebnis:
        st.warning("Bitte füll mindestens Thema, Zielgruppe und Ergebnis aus.")
    else:
        api_key = load_api_key()
        if not api_key:
            st.error("API-Key nicht gefunden.")
            st.stop()

        with st.spinner("Deine Hooks werden geschrieben..."):
            client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""Du bist Instagram Hook-Expertin auf dem Niveau der besten deutschen Content-Creators. Du kennst die exakten psychologischen Prinzipien die Reels viral machen. Aktuelles Jahr: 2026. WICHTIG: Erfinde KEINE konkreten Daten, Monate, Releases oder Zeitstempel — verwende nur Fakten aus den Nutzereingaben. Zahlen in Hooks müssen plausibel und nicht überprüfbar falsch sein.

KONTEXT:
Thema: {thema}
Zielgruppe: {zielgruppe}
Nische: {nische or 'nicht angegeben'}
Transformation/Ergebnis: {ergebnis}
Problem: {problem or 'nicht angegeben'}
Format: {format_typ}
Echte Ergebnisse / Social Proof: {social_proof if social_proof else 'nicht angegeben — verwende bei Zahlen-Hooks Platzhalter in eckigen Klammern wie [DEINE ZAHL] oder [DEIN ERGEBNIS], die der User selbst ausfüllen kann'}

WICHTIGE REGEL FÜR ZAHLEN: Wenn echte Ergebnisse angegeben sind, verwende GENAU diese Zahlen in den Hooks — verändere sie nicht. Wenn keine echten Ergebnisse angegeben sind, setze bei Zahlen-Hooks Platzhalter in eckigen Klammern ein (z.B. "[X] Follower", "[DEIN ERGEBNIS]") die der User mit seinen echten Werten ersetzen kann.

━━━ REFERENZ-BEISPIELE — GENAU DIESES NIVEAU ━━━

Zahlen + Social Proof (viral, weil unglaublich aber beweisbar):
"Bei 220 Followern hatte ich 44.000 Aufrufe in einer Woche. Hier ist exakt was ich getan habe."

Curiosity Gap (viral, weil Lücke offen bleibt):
"NIEMAND erklärt dir das über den Instagram-Algorithmus — dabei entscheidet genau das, ob du wächst oder nicht."

Provokation (viral, weil es spaltet und geteilt wird):
"Wer täglich postet und trotzdem nicht wächst, macht immer denselben einen Fehler."

Storytelling (viral, weil Cliffhanger + Spiegel-Effekt):
"Gestern früh um 6:47 Uhr habe ich aufgehört, meinen Content manuell zu erstellen. Seitdem nie wieder."

Pattern Interrupt (viral, weil Widerspruch den Autopiloten stoppt):
"Ich programmiere nicht. Ich habe trotzdem einen KI-Agenten der meinen Content macht — während ich schlafe."

━━━ DIE 5 GRUNDREGELN ━━━

1. KLAR — Konkret, direkt, keine Metaphern. Mit echten Details.
2. SIMPEL — Wie für ein 12-jähriges Kind. Kein Fachjargon.
3. RELEVANT — So spitz wie möglich auf die Zielgruppe zugeschnitten.
4. KONKRET — Unrunde Zahlen (213 statt 200), Zeitstempel (14:23 Uhr), echte Situationen.
5. TRIGGERT — MUSS Dopamin (Quick Win / AHA) ODER FOMO (ich verpasse etwas) auslösen.

━━━ DIE 7 PSYCHOLOGISCHEN TRIGGER ━━━

1. TRIGGER-WÖRTER (immer GROSSSCHREIBEN): NIEMAND, GEHEIM, VERBOTEN, ACHTUNG, BLINDSPOT, KAUM JEMAND, DIE WAHRHEIT, DAS HIER
2. CURIOSITY GAP: Lücke aufmachen — niemals schließen. Fragen-Hook oder CS-Methode ("Ich bin die, die X — obwohl sie nur Y")
3. PROVOKATION: Starkes Statement das spaltet. Geteilt werden = bestes Algorithmus-Signal.
4. STORYTELLING: Cliffhanger wie Netflix. Konkreter Zeitstempel + offenes Ende.
5. PATTERN INTERRUPT: Widerspruch, Kontrast, das Unerwartete. Reißt aus dem Autopiloten.
6. ZAHLEN: Unrunde Zahlen (37% statt 40%, 213 statt 200). Kleine Werte = Dringlichkeit. Extreme = Neugier.
7. SOCIAL PROOF: Echte Ergebnisse. Kunden-Zitate. "Von 127 sind 124 durchgekommen."

━━━ DEINE AUFGABE ━━━

Schreibe 5 Hooks. Jeder Hook hat GENAU 8 Elemente:

TEXT-HOOK: Einblendtext groß im Reel. 1-2 Sätze. Stoppt den Scroll sofort. KEIN "Hey" oder Begrüßung.
VISUAL-HOOK: Was in den ersten 3 Sekunden zu sehen ist — konkrete Filmregie-Anweisung passend zu Format "{format_typ}".
NEBEN-HOOK: Kurzer Satz 15-20 Sekunden später unten eingeblendet. Hält Spannung wenn erste Wirkung nachlässt.
AUDIO-EINSTIEG: Allererster gesprochener Satz. Direkt, kein "Hallo", kein "Hey". Sog von Sekunde 1.
CAPTION-HOOK: Erster Satz der Caption. Eigenständiger Hook — keine Wiederholung des Text-Hooks.
PSYCHOLOGIE: Erkläre in 1-2 Sätzen WARUM genau dieser Hook diese Zielgruppe nicht loslässt. Welches Gefühl feuert? Welcher neurologische Trigger? Sei spezifisch.
KILLER-FEHLER: Der eine Fehler den 90% machen wenn sie diesen Hook-Typ verwenden — und der ihn sofort tötet.
ZIEL-METRIK: Welche Instagram-Metrik maximiert dieser Hook? (Watchtime / Saves / Shares / Kommentare / Profilbesuche) — und warum genau diese.

Nutze für jeden Hook einen anderen Trigger. Deutsch, direkt, umgangssprachlich. Keine KI-Sprache. Keine Floskeln.

━━━ AUSGABE-FORMAT — EXAKT SO, KEINE ABWEICHUNGEN ━━━

HOOK 1 — ZAHLEN-HOOK
TEXT-HOOK: [Text]
VISUAL-HOOK: [Text]
NEBEN-HOOK: [Text]
AUDIO-EINSTIEG: [Text]
CAPTION-HOOK: [Text]
PSYCHOLOGIE: [Text]
KILLER-FEHLER: [Text]
ZIEL-METRIK: [Text]

HOOK 2 — CURIOSITY-HOOK
TEXT-HOOK: [Text]
VISUAL-HOOK: [Text]
NEBEN-HOOK: [Text]
AUDIO-EINSTIEG: [Text]
CAPTION-HOOK: [Text]
PSYCHOLOGIE: [Text]
KILLER-FEHLER: [Text]
ZIEL-METRIK: [Text]

HOOK 3 — PROVOKATIONS-HOOK
TEXT-HOOK: [Text]
VISUAL-HOOK: [Text]
NEBEN-HOOK: [Text]
AUDIO-EINSTIEG: [Text]
CAPTION-HOOK: [Text]
PSYCHOLOGIE: [Text]
KILLER-FEHLER: [Text]
ZIEL-METRIK: [Text]

HOOK 4 — STORY-HOOK
TEXT-HOOK: [Text]
VISUAL-HOOK: [Text]
NEBEN-HOOK: [Text]
AUDIO-EINSTIEG: [Text]
CAPTION-HOOK: [Text]
PSYCHOLOGIE: [Text]
KILLER-FEHLER: [Text]
ZIEL-METRIK: [Text]

HOOK 5 — PATTERN-INTERRUPT-HOOK
TEXT-HOOK: [Text]
VISUAL-HOOK: [Text]
NEBEN-HOOK: [Text]
AUDIO-EINSTIEG: [Text]
CAPTION-HOOK: [Text]
PSYCHOLOGIE: [Text]
KILLER-FEHLER: [Text]
ZIEL-METRIK: [Text]

"""

            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=5000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text

        st.success("Deine 5 Hooks sind fertig! 🎉")

        hook_display = [
            ("🔢", "Zahlen + Social Proof",  "#FF08C0"),
            ("🔐", "Curiosity Gap",          "#CC0099"),
            ("🎯", "Provokation",            "#FF08C0"),
            ("🎬", "Storytelling",           "#CC0099"),
            ("⚡", "Pattern Interrupt",      "#FF08C0"),
        ]

        def clean(text):
            """Bereinigt Markdown-Artefakte vollständig."""
            text = re.sub(r'^\*+\s*', '', text)           # Führende Sternchen
            text = re.sub(r'\s*\*+$', '', text)           # Nachfolgende Sternchen
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text) # **fett** → normal
            text = re.sub(r'\*([^*]+)\*', r'\1', text)    # *kursiv* → normal
            text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
            text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'^\*{2,}\s*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'\n{3,}', '\n', text)
            return text.strip()

        def extract_field(block, label):
            all_labels = "TEXT-HOOK|VISUAL-HOOK|NEBEN-HOOK|AUDIO-EINSTIEG|CAPTION-HOOK|PSYCHOLOGIE|KILLER-FEHLER|ZIEL-METRIK"
            pattern = rf'{label}:\s*(.*?)(?={all_labels}:|HOOK \d+|$)'
            match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
            return clean(match.group(1)) if match else ""

        # Positionsbasiertes Parsing
        blocks = re.split(r'(?=HOOK \d+ —)', result)
        hook_blocks = [b for b in blocks if re.match(r'HOOK \d+ —', b.strip())]

        for i, block in enumerate(hook_blocks[:5]):
            if i >= len(hook_display):
                continue

            text_hook   = extract_field(block, "TEXT-HOOK")
            visual_hook = extract_field(block, "VISUAL-HOOK")
            neben_hook  = extract_field(block, "NEBEN-HOOK")
            audio       = extract_field(block, "AUDIO-EINSTIEG")
            caption     = extract_field(block, "CAPTION-HOOK")
            psychologie = extract_field(block, "PSYCHOLOGIE")
            killer      = extract_field(block, "KILLER-FEHLER")
            metrik      = extract_field(block, "ZIEL-METRIK")

            if not text_hook:
                continue

            icon, title, border_color = hook_display[i]

            # Hook-Karte: Titel + Haupt-Text
            st.markdown(f"""
            <div style="border-left:5px solid {border_color}; background:white; border-radius:0 12px 12px 0;
                        padding:1.25rem 1.5rem 1rem 1.5rem; margin-bottom:0.5rem;
                        box-shadow:5px 5px 0 {border_color}33, 0 2px 12px rgba(0,0,0,0.05);">
                <div style="display:inline-block; background:{border_color}; color:white; border-radius:4px;
                            padding:0.18rem 0.7rem; font-size:0.62rem; font-weight:800; text-transform:uppercase;
                            letter-spacing:0.12em; margin-bottom:0.7rem;">{icon} Hook {i+1} — {title}</div>
                <div style="font-size:1.1rem; font-weight:700; color:#1a1a1a; line-height:1.5;">{text_hook}</div>
            </div>
            """, unsafe_allow_html=True)

            # Sub-Elemente: Umsetzung
            st.caption("📸 **Visual-Hook** — *erste 3 Sekunden im Bild*")
            st.write(visual_hook)
            st.caption("🔁 **Neben-Hook** — *15–20 Sek. später einblenden*")
            st.write(neben_hook)
            st.caption("🎙️ **Audio-Einstieg** — *erster Satz in die Kamera, kein Hey*")
            st.write(f'*„{audio}"*')
            st.caption("✍️ **Caption-Hook** — *erster Satz der Caption*")
            st.write(caption)

            # Coach-Bereich: Psychologie + Killer-Fehler + Metrik
            with st.expander("🧠 Warum funktioniert dieser Hook? + Killer-Fehler + Ziel-Metrik"):
                st.markdown(f"**🧠 Psychologie**\n\n{psychologie}")
                st.markdown("---")
                st.markdown(f"**⚠️ Killer-Fehler** *(den 90% machen)*\n\n{killer}")
                st.markdown("---")
                st.markdown(f"**📊 Ziel-Metrik**\n\n{metrik}")

            # Copy-Paste Block
            copy_text = f"""📱 TEXT-HOOK:
{text_hook}

📸 VISUAL (erste 3 Sek.):
{visual_hook}

🔁 NEBEN-HOOK (nach 15-20 Sek.):
{neben_hook}

🎙️ AUDIO-EINSTIEG:
{audio}

✍️ CAPTION-HOOK:
{caption}"""
            with st.expander("📋 Alles kopieren"):
                st.code(copy_text, language=None)

            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")
        st.caption("Schreib mir auf Instagram @karla.brenscheidt wenn du wissen willst welcher Hook bei dir am stärksten performed. 👋")

st.markdown("""
<div class="karla-badge">
    Gemacht mit ❤️ von <strong>Karla Brenscheidt</strong> | @karla.brenscheidt<br>
    <small>Ich zeige dir, wie du mit Claude Code in 3–5 Minuten Tools, Reels und KI-Systeme baust. Ohne Technik-Frust.</small>
</div>
""", unsafe_allow_html=True)
