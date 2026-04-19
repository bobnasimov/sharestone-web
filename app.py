import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ShareStone",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%230071E3'/><text y='22' x='6' font-size='18' fill='white' font-family='Helvetica Neue'>S</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "waitlist" not in st.session_state:
    st.session_state.waitlist = []
if "show_waitlist_modal" not in st.session_state:
    st.session_state.show_waitlist_modal = False
if "waitlist_property" not in st.session_state:
    st.session_state.waitlist_property = ""

# ─────────────────────────────────────────────
# DUMMY DATA
# ─────────────────────────────────────────────
DUMMY_COMPARABLES = [
    {"address": "142 Elm Ridge Dr",  "city": "Hilliard, OH",   "beds": 3, "baths": 2.0, "sqft": 1920, "price": 318000, "share": 3180, "delta": "+2.1%"},
    {"address": "87 Oakmont Blvd",   "city": "Dublin, OH",     "beds": 4, "baths": 3.0, "sqft": 2310, "price": 412000, "share": 4120, "delta": "+0.8%"},
    {"address": "29 Maple Creek Ln", "city": "Powell, OH",     "beds": 3, "baths": 2.5, "sqft": 2050, "price": 375000, "share": 3750, "delta": "-0.4%"},
    {"address": "511 Westfield Ct",  "city": "Worthington, OH","beds": 4, "baths": 2.0, "sqft": 2180, "price": 395000, "share": 3950, "delta": "+1.3%"},
    {"address": "204 Birchwood Dr",  "city": "New Albany, OH", "beds": 5, "baths": 3.5, "sqft": 2900, "price": 520000, "share": 5200, "delta": "+3.7%"},
]

DUMMY_KPI = {
    "listings":  "48,210",
    "avg_share": "$2,840",
    "markets":   "32",
    "aum":       "$124M",
}

DUMMY_STATE_VALUES = {
    "California": 680000, "New York": 590000, "Texas": 340000,
    "Florida": 390000, "Ohio": 295000, "Washington": 510000,
    "Colorado": 475000, "Georgia": 320000,
}

DUMMY_TREND = {
    "months": ["May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr"],
    "prices": [2410, 2480, 2520, 2610, 2570, 2640, 2700, 2750, 2820, 2795, 2860, 2910],
}

DUMMY_PORTFOLIO = [
    {"property": "142 Elm Ridge Dr",   "location": "Hilliard, OH",   "state": "Ohio",     "share_pct": "1.0%", "purchase": 3100, "current": 3420, "return_pct": "+10.3%"},
    {"property": "511 Westfield Ct",   "location": "Worthington, OH","state": "Ohio",     "share_pct": "0.5%", "purchase": 1950, "current": 1975, "return_pct": "+1.3%"},
    {"property": "88 Lakeview Pkwy",   "location": "Austin, TX",     "state": "Texas",    "share_pct": "2.0%", "purchase": 7200, "current": 8100, "return_pct": "+12.5%"},
    {"property": "33 Ocean Mist Blvd", "location": "Miami, FL",      "state": "Florida",  "share_pct": "0.5%", "purchase": 2800, "current": 3150, "return_pct": "+12.5%"},
    {"property": "17 Harbor Lofts",    "location": "Brooklyn, NY",   "state": "New York", "share_pct": "1.0%", "purchase": 8900, "current": 9600, "return_pct": "+7.9%"},
    {"property": "204 Birchwood Dr",   "location": "New Albany, OH", "state": "Ohio",     "share_pct": "0.5%", "purchase": 2600, "current": 2750, "return_pct": "+5.8%"},
    {"property": "29 Maple Creek Ln",  "location": "Powell, OH",     "state": "Ohio",     "share_pct": "1.5%", "purchase": 5625, "current": 5900, "return_pct": "+4.9%"},
    {"property": "88 Lakeview Pkwy B", "location": "Austin, TX",     "state": "Texas",    "share_pct": "1.0%", "purchase": 4600, "current": 5100, "return_pct": "+10.9%"},
]

DUMMY_LISTINGS = [
    {"address": "142 Elm Ridge Dr",   "city": "Hilliard, OH",   "price": 318000, "share": 3180, "beds": 3, "baths": 2.0, "sqft": 1920, "type": "Single Family", "yield": "6.2%",
     "img": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=600&q=80"},
    {"address": "29 Maple Creek Ln",  "city": "Powell, OH",     "price": 375000, "share": 3750, "beds": 3, "baths": 2.5, "sqft": 2050, "type": "Single Family", "yield": "5.9%",
     "img": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=600&q=80"},
    {"address": "88 Lakeview Pkwy",   "city": "Austin, TX",     "price": 460000, "share": 4600, "beds": 4, "baths": 3.0, "sqft": 2400, "type": "Single Family", "yield": "6.8%",
     "img": "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=600&q=80"},
    {"address": "204 Birchwood Dr",   "city": "New Albany, OH", "price": 520000, "share": 5200, "beds": 5, "baths": 3.5, "sqft": 2900, "type": "Single Family", "yield": "5.4%",
     "img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&q=80"},
    {"address": "33 Ocean Mist Blvd", "city": "Miami, FL",      "price": 710000, "share": 7100, "beds": 4, "baths": 4.0, "sqft": 3100, "type": "Condo",         "yield": "7.1%",
     "img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600&q=80"},
    {"address": "17 Harbor Lofts",    "city": "Brooklyn, NY",   "price": 890000, "share": 8900, "beds": 2, "baths": 2.0, "sqft": 1100, "type": "Multi-Family",  "yield": "7.8%",
     "img": "https://images.unsplash.com/photo-1460317442991-0ec209397118?w=600&q=80"},
]

DUMMY_TEAM = [
    {"name": "Alexandra Chen",  "title": "Co-Founder & CEO",    "init": "AC"},
    {"name": "Marcus Webb",     "title": "Co-Founder & CTO",    "init": "MW"},
    {"name": "Priya Nambiar",   "title": "Head of Acquisitions","init": "PN"},
]

SUPPORTED_STATES = ["Ohio", "New York", "Texas", "Florida", "California", "Washington", "Colorado", "Georgia"]

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');

#MainMenu, footer, header { visibility: hidden; }
* { box-sizing: border-box; }

.stApp {
    background-color: #F5F5F7;
    font-family: "Manrope", "Helvetica Neue", Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
}
.block-container { padding: 2rem 2rem 5rem; max-width: 1180px; }

[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E8E8ED; }
[data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
div[data-testid="stSidebar"] .stRadio > label { display: none !important; }
div[data-testid="stSidebar"] .stRadio > div { gap: 0 !important; flex-direction: column !important; }
div[data-testid="stSidebar"] .stRadio > div > label {
    font-family: "Manrope", sans-serif !important; font-size: 0.88rem !important;
    font-weight: 500 !important; color: #1D1D1F !important;
    padding: 0.6rem 1.1rem !important; border-radius: 10px !important;
    margin: 1px 6px !important; cursor: pointer !important; transition: background 0.1s ease !important;
}
div[data-testid="stSidebar"] .stRadio > div > label:hover { background: #F5F5F7 !important; }
div[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
div[data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] {
    background: #EBF2FF !important; color: #0071E3 !important; font-weight: 600 !important;
}
div[data-testid="stSidebar"] .stRadio > div > label > div:first-child { display: none !important; }

/* ── Hero ── */
.ss-hero {
    background: linear-gradient(135deg, #0058B8 0%, #0071E3 55%, #2E9BFF 100%);
    border-radius: 22px; padding: 2.8rem 3rem; margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.ss-hero::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 280px; height: 280px; background: rgba(255,255,255,0.06); border-radius: 50%;
}
.ss-hero::after {
    content: ''; position: absolute; bottom: -60px; right: 120px;
    width: 180px; height: 180px; background: rgba(255,255,255,0.04); border-radius: 50%;
}
.ss-hero-eyebrow {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: rgba(255,255,255,0.65); margin-bottom: 0.75rem;
}
.ss-hero-title {
    font-size: 2.2rem; font-weight: 800; color: #FFFFFF;
    letter-spacing: -0.04em; line-height: 1.15; margin-bottom: 0.85rem; max-width: 560px;
}
.ss-hero-sub {
    font-size: 1rem; color: rgba(255,255,255,0.78); line-height: 1.6;
    max-width: 520px; margin-bottom: 1.75rem; font-weight: 400;
}
.ss-hero-stats { display: flex; gap: 2.5rem; flex-wrap: wrap; }
.ss-hero-stat-val { font-size: 1.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.03em; line-height: 1; }
.ss-hero-stat-lbl { font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 3px; }

/* ── Page Header ── */
.ss-page-header { margin-bottom: 2.25rem; padding-bottom: 1.5rem; border-bottom: 1px solid #E8E8ED; }
.ss-page-title { font-size: 2rem; font-weight: 800; color: #1D1D1F; letter-spacing: -0.04em; line-height: 1.1; margin: 0 0 0.3rem 0; }
.ss-page-subtitle { font-size: 0.9rem; font-weight: 400; color: #86868B; }

/* ── Cards ── */
.ss-card {
    background: #FFFFFF; border-radius: 18px; padding: 1.75rem;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 1px 4px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.03); margin-bottom: 1.25rem;
}

/* ── Info banner ── */
.ss-info-banner {
    background: #EBF2FF; border: 1px solid #C5DCFA; border-radius: 12px;
    padding: 0.7rem 1rem; margin-bottom: 1.25rem;
    font-size: 0.84rem; color: #0055B3; font-weight: 500;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: #FFFFFF; border: 1px solid rgba(0,0,0,0.06);
    border-radius: 18px; padding: 1.5rem 1.75rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
[data-testid="stMetricValue"] {
    font-family: "Manrope", sans-serif !important; font-size: 1.85rem !important;
    font-weight: 800 !important; color: #1D1D1F !important; letter-spacing: -0.04em !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.07em !important; color: #86868B !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #FFFFFF; border-radius: 18px; padding: 1.6rem 1.75rem;
    border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #1D1D1F; letter-spacing: -0.04em; line-height: 1; margin-bottom: 0.35rem; }
.kpi-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #86868B; }
.kpi-sub { font-size: 0.78rem; color: #86868B; margin-top: 0.45rem; font-weight: 400; }

/* ── Buttons ── */
.stButton > button {
    background: #0071E3 !important; color: #FFFFFF !important; border: none !important;
    border-radius: 980px !important; padding: 0.6rem 1.6rem !important;
    font-family: "Manrope", sans-serif !important; font-weight: 600 !important;
    font-size: 0.88rem !important; letter-spacing: -0.01em !important;
    transition: box-shadow 0.15s ease, background 0.15s ease !important; cursor: pointer !important;
}
.stButton > button:hover { background: #0077ED !important; box-shadow: 0 4px 14px rgba(0,113,227,0.35) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    background: #FFFFFF !important; border: 1px solid #D2D2D7 !important;
    border-radius: 10px !important; color: #1D1D1F !important;
    font-family: "Manrope", sans-serif !important; font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
    border-color: #0071E3 !important; box-shadow: 0 0 0 3px rgba(0,113,227,0.15) !important;
}
.stSelectbox > div > div { background: #FFFFFF !important; border: 1px solid #D2D2D7 !important; border-radius: 10px !important; }
.stTextInput label, .stNumberInput label, .stSelectbox label, .stSlider label {
    font-family: "Manrope", sans-serif !important; font-size: 0.72rem !important;
    font-weight: 700 !important; color: #1D1D1F !important;
    text-transform: uppercase !important; letter-spacing: 0.06em !important;
}

h3 {
    font-family: "Manrope", sans-serif !important; font-size: 1.05rem !important;
    font-weight: 700 !important; color: #1D1D1F !important;
    letter-spacing: -0.02em !important; margin: 1.5rem 0 0.75rem !important;
}

/* ── Tables ── */
.ss-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.ss-table thead tr { border-bottom: 1px solid #E8E8ED; }
.ss-table th {
    font-size: 0.67rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; color: #86868B; padding: 0 1rem 0.75rem; text-align: left; white-space: nowrap;
}
.ss-table td { padding: 0.9rem 1rem; border-bottom: 1px solid #F2F2F7; color: #1D1D1F; vertical-align: middle; }
.ss-table tr:last-child td { border-bottom: none; }
.td-primary { font-weight: 600; color: #1D1D1F; }
.td-secondary { font-size: 0.78rem; color: #86868B; margin-top: 1px; }
.td-pos { color: #1A7A1A; font-weight: 600; }
.td-neg { color: #C0392B; font-weight: 600; }

/* ── Pills ── */
.pill { display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px; border-radius: 980px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.02em; }
.pill-green { background: #F0FAF0; color: #1A7A1A; }
.pill-blue  { background: #EBF2FF; color: #0055B3; }
.pill-dot   { width: 5px; height: 5px; border-radius: 50%; background: currentColor; display: inline-block; }

/* ── Property Cards ── */
.prop-card {
    background: #FFFFFF; border-radius: 18px; overflow: hidden;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 1px 4px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.03);
    transition: box-shadow 0.2s ease, transform 0.2s ease; margin-bottom: 0.5rem;
}
.prop-card:hover { box-shadow: 0 8px 32px rgba(0,0,0,0.1); transform: translateY(-2px); }
.prop-img-wrap { position: relative; overflow: hidden; height: 175px; background: #F5F5F7; }
.prop-img-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s ease; }
.prop-card:hover .prop-img-wrap img { transform: scale(1.04); }
.prop-tag {
    position: absolute; top: 10px; background: rgba(255,255,255,0.92);
    backdrop-filter: blur(8px); border-radius: 980px; padding: 3px 9px;
    font-size: 0.68rem; font-weight: 700; color: #1D1D1F; letter-spacing: 0.03em;
}
.prop-tag-left { left: 10px; }
.prop-tag-right { right: 10px; background: rgba(0,113,227,0.92) !important; color: #FFF !important; }
.prop-body { padding: 1.1rem 1.2rem 1rem; }
.prop-address { font-size: 0.92rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.02em; margin-bottom: 2px; }
.prop-city { font-size: 0.78rem; color: #86868B; margin-bottom: 0.85rem; }
.prop-price { font-size: 1.25rem; font-weight: 800; color: #1D1D1F; letter-spacing: -0.03em; }
.prop-share-line { font-size: 0.78rem; color: #86868B; margin: 2px 0 0.85rem; }
.prop-specs { display: flex; gap: 0.9rem; font-size: 0.76rem; color: #636366; padding-top: 0.85rem; border-top: 1px solid #F2F2F7; font-weight: 500; }

/* ── Team Cards ── */
.team-card {
    background: #FFFFFF; border-radius: 18px; padding: 1.75rem 1.5rem;
    border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 1px 4px rgba(0,0,0,0.04); text-align: center;
}
.team-avatar {
    width: 68px; height: 68px; background: linear-gradient(135deg, #1D1D1F, #3A3A3C);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    color: #FFFFFF; font-size: 1rem; font-weight: 700; margin: 0 auto 1rem;
}
.team-name { font-size: 0.92rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.02em; }
.team-role { font-size: 0.78rem; color: #86868B; margin-top: 0.2rem; }

.ss-divider { border: none; border-top: 1px solid #E8E8ED; margin: 2rem 0; }
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 0 !important; border-bottom: 1px solid #E8E8ED !important; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border: none !important; padding: 0.6rem 1.1rem !important;
    font-family: "Manrope", sans-serif !important; font-size: 0.86rem !important;
    font-weight: 500 !important; color: #86868B !important; border-radius: 0 !important;
}
.stTabs [aria-selected="true"] { color: #0071E3 !important; font-weight: 700 !important; border-bottom: 2px solid #0071E3 !important; }

@media (max-width: 768px) {
    .block-container { padding: 1rem 1rem 4rem; }
    .ss-hero { padding: 1.75rem 1.5rem; }
    .ss-hero-title { font-size: 1.5rem; }
    .ss-hero-stats { gap: 1.25rem; }
    .ss-hero-stat-val { font-size: 1.2rem; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0 1rem 1.5rem;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.5rem;">
            <div style="width:34px;height:34px;background:#0071E3;border-radius:9px;
                display:flex;align-items:center;justify-content:center;
                font-family:Manrope,sans-serif;font-weight:800;font-size:1rem;color:#FFF;flex-shrink:0;">S</div>
            <span style="font-family:Manrope,sans-serif;font-size:1.05rem;font-weight:800;color:#1D1D1F;letter-spacing:-0.04em;">ShareStone</span>
        </div>
        <div style="display:inline-block;margin-left:44px;background:#F2F2F7;color:#636366;
            font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
            padding:2px 8px;border-radius:980px;">Early Access</div>
    </div>
    <div style="height:1px;background:#E8E8ED;margin:0 1rem 1.25rem;"></div>
    """, unsafe_allow_html=True)

    page = st.radio("nav",
        ["Valuation Engine", "Market Dashboard", "My Portfolio", "Property Explorer", "Settings"],
        label_visibility="collapsed")

    st.markdown("""
    <div style="height:1px;background:#E8E8ED;margin:1.25rem 1rem 1.25rem;"></div>
    <div style="padding:0 1rem 1.5rem;">
        <div style="font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#86868B;margin-bottom:0.85rem;">System</div>
        <div style="display:flex;align-items:center;gap:7px;margin-bottom:0.5rem;">
            <div style="width:6px;height:6px;background:#30D158;border-radius:50%;flex-shrink:0;"></div>
            <span style="font-size:0.82rem;color:#1D1D1F;font-weight:500;flex:1;">Inference API</span>
            <span style="font-size:0.75rem;color:#86868B;">Online</span>
        </div>
        <div style="display:flex;align-items:center;gap:7px;">
            <div style="width:6px;height:6px;background:#30D158;border-radius:50%;flex-shrink:0;"></div>
            <span style="font-size:0.82rem;color:#1D1D1F;font-weight:500;flex:1;">Market Data</span>
            <span style="font-size:0.75rem;color:#86868B;">Live</span>
        </div>
    </div>
    <div style="padding:0 1rem;font-size:0.7rem;color:#C7C7CC;">© 2025 ShareStone, Inc.</div>
    """, unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────
def page_header(title, subtitle):
    st.markdown(f"""
    <div class="ss-page-header">
        <div class="ss-page-title">{title}</div>
        <div class="ss-page-subtitle">{subtitle}</div>
    </div>""", unsafe_allow_html=True)

def section_head(text):
    st.markdown(f"<h3>{text}</h3>", unsafe_allow_html=True)

def apply_chart_theme(fig, height=310):
    fig.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        title="",
        font=dict(family="Manrope, Helvetica Neue, sans-serif", color="#1D1D1F"),
        title_font=dict(family="Manrope, Helvetica Neue, sans-serif", size=13, color="#1D1D1F"),
        margin=dict(l=12, r=12, t=12, b=12), height=height,
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11, color="#86868B")),
        yaxis=dict(gridcolor="#F2F2F7", zeroline=False, tickfont=dict(size=11, color="#86868B")),
    )
    return fig


# ═════════════════════════════════════════════
# PAGE 1 — VALUATION ENGINE
# ═════════════════════════════════════════════
if page == "Valuation Engine":

    st.markdown("""
    <div class="ss-hero">
        <div class="ss-hero-eyebrow">AI-Powered Real Estate · Early Access</div>
        <div class="ss-hero-title">Own a piece of any home.<br>Starting at $100.</div>
        <div class="ss-hero-sub">
            ShareStone uses machine learning trained on 2.2 million US listings
            to price fractional shares with institutional precision —
            then opens the door to any investor.
        </div>
        <div class="ss-hero-stats">
            <div><div class="ss-hero-stat-val">$124M</div><div class="ss-hero-stat-lbl">Platform AUM</div></div>
            <div><div class="ss-hero-stat-val">48K+</div><div class="ss-hero-stat-lbl">Listings</div></div>
            <div><div class="ss-hero-stat-val">6.4%</div><div class="ss-hero-stat-lbl">Avg. Annual Yield</div></div>
            <div><div class="ss-hero-stat-val">8 States</div><div class="ss-hero-stat-lbl">Coverage</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page_header("Valuation Engine", "Enter property details to get an AI-generated fair market value and fractional share price.")

    st.markdown("""
    <div class="ss-info-banner">
        ℹ️ &nbsp;Currently available in 8 states: Ohio, New York, Texas, Florida, California, Washington, Colorado, and Georgia.
        More states coming soon.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        state     = st.selectbox("State", SUPPORTED_STATES)
        bedrooms  = st.number_input("Bedrooms", min_value=1, max_value=10, value=3)
        sqft      = st.number_input("Square Footage", min_value=500, max_value=10000, value=2000, step=100)
    with c2:
        city      = st.text_input("City", "Hilliard")
        bathrooms = st.number_input("Bathrooms", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
        lot       = st.number_input("Lot Size (Acres)", min_value=0.01, max_value=50.0, value=0.25, step=0.05)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    btn_col, _ = st.columns([1, 4])
    with btn_col:
        run = st.button("Run Valuation")

    if run:
        payload = {"state": state, "city": city, "bed": bedrooms,
                   "bath": bathrooms, "house_size": sqft, "acre_lot": lot}
        with st.spinner("Querying inference engine…"):
            try:
                resp = requests.post(
                    "https://sharestone-api-861810670522.us-central1.run.app/predict",
                    json=payload, timeout=15)
                if resp.status_code == 200:
                    data  = resp.json()
                    fmv   = data.get("fair_market_value", 0)
                    share = data.get("one_percent_share", 0)
                    st.markdown("<br>", unsafe_allow_html=True)
                    m1, m2, m3, m4 = st.columns(4, gap="medium")
                    m1.metric("Fair Market Value",   f"${fmv:,.0f}")
                    m2.metric("1% Fractional Share", f"${share:,.0f}")
                    m3.metric("Est. Annual Yield",   "6.4%",  "+0.3%")
                    m4.metric("Market Percentile",   "72nd",  "+4 pts")

                    st.markdown("<br>", unsafe_allow_html=True)
                    section_head("Comparable Sales")
                    rows = ""
                    for c in DUMMY_COMPARABLES:
                        cls = "td-pos" if "+" in c["delta"] else "td-neg"
                        rows += f"""<tr>
                            <td><div class="td-primary">{c['address']}</div>
                                <div class="td-secondary">{c['city']}</div></td>
                            <td>{c['beds']} bd / {c['baths']} ba</td>
                            <td>{c['sqft']:,} sqft</td>
                            <td><strong>${c['price']:,}</strong></td>
                            <td>${c['share']:,}</td>
                            <td class="{cls}">{c['delta']}</td></tr>"""
                    st.markdown(f"""
                    <div class="ss-card" style="padding: 0.5rem 0;">
                    <table class="ss-table">
                        <thead><tr>
                            <th>Address</th><th>Beds / Baths</th><th>Size</th>
                            <th>List Price</th><th>1% Share</th><th>vs. Subject</th>
                        </tr></thead>
                        <tbody>{rows}</tbody>
                    </table></div>""", unsafe_allow_html=True)
                else:
                    st.error(f"Inference engine returned HTTP {resp.status_code}. Please try again.")
            except Exception as e:
                st.error(f"Unable to reach the valuation API. {e}")


# ═════════════════════════════════════════════
# PAGE 2 — MARKET DASHBOARD
# ═════════════════════════════════════════════
elif page == "Market Dashboard":
    page_header("Market Dashboard", "Platform-wide analytics and real estate market intelligence.")

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    for col, (label, val, sub) in zip(
        [k1, k2, k3, k4],
        [("Listings Analyzed", DUMMY_KPI["listings"], "+1,240 this week"),
         ("Avg. Share Price",  DUMMY_KPI["avg_share"], "+$64 this month"),
         ("Markets Covered",   DUMMY_KPI["markets"],   "8 states"),
         ("Platform AUM",      DUMMY_KPI["aum"],       "+$12M this quarter")]
    ):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    d1, d2 = st.columns(2, gap="large")

    with d1:
        section_head("Avg. Property Value by State")
        df_s = pd.DataFrame({
            "State": list(DUMMY_STATE_VALUES.keys()),
            "Value": list(DUMMY_STATE_VALUES.values())
        }).sort_values("Value", ascending=True)
        fig_bar = px.bar(df_s, x="Value", y="State", orientation="h",
                         color="Value", color_continuous_scale=["#E8E8ED", "#0071E3"])
        fig_bar.update_traces(marker_line_width=0, marker_cornerradius=4)
        fig_bar.update_coloraxes(showscale=False)
        fig_bar = apply_chart_theme(fig_bar, 300)
        fig_bar.update_layout(xaxis_title="", yaxis_title="")
        st.markdown('<div class="ss-card" style="padding:1.25rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with d2:
        section_head("Fractional Share Price Trend")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=DUMMY_TREND["months"], y=DUMMY_TREND["prices"],
            mode="lines",
            line=dict(color="#0071E3", width=2.5, shape="spline", smoothing=0.8),
            fill="tozeroy", fillcolor="rgba(0,113,227,0.06)",
            hovertemplate="<b>$%{y:,}</b><extra></extra>",
        ))
        fig_line = apply_chart_theme(fig_line, 300)
        fig_line.update_layout(yaxis_title="Avg 1% Share ($)", xaxis_title="")
        st.markdown('<div class="ss-card" style="padding:1.25rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    section_head("Recent Transactions")
    st.markdown("""
    <div class="ss-card" style="padding:0.5rem 0;">
    <table class="ss-table">
        <thead><tr><th>Time</th><th>Property</th><th>Investor</th><th>Share</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
            <tr><td style="color:#86868B;font-size:0.8rem;">2 min ago</td>
                <td><div class="td-primary">142 Elm Ridge Dr</div><div class="td-secondary">Hilliard, OH</div></td>
                <td>J. Morrison</td><td>0.5%</td><td><strong>$1,590</strong></td>
                <td><span class="pill pill-green"><span class="pill-dot"></span>Settled</span></td></tr>
            <tr><td style="color:#86868B;font-size:0.8rem;">11 min ago</td>
                <td><div class="td-primary">88 Lakeview Pkwy</div><div class="td-secondary">Austin, TX</div></td>
                <td>S. Patel</td><td>1.0%</td><td><strong>$4,600</strong></td>
                <td><span class="pill pill-green"><span class="pill-dot"></span>Settled</span></td></tr>
            <tr><td style="color:#86868B;font-size:0.8rem;">34 min ago</td>
                <td><div class="td-primary">33 Ocean Mist Blvd</div><div class="td-secondary">Miami, FL</div></td>
                <td>R. Kim</td><td>0.5%</td><td><strong>$3,550</strong></td>
                <td><span class="pill pill-green"><span class="pill-dot"></span>Settled</span></td></tr>
            <tr><td style="color:#86868B;font-size:0.8rem;">1 hr ago</td>
                <td><div class="td-primary">17 Harbor Lofts</div><div class="td-secondary">Brooklyn, NY</div></td>
                <td>T. Nguyen</td><td>2.0%</td><td><strong>$17,800</strong></td>
                <td><span class="pill pill-blue"><span class="pill-dot"></span>Pending</span></td></tr>
        </tbody>
    </table></div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# PAGE 3 — MY PORTFOLIO
# ═════════════════════════════════════════════
elif page == "My Portfolio":
    page_header("My Portfolio", "Track your fractional holdings, returns, and geographic exposure.")

    total_invested = sum(h["purchase"] for h in DUMMY_PORTFOLIO)
    total_current  = sum(h["current"]  for h in DUMMY_PORTFOLIO)
    total_return   = (total_current - total_invested) / total_invested * 100

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    m1.metric("Total Invested",   f"${total_invested:,}")
    m2.metric("Current Value",    f"${total_current:,}", f"+${total_current - total_invested:,}")
    m3.metric("Total Return",     f"+{total_return:.1f}%", "+2.1% YTD")
    m4.metric("Active Positions", str(len(DUMMY_PORTFOLIO)))

    st.markdown("<br>", unsafe_allow_html=True)
    p1, p2 = st.columns([1, 1.55], gap="large")

    with p1:
        section_head("Holdings by Type")
        type_map = {"Ohio": "Single Family", "Texas": "Single Family", "Florida": "Condo", "New York": "Multi-Family"}
        type_values = {}
        for h in DUMMY_PORTFOLIO:
            t = type_map.get(h["state"], "Single Family")
            type_values[t] = type_values.get(t, 0) + h["current"]

        fig_d = go.Figure(go.Pie(
            labels=list(type_values.keys()), values=list(type_values.values()), hole=0.68,
            marker=dict(colors=["#1D1D1F","#636366","#D2D2D7"], line=dict(color="#FFFFFF", width=3)),
            textinfo="none", hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
        ))
        fig_d.add_annotation(text=f"<b>${total_current:,}</b>", x=0.5, y=0.56,
            font=dict(size=12, color="#1D1D1F", family="Manrope"), showarrow=False)
        fig_d.add_annotation(text="Total Value", x=0.5, y=0.39,
            font=dict(size=10, color="#86868B", family="Manrope"), showarrow=False)
        fig_d.update_layout(
            paper_bgcolor="#FFFFFF", margin=dict(l=12,r=12,t=12,b=12), height=230, title="",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
                        font=dict(size=10, color="#636366", family="Manrope"))
        )
        st.markdown('<div class="ss-card" style="padding:1.25rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_d, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with p2:
        section_head("Active Positions")
        rows = ""
        for h in DUMMY_PORTFOLIO:
            ret_cls = "td-pos" if "+" in h["return_pct"] else "td-neg"
            rows += f"""<tr>
                <td><div class="td-primary">{h['property']}</div>
                    <div class="td-secondary">{h['location']}</div></td>
                <td>{h['share_pct']}</td>
                <td>${h['purchase']:,}</td>
                <td>${h['current']:,}</td>
                <td class="{ret_cls}">{h['return_pct']}</td></tr>"""
        st.markdown(f"""
        <div class="ss-card" style="padding:0.5rem 0;">
        <table class="ss-table">
            <thead><tr><th>Property</th><th>Share</th><th>Cost Basis</th>
            <th>Market Value</th><th>Return</th></tr></thead>
            <tbody>{rows}</tbody>
        </table></div>""", unsafe_allow_html=True)

    section_head("Geographic Allocation")
    state_totals = {}
    for h in DUMMY_PORTFOLIO:
        state_totals[h["state"]] = state_totals.get(h["state"], 0) + h["current"]
    total_val = sum(state_totals.values())
    df_geo = pd.DataFrame({
        "State": list(state_totals.keys()),
        "Pct":   [round(v / total_val * 100) for v in state_totals.values()]
    }).sort_values("Pct", ascending=False)

    fig_g = px.bar(df_geo, x="State", y="Pct", color_discrete_sequence=["#0071E3"], text="Pct")
    fig_g.update_traces(texttemplate="%{text}%", textposition="outside",
                        marker_cornerradius=6, marker_line_width=0)
    fig_g = apply_chart_theme(fig_g, 260)
    fig_g.update_layout(yaxis_title="Allocation (%)", xaxis_title="", showlegend=False,
                        yaxis=dict(range=[0, df_geo["Pct"].max() + 12],
                                   gridcolor="#F2F2F7", zeroline=False,
                                   tickfont=dict(size=11, color="#86868B")))
    st.markdown('<div class="ss-card" style="padding:1.25rem;">', unsafe_allow_html=True)
    st.plotly_chart(fig_g, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════
# PAGE 4 — PROPERTY EXPLORER
# ═════════════════════════════════════════════
elif page == "Property Explorer":
    page_header("Property Explorer", "Browse available fractional investment opportunities.")

    # ── Waitlist form (shown inline when triggered) ──
    if st.session_state.show_waitlist_modal:
        prop = st.session_state.waitlist_property
        st.markdown(f"""
        <div class="ss-card" style="border: 2px solid #0071E3; max-width: 520px;">
            <div style="font-size:1.2rem;font-weight:800;color:#1D1D1F;letter-spacing:-0.03em;margin-bottom:0.3rem;">
                Join the waitlist
            </div>
            <div style="font-size:0.88rem;color:#86868B;margin-bottom:1.25rem;line-height:1.55;">
                Be first to invest in <strong style="color:#1D1D1F;">{prop}</strong>
                when shares become available.
            </div>
        </div>""", unsafe_allow_html=True)

        wl_col1, wl_col2 = st.columns(2, gap="medium")
        with wl_col1:
            wl_name  = st.text_input("Full Name", key="wl_name", placeholder="Jane Smith")
        with wl_col2:
            wl_email = st.text_input("Email Address", key="wl_email", placeholder="jane@example.com")

        wl_amount = st.selectbox("Intended investment amount",
            ["$100 – $500", "$500 – $2,000", "$2,000 – $10,000", "$10,000+"], key="wl_amount")

        b1, b2, _ = st.columns([1, 1, 4])
        with b1:
            if st.button("✓ Join Waitlist", key="wl_submit"):
                if wl_name and wl_email:
                    st.session_state.waitlist.append({
                        "name": wl_name, "email": wl_email,
                        "amount": wl_amount, "property": prop
                    })
                    st.session_state.show_waitlist_modal = False
                    st.success(f"You're on the waitlist for {prop}! We'll be in touch.")
                    st.rerun()
                else:
                    st.warning("Please fill in your name and email.")
        with b2:
            if st.button("Cancel", key="wl_cancel"):
                st.session_state.show_waitlist_modal = False
                st.rerun()

        st.markdown("<hr class='ss-divider'>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns([1.1, 1.1, 2], gap="medium")
    with f1:
        filter_state = st.selectbox("State", ["All States","Ohio","Texas","Florida","New York"])
    with f2:
        filter_type  = st.selectbox("Property Type", ["All Types","Single Family","Condo","Multi-Family"])
    with f3:
        max_price = st.slider("Max Property Price", 200000, 1000000, 1000000, step=50000, format="$%d")

    filtered = [
        p for p in DUMMY_LISTINGS
        if (filter_state == "All States" or filter_state in p["city"])
        and (filter_type == "All Types" or filter_type == p["type"])
        and p["price"] <= max_price
    ]

    n = len(filtered)
    st.markdown(f"""
    <div style="font-size:0.82rem;color:#86868B;margin:0.4rem 0 1.25rem;font-weight:500;">
        {n} propert{"y" if n==1 else "ies"} found
    </div>""", unsafe_allow_html=True)

    if not filtered:
        st.info("No properties match your current filters.")
    else:
        cols = st.columns(3, gap="medium")
        for i, p in enumerate(filtered):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="prop-card">
                    <div class="prop-img-wrap">
                        <img src="{p['img']}" alt="{p['address']}">
                        <span class="prop-tag prop-tag-left">{p['type']}</span>
                        <span class="prop-tag prop-tag-right">{p['yield']} yield</span>
                    </div>
                    <div class="prop-body">
                        <div class="prop-address">{p['address']}</div>
                        <div class="prop-city">{p['city']}</div>
                        <div class="prop-price">${p['price']:,}</div>
                        <div class="prop-share-line">1% share &nbsp;&middot;&nbsp; <strong>${p['share']:,}</strong></div>
                        <div class="prop-specs">
                            <span>{p['beds']} bd</span>
                            <span>{p['baths']} ba</span>
                            <span>{p['sqft']:,} sqft</span>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                if st.button("Join Waitlist", key=f"waitlist_{i}"):
                    st.session_state.show_waitlist_modal = True
                    st.session_state.waitlist_property   = p["address"]
                    st.rerun()


# ═════════════════════════════════════════════
# PAGE 5 — SETTINGS
# ═════════════════════════════════════════════
elif page == "Settings":
    page_header("Settings", "Account preferences and platform information.")

    tab1, tab2 = st.tabs(["Account", "About ShareStone"])

    with tab1:
        section_head("Profile")
        st.markdown('<div class="ss-card">', unsafe_allow_html=True)
        a1, a2 = st.columns(2, gap="large")
        with a1:
            st.text_input("Full Name",     "Jane Investor")
            st.text_input("Email Address", "jane@example.com")
            st.selectbox("Accreditation Status", ["Accredited Investor","Non-Accredited","Pending Review"])
        with a2:
            st.text_input("Organization", "Independent")
            st.selectbox("Notifications", ["All Alerts","Digest Only","None"])
            st.selectbox("Currency",      ["USD ($)","EUR (€)","GBP (£)"])
        st.markdown("<br>", unsafe_allow_html=True)
        bc, _ = st.columns([1,5])
        with bc: st.button("Save Changes")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr class='ss-divider'>", unsafe_allow_html=True)
        section_head("Security")
        st.markdown('<div class="ss-card">', unsafe_allow_html=True)
        s1, s2 = st.columns(2, gap="large")
        with s1:
            st.text_input("Current Password", type="password")
            st.text_input("New Password",      type="password")
        with s2:
            st.text_input("Confirm Password",  type="password")
            st.selectbox("Two-Factor Auth", ["Disabled","SMS","Authenticator App"])
        st.markdown("<br>", unsafe_allow_html=True)
        uc, _ = st.columns([1,5])
        with uc: st.button("Update Password")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        section_head("About ShareStone")
        st.markdown("""
        <div class="ss-card">
            <p style="font-size:0.93rem;color:#3A3A3C;line-height:1.78;max-width:680px;font-weight:400;letter-spacing:-0.01em;margin:0 0 1.5rem;">
                ShareStone is an institutional-grade fractional real estate platform that democratizes
                access to residential and commercial property assets. Using proprietary AI-driven
                valuation models trained on 2.2 million US listings, we price fractional shares
                with the precision previously reserved for institutional buyers —
                making real estate wealth-building accessible to everyone.
            </p>
            <div style="display:flex;gap:2.5rem;flex-wrap:wrap;padding-top:1.5rem;border-top:1px solid #F2F2F7;">
                <div>
                    <div style="font-family:Manrope,sans-serif;font-size:1.7rem;font-weight:800;color:#1D1D1F;letter-spacing:-0.04em;">2024</div>
                    <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:#86868B;margin-top:2px;">Founded</div>
                </div>
                <div>
                    <div style="font-family:Manrope,sans-serif;font-size:1.7rem;font-weight:800;color:#1D1D1F;letter-spacing:-0.04em;">32</div>
                    <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:#86868B;margin-top:2px;">Markets</div>
                </div>
                <div>
                    <div style="font-family:Manrope,sans-serif;font-size:1.7rem;font-weight:800;color:#1D1D1F;letter-spacing:-0.04em;">$124M</div>
                    <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:#86868B;margin-top:2px;">AUM</div>
                </div>
                <div>
                    <div style="font-family:Manrope,sans-serif;font-size:1.7rem;font-weight:800;color:#1D1D1F;letter-spacing:-0.04em;">4,800+</div>
                    <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:#86868B;margin-top:2px;">Investors</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        section_head("Team")
        t1, t2, t3 = st.columns(3, gap="medium")
        for col, m in zip([t1, t2, t3], DUMMY_TEAM):
            with col:
                st.markdown(f"""
                <div class="team-card">
                    <div class="team-avatar">{m['init']}</div>
                    <div class="team-name">{m['name']}</div>
                    <div class="team-role">{m['title']}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("""
        <hr class="ss-divider">
        <div style="font-size:0.73rem;color:#C7C7CC;text-align:center;padding-bottom:1rem;">
            ShareStone Inc. &nbsp;&middot;&nbsp; All investments involve risk &nbsp;&middot;&nbsp;
            Not financial advice &nbsp;&middot;&nbsp; © 2025
        </div>""", unsafe_allow_html=True)

        # Admin: show collected waitlist entries
        if st.session_state.waitlist:
            st.markdown("<hr class='ss-divider'>", unsafe_allow_html=True)
            section_head(f"Waitlist Signups ({len(st.session_state.waitlist)})")
            wl_rows = ""
            for entry in st.session_state.waitlist:
                wl_rows += f"""<tr>
                    <td class="td-primary">{entry['name']}</td>
                    <td>{entry['email']}</td>
                    <td>{entry['property']}</td>
                    <td>{entry['amount']}</td></tr>"""
            st.markdown(f"""
            <div class="ss-card" style="padding:0.5rem 0;">
            <table class="ss-table">
                <thead><tr><th>Name</th><th>Email</th><th>Property</th><th>Amount</th></tr></thead>
                <tbody>{wl_rows}</tbody>
            </table></div>""", unsafe_allow_html=True)
