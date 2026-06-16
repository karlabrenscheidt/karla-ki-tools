import streamlit as st
import anthropic
import base64
from pathlib import Path

# Konfiguration
API_KEY_FILE = Path("/Users/admin/Desktop/Claude Code Mastery/.env")
PHOTO_FILE   = Path(__file__).parent / "karla-photo-small.jpg"

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
    except:
        return None

# Page Setup
st.set_page_config(
    page_title="Bio-Generator | Karla Brenscheidt",
    page_icon="✨",
    layout="centered"
)

# Custom CSS
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
        bottom: -1px;
        left: 0;
        right: 0;
        height: 40px;
        background: white;
        border-radius: 50% 50% 0 0 / 40px 40px 0 0;
        z-index: 2;
    }
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

    .result-box {
        background: white;
        border-left: 5px solid #FF08C0;
        border-radius: 0 16px 16px 0;
        padding: 1.4rem 1.5rem;
        margin: 0.6rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    }
    .result-label {
        font-size: 0.65rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: #FF08C0;
        margin-bottom: 0.6rem;
    }
    .result-text {
        font-size: 1rem;
        line-height: 1.7;
        color: #1a1a1a;
        font-weight: 500;
    }

    .pitch-box {
        background: #C4007A;
        border-radius: 20px;
        padding: 2rem 2.2rem;
        margin: 2rem 0 1rem 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .pitch-box::after {
        content: '✦';
        position: absolute;
        font-size: 12rem;
        color: rgba(255,255,255,0.04);
        bottom: -40px;
        right: -10px;
        line-height: 1;
        pointer-events: none;
    }
    .pitch-eyebrow {
        font-size: 0.62rem;
        font-weight: 800;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.55);
        margin-bottom: 0.6rem;
    }
    .pitch-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: white;
        line-height: 1.15;
        letter-spacing: -0.02em;
        margin-bottom: 0.8rem;
    }
    .pitch-sub {
        font-size: 0.88rem;
        color: rgba(255,255,255,0.72);
        line-height: 1.6;
        margin-bottom: 1.4rem;
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
    }
    .pitch-btn {
        display: inline-block;
        background: white;
        color: #C4007A;
        border-radius: 50px;
        padding: 0.85rem 2.2rem;
        font-size: 0.88rem;
        font-weight: 800;
        text-decoration: none;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        box-shadow: 0 6px 24px rgba(0,0,0,0.2);
        position: relative;
        z-index: 2;
    }

    .karla-badge {
        text-align: center;
        font-size: 0.75rem;
        color: rgba(0,0,0,0.4);
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(0,0,0,0.08);
        letter-spacing: 0.05em;
    }

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
    div[data-testid="stExpander"] summary { color: #1a1a1a !important; }
    div[data-testid="stCode"] {
        background: rgba(255,8,192,0.04) !important;
        border: 1px solid rgba(255,8,192,0.12) !important;
        border-radius: 8px !important;
    }
    hr { border-color: rgba(0,0,0,0.07) !important; }
</style>
""", unsafe_allow_html=True)

# Header
_photo = get_photo_b64()
_img = f'<img src="data:image/jpeg;base64,{_photo}" style="width:92px;height:92px;border-radius:50%;object-fit:cover;object-position:center top;border:3px solid white;box-shadow:0 6px 20px rgba(0,0,0,0.3);">' if _photo else ""
st.markdown(f"""
<div class="header-box">
  <div style="position:relative;z-index:3;text-align:center;">
    <div style="margin-bottom:0.75rem;">{_img}</div>
    <div class="header-pill">✦ 0€ Tool</div>
    <div style="font-size:3rem;font-weight:900;color:white;line-height:0.92;
                letter-spacing:-0.02em;text-transform:uppercase;margin:0.5rem 0 0.25rem;">
      Instagram<br>Bio-Generator
    </div>
    <div style="font-size:0.76rem;color:rgba(255,255,255,0.65);letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:1.1rem;">by Karla Brenscheidt</div>
    <div style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;">
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ 3 Bio-Varianten</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Profilnamen</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Highlight-Titel</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Erzähl mir von dir")
st.caption("Pflicht sind nur Nische, Zielgruppe und Ergebnis. Der Rest macht deine Bio noch stärker. Deine Angaben werden nicht gespeichert.")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Dein Name", placeholder="z.B. Sarah")
    nische = st.text_input("Deine Nische / Was du machst", placeholder="z.B. Ernährungsberatung für Mütter")
    zielgruppe = st.text_input("Deine Zielgruppe", placeholder="z.B. Mütter nach der Geburt, die abnehmen wollen")

with col2:
    ergebnis = st.text_input("Welches Ergebnis lieferst du?", placeholder="z.B. 5kg in 8 Wochen ohne Diät")
    angebot = st.text_input("Dein Produkt / Angebot (optional)", placeholder="z.B. 8-Wochen-Programm, kostenloses Erstgespräch")
    persoenlich = st.text_input("Ein persönlicher Fakt über dich", placeholder="z.B. Mama von 2 Kids, lebe in München")

ton = st.selectbox(
    "Wie soll deine Bio klingen?",
    ["Direkt und ehrlich", "Warm und persönlich", "Frech und selbstbewusst", "Sachlich und professionell"],
)

cta_link = st.text_input("Dein Link-in-Bio (optional)", placeholder="z.B. karla.de/starten")

social_proof = st.text_area(
    "Deine echten Ergebnisse / Social Proof (optional, aber macht deine Bio 10x stärker)",
    placeholder="z.B. 44.000 Views bei 220 Followern. 3 Kundinnen in einer Woche. In 10 Minuten meinen ersten KI-Agenten gebaut.",
    height=80
)

st.markdown("---")

if st.button("Bio jetzt generieren"):
    if not nische or not zielgruppe or not ergebnis:
        st.warning("Bitte füll mindestens Nische, Zielgruppe und Ergebnis aus.")
    else:
        api_key = load_api_key()
        if not api_key:
            st.error("API-Key nicht gefunden.")
            st.stop()

        with st.spinner("Deine Bio wird geschrieben..."):
            client = anthropic.Anthropic(api_key=api_key)

            hat_link = bool(cta_link and cta_link.strip())
            ton_hinweis = {
                "Direkt und ehrlich": "klar, ohne Umschweife, ehrlich auf Augenhöhe, wie ein gutes Gespräch unter Freundinnen",
                "Warm und persönlich": "herzlich, nahbar, einfühlsam, mit echtem Verständnis für die Situation der Zielgruppe",
                "Frech und selbstbewusst": "selbstbewusst, mit einer Prise Humor und Haltung, mutig statt brav",
                "Sachlich und professionell": "kompetent, präzise und vertrauenswürdig, ohne kühl oder distanziert zu wirken",
            }.get(ton, "klar, ehrlich und direkt auf Augenhöhe")
            prompt = f"""Du bist Instagram-Profil-Expertin und erstellst komplette Profil-Pakete auf Deutsch. Aktuelles Jahr: 2026. NIEMALS das Wort "Freebie" oder "Freebies" verwenden, immer "0€-Produkt" oder "Gratis-Tool".

KONTEXT:
Name: {name or 'nicht angegeben'}
Nische: {nische}
Zielgruppe: {zielgruppe}
Ergebnis / Transformation: {ergebnis}
Produkt/Angebot: {angebot or 'noch kein konkretes Angebot'}
Persönliches: {persoenlich or 'nicht angegeben'}
Link: {cta_link if hat_link else 'kein Link angegeben'}
Echte Ergebnisse / Social Proof: {social_proof if social_proof else 'nicht angegeben'}

ZAHLEN-REGEL: Wenn echte Ergebnisse angegeben sind, verwende GENAU diese Zahlen. Wenn KEIN Social Proof angegeben ist, erfinde KEINE Zahlen und setze KEINE Platzhalter in eckigen Klammern. Verwende stattdessen das konkrete Ergebnis aus dem Kontext-Feld ohne Zahlen — z.B. "gesunde Familienküche in 20 Min." statt "[X] Rezepte in [Y] Min."

STRIKTE TON-REGELN — verbotene Phrasen (NIEMALS verwenden):
"Ich zeige dir", "Ich helfe dir", "Ich begleite dich", "Du lernst", "Du entdeckst", "Du wirst", "leidenschaftlich", "authentisch", "auf deiner Reise", "Transformation", "Traumversion", "Ich unterstütze", "helfe dir dabei", "Herzlich Willkommen"
Stattdessen: direkte Aussagen, Fakten, konkrete Ergebnisse, spezifische Zeitangaben.

GEWÜNSCHTE TONALITÄT: {ton} — {ton_hinweis}. Alle drei Bios klingen in diesem Ton, jede aber mit ihrem eigenen Fokus.

CTA-REGEL für die dritte Zeile der Bio:
{'↓ CTA mit KONKRETEM Versprechen was nach dem Klick passiert, z.B. "↓ Kostenlos starten → ' + ergebnis[:30] + '"' if hat_link else 'KEIN CTA — kein Link vorhanden. Dritte Zeile ist ein persönlicher Touch oder eine starke Aussage über die Person oder das Ergebnis. Niemals einen leeren Handlungsaufruf schreiben.'}

FORMAT-REGELN:
- Schreibe den Bio-Text exakt so, wie er in Instagram eingefügt werden soll: jede Zeile auf einer neuen Zeile, kein Markdown, keine Aufzählungszeichen, keine Nummerierungen im Bio-Text selbst.
- Verwende höchstens 1 bis 2 EINFACHE Emojis (z.B. 🎯 🥗 🧡). NIEMALS zusammengesetzte Emojis wie 👩‍🍳, 👨‍👩‍👧 oder Hautton-Varianten — die zählen auf Instagram doppelt und sprengen das Limit.
- Halte jede Bio inklusive Leerzeichen und Zeilenumbrüche unter 140 Zeichen. Das gibt Sicherheitspuffer zum harten Instagram-Limit von 150.

TEIL 1: 3 BIO-VARIANTEN

Regeln für alle 3 Bios:
- Erste Zeile: WER sie ist / ihre Nische — sofort klar ohne Erklärung
- Zweite Zeile: Konkretes ERGEBNIS mit Zeitrahmen oder spezifischem Kontext
- Dritte Zeile: Nach CTA-Regel oben (CTA mit Link ODER persönlicher Abschluss ohne Link)
- Kein Bullshit, keine Floskeln, direkt und spezifisch

VARIANTE 1: ERGEBNIS-FOKUS
[Bio Text — drei Zeilen, exakt kopierbereit]
Zeichenanzahl: [X]

VARIANTE 2: ZIELGRUPPEN-FOKUS
[Bio Text — drei Zeilen, exakt kopierbereit]
Zeichenanzahl: [X]

VARIANTE 3: PERSÖNLICHKEITS-FOKUS
[Bio Text — drei Zeilen, exakt kopierbereit]
Zeichenanzahl: [X]

MEIN TIPP FÜR DICH:
[1-2 Sätze welche Variante am stärksten ist und warum]

TEIL 2: PROFILNAME-VORSCHLÄGE

3 Vorschläge für den Profilnamen (die Zeile direkt über der Bio). Maximal 30 Zeichen. Klar, sofort verständlich, positionierend. Format kann "Name | Kernaussage" sein oder ein starkes Keyword-Set — was besser passt.

PROFILNAME 1: [Text]
PROFILNAME 2: [Text]
PROFILNAME 3: [Text]

TEIL 3: HIGHLIGHT-TITEL

5 Highlight-Titel passend zur Nische. Maximal 15 Zeichen pro Titel (Instagram-Limit). Kurz, neugierig machend, klar was drin ist.

HIGHLIGHT 1: [Titel]
HIGHLIGHT 2: [Titel]
HIGHLIGHT 3: [Titel]
HIGHLIGHT 4: [Titel]
HIGHLIGHT 5: [Titel]"""

            try:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2500,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text
            except Exception:
                st.error("Da ist gerade etwas schiefgelaufen. Warte einen Moment und klick einfach nochmal auf den Button.")
                st.stop()

        st.success("Deine 3 Bio-Varianten sind fertig!")
        st.caption("Klick auf den grauen Kasten unter jeder Bio, um den Text zu kopieren — direkt so in deine Instagram-Bio einfügen.")

        import re

        icons  = ["🎯", "👥", "✨"]
        keys   = ["ERGEBNIS-FOKUS", "ZIELGRUPPEN-FOKUS", "PERSÖNLICHKEITS-FOKUS"]
        titles = ["Ergebnis-Fokus", "Zielgruppen-Fokus", "Persönlichkeits-Fokus"]
        card_colors = ["#FF08C0", "#CC0099", "#FF08C0"]

        def clean_text(text):
            text = re.sub(r'```[^\n]*\n?(.*?)```', r'\1', text, flags=re.DOTALL)
            text = re.sub(r'`', '', text)
            text = re.sub(r'^\*+\s*', '', text)
            text = re.sub(r'\s*\*+$', '', text)
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
            text = re.sub(r'^\*{2,}\s*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'\n---+\n?', '', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()

        bios_gefunden = 0
        for i, key in enumerate(keys):
            pattern = rf'{re.escape(key)}\s*(.*?)(?=\*{{0,2}}(?:VARIANTE|ERGEBNIS-FOKUS|ZIELGRUPPEN-FOKUS|PERSÖNLICHKEITS-FOKUS|MEIN TIPP)|━|$)'
            match = re.search(pattern, result, re.DOTALL)
            if not match:
                continue
            bios_gefunden += 1

            bio_text = match.group(1).strip()
            bio_clean = re.sub(r'\*?\*?Zeichenanzahl:\*?\*?\s*\d+', '', bio_text)
            bio_clean = clean_text(bio_clean)
            # Zeichenzahl selbst zählen, nicht Claude vertrauen (Instagram-Limit: 150)
            real_len = len(bio_clean)
            if real_len <= 150:
                zeichen_str = f"  ·  {real_len} Zeichen"
            else:
                zeichen_str = f"  ·  {real_len} Zeichen · kürze eine Zeile"

            st.markdown(f"""
            <div class="result-box" style="border-left-color:{card_colors[i]};
                        box-shadow:5px 5px 0 {card_colors[i]}33, 0 2px 12px rgba(0,0,0,0.05);">
                <div class="result-label" style="color:{card_colors[i]};">{icons[i]} Variante {i+1}: {titles[i]}{zeichen_str}</div>
                <div class="result-text">{bio_clean.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            st.code(bio_clean, language=None)
            if real_len > 150:
                st.caption("Diese Variante ist etwas über dem Instagram-Limit von 150 Zeichen. Lösch ein paar Wörter aus der längsten Zeile, dann passt sie.")

        if bios_gefunden == 0:
            st.warning("Die Bios kamen in einem ungewohnten Format zurück. Hier ist dein vollständiges Ergebnis zum Kopieren:")
            st.code(clean_text(result), language=None)

        if "MEIN TIPP" in result:
            tipp_raw = result.split("MEIN TIPP FÜR DICH:")[1]
            tipp = clean_text(tipp_raw.split("━")[0].split("TEIL")[0])
            st.info(f"Mein Tipp: {tipp}")

        if "PROFILNAME 1:" in result:
            st.markdown("---")
            st.markdown("### Deine Profilname-Vorschläge")
            st.caption("Die Zeile direkt über deiner Bio, der erste Eindruck.")
            for j in range(1, 4):
                match = re.search(rf'PROFILNAME {j}:\s*(.+)', result)
                if match:
                    pname = clean_text(match.group(1))
                    pname_len = len(pname)
                    pname_hinweis = f"{pname_len}/30" if pname_len <= 30 else f"{pname_len}/30 · zu lang"
                    pcolor = card_colors[j-1]
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"""
                        <div class="result-box" style="margin:0.4rem 0; border-left-color:{pcolor};">
                            <div class="result-label" style="color:{pcolor};">Variante {j}  ·  {pname_hinweis}</div>
                            <div class="result-text" style="font-weight:600;">{pname}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        st.code(pname, language=None)

        if "HIGHLIGHT 1:" in result:
            st.markdown("---")
            st.markdown("### Deine 5 Highlight-Titel")
            st.caption("Klick auf deine Highlights, das sind die Namen. Maximal 15 Zeichen.")
            highlight_cols = st.columns(5)
            highlight_zu_lang = False
            for j in range(1, 6):
                match = re.search(rf'HIGHLIGHT {j}:\s*(.+)', result)
                if match:
                    htitel = clean_text(match.group(1))
                    if len(htitel) > 15:
                        highlight_zu_lang = True
                    with highlight_cols[j-1]:
                        st.markdown(f"""
                        <div style="background:rgba(199,125,255,0.12); border:1px solid rgba(199,125,255,0.35);
                                    border-radius:50px; padding:0.6rem 0.5rem;
                                    text-align:center; font-size:0.82rem; font-weight:700; color:#C77DFF;
                                    letter-spacing:0.04em;">
                            {htitel}
                        </div>
                        """, unsafe_allow_html=True)
            if highlight_zu_lang:
                st.caption("Ein paar Titel sind etwas lang. Instagram zeigt unter dem Highlight nur rund 15 Zeichen, der Rest wird abgeschnitten. Kürz sie bei Bedarf.")

        # Pitch zum Minikurs
        st.markdown(f"""
        <div class="pitch-box">
          <div class="pitch-eyebrow">Nächster Schritt</div>
          <div class="pitch-title"><!-- PITCH-TITEL --></div>
          <div class="pitch-sub">
            <!-- PITCH-TEXT -->
          </div>
          <a href="<!-- LINK -->" target="_blank" class="pitch-btn">
            <!-- BUTTON-TEXT --> →
          </a>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="karla-badge">
    Gemacht mit Liebe von <strong>Karla Brenscheidt</strong> | @karla.brenscheidt<br>
    <small>Ich zeige dir, wie du mit Claude in Minuten Tools, Reels und KI-Systeme baust. Ohne Technik-Frust.</small>
</div>
""", unsafe_allow_html=True)
