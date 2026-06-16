import streamlit as st
import anthropic
import base64
import re
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────
API_KEY_FILE = Path("/Users/admin/Desktop/Claude Code Mastery/.env")
PHOTO_FILE   = Path(__file__).parent / "karla-photo-small.jpg"

SYSTEM_PROMPT = """Du bist Karlas KI-Assistentin für Instagram-Reels. Karla Brenscheidt (@karla.brenscheidt) zeigt Frauen, wie sie mit Claude Code und KI ein Online-Business aufbauen. Aktuelles Jahr: 2026.

Wichtige Regeln:
- Antworte immer auf Deutsch
- Schreibe wie eine echte Person spricht — direkt, lebendig, ohne Corporate-Sprech
- NIEMALS das Wort "Freebie" oder "Freebies" — immer "0€-Produkt" oder "Gratis-Tool"
- Konkret und spezifisch — keine leeren Floskeln
- Instagram-Sprache: kurz, direkt, emotional, auf den Punkt"""

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

def call_claude(prompt: str, max_tokens: int = 1500) -> str:
    api_key = load_api_key()
    if not api_key:
        return "API-Key nicht gefunden."
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text

# ─── Page Setup ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Reel-Skript-Generator | Karla Brenscheidt",
    page_icon="🎬",
    layout="centered",
)

# ─── Session State ───────────────────────────────────────────────
for key, val in {
    "step":         1,
    "nische":       "",
    "zielgruppe":   "",
    "ziel":         "Neue Follower gewinnen",
    "topics":       [],
    "sel_topic":    0,
    "hooks":        [],
    "sel_hook":     0,
    "skript_raw":   "",
    "caption_raw":  "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─── CSS ─────────────────────────────────────────────────────────
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

    /* ── MAGENTA HEADER ── */
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
        content: '🎬';
        position: absolute;
        font-size: 10rem;
        opacity: 0.06;
        bottom: -20px; right: -10px;
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

    /* ── STEP TRACKER ── */
    .step-tracker {
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding: 1.5rem 0 0.5rem;
        margin-bottom: 1.5rem;
        gap: 0;
    }
    .step-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.3rem;
        flex-shrink: 0;
    }
    .step-dot {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 800;
        flex-shrink: 0;
    }
    .step-dot.active  { background: #FF08C0; color: white; box-shadow: 0 0 0 5px rgba(255,8,192,0.15); }
    .step-dot.done    { background: #FF08C0; color: white; }
    .step-dot.inactive{ background: rgba(0,0,0,0.08); color: rgba(0,0,0,0.3); }
    .step-label {
        font-size: 0.52rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        text-align: center;
        white-space: nowrap;
    }
    .step-line {
        flex: 1;
        height: 2px;
        max-width: 50px;
        min-width: 16px;
        margin-top: 17px;
        align-self: flex-start;
    }
    .step-line.done    { background: #FF08C0; }
    .step-line.inactive{ background: rgba(0,0,0,0.1); }

    /* ── BREADCRUMB ── */
    .breadcrumb {
        background: rgba(255,8,192,0.05);
        border: 1px solid rgba(255,8,192,0.15);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 1.5rem;
        font-size: 0.82rem;
        color: #555;
    }
    .breadcrumb strong { color: #FF08C0; }

    /* ── RESULT CARDS ── */
    .result-box {
        background: white;
        border-left: 5px solid #FF08C0;
        border-radius: 0 16px 16px 0;
        padding: 1.2rem 1.4rem;
        margin: 0.6rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .result-label {
        font-size: 0.62rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: #FF08C0;
        margin-bottom: 0.5rem;
    }
    .result-text {
        font-size: 0.97rem;
        line-height: 1.7;
        color: #1a1a1a;
        font-weight: 500;
    }

    /* ── RADIO BUTTONS ── */
    div[data-testid="stRadio"] { gap: 0 !important; }
    div[data-testid="stRadio"] > div { gap: 0.5rem !important; }
    div[data-testid="stRadio"] label {
        background: white !important;
        border: 2px solid rgba(255,8,192,0.12) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        cursor: pointer !important;
        font-size: 0.9rem !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-weight: 500 !important;
        color: #1a1a1a !important;
        width: 100% !important;
        transition: border-color 0.15s !important;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: rgba(255,8,192,0.4) !important;
    }
    div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
        color: #1a1a1a !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }

    /* ── UPSELL BOX ── */
    .upsell-box {
        background: rgba(255,8,192,0.04);
        border: 2px solid rgba(255,8,192,0.2);
        border-radius: 18px;
        padding: 1.6rem;
        text-align: center;
        margin-top: 1.5rem;
    }

    /* ── BUTTON ── */
    .stButton > button {
        background: #FF08C0 !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.85rem 2rem !important;
        font-size: 0.9rem !important;
        font-weight: 800 !important;
        width: 100% !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        box-shadow: 0 6px 28px rgba(255,8,192,0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #CC0099 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 36px rgba(255,8,192,0.45) !important;
    }
    .stButton > button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background: white !important;
        color: #FF08C0 !important;
        border: 2px solid rgba(255,8,192,0.3) !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255,8,192,0.05) !important;
        transform: none !important;
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
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #FF08C0 !important;
        box-shadow: 0 0 0 3px rgba(255,8,192,0.1) !important;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSelectbox"] label {
        color: #FF08C0 !important;
        font-size: 0.72rem !important;
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
    div[data-testid="stCode"] {
        background: rgba(255,8,192,0.03) !important;
        border: 1px solid rgba(255,8,192,0.12) !important;
        border-radius: 8px !important;
    }
    hr { border-color: rgba(0,0,0,0.07) !important; }

    /* ── FOOTER ── */
    .karla-badge {
        text-align: center;
        font-size: 0.75rem;
        color: rgba(0,0,0,0.4);
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(0,0,0,0.08);
        letter-spacing: 0.04em;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────
photo   = get_photo_b64()
img_html = (
    f'<img src="data:image/jpeg;base64,{photo}" '
    'style="width:88px;height:88px;border-radius:50%;object-fit:cover;'
    'object-position:center top;border:3px solid white;box-shadow:0 6px 20px rgba(0,0,0,0.3);">'
    if photo else ""
)

st.markdown(f"""
<div class="header-box">
  <div style="position:relative;z-index:3;text-align:center;">
    <div style="margin-bottom:0.75rem;">{img_html}</div>
    <div class="header-pill">✦ 0€-Produkt</div>
    <div style="font-size:2.9rem;font-weight:900;color:white;line-height:0.9;
                letter-spacing:-0.02em;text-transform:uppercase;margin:0.5rem 0 0.3rem;">
      Reel-Skript<br>Generator
    </div>
    <div style="font-size:0.76rem;color:rgba(255,255,255,0.65);letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:1.1rem;">by Karla Brenscheidt</div>
    <div style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;">
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Reel-Ideen</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ 5 Hooks</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Vollständiges Skript</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.35);
                   color:white;border-radius:50px;padding:0.22rem 0.8rem;
                   font-size:0.62rem;font-weight:700;letter-spacing:0.06em;">✓ Caption + Hashtags</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── Step Tracker ────────────────────────────────────────────────
STEP_NAMES  = ["Deine Basis", "Thema", "Hook", "Skript", "Dein Paket"]
step = st.session_state.step

def render_steps(current: int) -> str:
    parts = []
    for i, name in enumerate(STEP_NAMES, 1):
        if i < current:
            dot_cls, icon = "done",     "✓"
            label_color   = "#FF08C0"
        elif i == current:
            dot_cls, icon = "active",   str(i)
            label_color   = "#FF08C0"
        else:
            dot_cls, icon = "inactive", str(i)
            label_color   = "rgba(0,0,0,0.3)"

        parts.append(
            f'<div class="step-wrap">'
            f'  <div class="step-dot {dot_cls}">{icon}</div>'
            f'  <span class="step-label" style="color:{label_color};">{name}</span>'
            f'</div>'
        )
        if i < len(STEP_NAMES):
            line_cls = "done" if i < current else "inactive"
            parts.append(f'<div class="step-line {line_cls}"></div>')

    return f'<div class="step-tracker">{"".join(parts)}</div>'

st.markdown(render_steps(step), unsafe_allow_html=True)


# ─── Helper: extract section ─────────────────────────────────────
def extract(text: str, label: str) -> str:
    """Extract content after LABEL: up to next ALL-CAPS label or end of string."""
    pattern = rf'{re.escape(label)}:\s*(.+?)(?=\n[A-ZÄÖÜ\-]{{2,}}[0-9\s]*:|$)'
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


# ═══════════════════════════════════════════════════════════════════
# SCHRITT 1 — Deine Basis
# ═══════════════════════════════════════════════════════════════════
if step == 1:
    st.markdown("### Erzähl mir kurz von dir")
    st.caption("3 Angaben — der Rest erledigt Claude für dich.")

    nische      = st.text_input("Deine Nische / Was du machst",
                                value=st.session_state.nische,
                                placeholder="z.B. KI-Tools für Frauen · Ernährungsberatung für Mütter · Online-Yoga")
    zielgruppe  = st.text_input("Deine Zielgruppe",
                                value=st.session_state.zielgruppe,
                                placeholder="z.B. Frauen 30-45, die neben der Familie ein Online-Business aufbauen wollen")
    ziel        = st.selectbox("Was soll dieser Reel erreichen?", [
        "Neue Follower gewinnen",
        "Vertrauen & Authority aufbauen",
        "Produkt vorstellen oder verkaufen",
        "Persönliche Story / Einblick hinter die Kulissen",
        "Kommentare und Engagement generieren",
        "Leads — Menschen in die DMs holen",
    ], index=["Neue Follower gewinnen","Vertrauen & Authority aufbauen",
              "Produkt vorstellen oder verkaufen","Persönliche Story / Einblick hinter die Kulissen",
              "Kommentare und Engagement generieren","Leads — Menschen in die DMs holen"
              ].index(st.session_state.ziel) if st.session_state.ziel in [
        "Neue Follower gewinnen","Vertrauen & Authority aufbauen",
        "Produkt vorstellen oder verkaufen","Persönliche Story / Einblick hinter die Kulissen",
        "Kommentare und Engagement generieren","Leads — Menschen in die DMs holen"] else 0)

    st.markdown("")

    if st.button("🎬 Reel-Ideen generieren →"):
        if not nische.strip() or not zielgruppe.strip():
            st.warning("Bitte gib mindestens deine Nische und Zielgruppe ein.")
        else:
            st.session_state.nische     = nische.strip()
            st.session_state.zielgruppe = zielgruppe.strip()
            st.session_state.ziel       = ziel

            with st.spinner("Claude denkt sich 5 Reel-Ideen aus..."):
                prompt = f"""Erstelle 5 spezifische Reel-Themen für diese Person.
PFLICHT: Perfekte deutsche Rechtschreibung und Zeichensetzung in jedem Satz. Kommafehler, falsche Groß-/Kleinschreibung oder fehlende Satzzeichen sind nicht akzeptabel.
Nische: {nische}
Zielgruppe: {zielgruppe}
Ziel des Reels: {ziel}

Formatiere GENAU so — keine Einleitung, direkt die Liste:
THEMA 1: [Thema]
THEMA 2: [Thema]
THEMA 3: [Thema]
THEMA 4: [Thema]
THEMA 5: [Thema]

Jedes Thema ist konkret und provokant — nicht "Wie du erfolgreicher wirst" sondern spezifisch wie z.B. "Warum deine ersten 100 Instagram-Posts keine Kunden bringen — und was du stattdessen tun musst". Jedes Thema muss sich klar von den anderen unterscheiden."""
                raw    = call_claude(prompt)
                topics = re.findall(r'THEMA \d+:\s*(.+)', raw)
                st.session_state.topics  = topics if topics else [raw.strip()]
                st.session_state.step    = 2
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
# SCHRITT 2 — Thema wählen
# ═══════════════════════════════════════════════════════════════════
elif step == 2:
    st.markdown(f"""
    <div class="breadcrumb">
        <strong>Deine Basis:</strong> {st.session_state.nische}
        &nbsp;·&nbsp; {st.session_state.zielgruppe}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Welches Thema trifft am meisten?")
    st.caption("Wähle das Thema, das sich für dich am authentischsten anfühlt.")

    topics   = st.session_state.topics
    selected = st.radio("", topics,
                         index=min(st.session_state.sel_topic, len(topics) - 1),
                         label_visibility="collapsed")
    sel_idx  = topics.index(selected) if selected in topics else 0

    st.markdown("")
    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Zurück", key="back2"):
            st.session_state.step = 1
            st.rerun()
    with col_next:
        if st.button("Mit diesem Thema → Hooks schreiben"):
            st.session_state.sel_topic = sel_idx

            with st.spinner("Hooks werden generiert..."):
                thema  = topics[sel_idx]
                prompt = f"""Erstelle 5 verschiedene Instagram-Hooks für dieses Reel.
PFLICHT: Perfekte deutsche Rechtschreibung und Zeichensetzung in jedem Satz. Kommafehler, falsche Groß-/Kleinschreibung oder fehlende Satzzeichen sind nicht akzeptabel.
Nische: {st.session_state.nische}
Zielgruppe: {st.session_state.zielgruppe}
Thema: {thema}

Ein Hook = die allererste Zeile/die ersten Worte des Reels. Maximal 8-10 Wörter. Er entscheidet, ob jemand weiterschaut oder wegwischt.

Nutze verschiedene Hook-Typen:
- Frage die schmerzt (z.B. "Warum schaffen es so wenige Frauen...")
- Kontroverse Behauptung (z.B. "Du brauchst keine Follower um Geld zu verdienen")
- Überraschende Zahl (z.B. "44.000 Views mit 220 Followern — so geht's")
- Fehler benennen (z.B. "Dieser Fehler kostet dich täglich 2 Stunden")
- Direkte Ansprache + Versprechen (z.B. "Wenn du Mutter bist und online Geld verdienen willst...")

Formatiere GENAU so — keine Einleitung:
HOOK 1: [Hook-Text]
HOOK 2: [Hook-Text]
HOOK 3: [Hook-Text]
HOOK 4: [Hook-Text]
HOOK 5: [Hook-Text]

Kein Punkt am Ende. Kurz. Punchend. Jeder Hook muss anders sein."""
                raw   = call_claude(prompt)
                hooks = re.findall(r'HOOK \d+:\s*(.+)', raw)
                st.session_state.hooks  = hooks if hooks else [raw.strip()]
                st.session_state.step   = 3
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
# SCHRITT 3 — Hook wählen
# ═══════════════════════════════════════════════════════════════════
elif step == 3:
    topics  = st.session_state.topics
    thema   = topics[st.session_state.sel_topic] if topics else ""

    st.markdown(f"""
    <div class="breadcrumb">
        <strong>Thema:</strong> {thema}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Wähle deinen stärksten Hook")
    st.caption("Der erste Satz entscheidet alles. Welcher fühlt sich am stärksten an?")

    hooks    = st.session_state.hooks
    selected = st.radio("", hooks,
                         index=min(st.session_state.sel_hook, len(hooks) - 1),
                         label_visibility="collapsed")
    sel_idx  = hooks.index(selected) if selected in hooks else 0

    st.markdown("")
    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Zurück", key="back3"):
            st.session_state.step = 2
            st.rerun()
    with col_next:
        if st.button("Skript schreiben →"):
            st.session_state.sel_hook = sel_idx

            with st.spinner("Dein Reel-Skript wird geschrieben..."):
                hook   = hooks[sel_idx]
                prompt = f"""Schreibe ein vollständiges Reel-Skript für einen 45–60 Sekunden Reel.
PFLICHT: Perfekte deutsche Rechtschreibung und Zeichensetzung in jedem Satz. Kommafehler, falsche Groß-/Kleinschreibung oder fehlende Satzzeichen sind nicht akzeptabel.

Nische: {st.session_state.nische}
Zielgruppe: {st.session_state.zielgruppe}
Thema: {thema}
Hook (bereits gewählt): {hook}

Das Skript wird GESPROCHEN — schreib so, wie ein Mensch wirklich spricht. Kurze Sätze. Direkt. Authentisch.

Formatiere GENAU so — keine Einleitung, direkt das Skript:

HOOK: {hook}

PUNKT 1: [Ein gesprochener Satz — konkret und spezifisch]
PUNKT 2: [Ein gesprochener Satz — konkret und spezifisch]
PUNKT 3: [Ein gesprochener Satz — konkret und spezifisch]

CTA: [Was soll die Person jetzt konkret tun? — z.B. "Schreib mir REEL in die DMs und ich schick dir meinen Prompt-Vorlage gratis." oder "Folge mir für mehr solche Tipps."]

VISUAL-TIPP: [Was soll im Video zu sehen sein? 1 konkreter Satz — z.B. "Zeige deinen Laptop-Bildschirm mit Claude geöffnet" oder "Sprich direkt in die Kamera, Küche oder Schreibtisch im Hintergrund"]

TEXT-OVERLAY: [Kurzer Text der über das Video eingeblendet wird — maximal 6 Wörter — z.B. "Das kostet 0€" oder "Kein Technik-Wissen nötig"]"""
                raw = call_claude(prompt, max_tokens=1500)
                st.session_state.skript_raw = raw
                st.session_state.step = 4
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
# SCHRITT 4 — Skript anzeigen
# ═══════════════════════════════════════════════════════════════════
elif step == 4:
    topics = st.session_state.topics
    hooks  = st.session_state.hooks
    thema  = topics[st.session_state.sel_topic] if topics else ""
    hook   = hooks[st.session_state.sel_hook]   if hooks  else ""
    raw    = st.session_state.skript_raw

    st.markdown(f"""
    <div class="breadcrumb">
        <strong>Hook:</strong> {hook}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎬 Dein Reel-Skript")
    st.caption("Alles was du zum Drehen brauchst — strukturiert und sofort verwendbar.")

    SECTIONS = [
        ("HOOK",          "🪝 Hook — Erster Satz",             "#FF08C0"),
        ("PUNKT 1",       "1️⃣ Punkt 1",                         "#CC0099"),
        ("PUNKT 2",       "2️⃣ Punkt 2",                         "#FF08C0"),
        ("PUNKT 3",       "3️⃣ Punkt 3",                         "#CC0099"),
        ("CTA",           "📣 Call to Action",                  "#FF08C0"),
        ("VISUAL-TIPP",   "🎥 Visual-Tipp — Was du zeigst",     "#9B59B6"),
        ("TEXT-OVERLAY",  "✏️ Text-Overlay — Einblendung",      "#9B59B6"),
    ]

    for key, label, color in SECTIONS:
        content = extract(raw, key)
        if not content:
            # fallback: look for the key anywhere
            m = re.search(rf'{re.escape(key)}:\s*(.+)', raw, re.IGNORECASE)
            content = m.group(1).strip() if m else ""
        if content:
            st.markdown(f"""
            <div class="result-box" style="border-left-color:{color};">
                <div class="result-label" style="color:{color};">{label}</div>
                <div class="result-text">{content.replace(chr(10), "<br>")}</div>
            </div>
            """, unsafe_allow_html=True)

    # Full script as copyable text
    with st.expander("📋 Alles als Text (zum Kopieren)"):
        st.code(raw, language=None)

    st.markdown("")
    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Zurück", key="back4"):
            st.session_state.step = 3
            st.rerun()
    with col_next:
        if st.button("Caption & Hashtags erstellen →"):
            with st.spinner("Caption wird geschrieben..."):
                prompt = f"""Schreibe eine Instagram-Caption für diesen Reel.
PFLICHT: Perfekte deutsche Rechtschreibung und Zeichensetzung in jedem Satz. Kommafehler, falsche Groß-/Kleinschreibung oder fehlende Satzzeichen sind nicht akzeptabel.

Thema: {thema}
Hook (erste Zeile): {hook}
Nische: {st.session_state.nische}
Zielgruppe: {st.session_state.zielgruppe}

Formatiere GENAU so — keine Einleitung:

CAPTION: [3-5 Zeilen. Erste Zeile = der Hook aus dem Reel. Dann 2-3 kurze Sätze die neugierig machen. Dann 1 klarer CTA. Mit sparsamen Emojis. Keine Hashtags hier.]

HASHTAGS: [15 relevante Hashtags — Mix aus groß (500k+), mittel (50-500k) und klein (<50k). Deutsch und Englisch. Alles in einer Zeile mit Leerzeichen getrennt.]

POSTING-TIPP: [1 konkreter Satz — wann oder wie dieser Reel am besten performt]"""
                raw_caption = call_claude(prompt, max_tokens=800)
                st.session_state.caption_raw = raw_caption
                st.session_state.step = 5
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
# SCHRITT 5 — Komplettes Paket
# ═══════════════════════════════════════════════════════════════════
elif step == 5:
    topics      = st.session_state.topics
    hooks       = st.session_state.hooks
    thema       = topics[st.session_state.sel_topic] if topics else ""
    hook        = hooks[st.session_state.sel_hook]   if hooks  else ""
    raw_caption = st.session_state.caption_raw

    st.success("🎉 Dein komplettes Reel-Paket ist fertig!")

    # Caption
    caption_text   = extract(raw_caption, "CAPTION")
    hashtags_text  = extract(raw_caption, "HASHTAGS")
    tipp_text      = extract(raw_caption, "POSTING-TIPP")

    if caption_text:
        st.markdown("### 📝 Deine Caption")
        st.markdown(f"""
        <div class="result-box">
            <div class="result-label" style="color:#FF08C0;">CAPTION</div>
            <div class="result-text">{caption_text.replace(chr(10), "<br>")}</div>
        </div>
        """, unsafe_allow_html=True)
        st.code(caption_text, language=None)

    if hashtags_text:
        st.markdown("### # Hashtags")
        st.code(hashtags_text, language=None)

    if tipp_text:
        st.info(f"💡 **Posting-Tipp:** {tipp_text}")

    # Full package overview
    st.markdown("---")
    st.markdown("### 🎬 Alles auf einen Blick")
    full_pkg = (
        f"THEMA: {thema}\n\n"
        f"=== SKRIPT ===\n{st.session_state.skript_raw}\n\n"
        f"=== CAPTION & HASHTAGS ===\n{raw_caption}"
    )
    with st.expander("Komplett-Paket (zum Kopieren)"):
        st.code(full_pkg, language=None)

    # Upsell block
    st.markdown("""
    <div class="upsell-box">
        <div style="font-size:0.68rem;font-weight:800;text-transform:uppercase;
                    letter-spacing:0.15em;color:#FF08C0;margin-bottom:0.5rem;">
            Willst du mehr davon?
        </div>
        <div style="font-size:1.05rem;font-weight:700;color:#1a1a1a;margin-bottom:0.6rem;">
            Ich zeige dir, wie du mit Claude ein komplettes<br>Content-System aufbaust — einmal einrichten, für immer sparen.
        </div>
        <div style="font-size:0.88rem;color:#555;margin-bottom:1rem;line-height:1.6;">
            30 Minuten Setup · keine Technik-Kenntnisse nötig · funktioniert neben Familie und Vollzeitjob
        </div>
        <div style="font-size:0.88rem;font-weight:800;color:#FF08C0;">
            👉 Folge mir auf Instagram @karla.brenscheidt
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    if st.button("🔄 Neues Reel erstellen"):
        for k, v in {
            "step": 1, "topics": [], "sel_topic": 0,
            "hooks": [], "sel_hook": 0,
            "skript_raw": "", "caption_raw": "",
        }.items():
            st.session_state[k] = v
        st.rerun()


# ─── Footer ──────────────────────────────────────────────────────
st.markdown("""
<div class="karla-badge">
    Gemacht mit ❤️ von <strong>Karla Brenscheidt</strong> | @karla.brenscheidt<br>
    <small>Ich zeige dir, wie du mit Claude Code in 5 Minuten Reels, Tools und KI-Systeme baust.</small>
</div>
""", unsafe_allow_html=True)
