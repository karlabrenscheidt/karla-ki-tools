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
KURS_URL      = "https://karla.brenscheidt.de/content-flow-mit-claude"
MODEL         = "claude-haiku-4-5-20251001"

KARLA_KONTEXT = """Karla Brenscheidt (@karla.brenscheidt), Instagram-Creatorin aus Köln.
Dreifache Mutter. Hat alles auf Selbstständigkeit gesetzt.
Mit Claude Code: 0 → 100k+ Views in 60 Tagen.
NISCHE: Claude Code + KI für Frauen die ein Online-Business auf Instagram aufbauen wollen.
ZIELGRUPPE: Frauen 30–45, überfordert, wenig Zeit, wollen 1.000–5.000€/Monat online verdienen.
TON: Direkt, ehrlich, keine KI-Sprache, keine Floskeln, umgangssprachlich."""

STORY_TYPEN = {
    "🛒 Story die verkauft": "verkaufen",
    "❤️ Community-Bindungs-Story": "community",
}

STORY_FORMATE = [
    "Persönlichkeits-Story (wer du bist, dein Alltag)",
    "Inspirations-Story (motiviert, begeistert, pusht)",
    "Expertise-Story (Minitraining, Tipp, Strategie)",
    "Blick hinter die Kulissen (Making-of, ehrlicher Einblick)",
    "Social-Proof-Story (Kundin vorstellen, Ergebnis zeigen)",
    "Einwand-Killer-Story (Zweifel vorab entkräften)",
]


def load_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
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
    except Exception:
        return None


def generiere_themen_ideen(api_key, nische, zielgruppe, story_typ):
    client = anthropic.Anthropic(api_key=api_key)
    typ_text = "die verkaufen" if story_typ == "verkaufen" else "die Vertrauen und Verbindung aufbauen"

    prompt = f"""Du bist Instagram-Story-Expertin für deutschsprachige Creator. Aktuelles Jahr: 2026.
PFLICHT: Perfekte deutsche Rechtschreibung und Zeichensetzung in jedem Satz. Kommafehler, falsche Groß-/Kleinschreibung oder fehlende Satzzeichen sind nicht akzeptabel.

KONTEXT:
Nische: {nische}
Zielgruppe: {zielgruppe}

Generiere 6 kurze, konkrete Story-Themen {typ_text}.

REGELN:
- Maximal 8 Wörter pro Thema
- Kein Komma, kein Doppelpunkt, kein "und dann auch noch"
- Klingt wie ein echter Satz den man so sagen würde
- Niedrigschwellig — keine kompletten Anleitungen, nur das Thema
- Beispiele für guten Stil: "Wie ich heute meinen Content in 10 Minuten fertig hatte", "Der Fehler den ich letzte Woche gemacht habe", "Was mir heute Morgen passiert ist"

Format: Eine Zeile pro Thema, nummeriert 1-6. Kein Markdown."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    ideen = []
    for zeile in raw.splitlines():
        zeile = zeile.strip()
        if zeile and zeile[0].isdigit():
            text = re.sub(r"^\d+[\.\)]\s*", "", zeile).strip()
            if text:
                ideen.append(text)
    return ideen[:6]


def generiere_story_sequenz(api_key, story_typ, story_format, thema, zielgruppe,
                             nische, produkt, transformation, social_proof):
    client = anthropic.Anthropic(api_key=api_key)

    ist_verkauf = story_typ == "verkaufen"

    kaeufertypen_block = """
━━━ DIE 6 KÄUFERTYPEN — ALLE ANSPRECHEN ━━━

1. INSPIRIERTE INA: Kauft durch Emotion, Vision, Energie. Braucht: vorher/nachher, mitreißende Geschichte, High-Energy.
2. RUDELTIER RUDI: Kauft wenn andere dabei sind. Braucht: Social Proof, "du bist nicht allein".
3. FAKTEN-FRANK: Kauft durch Daten & Fakten. Braucht: Inhalte, Preise, konkrete Zahlen.
4. WISSBEGIERIGER WILLI: Kauft durch Mehrwert & Learnings. Braucht: direkt umsetzbaren Tipp, Minitraining.
5. ÄNGSTLICHE AMELIE: Kauft durch Empathie & Sicherheit. Braucht: deine eigene Angst-Geschichte, liebevolle Stränge.
6. ZÖGERLICHE ZOE: Kauft durch sanften FOMO-Druck. Braucht: warum JETZT der richtige Zeitpunkt ist.
""" if ist_verkauf else ""

    cta_anweisung = f"""
━━━ CTA-STRATEGIE ━━━
Nur EINE Handlungsaufforderung in der gesamten Story — auf der letzten Slide.
Wenn Verkaufs-Story: Keyword für ManyChat (z.B. "Kommentiere KEYWORD und ich schicke dir den Link") ODER direkter Link.
CTA muss eine konkrete Transformation zeigen: "Finde heraus [was] — damit du [konkretes Ergebnis] erreichst."
""" if ist_verkauf else """
━━━ CTA-STRATEGIE ━━━
Nur EINE Interaktions-Aufforderung — auf der letzten Slide.
Ziel: Konversation starten, Antwort provozieren, Gemeinschaftsgefühl erzeugen.
Beispiel: offene Frage, Abstimmung, "schreib mir deine Antwort".
"""

    story_typ_anweisung = (
        "ZIEL: Verkaufen. Die Story führt die Leserin emotional durch eine Reise, die direkt zum Kauf motiviert."
        if ist_verkauf else
        "ZIEL: Community-Bindung. Die Story baut Vertrauen, Verbindung und Sympathie auf. Kein direktes Verkaufen."
    )

    prompt = f"""Du bist Instagram-Story-Expertin auf dem Niveau der besten deutschen Content-Creator. Du kennst die psychologischen Prinzipien magnetischer Stories. Aktuelles Jahr: 2026.
PFLICHT: Perfekte deutsche Rechtschreibung und Zeichensetzung in jedem Satz. Kommafehler, falsche Groß-/Kleinschreibung oder fehlende Satzzeichen sind nicht akzeptabel.

{story_typ_anweisung}

KONTEXT CREATOR:
{KARLA_KONTEXT if not nische else f"Nische: {nische}\\nZielgruppe: {zielgruppe}"}

STORY-BRIEFING:
Format: {story_format}
Thema: {thema}
Zielgruppe: {zielgruppe}
Nische: {nische}
{"Produkt/Angebot: " + produkt if produkt else ""}
{"Transformation/Ergebnis: " + transformation if transformation else ""}
{"Social Proof / echte Ergebnisse: " + social_proof if social_proof else ""}

━━━ STORYTELLING-GRUNDREGELN ━━━

1. IMMER eine Person ansprechen — nie "ihr" oder "Sie", immer "du".
2. Mit BAM einsteigen — kein Hallo, kein Intro. Direkt in die Geschichte.
3. Konkret & spezifisch — Zeitstempel, echte Details, Bilder im Kopf erzeugen.
4. Spreche wie du schreibst — umgangssprachlich, kein Fachwort-Kauderwelsch.
5. Eine Sache pro Slide — nicht überfüllen.
6. EINE Interaktion pro gesamter Sequenz — nicht auf jeder Slide.
7. Keine KI-Sprache, keine Floskeln: KEIN "boah", KEIN "mega spannend", KEIN "lass uns".
8. Vergleiche & Metaphern nutzen: "X ist wie Y", macht es greifbarer.
9. Kurze Sätze. Echtes Sprechtempo. Wenn du es laut lesen würdest — klingt es natürlich?
10. Jede Slide braucht einen Untertitel/Text — niemand schaut Stories mit Ton.

{kaeufertypen_block}
{cta_anweisung}

━━━ AUSGABE: STORY-SEQUENZ ━━━

Erstelle eine Story-Sequenz mit 7–10 Slides.
Jede Slide hat EXAKT dieses Format:

---SLIDE [Nummer]: [Slide-Titel z.B. "HOOK" / "PROBLEM" / "WENDEPUNKT" / "LÖSUNG" / "CTA"]---
TEXT: [Was auf der Slide steht — max. 2–3 kurze Sätze. Klar, direkt, kein Fülltext.]
BILD: [Was visuell zu sehen ist — konkrete Regieanweisung: Selfie, B-Roll, Screenshot, Textkarte etc.]
{"KÄUFERTYP: [Welchen der 6 Käufertypen spricht diese Slide an?]" if ist_verkauf else "VERBINDUNGS-ELEMENT: [Was erzeugt hier Nähe, Empathie oder Wiedererkennung?]"}
HINWEIS: [Praktischer Umsetzungstipp: Schriftfarbe, Sticker, Interaktions-Element, etc. — nur wenn sinnvoll, sonst weglassen.]

---SLIDE [Nummer]: ...---
...

━━━ NACH DER SEQUENZ ━━━

## DEIN STORY-COACH
Analysiere die Sequenz in 3 Sätzen:
- Welche Story-Struktur wurde verwendet und warum?
{"- Welche Käufertypen werden angesprochen und an welcher Stelle?" if ist_verkauf else "- Wo entsteht die stärkste emotionale Verbindung?"}
- Was ist der eine Killer-Fehler, den 80% bei diesem Story-Format machen?

## DEIN STÄRKSTER OPENER
Welche Slide 1 (HOOK) hat das höchste "Bleib-dran-Potenzial" — und warum genau?
"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        result = ""
        placeholder = st.empty()
        for text in stream.text_stream:
            result += text
            # Live-Preview der ersten 300 Zeichen
            preview = result[:300] + ("..." if len(result) > 300 else "")
            placeholder.markdown(f"<div style='font-size:0.82rem;color:#666;font-style:italic;'>{preview}</div>",
                                   unsafe_allow_html=True)
        placeholder.empty()
    return result


def parse_slides(raw):
    """Parsed die Slides aus dem LLM-Output."""
    slides = []
    pattern = r"---SLIDE (\d+): ([^\-]+)---\n(.*?)(?=---SLIDE |\Z)"
    matches = re.findall(pattern, raw, re.DOTALL)
    for num, titel, inhalt in matches:
        felder = {}
        felder["nummer"] = num.strip()
        felder["titel"] = titel.strip()
        for feld in ["TEXT", "BILD", "KÄUFERTYP", "VERBINDUNGS-ELEMENT", "HINWEIS"]:
            m = re.search(rf"{feld}: (.*?)(?=(?:TEXT|BILD|KÄUFERTYP|VERBINDUNGS-ELEMENT|HINWEIS): |\Z)", inhalt, re.DOTALL)
            if m:
                felder[feld.lower().replace("-", "_").replace("ä", "ae")] = m.group(1).strip()
    slides.append(felder)
    return slides


def extrahiere_coaches_block(raw):
    """Extrahiert den Coach-Block nach der Sequenz."""
    m = re.search(r"##\s*DEIN STORY-COACH(.*?)(?:##\s*DEIN STÄRKSTER OPENER|\Z)", raw, re.DOTALL)
    coach = m.group(1).strip() if m else ""
    m2 = re.search(r"##\s*DEIN STÄRKSTER OPENER(.*?)$", raw, re.DOTALL)
    opener = m2.group(1).strip() if m2 else ""
    return coach, opener


# ─── Page Setup ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Story-Generator | Karla Brenscheidt",
    page_icon="📱",
    layout="centered"
)

# ─── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #FAF0D4 !important; }
    .main  { background: transparent !important; }

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

    .header-box {
        background: #FF08C0;
        padding: 2.5rem 2rem 3.8rem 2rem;
        text-align: center;
        margin: 0 -2rem 2rem -2rem;
        position: relative;
        overflow: hidden;
        border-radius: 28px 28px 0 0;
    }
    .header-box::before {
        content: '';
        position: absolute;
        bottom: -1px; left: 0; right: 0;
        height: 40px;
        background: white;
        border-radius: 50% 50% 0 0 / 40px 40px 0 0;
        z-index: 2;
    }
    .header-box::after {
        content: '📱';
        position: absolute;
        font-size: 10rem;
        bottom: -20px; right: 0px;
        line-height: 1;
        pointer-events: none;
        z-index: 1;
        opacity: 0.12;
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

    /* Slide-Karten */
    .slide-card {
        background: white;
        border-radius: 20px;
        padding: 0;
        margin: 1rem 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
        overflow: hidden;
        border: 1px solid rgba(255,8,192,0.08);
    }
    .slide-header {
        background: #FF08C0;
        padding: 0.65rem 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .slide-number {
        background: rgba(255,255,255,0.25);
        color: white;
        border-radius: 50%;
        width: 28px; height: 28px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.72rem; font-weight: 900;
        flex-shrink: 0;
    }
    .slide-title {
        color: white;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }
    .slide-body {
        padding: 1.2rem 1.4rem 1rem 1.4rem;
    }
    .slide-field-label {
        font-size: 0.6rem;
        font-weight: 800;
        color: #FF08C0;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
        margin-top: 0.75rem;
    }
    .slide-field-text {
        font-size: 0.92rem;
        color: #1a1a1a;
        line-height: 1.6;
        font-weight: 500;
    }
    .slide-field-text.is-text {
        font-size: 1.0rem;
        font-weight: 700;
        background: rgba(255,8,192,0.04);
        border-left: 3px solid #FF08C0;
        padding: 0.6rem 0.9rem;
        border-radius: 0 10px 10px 0;
    }
    .slide-field-meta {
        font-size: 0.8rem;
        color: #666;
        font-style: italic;
        line-height: 1.55;
    }
    .slide-badge {
        display: inline-block;
        background: rgba(255,8,192,0.08);
        color: #CC0099;
        border-radius: 50px;
        padding: 0.15rem 0.65rem;
        font-size: 0.62rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }

    /* Coach-Block */
    .coach-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        padding: 1.5rem 1.75rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255,8,192,0.3);
        color: white;
    }
    .coach-label {
        font-size: 0.6rem;
        font-weight: 800;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #FF08C0;
        margin-bottom: 0.6rem;
    }
    .coach-text {
        font-size: 0.9rem;
        line-height: 1.65;
        color: rgba(255,255,255,0.88);
    }

    /* Themen-Buttons */
    .stButton > button {
        background: #FF08C0 !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.85rem 2rem !important;
        font-size: 0.88rem !important;
        font-weight: 800 !important;
        width: 100% !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        box-shadow: 0 6px 28px rgba(255,8,192,0.35) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #CC0099 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 36px rgba(255,8,192,0.5) !important;
    }

    /* Inputs */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        border: 2px solid rgba(255,8,192,0.15) !important;
        border-radius: 12px !important;
        background: white !important;
        color: #1a1a1a !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #FF08C0 !important;
        box-shadow: 0 0 0 3px rgba(255,8,192,0.1) !important;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stRadio"] label {
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
    div[data-testid="stRadio"] > div {
        gap: 0.5rem !important;
    }

    /* Radio als Karten */
    div[data-testid="stRadio"] > div > label {
        background: white !important;
        border: 2px solid rgba(255,8,192,0.15) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.2rem !important;
        cursor: pointer !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #1a1a1a !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        transition: all 0.15s ease !important;
        margin-bottom: 0.4rem !important;
    }
    div[data-testid="stRadio"] > div > label:has(input:checked) {
        border-color: #FF08C0 !important;
        background: rgba(255,8,192,0.04) !important;
    }

    /* Typography */
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
    hr { border-color: rgba(0,0,0,0.07) !important; }

    .karla-badge {
        text-align: center;
        font-size: 0.75rem;
        color: rgba(0,0,0,0.4);
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(0,0,0,0.08);
        letter-spacing: 0.05em;
    }

    .themen-btn-wrapper .stButton > button {
        background: white !important;
        color: #333 !important;
        border: 2px solid rgba(255,8,192,0.18) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        padding: 0.7rem 1.2rem !important;
        box-shadow: none !important;
        border-radius: 12px !important;
        text-align: left !important;
        white-space: normal !important;
        height: auto !important;
        line-height: 1.4 !important;
    }
    .themen-btn-wrapper .stButton > button:hover {
        border-color: #FF08C0 !important;
        color: #FF08C0 !important;
        background: rgba(255,8,192,0.03) !important;
        transform: none !important;
        box-shadow: none !important;
    }
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
        <div style="font-size:2.8rem;font-weight:900;color:white;line-height:0.92;
                    letter-spacing:-0.02em;text-transform:uppercase;margin:0.5rem 0 0.25rem;">
          Instagram<br>Story-Generator
        </div>
        <div style="font-size:0.76rem;color:rgba(255,255,255,0.65);letter-spacing:0.1em;
                    text-transform:uppercase;margin-bottom:1.1rem;">by Karla Brenscheidt</div>
        <div style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;">
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                       color:white;border-radius:50px;padding:0.22rem 0.8rem;
                       font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Komplette Slide-Sequenz</span>
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                       color:white;border-radius:50px;padding:0.22rem 0.8rem;
                       font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Verkaufen + Community</span>
          <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                       color:white;border-radius:50px;padding:0.22rem 0.8rem;
                       font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Themen-Ideen</span>
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
            st.error("Falscher Code. Schreib mir auf Instagram @karla.brenscheidt 👋")

    st.markdown("""
<div style="background:white;border:2px solid rgba(255,8,192,0.12);border-radius:16px;
            padding:1.4rem 1.6rem;margin:1.2rem 0;">
    <div style="font-size:0.7rem;font-weight:800;color:#FF08C0;letter-spacing:0.18em;
                text-transform:uppercase;margin-bottom:0.9rem;">Was du bekommst</div>
    <div style="display:flex;flex-direction:column;gap:0.6rem;">
        <div style="font-size:0.88rem;color:#333;">✓ &nbsp;Komplette Story-Sequenz — sofort postbar</div>
        <div style="font-size:0.88rem;color:#333;">✓ &nbsp;Slide für Slide: Text, Bild-Anweisung, Umsetzungstipp</div>
        <div style="font-size:0.88rem;color:#333;">✓ &nbsp;Stories die verkaufen + Community-Bindungs-Stories</div>
        <div style="font-size:0.88rem;color:#333;">✓ &nbsp;6 Käufertypen — alle angesprochen, kein potenzieller Käufer verloren</div>
        <div style="font-size:0.88rem;color:#333;">✓ &nbsp;"Keine Idee?" — KI generiert 6 Story-Themen für deine Nische</div>
        <div style="font-size:0.88rem;color:#333;">✓ &nbsp;Dein Story-Coach: Analyse, Killer-Fehler, stärkster Opener</div>
    </div>
</div>
<div style="text-align:center;font-size:0.82rem;color:rgba(0,0,0,0.45);margin-top:0.9rem;line-height:1.7;">
    Noch kein Zugang? <strong>9 €</strong> &nbsp;·&nbsp; Bundle mit Hook + Bio-Generator: <strong>17 €</strong><br>
    <a href="https://www.instagram.com/karla.brenscheidt" target="_blank"
       style="color:#FF08C0;font-weight:800;text-decoration:none;">
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
    <div style="font-size:2.8rem;font-weight:900;color:white;line-height:0.92;
                letter-spacing:-0.02em;text-transform:uppercase;margin:0.5rem 0 0.25rem;">
      Instagram<br>Story-Generator
    </div>
    <div style="font-size:0.76rem;color:rgba(255,255,255,0.65);letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:1.1rem;">by Karla Brenscheidt</div>
    <div style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;">
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Komplette Slide-Sequenz</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Verkaufen + Community</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Käufertypen-Strategie</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────
for key in ["thema_input", "story_themen", "story_result", "story_typ", "story_format"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key not in ["story_themen"] else []


# ─── Step 1: Story-Typ wählen ─────────────────────────────────────
st.markdown("### 1. Was soll deine Story erreichen?")

story_typ_label = st.radio(
    "Story-Ziel",
    options=list(STORY_TYPEN.keys()),
    index=0,
    horizontal=False,
    label_visibility="collapsed"
)
story_typ = STORY_TYPEN[story_typ_label]

if story_typ == "verkaufen":
    st.markdown("""
    <div style="background:rgba(255,8,192,0.04);border:1.5px solid rgba(255,8,192,0.15);
                border-radius:12px;padding:0.8rem 1.1rem;font-size:0.85rem;color:#333;margin-top:0.5rem;">
        📣 Deine Follower gehen rein, fühlen sich verstanden und wollen am Ende kaufen. Alle 6 Käufertypen abgeholt. Kein Zufall. Das ist mein System.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:rgba(255,8,192,0.04);border:1.5px solid rgba(255,8,192,0.15);
                border-radius:12px;padding:0.8rem 1.1rem;font-size:0.85rem;color:#333;margin-top:0.5rem;">
        ❤️ Die Story baut Vertrauen, Nähe und Verbindung auf. Kein direktes Verkaufen — aber genau das, was
        später zum Kauf führt. Know → Like → Trust.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── Step 2: Story-Format ─────────────────────────────────────────
st.markdown("### 2. Story-Format wählen")

story_format = st.selectbox(
    "Format",
    STORY_FORMATE,
    label_visibility="collapsed"
)

st.markdown("---")

# ─── Step 3: Dein Kontext ─────────────────────────────────────────
st.markdown("### 3. Dein Kontext")

col1, col2 = st.columns(2)
with col1:
    zielgruppe = st.text_input(
        "Deine Zielgruppe",
        placeholder="z.B. Frauen 30–45, die ein Online-Business aufbauen wollen"
    )
    nische = st.text_input(
        "Deine Nische",
        placeholder="z.B. KI / Claude Code für Instagram-Starter"
    )

with col2:
    if story_typ == "verkaufen":
        produkt = st.text_input(
            "Dein Produkt / Angebot",
            placeholder="z.B. Mini-Kurs 'Hook-Generator in 3 Minuten'"
        )
        transformation = st.text_input(
            "Die Transformation (vorher → nachher)",
            placeholder="z.B. Von 'Keine Ahnung was posten' zu 5 fertigen Hooks in 10 Min."
        )
    else:
        produkt = ""
        transformation = ""

social_proof = st.text_area(
    "✨ Echte Ergebnisse / Social Proof (optional — macht deine Story 10x stärker)",
    placeholder="z.B. 3 Kundinnen in einer Woche. Mein letzter Reel: 44.000 Views bei 220 Followern.",
    height=70
)

st.markdown("---")

# ─── Step 4: Story-Thema ─────────────────────────────────────────
st.markdown("### 4. Dein Story-Thema")

st.markdown("""
<div style="background:rgba(255,8,192,0.04);border:1.5px solid rgba(255,8,192,0.12);
            border-radius:12px;padding:0.8rem 1.1rem;font-size:0.85rem;color:#555;margin-bottom:1rem;">
    💡 <strong>Keine Idee was du posten sollst?</strong> Klick auf den Button — Claude generiert 6 Themen für deine Nische.
    Oder gib dein eigenes Thema ein.
</div>
""", unsafe_allow_html=True)

thema = st.text_input(
    "Dein Story-Thema",
    value=st.session_state["thema_input"],
    placeholder="z.B. Wie ich heute Morgen um 7 Uhr mit Claude meinen Content für die Woche fertig hatte",
    key="thema_widget"
)

# Themen-Generator
if zielgruppe or nische:
    if st.button("💡 6 Story-Themen generieren — keine Ideen nötig"):
        api_key = load_api_key()
        if api_key:
            with st.spinner("Themen werden generiert..."):
                n = nische or "Online-Business auf Instagram"
                z = zielgruppe or "Frauen 30–45, die ein Online-Business aufbauen wollen"
                st.session_state["story_themen"] = generiere_themen_ideen(api_key, n, z, story_typ)
            st.rerun()
        else:
            st.error("API-Key nicht gefunden. Bitte .env prüfen.")

if st.session_state["story_themen"]:
    st.markdown("**Klick auf ein Thema — es wird übernommen:**")
    st.markdown('<div class="themen-btn-wrapper">', unsafe_allow_html=True)
    for idee in st.session_state["story_themen"]:
        if st.button(f"📌  {idee}", key=f"idee_{idee[:40]}", use_container_width=True):
            st.session_state["thema_input"] = idee
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")


# ─── Generieren ──────────────────────────────────────────────────
if st.button("📱 Story-Sequenz generieren", use_container_width=True):
    thema_final = st.session_state.get("thema_input") or thema
    if not thema_final:
        st.warning("Bitte gib ein Story-Thema ein oder generiere eines mit dem Button oben.")
    elif not zielgruppe:
        st.warning("Bitte gib deine Zielgruppe ein.")
    else:
        api_key = load_api_key()
        if not api_key:
            st.error("API-Key nicht gefunden.")
            st.stop()

        with st.spinner(f"Claude Opus 4.8 schreibt deine Story-Sequenz... (~30 Sek.)"):
            result = generiere_story_sequenz(
                api_key=api_key,
                story_typ=story_typ,
                story_format=story_format,
                thema=thema_final,
                zielgruppe=zielgruppe,
                nische=nische,
                produkt=produkt,
                transformation=transformation,
                social_proof=social_proof,
            )
            st.session_state["story_result"] = result
            st.session_state["story_typ_last"] = story_typ

        st.rerun()


# ─── Ergebnis anzeigen ────────────────────────────────────────────
if st.session_state.get("story_result"):
    raw = st.session_state["story_result"]
    ist_verkauf = st.session_state.get("story_typ_last", "verkaufen") == "verkaufen"

    st.success("Deine Story-Sequenz ist fertig! 📱")
    st.caption("Jede Slide zeigt dir: Was du schreibst, was du zeigst, und wie du es umsetzt.")

    # ── Coach & Opener Blocks ─────────────────────────────────────
    coach_text, opener_text = extrahiere_coaches_block(raw)

    if opener_text:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
                    border:2px solid #FFD700; border-radius:18px;
                    padding:1.4rem 1.6rem; margin:0 0 1.5rem 0;
                    box-shadow:0 8px 30px rgba(255,215,0,0.18);">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
                <span style="font-size:1.1rem;">🏆</span>
                <span style="font-size:0.6rem;font-weight:800;letter-spacing:0.22em;
                             text-transform:uppercase;color:#FFD700;">Dein stärkster Opener</span>
            </div>
            <div style="font-size:0.95rem;line-height:1.55;color:white;font-weight:500;">
                {opener_text.replace(chr(10), "<br>")}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Slides parsen und anzeigen ────────────────────────────────
    slide_farben = [
        "#FF08C0", "#CC0099", "#FF08C0", "#CC0099", "#FF08C0",
        "#CC0099", "#FF08C0", "#CC0099", "#FF08C0", "#CC0099",
    ]
    slide_icons = ["🎬", "💬", "🔥", "💡", "🎯", "❤️", "🌟", "⚡", "📣", "✅"]

    # Slides aus dem Raw-Text extrahieren
    slide_blocks = re.split(r"---SLIDE \d+:", raw)
    slide_blocks = [b for b in slide_blocks if b.strip() and not b.strip().startswith("##")]

    all_slides_text = ""

    for idx, block in enumerate(slide_blocks):
        header_match = re.match(r"\s*([A-ZÄÜÖ\- /]+)\s*---\n?(.*)", block, re.DOTALL)
        if not header_match:
            header_match2 = re.match(r"\s*([^\n]+)\n(.*)", block, re.DOTALL)
            if not header_match2:
                continue
            slide_titel = header_match2.group(1).strip().rstrip("-").strip()
            rest = header_match2.group(2)
        else:
            slide_titel = header_match.group(1).strip()
            rest = header_match.group(2)

        nummer = idx + 1
        farbe = slide_farben[idx % len(slide_farben)]
        icon = slide_icons[idx % len(slide_icons)]

        def get_feld(key, text):
            m = re.search(rf"{key}: (.*?)(?=(?:TEXT|BILD|KÄUFERTYP|VERBINDUNGS-ELEMENT|HINWEIS): |\Z)",
                          text, re.DOTALL | re.IGNORECASE)
            return m.group(1).strip() if m else ""

        text_val  = get_feld("TEXT", rest)
        bild_val  = get_feld("BILD", rest)
        kaeufer   = get_feld("KÄUFERTYP", rest)
        verbindung = get_feld("VERBINDUNGS-ELEMENT", rest)
        hinweis   = get_feld("HINWEIS", rest)

        if not text_val and not bild_val:
            continue

        # Für Copy-Block sammeln
        all_slides_text += f"📱 SLIDE {nummer}: {slide_titel}\n"
        if text_val:
            all_slides_text += f"TEXT: {text_val}\n"
        if bild_val:
            all_slides_text += f"BILD: {bild_val}\n"
        if hinweis:
            all_slides_text += f"TIPP: {hinweis}\n"
        all_slides_text += "\n"

        # Slide rendern
        st.markdown(f"""
        <div class="slide-card">
            <div class="slide-header" style="background:{farbe};">
                <div class="slide-number">{nummer}</div>
                <div class="slide-title">{icon} {slide_titel}</div>
            </div>
            <div class="slide-body">
                <div class="slide-field-label">📝 Was du schreibst</div>
                <div class="slide-field-text is-text">{text_val}</div>
                {"<div class='slide-field-label'>📸 Was du zeigst</div><div class='slide-field-meta'>" + bild_val + "</div>" if bild_val else ""}
                {"<div class='slide-badge'>🎯 " + kaeufer + "</div>" if kaeufer and ist_verkauf else ""}
                {"<div class='slide-badge'>❤️ " + verbindung + "</div>" if verbindung and not ist_verkauf else ""}
                {"<div class='slide-field-label'>💡 Umsetzungstipp</div><div class='slide-field-meta'>" + hinweis + "</div>" if hinweis else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Coach-Block ───────────────────────────────────────────────
    if coach_text:
        st.markdown(f"""
        <div class="coach-box">
            <div class="coach-label">🧠 Dein Story-Coach</div>
            <div class="coach-text">{coach_text.replace(chr(10), "<br>")}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Copy-Block ────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📋 Alle Slides kopieren — für deine Notizen"):
        st.caption("Kopiere den Text und speichere ihn in deinen Notizen oder Canva.")
        st.code(all_slides_text.strip(), language=None)

    # ── Nochmal generieren ────────────────────────────────────────
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Neue Variante — gleiches Thema", use_container_width=True):
            st.session_state["story_result"] = ""
            st.rerun()
    with col_b:
        if st.button("✨ Anderes Thema", use_container_width=True):
            st.session_state["story_result"] = ""
            st.session_state["thema_input"] = ""
            st.rerun()

    # ── Upsell ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FF08C0 0%, #CC0099 100%);
                border-radius: 20px; padding: 2rem 2rem 1.75rem 2rem;
                text-align: center; box-shadow: 0 12px 40px rgba(255,8,192,0.35);">
        <div style="display:inline-block; background:rgba(255,255,255,0.2);
                    border:1.5px solid rgba(255,255,255,0.4); color:white;
                    border-radius:50px; padding:0.2rem 0.9rem;
                    font-size:0.6rem; font-weight:800; letter-spacing:0.2em;
                    text-transform:uppercase; margin-bottom:1rem;">
            ✦ Der nächste Schritt
        </div>
        <div style="font-size:1.5rem; font-weight:900; color:white;
                    line-height:1.1; letter-spacing:-0.02em; margin-bottom:0.75rem;">
            Deine Stories stehen.<br>Jetzt fehlen die Hooks und der Content.
        </div>
        <div style="font-size:0.9rem; color:rgba(255,255,255,0.88);
                    line-height:1.6; margin-bottom:1.5rem; max-width:480px; margin-left:auto; margin-right:auto;">
            Im Kurs <strong style="color:white;">Content-Flow mit Claude</strong> baust du eine ganze Woche
            Content — Reels, Stories, Karussells — in einer einzigen Session.
        </div>
        <a href="{KURS_URL}" target="_blank" style="
            display:inline-block; background:white; color:#FF08C0;
            border-radius:50px; padding:0.85rem 2.2rem; font-size:0.9rem;
            font-weight:900; text-decoration:none; letter-spacing:0.08em;
            text-transform:uppercase; box-shadow:0 6px 24px rgba(0,0,0,0.2);">
            Content-Flow mit Claude · 27 € →
        </a>
        <div style="font-size:0.7rem; color:rgba(255,255,255,0.55); margin-top:1rem;">
            @karla.brenscheidt
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ─── Footer ──────────────────────────────────────────────────────
st.markdown("""
<div class="karla-badge">
    Gemacht mit ❤️ von <strong>Karla Brenscheidt</strong> | @karla.brenscheidt<br>
    <small>Ich zeige dir, wie du mit Claude Code in 3–5 Minuten Tools, Reels und KI-Systeme baust. Ohne Technik-Frust.</small>
    <br><small style="color:rgba(0,0,0,0.3);font-style:italic;">Powered by Claude Opus 4.8 — das stärkste Modell von Anthropic.</small>
</div>
""", unsafe_allow_html=True)
