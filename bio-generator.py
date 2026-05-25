import streamlit as st
import anthropic
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
    page_title="Bio-Generator | Karla Brenscheidt",
    page_icon="✨",
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

    /* ── RESULT CARDS ── */
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

    st.markdown("### Bitte gib deinen Zugangscode ein")
    code = st.text_input("Zugangscode", type="password", placeholder="Dein Code aus der DM")

    if st.button("Zugang freischalten"):
        if code.strip().upper() == ACCESS_CODE:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Falscher Code. Hast du den Bio-Generator bereits gekauft? Schreib mir auf Instagram @karla.brenscheidt 👋")

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
st.caption("Je mehr du einträgst, desto besser wird deine Bio. Füll alle Felder aus.")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Dein Name", placeholder="z.B. Sarah")
    nische = st.text_input("Deine Nische / Was du machst", placeholder="z.B. Ernährungsberatung für Mütter")
    zielgruppe = st.text_input("Deine Zielgruppe", placeholder="z.B. Mütter nach der Geburt, die abnehmen wollen")

with col2:
    ergebnis = st.text_input("Welches Ergebnis lieferst du?", placeholder="z.B. 5kg in 8 Wochen ohne Diät")
    angebot = st.text_input("Dein Produkt / Angebot (optional)", placeholder="z.B. 8-Wochen-Programm, kostenloses Erstgespräch")
    persoenlich = st.text_input("Ein persönlicher Fakt über dich", placeholder="z.B. Mama von 2 Kids, lebe in München")

cta_link = st.text_input("Dein Link-in-Bio (optional)", placeholder="z.B. karla.de/starten")

social_proof = st.text_area(
    "✨ Deine echten Ergebnisse / Social Proof (optional — aber macht deine Bio 10x stärker)",
    placeholder="z.B. 44.000 Views bei 220 Followern. 3 Kundinnen in einer Woche. In 10 Minuten meinen ersten KI-Agenten gebaut.",
    height=80
)

st.markdown("---")

if st.button("🪄 Bio jetzt generieren"):
    if not nische or not zielgruppe or not ergebnis:
        st.warning("Bitte füll mindestens Nische, Zielgruppe und Ergebnis aus.")
    else:
        api_key = load_api_key()
        if not api_key:
            st.error("API-Key nicht gefunden.")
            st.stop()

        with st.spinner("Deine Bio wird geschrieben..."):
            client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""Du bist Instagram-Profil-Expertin und erstellst komplette Profil-Pakete auf Deutsch. Aktuelles Jahr: 2026. NIEMALS das Wort "Freebie" oder "Freebies" verwenden — immer "0€-Produkt" oder "Gratis-Tool".

KONTEXT:
Name: {name or 'nicht angegeben'}
Nische: {nische}
Zielgruppe: {zielgruppe}
Ergebnis / Transformation: {ergebnis}
Produkt/Angebot: {angebot or 'noch kein konkretes Angebot'}
Persönliches: {persoenlich or 'nicht angegeben'}
Link: {cta_link or 'nicht angegeben'}
Echte Ergebnisse / Social Proof: {social_proof if social_proof else 'nicht angegeben — verwende bei Zahlen Platzhalter in eckigen Klammern wie [DEINE ZAHL]'}

WICHTIG bei Zahlen: Wenn echte Ergebnisse angegeben sind, verwende GENAU diese Zahlen. Wenn nicht, setze Platzhalter in eckigen Klammern ein die der User selbst ausfüllen kann.

━━━ TEIL 1: 3 BIO-VARIANTEN ━━━

Regeln für alle 3 Bios:
- Maximal 150 Zeichen (Instagram-Limit)
- Erste Zeile: WER sie ist und FÜR WEN (sofort klar)
- Zweite Zeile: Konkretes ERGEBNIS oder TRANSFORMATION (mit Zahl wenn möglich)
- Dritte Zeile: CTA oder persönlicher Touch
- Kein Bullshit, keine Floskeln wie "leidenschaftlich" oder "helfe dir dabei"
- Direkt, spezifisch, konversionsstark

VARIANTE 1 — ERGEBNIS-FOKUS
[Bio Text]
Zeichenanzahl: [X]

VARIANTE 2 — ZIELGRUPPEN-FOKUS
[Bio Text]
Zeichenanzahl: [X]

VARIANTE 3 — PERSÖNLICHKEITS-FOKUS
[Bio Text]
Zeichenanzahl: [X]

MEIN TIPP FÜR DICH:
[1-2 Sätze welche Variante am stärksten ist und warum]

━━━ TEIL 2: PROFILNAME-VORSCHLÄGE ━━━

3 Vorschläge für den Profilnamen (die Zeile direkt über der Bio). Maximal 30 Zeichen. Format: "Name | Kernaussage in 3-4 Wörtern". Klar, sofort verständlich, positionierend.

PROFILNAME 1: [Text]
PROFILNAME 2: [Text]
PROFILNAME 3: [Text]

━━━ TEIL 3: HIGHLIGHT-TITEL ━━━

5 Highlight-Titel passend zur Nische. Maximal 15 Zeichen pro Titel (Instagram-Limit). Kurz, neugierig machend, klar was drin ist.

HIGHLIGHT 1: [Titel]
HIGHLIGHT 2: [Titel]
HIGHLIGHT 3: [Titel]
HIGHLIGHT 4: [Titel]
HIGHLIGHT 5: [Titel]"""

            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text

        st.success("Deine 3 Bio-Varianten sind fertig! 🎉")

        # Varianten parsen und einzeln anzeigen
        import re

        icons  = ["🎯", "👥", "✨"]
        keys   = ["ERGEBNIS-FOKUS", "ZIELGRUPPEN-FOKUS", "PERSÖNLICHKEITS-FOKUS"]
        titles = ["Ergebnis-Fokus", "Zielgruppen-Fokus", "Persönlichkeits-Fokus"]
        card_colors = ["#FF08C0", "#CC0099", "#FF08C0"]

        def clean_text(text):
            text = re.sub(r'```[^\n]*\n?(.*?)```', r'\1', text, flags=re.DOTALL)  # Inhalt aus Code-Blöcken extrahieren
            text = re.sub(r'`', '', text)                           # Einzelne Backticks
            text = re.sub(r'^\*+\s*', '', text)                     # Führende Sternchen
            text = re.sub(r'\s*\*+$', '', text)                     # Nachfolgende Sternchen
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)          # **fett** → normal
            text = re.sub(r'\*([^*]+)\*', r'\1', text)              # *kursiv* → normal
            text = re.sub(r'^\*{2,}\s*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'\n---+\n?', '', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()

        for i, key in enumerate(keys):
            # Stop vor dem nächsten VARIANTE-Header (auch mit ** davor) oder MEIN TIPP
            pattern = rf'{re.escape(key)}\s*(.*?)(?=\*{{0,2}}(?:VARIANTE|ERGEBNIS-FOKUS|ZIELGRUPPEN-FOKUS|PERSÖNLICHKEITS-FOKUS|MEIN TIPP)|━|$)'
            match = re.search(pattern, result, re.DOTALL)
            if not match:
                continue

            bio_text = match.group(1).strip()
            # Zeichenanzahl extrahieren (vor dem Bereinigen)
            zeichen = re.search(r'\*?\*?Zeichenanzahl:\*?\*?\s*(\d+)', bio_text)
            zeichen_str = f"  ·  {zeichen.group(1)} Zeichen" if zeichen else ""
            # Bereinigen
            bio_clean = re.sub(r'\*?\*?Zeichenanzahl:\*?\*?\s*\d+', '', bio_text)
            bio_clean = clean_text(bio_clean)

            st.markdown(f"""
            <div class="result-box" style="border-left-color:{card_colors[i]};
                        box-shadow:5px 5px 0 {card_colors[i]}33, 0 2px 12px rgba(0,0,0,0.05);">
                <div class="result-label" style="color:{card_colors[i]};">{icons[i]} Variante {i+1} — {titles[i]}{zeichen_str}</div>
                <div class="result-text">{bio_clean.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            st.code(bio_clean, language=None)

        # Tipp extrahieren
        if "MEIN TIPP" in result:
            tipp_raw = result.split("MEIN TIPP FÜR DICH:")[1]
            tipp = clean_text(tipp_raw.split("━")[0])
            st.info(f"💡 **Mein Tipp:** {tipp}")

        # Profilname-Vorschläge
        if "PROFILNAME 1:" in result:
            st.markdown("---")
            st.markdown("### 👤 Deine Profilname-Vorschläge")
            st.caption("Die Zeile direkt über deiner Bio — der erste Eindruck.")
            for j in range(1, 4):
                match = re.search(rf'PROFILNAME {j}:\s*(.+)', result)
                if match:
                    pname = clean_text(match.group(1))
                    pcolor = card_colors[j-1]
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"""
                        <div class="result-box" style="margin:0.4rem 0; border-left-color:{pcolor};">
                            <div class="result-label" style="color:{pcolor};">Variante {j}</div>
                            <div class="result-text" style="font-weight:600;">{pname}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        st.code(pname, language=None)

        # Highlight-Titel
        if "HIGHLIGHT 1:" in result:
            st.markdown("---")
            st.markdown("### 🔆 Deine 5 Highlight-Titel")
            st.caption("Klick auf deine Highlights → das sind die Namen. Maximal 15 Zeichen.")
            highlight_cols = st.columns(5)
            for j in range(1, 6):
                match = re.search(rf'HIGHLIGHT {j}:\s*(.+)', result)
                if match:
                    htitel = clean_text(match.group(1))
                    with highlight_cols[j-1]:
                        st.markdown(f"""
                        <div style="background:rgba(199,125,255,0.12); border:1px solid rgba(199,125,255,0.35);
                                    border-radius:50px; padding:0.6rem 0.5rem;
                                    text-align:center; font-size:0.82rem; font-weight:700; color:#C77DFF;
                                    letter-spacing:0.04em;">
                            {htitel}
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        **Nächster Schritt:** Teste alle 3 Bio-Varianten — poste eine, warte 2 Wochen, schau was besser performt.
        Oder schreib mir direkt auf Instagram @karla.brenscheidt, ich sag dir welche am stärksten ist. 👋
        """)

st.markdown("""
<div class="karla-badge">
    Gemacht mit ❤️ von <strong>Karla Brenscheidt</strong> | @karla.brenscheidt<br>
    <small>Ich zeige dir, wie du mit Claude Code in 3–5 Minuten Tools, Reels und KI-Systeme baust. Ohne Technik-Frust.</small>
</div>
""", unsafe_allow_html=True)
