import streamlit as st
import anthropic
import re
import base64
from pathlib import Path

# ─── Konfiguration ───────────────────────────────────────────────
WORKSPACE     = Path("/Users/admin/Desktop/Claude Code Mastery")
API_KEY_FILE  = WORKSPACE / ".env"
PHOTO_FILE    = Path(__file__).parent / "karla-photo-small.jpg"
ACCESS_CODE   = "KARLA2026"


def load_marktforschung():
    """Liest die neueste Queen-Agent-Marktforschung und extrahiert Fragen + Trends."""
    mf_dir = WORKSPACE / "outputs" / "marktforschung"
    if not mf_dir.exists():
        return None
    dateien = sorted(mf_dir.glob("marktforschung-*.md"), reverse=True)
    if not dateien:
        return None
    inhalt = dateien[0].read_text()
    fragen, trends = [], []
    aktuell = None
    for zeile in inhalt.splitlines():
        z = zeile.strip()
        if "TOP 10 FRAGEN" in z.upper() or "TOP 20 FRAGEN" in z.upper():
            aktuell = "fragen"
        elif "TRENDING" in z.upper():
            aktuell = "trends"
        elif "FRUSTRATIONEN" in z.upper() or "KONTRÄRE" in z.upper():
            aktuell = None
        elif aktuell == "fragen" and z and z[0].isdigit():
            text = re.sub(r"^\d+[\.\)]\s*", "", z)
            if text and len(text) > 10:
                fragen.append(text)
        elif aktuell == "trends" and z.startswith(("1.", "2.", "3.", "4.", "5.", "-", "**")):
            text = re.sub(r"^[\d\.\-\*\s]+", "", z).strip()
            if text and len(text) > 10:
                trends.append(text)
    return {
        "datei": dateien[0].name,
        "fragen": fragen[:5],
        "trends": trends[:3],
    }


def load_queen_agent_hooks():
    """Liest die neuesten vom Queen Agent generierten Hooks."""
    qa_dir = WORKSPACE / "outputs" / "queen-agent"
    if not qa_dir.exists():
        return None
    dateien = sorted(qa_dir.glob("hooks-*.md"), reverse=True)
    if not dateien:
        return None
    inhalt = dateien[0].read_text()
    # Marktforschung-Abschnitt extrahieren
    mf_start = inhalt.find("## Marktforschung")
    thema_abschnitt_start = inhalt.find("## Gewähltes Thema")
    marktforschung_text = ""
    if mf_start > -1 and thema_abschnitt_start > -1:
        marktforschung_text = inhalt[mf_start:thema_abschnitt_start].replace("## Marktforschung\n", "").strip()
    # Thema-Block extrahieren (THEMA: + WARUM: + TRANSFORMATION:)
    thema_block = ""
    hooks_start_pos = inhalt.find("## Deine 5 Hooks")
    if thema_abschnitt_start > -1 and hooks_start_pos > -1:
        thema_block = inhalt[thema_abschnitt_start:hooks_start_pos].replace("## Gewähltes Thema\n", "").strip()
    # Einzelnes THEMA: für Anzeige
    thema = ""
    for zeile in thema_block.splitlines():
        if "THEMA:" in zeile:
            thema = zeile.replace("THEMA:", "").strip()
            break
    # Hooks-Abschnitt extrahieren
    hooks_text = inhalt[hooks_start_pos:].replace("## Deine 5 Hooks\n", "").strip() if hooks_start_pos > -1 else ""
    # Datum aus Dateiname
    name = dateien[0].stem  # hooks-KW23-2026_02-21
    return {
        "datei": dateien[0].name,
        "thema": thema,
        "thema_block": thema_block,
        "marktforschung_text": marktforschung_text,
        "hooks_text": hooks_text,
        "datum": name.replace("hooks-", "").replace("_", " "),
    }

def regeneriere_hooks(api_key, marktforschung, thema_block):
    """Generiert 5 neue Hooks für dasselbe Thema — ohne neue Marktforschung."""
    from datetime import datetime
    client = anthropic.Anthropic(api_key=api_key)
    thema, transformation = "", ""
    for zeile in thema_block.splitlines():
        if zeile.startswith("THEMA:"):
            thema = zeile.replace("THEMA:", "").strip()
        elif zeile.startswith("TRANSFORMATION:"):
            transformation = zeile.replace("TRANSFORMATION:", "").strip()

    KARLA_KONTEXT = """Karla Brenscheidt (@karla.brenscheidt), Instagram-Creatorin aus Köln.
Dreifache Mutter. Hat alles auf Selbstständigkeit gesetzt.
Mit Claude Code: 0 → 100k+ Views in 60 Tagen.
NISCHE: Claude Code + KI für Frauen die ein Online-Business auf Instagram aufbauen wollen.
ZIELGRUPPE: Frauen 30–45, überfordert, wenig Zeit, wollen 1.000–5.000€/Monat online verdienen.
TON: Direkt, ehrlich, keine KI-Sprache, keine Floskeln, umgangssprachlich."""

    prompt = f"""Du bist Instagram Hook-Expertin auf dem Niveau der besten deutschen Content-Creators. Du kennst die exakten psychologischen Prinzipien die Reels viral machen. Aktuelles Jahr: 2026.

KONTEXT KARLA:
{KARLA_KONTEXT}

MARKTFORSCHUNG DIESE WOCHE (echte Zielgruppen-Daten):
{marktforschung}

THEMA DIESES REELS: {thema}
Zielgruppe: Frauen 30–45, Online-Business aufbauen, wenig Zeit, überfordert von KI/Technik
Nische: Claude Code + KI für Instagram-Starter
Transformation/Ergebnis: {transformation}
Problem: Content-Lähmung, weiß nicht was posten, zu viele Tools
Format: Talking Head (Reel gesprochen) — Dascha Stories Methode anwenden:
Skript 2 (Fehler+Lösung): Start "Hör auf, [Fehler] zu machen" + Autorität + Konsequenz + Lösung.
Skript 3 (Wunsch+Eine Sache): Eigenes Ergebnis + "Diese EINE Sache" — nie mehr als einen Trick.
Anti-Wörter vermeiden: Mindset, Klarheit, Wachstum, Transformation, Energie, sichtbar.
Beweise Pflicht: Eigenes Ergebnis, Zeitstempel oder Kundenzahl in Satz 2-3 einbauen.
WICHTIGE REGEL FÜR ZAHLEN: Wenn echte Ergebnisse angegeben sind, verwende GENAU diese Zahlen — verändere sie nicht. Wenn keine echten Ergebnisse angegeben sind, setze Platzhalter in eckigen Klammern ein (z.B. "[X] Follower", "[DEIN ERGEBNIS]").

━━━ KARLAS ECHTE TOP-HOOKS — GENAU DIESES NIVEAU ━━━

165.009 Views (Karlas bester Reel):
"Donnerstag, 8:52 Uhr. Ich verschicke meine Bewerbung. Freitag um 11 Uhr: die Zusage."
→ Warum es funktioniert: spezifischer Zeitstempel, echter persönlicher Moment, kein Tool-Tutorial.

56.980 Views:
"Unser Garten war der einzige Ort wo meine Kinder nie spielen wollten. Dann habe ich Claude gefragt. Jetzt wollen sie nicht mehr drinnen spielen."
→ Warum es funktioniert: alltägliches Problem + Claude als unerwartete Lösung + leichte Ironie.

DAS IST DER STIL: kurz, persönlich, konkreter Zeitstempel oder Alltagssituation, Claude löst etwas Unerwartetes. KEIN Tutorial-Sprech, KEIN "ich zeige dir wie".

━━━ KARLAS ALLEINSTELLUNGSMERKMAL ━━━
Karla ist die EINZIGE deutsche Creatorin die Claude Code live auf Instagram zeigt.
Kein Technik-Tutorial. Echte Ergebnisse im Alltag.
Die Hooks müssen diesen Kontrast nutzen: normale Frau + unerwartetes KI-Tool = unglaubliches Ergebnis.

━━━ 5 NEUE HOOK-VARIANTEN (andere als vorher!) ━━━

Schreibe 5 NEUE Hooks — komplett anders als typische Varianten, frisch, unerwartet.
Jeder Hook enthält GENAU diese 8 Elemente. ZIEL-METRIK immer mit konkreter Prozent-Zielzahl (z.B. "Watchtime: Ziel 65%+").
ABSOLUTES VERBOT: Kein Satz darf mit einem Gedankenstrich (—) enden. Vollständige Sätze, kein KI-Cliffhanger-Muster.
PFLICHT: Perfekte deutsche Rechtschreibung und Zeichensetzung. Kommafehler oder fehlende Satzzeichen sind nicht akzeptabel.
VISUAL-CUE REGEL: Der VISUAL-HOOK ist maximal 5 Wörter — nur was zu sehen ist (z.B. "Handy-Screen, Zahlen steigen"). KEINE Szenen-Beschreibung, KEIN Regietext, KEINE Filmregieanweisungen.
CAPTION-HOOK REGEL: "Mutter von 3 Kindern", Wohnort oder Alter NICHT in den Caption-Hook.
TRIGGER-WÖRTER REGEL: Wo es natürlich passt, ein Power-Wort einbauen und GROSS schreiben (NIEMAND, KAUM JEMAND, ACHTUNG, NIE, EINZIGE). Niemals erzwingen, nie mehr als eins pro Hook, es muss klingen wie Karla spricht.

KATEGORIE-MECHANIK (je ein Hook pro Typ):
1. ZAHLEN & BEWEIS-HOOK → Eine konkrete, unrunde Zahl oder ein echtes Ergebnis als Beweis (z.B. "Bei 213 Followern 44.000 Aufrufe"). Social Proof, nie Prahlerei. Wenn keine echte Zahl da ist, Platzhalter in eckigen Klammern.
2. NEUGIER-HOOK → Wissenslücke aufmachen und NICHT schließen. Eine Behauptung, die sofort die Frage "Was denn genau?" auslöst.
3. PROVOKATIONS-HOOK → Sanfte Reibung im Dascha-Stil: "Hör auf, [konkreter Fehler] zu machen" oder "Du machst wahrscheinlich diesen einen Fehler". Reibung am Verhalten der Zielgruppe, NIE Angriff auf andere Personen, kein Leadership-Pathos.
4. MOMENT-HOOK → Exakter Zeitstempel plus persönlicher Alltagsmoment. Zwei Zeitpunkte, dazwischen die Veränderung. Kein Tutorial, nur das Ergebnis.
5. STOPP-HOOK → Erwartungsbruch. Etwas das nicht zusammenpasst (normale Frau, unmögliches Ergebnis). Stoppt den Daumen sofort.

## HOOK 1 — ZAHLEN & BEWEIS-HOOK
**TEXT-HOOK:** [Text]
**VISUAL-HOOK:** [max. 5 Wörter]
**NEBEN-HOOK:** [Text]
**AUDIO-EINSTIEG:** [Text]
**CAPTION-HOOK:** [Text]
**PSYCHOLOGIE:** [Text]
**KILLER-FEHLER:** [Text]
**ZIEL-METRIK:** [Text]

## HOOK 2 — NEUGIER-HOOK
**TEXT-HOOK:** [Text]
**VISUAL-HOOK:** [max. 5 Wörter]
**NEBEN-HOOK:** [Text]
**AUDIO-EINSTIEG:** [Text]
**CAPTION-HOOK:** [Text]
**PSYCHOLOGIE:** [Text]
**KILLER-FEHLER:** [Text]
**ZIEL-METRIK:** [Text]

## HOOK 3 — PROVOKATIONS-HOOK
**TEXT-HOOK:** [Text]
**VISUAL-HOOK:** [max. 5 Wörter]
**NEBEN-HOOK:** [Text]
**AUDIO-EINSTIEG:** [Text]
**CAPTION-HOOK:** [Text]
**PSYCHOLOGIE:** [Text]
**KILLER-FEHLER:** [Text]
**ZIEL-METRIK:** [Text]

## HOOK 4 — MOMENT-HOOK
**TEXT-HOOK:** [Text]
**VISUAL-HOOK:** [max. 5 Wörter]
**NEBEN-HOOK:** [Text]
**AUDIO-EINSTIEG:** [Text]
**CAPTION-HOOK:** [Text]
**PSYCHOLOGIE:** [Text]
**KILLER-FEHLER:** [Text]
**ZIEL-METRIK:** [Text]

## HOOK 5 — STOPP-HOOK
**TEXT-HOOK:** [Text]
**VISUAL-HOOK:** [max. 5 Wörter]
**NEBEN-HOOK:** [Text]
**AUDIO-EINSTIEG:** [Text]
**CAPTION-HOOK:** [Text]
**PSYCHOLOGIE:** [Text]
**KILLER-FEHLER:** [Text]
**ZIEL-METRIK:** [Text]

━━━ BONUS: DEIN STÄRKSTER HOOK ━━━
Welcher der 5 Hooks hat das höchste Viral-Potenzial für diese spezifische Nische und Zielgruppe — und warum genau? Ein Satz.
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}]
    )
    neue_hooks = response.content[0].text.strip()

    # Speichern
    qa_dir = WORKSPACE / "outputs" / "queen-agent"
    qa_dir.mkdir(parents=True, exist_ok=True)
    kw = datetime.now().strftime("KW%V-%Y_%H-%M")
    datei = qa_dir / f"hooks-{kw}.md"
    datei.write_text(
        f"# Queen Agent Output — {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"## Marktforschung\n{marktforschung}\n\n"
        f"## Gewähltes Thema\n{thema_block}\n\n"
        f"## Deine 5 Hooks\n{neue_hooks}\n"
    )
    return neue_hooks


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
                       font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Sofort postbar</span>
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                       color:white;border-radius:50px;padding:0.22rem 0.8rem;
                       font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ In Karlas Stil</span>
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
<div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);
            border-radius:16px;padding:1.4rem 1.6rem;margin:1.2rem 0;">
    <div style="font-size:0.7rem;font-weight:800;color:#FF08C0;letter-spacing:0.18em;
                text-transform:uppercase;margin-bottom:0.9rem;">Was du bekommst</div>
    <div style="display:flex;flex-direction:column;gap:0.6rem;">
        <div style="font-size:0.88rem;color:rgba(255,255,255,0.85);">✓ &nbsp;5 fertige Hooks zum Posten</div>
        <div style="font-size:0.88rem;color:rgba(255,255,255,0.85);">✓ &nbsp;Nur der Hook — sofort einsetzbar</div>
        <div style="font-size:0.88rem;color:rgba(255,255,255,0.85);">✓ &nbsp;5 verschiedene Hook-Typen für jedes Thema</div>
        <div style="font-size:0.88rem;color:rgba(255,255,255,0.85);">✓ &nbsp;Dein stärkster Hook — direkt hervorgehoben</div>
        <div style="font-size:0.88rem;color:rgba(255,255,255,0.85);">✓ &nbsp;Einfach Thema eingeben, fertig</div>
    </div>
</div>
<div style="text-align:center;font-size:0.82rem;color:rgba(255,255,255,0.45);margin-top:0.9rem;line-height:1.7;">
    Noch kein Zugang? <strong style="color:white;">7 €</strong> &nbsp;·&nbsp; Bundle mit Bio-Generator: <strong style="color:white;">9 €</strong><br>
    <a href="https://www.instagram.com/karla.brenscheidt" target="_blank"
       style="color:#FF08C0;font-weight:800;text-decoration:none;letter-spacing:0.05em;">
        ↗ @karla.brenscheidt auf Instagram
    </a>
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
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Sofort postbar</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ In Karlas Stil</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Queen Agent Hooks (deaktiviert — Generator soll ganz einfach bleiben) ──────────
qa = None
if qa and qa["hooks_text"]:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 20px; padding: 1.5rem 1.75rem 1.75rem;
                margin-bottom: 1.5rem; border: 1px solid rgba(255,8,192,0.3);">
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
            <span style="font-size:1.3rem;">👑</span>
            <span style="font-size:0.6rem; font-weight:800; letter-spacing:0.2em;
                         text-transform:uppercase; color:#FF08C0;">Queen Agent — Frisch gescannt</span>
            <span style="margin-left:auto; font-size:0.58rem; color:rgba(255,255,255,0.3);">{qa["datum"]}</span>
        </div>
        <div style="font-size:0.95rem; font-weight:700; color:white; margin-bottom:0.3rem;">
            {qa["thema"] or "5 Hooks diese Woche"}
        </div>
        <div style="font-size:0.75rem; color:rgba(255,255,255,0.5);">
            Der Agent hat gescannt und 5 Hooks für dich generiert. Scroll runter um sie zu sehen.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("👑 Deine Queen Agent Hooks — direkt verwendbar", expanded=True):
        hook_typen = ["ZAHLEN & BEWEIS-HOOK", "NEUGIER-HOOK", "PROVOKATIONS-HOOK", "MOMENT-HOOK", "STOPP-HOOK"]
        farben = ["#FF08C0", "#CC0099", "#FF08C0", "#CC0099", "#FF08C0"]
        icons = ["⏱️", "🍽️", "🙃", "🚪", "🌆"]

        # Bonus-Block extrahieren und aus hooks_text entfernen
        qa_hooks_clean = qa["hooks_text"]
        qa_bonus_text = ""
        qa_bonus_match = re.search(
            r"━+\s*BONUS:?\s*DEIN STÄRKSTER HOOK\s*━+\s*(.*?)$",
            qa_hooks_clean, re.DOTALL | re.IGNORECASE,
        )
        if not qa_bonus_match:
            qa_bonus_match = re.search(r"BONUS[^\n]*\n+(.*?)$", qa_hooks_clean, re.DOTALL | re.IGNORECASE)
        if qa_bonus_match:
            qa_bonus_text = re.sub(r"\*+", "", qa_bonus_match.group(1)).strip()
            qa_hooks_clean = qa_hooks_clean[: qa_bonus_match.start()].strip()

        # Stärkster Hook prominent oben
        if qa_bonus_text:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
                        border:2px solid #FFD700; border-radius:16px;
                        padding:1.2rem 1.5rem; margin:0 0 1.2rem 0;
                        box-shadow:0 8px 30px rgba(255,215,0,0.18);">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
                    <span style="font-size:1.2rem;">🏆</span>
                    <span style="font-size:0.6rem;font-weight:800;letter-spacing:0.22em;
                                 text-transform:uppercase;color:#FFD700;">Dein stärkster Hook</span>
                </div>
                <div style="font-size:0.95rem;line-height:1.55;color:white;font-weight:500;">
                    {qa_bonus_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        bloecke = re.split(r"(?=## HOOK \d+)", qa_hooks_clean)
        bloecke = [b for b in bloecke if b.strip().startswith("## HOOK")]

        def extrahiere(block, feld):
            m = re.search(rf"\*\*{feld}:\*\*\s*(.*?)(?=\n\*\*|\Z)", block, re.DOTALL)
            if m:
                return re.sub(r"\*", "", m.group(1)).strip()
            return ""

        for i, block in enumerate(bloecke[:5]):
            typ = hook_typen[i] if i < len(hook_typen) else f"HOOK {i+1}"
            farbe = farben[i % len(farben)]
            icon = icons[i % len(icons)]
            text_hook = extrahiere(block, "TEXT-HOOK")
            audio = extrahiere(block, "AUDIO-EINSTIEG")
            caption = extrahiere(block, "CAPTION-HOOK")
            metrik = extrahiere(block, "ZIEL-METRIK")
            if not text_hook:
                continue

            st.markdown(f"""
            <div style="border-left:4px solid {farbe}; background:#f9f9f9; border-radius:0 12px 12px 0;
                        padding:1rem 1.25rem; margin:0.75rem 0;">
                <div style="font-size:0.58rem; font-weight:800; color:{farbe}; letter-spacing:0.15em;
                            text-transform:uppercase; margin-bottom:0.4rem;">{icon} {typ}</div>
                <div style="font-size:1rem; font-weight:700; color:#1a1a1a; line-height:1.4;
                            margin-bottom:0.6rem;">{text_hook}</div>
                <div style="font-size:0.78rem; color:#555; margin-bottom:0.2rem;">
                    🎙️ <em>"{audio}"</em></div>
                <div style="font-size:0.78rem; color:#555; margin-bottom:0.2rem;">
                    ✍️ Caption: <em>{caption}</em></div>
                {"<div style='font-size:0.75rem;color:#888;margin-top:0.4rem;'>📊 " + metrik + "</div>" if metrik else ""}
            </div>
            """, unsafe_allow_html=True)

        st.caption(f"Quelle: {qa['datei']} — Hooks basieren auf echten Marktdaten")
        st.caption("Diese Hooks basieren auf echten Zielgruppen-Daten. Nutze sie als Inspiration oder generiere unten deine eigenen mit deinem spezifischen Thema.")

        st.markdown("---")
        st.caption("Diese Hooks wurden vom Queen Agent generiert — basierend auf echten Marktdaten deiner Nische. Generiere darunter eigene Hooks für dein spezifisches Reel-Thema.")
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("🔄 5 neue Hooks generieren — gleiches Thema, frische Ideen", key="regen_btn",
                     use_container_width=True):
            api_key = load_api_key()
            if api_key:
                with st.spinner("5 neue Hook-Varianten werden generiert..."):
                    regeneriere_hooks(api_key, qa["marktforschung_text"], qa["thema_block"])
                st.rerun()
            else:
                st.error("API Key nicht gefunden. Bitte .env prüfen.")

    st.markdown("---")

st.markdown("""
<div class="info-pill">
💡 Gib dein Thema ein — Claude schreibt dir 5 fertige Hooks zum Posten.
</div>
""", unsafe_allow_html=True)

# ─── Queen Agent Marktforschung ───────────────────────────────────
if "thema_input" not in st.session_state:
    st.session_state["thema_input"] = ""

mf = load_marktforschung()
if mf and (mf["fragen"] or mf["trends"]):
    with st.expander("👑 Queen Agent — Diese Woche heiß in deiner Nische (als Thema übernehmen)", expanded=False):
        st.markdown(f"<small style='color:rgba(0,0,0,0.4);'>Quelle: {mf['datei']}</small>", unsafe_allow_html=True)

        if mf["fragen"]:
            st.markdown("**🔥 Top-Fragen deiner Zielgruppe**")
            cols = st.columns(1)
            for frage in mf["fragen"]:
                kurzfrage = frage[:90] + "..." if len(frage) > 90 else frage
                if st.button(f"📌 {kurzfrage}", key=f"frage_{frage[:30]}", use_container_width=True):
                    st.session_state["thema_input"] = frage
                    st.rerun()

        if mf["trends"]:
            st.markdown("**📈 Trending Topics**")
            for trend in mf["trends"]:
                kurz = trend[:90] + "..." if len(trend) > 90 else trend
                if st.button(f"🚀 {kurz}", key=f"trend_{trend[:30]}", use_container_width=True):
                    st.session_state["thema_input"] = trend
                    st.rerun()

        st.caption("Klick auf ein Thema — es wird direkt ins Formular übernommen.")

st.markdown("### Dein Reel — kurz beschrieben")

col1, col2 = st.columns(2)

with col1:
    thema = st.text_input("Worum geht es in deinem Reel?", placeholder="z.B. Wie ich in 3 Minuten einen Reel-Hook mit Claude schreibe", key="thema_input")
    zielgruppe = st.text_input("Deine Zielgruppe", placeholder="z.B. Frauen, die ein Online-Business aufbauen wollen")
    nische = st.text_input("Deine Nische", placeholder="z.B. KI / Claude Code für Instagram-Starter")

with col2:
    ergebnis = st.text_input("Was ist das Ergebnis / die Transformation?", placeholder="z.B. Hooks in 3 Minuten statt 1 Stunde")
    problem = st.text_input("Welches Problem löst du?", placeholder="z.B. Kein Reel performt, weil der Hook schwach ist")
    format_typ = st.selectbox(
        "Format",
        ["Talking Head (Reel gesprochen)", "B-Roll (Text over Video)"]
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

        with st.spinner("Claude analysiert dein Thema und schreibt 5 Hooks mit Marktpsychologie... (~25 Sek.)"):
            client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""Du bist Instagram Hook-Expertin auf dem Niveau der besten deutschen Content-Creators. Du kennst die exakten psychologischen Prinzipien die Reels viral machen. Aktuelles Jahr: 2026. WICHTIG: Erfinde KEINE konkreten Daten, Monate, Releases oder Zeitstempel als Fakten — Zeitstempel sind nur als erzählerischer Rahmen erlaubt, echte Zahlen verwende nur aus den Nutzereingaben.

KONTEXT:
Thema: {thema}
Zielgruppe: {zielgruppe}
Nische: {nische or 'nicht angegeben'}
Transformation/Ergebnis: {ergebnis}
Problem: {problem or 'nicht angegeben'}
Format: {format_typ}
Echte Ergebnisse / Social Proof: {social_proof if social_proof else 'nicht angegeben — verwende bei Hooks mit Zahlen Platzhalter in eckigen Klammern wie [DEINE ZAHL] oder [DEIN ERGEBNIS], die der User selbst ausfüllen kann'}

WICHTIGE REGEL FÜR ZAHLEN: Wenn echte Ergebnisse angegeben sind, verwende GENAU diese Zahlen — verändere sie nicht. Wenn keine angegeben sind, setze Platzhalter in eckigen Klammern ein (z.B. "[X] Follower", "[DEIN ERGEBNIS]"), die der User mit seinen echten Werten ersetzen kann.
ABSOLUTES VERBOT: Kein Satz darf mit einem Gedankenstrich (—) enden. Vollständige Sätze, kein KI-Cliffhanger-Muster.
PFLICHT: Perfekte deutsche Rechtschreibung und Zeichensetzung in jedem Satz.

━━━ REFERENZ-NIVEAU ━━━

Bester Hook-Stil (165.000+ Views):
"Donnerstag, 8:52 Uhr. Ich verschicke meine Bewerbung. Freitag um 11 Uhr: die Zusage."
→ Warum es zieht: exakter Zeitstempel, echter Alltagsmoment, Ergebnis ohne Erklärung.

Weiterer Top-Hook (56.980 Views):
"Unser Garten war der einzige Ort wo meine Kinder nie spielen wollten. Dann habe ich Claude gefragt. Jetzt wollen sie nicht mehr drinnen spielen."
→ Warum es zieht: banales Alltagsproblem + unerwartete Lösung + leise Ironie.

DAS IST DAS NIVEAU: kurz, persönlich, konkreter Moment oder Alltagsszene, unerwartetes Ergebnis. NIEMALS "ich zeige dir wie", NIEMALS Tutorial-Sprech.

{"" if "B-Roll" in format_typ else """
━━━ TALKING HEAD — DASCHA STORIES METHODE (PFLICHT) ━━━

SKRIPT 2 — FEHLER + LÖSUNG
Schritt 1 (Hook): "Hör auf, [konkreter Fehler] zu machen." oder "Machst du auch diesen Fehler?"
Schritt 2 (Autorität): 1 Satz eigenes Ergebnis oder Zeitstempel.
Schritt 3 (Konsequenz): Was passiert wenn man weitermacht — konkret und filmbar.
Schritt 4 (Lösung): So kurz wie möglich. Ein Trick. Nicht mehr.

SKRIPT 3 — WUNSCH + EINE SACHE
Schritt 1 (Hook): Mit eigenem konkretem Ergebnis starten das die Zielgruppe auch will.
Schritt 2 (Autorität): Konkrete Zahl oder Zeitstempel.
Schritt 3 (Die eine Sache): "Dabei habe ich nur auf DIESE EINE SACHE geachtet."

ANTI-WÖRTER — NIEMALS VERWENDEN:
Mindset, Klarheit, Wachstum, Transformation, Selbstwert, Energie, Balance, authentisch, nachhaltig.
Immer konkret und filmbar. Wenn du es nicht FILMEN kannst, ist es nicht konkret genug.
"""}

━━━ DIE 5 GRUNDREGELN ━━━

1. KLAR — Konkret, direkt, keine Metaphern. Mit echten Details.
2. SIMPEL — Wie für ein 12-jähriges Kind. Kein Fachjargon.
3. RELEVANT — So spitz wie möglich auf die Zielgruppe zugeschnitten.
4. KONKRET — Unrunde Zahlen (213 statt 200), Zeitstempel (14:23 Uhr), echte Situationen.
5. AUTHENTISCH — Jeder Satz muss klingen wie ein Mensch, der wirklich spricht. Keine KI-Sprache, keine Floskeln.

━━━ 5 HOOK-TYPEN — PSYCHOLOGISCHE MECHANIK ━━━

1. ZAHLEN & BEWEIS-HOOK → Eine konkrete, unrunde Zahl oder ein echtes Ergebnis als Beweis (z.B. "Bei 213 Followern 44.000 Aufrufe"). Social Proof statt Prahlerei. Ohne echte Zahl Platzhalter in eckigen Klammern.
2. NEUGIER-HOOK → Wissenslücke öffnen. Eine Behauptung die sofort eine Frage aufwirft. Was fehlt? Was weiß ich nicht? Die Lücke bleibt offen bis zum Ende.
3. PROVOKATIONS-HOOK → Sanfte Reibung im Dascha-Stil: "Hör auf, [konkreter Fehler] zu machen" oder "Du machst wahrscheinlich diesen einen Fehler". Reibung am Verhalten der Zielgruppe, NIE Angriff auf andere Personen, kein Leadership-Pathos.
4. MOMENT-HOOK → Exakter Zeitstempel + persönlicher Moment. Zwei Zeitpunkte, dazwischen die Veränderung. Kein Tutorial, nur das Ergebnis.
5. STOPP-HOOK → Das Unerwartete. Etwas das nicht zum Kontext passt — eine normale Frau mit einem unmöglichen Ergebnis. Der Erwartungsbruch erzeugt den Sog.

HILFSMITTEL (sparsam, nie aufgesetzt):
- TRIGGER-WÖRTER: Wo es natürlich passt, ein Power-Wort einbauen und GROSS schreiben (NIEMAND, KAUM JEMAND, ACHTUNG, NIE, EINZIGE). Nie erzwingen, nie mehr als eins pro Hook, muss klingen wie Karla spricht.
- Unrunde Zahlen statt runde (37 statt 40, 213 statt 200).

━━━ AUSGABE-FORMAT — EXAKT SO, KEINE ABWEICHUNGEN ━━━

Pro Hook NUR den Hook selbst. Eine Zeile. Sonst NICHTS — keine Visual-Beschreibung, keine Caption, keine Psychologie, keine Erklärung, keine Metrik.
Kein Wohnort, kein Alter, keine Familieninfo im Hook.

HOOK 1 — ZAHLEN & BEWEIS-HOOK
TEXT-HOOK: [der Hook]

HOOK 2 — NEUGIER-HOOK
TEXT-HOOK: [der Hook]

HOOK 3 — PROVOKATIONS-HOOK
TEXT-HOOK: [der Hook]

HOOK 4 — MOMENT-HOOK
TEXT-HOOK: [der Hook]

HOOK 5 — STOPP-HOOK
TEXT-HOOK: [der Hook]

━━━ BONUS: DEIN STÄRKSTER HOOK ━━━
Welcher der 5 Hooks hat das höchste Viral-Potenzial — und warum? Ein Satz.
"""

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=5000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text

        st.success("Deine 5 Hooks sind fertig! 🎉")
        st.caption("💡 Tipp: Teste erst als Trial Reel bevor du Zeit in Produktion investierst. Nur was performt, wird ausgebaut.")

        # Bonus-Abschnitt "Dein stärkster Hook" aus dem Result extrahieren
        bonus_match = re.search(
            r"━+\s*BONUS:?\s*DEIN STÄRKSTER HOOK\s*━+\s*(.*?)$",
            result,
            re.DOTALL | re.IGNORECASE,
        )
        if not bonus_match:
            bonus_match = re.search(r"BONUS[^\n]*\n+(.*?)$", result, re.DOTALL | re.IGNORECASE)
        if bonus_match:
            bonus_text = bonus_match.group(1).strip()
            bonus_text = re.sub(r"\*+", "", bonus_text)
            bonus_text = re.sub(r"^#+\s.*$", "", bonus_text, flags=re.MULTILINE).strip()
            # Result bereinigen, damit der Bonus nicht doppelt im Hook-Parsing landet
            result = result[: bonus_match.start()].strip()
            if bonus_text:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                            border: 2px solid #FFD700; border-radius: 18px;
                            padding: 1.4rem 1.6rem; margin: 1rem 0 1.5rem 0;
                            box-shadow: 0 8px 30px rgba(255,215,0,0.18), 0 0 0 1px rgba(255,8,192,0.25) inset;">
                    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem;">
                        <span style="font-size:1.1rem;">🏆</span>
                        <span style="font-size:0.62rem; font-weight:800; letter-spacing:0.22em;
                                     text-transform:uppercase; color:#FFD700;">Dein stärkster Hook</span>
                    </div>
                    <div style="font-size:0.98rem; line-height:1.55; color:white; font-weight:500;">
                        {bonus_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        hook_display = [
            ("⏱️", "Der Zeitstempel",            "#FF08C0"),
            ("🍽️", "Der Küchentisch-Moment",     "#CC0099"),
            ("🙃", "Das habe ich nie geglaubt",  "#FF08C0"),
            ("🚪", "Die offene Tür",             "#CC0099"),
            ("🌆", "Die normale Frau aus Köln",  "#FF08C0"),
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

            text_hook = extract_field(block, "TEXT-HOOK")

            if not text_hook:
                continue

            icon, title, border_color = hook_display[i]

            # Hook-Karte: Titel + Hook
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

            # Copy-Paste Block (nur der Hook)
            with st.expander("📋 Hook kopieren"):
                st.code(text_hook, language=None)

            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")
        st.caption("Schreib mir auf Instagram @karla.brenscheidt wenn du wissen willst welcher Hook bei dir am stärksten performed. 👋")

st.markdown("""
<div class="karla-badge">
    Gemacht mit ❤️ von <strong>Karla Brenscheidt</strong> | @karla.brenscheidt<br>
    <small>Ich zeige dir, wie du mit Claude Code in 3–5 Minuten Tools, Reels und KI-Systeme baust. Ohne Technik-Frust.</small>
    <br><small style="color:rgba(0,0,0,0.3);font-style:italic;">KI ist nur ein Werkzeug. Das Hirn bringst du mit.</small>
    <br><small style="color:rgba(0,0,0,0.3);font-style:italic;">KI ist nur ein Werkzeug. Du bist die Expertin.</small>
</div>
""", unsafe_allow_html=True)
