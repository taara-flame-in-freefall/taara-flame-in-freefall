import base64
import json
import os
import time
from io import BytesIO
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="TAARA | Flame in Freefall — PSI Microgravity Fire Safety",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- LOAD ENVIRONMENT & GEMINI CLIENT ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

@st.cache_resource
def get_gemini_client(api_key: str):
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

client = get_gemini_client(API_KEY)

# --- AUTO-RESOLVE EXTENSIONS (.jpg, .jpeg, .png, .webp) ---
def resolve_asset_path(path: str) -> str:
    if os.path.exists(path):
        return path
    base, _ = os.path.splitext(path)
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        alt_path = base + ext
        if os.path.exists(alt_path):
            return alt_path
    return path

# --- IMAGE HELPER: true-alpha black keying, opacity, radial feathering ---
@st.cache_data(show_spinner=False)
def _process_image_b64(
    image_path: str,
    mtime: float,
    key_black: bool,
    opacity: float,
    vignette: bool,
    max_width: int,
) -> str:
    img = Image.open(image_path).convert("RGBA")
    if max_width and img.width > max_width:
        new_h = int(img.height * max_width / img.width)
        img = img.resize((max_width, new_h), Image.LANCZOS)
    w, h = img.size

    arr = np.asarray(img).astype(np.float32)
    alpha = arr[..., 3]
    if key_black:
        lum = arr[..., :3].max(axis=2)
        ramp = np.clip((lum - 18.0) / 37.0, 0.0, 1.0)
        alpha = alpha * ramp
    alpha = alpha * float(opacity)
    img = Image.fromarray(np.dstack([arr[..., :3], alpha]).astype(np.uint8), "RGBA")

    if vignette:
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        mx, my = int(w * 0.08), int(h * 0.08)
        draw.ellipse((mx, my, w - mx, h - my), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=max(1, int(min(w, h) * 0.12))))
        r, g, b, a = img.split()
        a = Image.composite(a, Image.new("L", (w, h), 0), mask)
        img = Image.merge("RGBA", (r, g, b, a))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def get_processed_image_b64(
    image_path: str,
    key_black: bool = False,
    opacity: float = 1.0,
    vignette: bool = False,
    max_width: int = 900,
) -> str:
    resolved_path = resolve_asset_path(image_path)
    if not os.path.exists(resolved_path):
        return ""
    try:
        return _process_image_b64(
            resolved_path, os.path.getmtime(resolved_path), key_black, opacity, vignette, max_width
        )
    except Exception:
        return ""


def render_image(b64: str, style: str = "width:100%;", alt: str = "") -> None:
    if b64:
        st.markdown(
            f'<img src="data:image/png;base64,{b64}" alt="{alt}" style="{style}" />',
            unsafe_allow_html=True,
        )


# --- GRAPHICS SETTINGS ---
IMG_SETTINGS = {
    "sidebar_unicorn_width_pct": 85,
    "tab_min_height_vh": 80,
    "tab_bg_max_width": 1400,
    "fireball_size_px": 150,
    "fireball_orbit_radius_px": 125,
    "fireball_orbit_seconds": 5,
    "fireball_stage_height_px": 340,
}

TAB_STYLE = {
    1: {"overlay_top": 0.36, "overlay_bottom": 0.50, "brightness": 1.20},
    2: {"overlay_top": 0.40, "overlay_bottom": 0.52, "brightness": 1.20},
    3: {"overlay_top": 0.18, "overlay_bottom": 0.34, "brightness": 1.75},
    4: {"overlay_top": 0.34, "overlay_bottom": 0.48, "brightness": 1.25},
}

TAB_IMAGES = {
    "tab1": "assets/flame_comparison_1g_vs_0g.jpg",
    "tab2_lunar": "assets/moon_habitat.jpg",
    "tab2_mars": "assets/mars_habitat.jpg",
    "tab2_orbital": "assets/iss_cygnus_orbit.jpg",
    "tab3": "assets/detection_suppression.jpg",
    "tab4": "assets/iss_cygnus_orbit.jpg",
}


@st.cache_data(show_spinner=False)
def _background_b64(image_path: str, mtime: float, max_width: int, quality: int, brightness: float) -> str:
    img = Image.open(image_path).convert("RGB")
    if max_width and img.width > max_width:
        img = img.resize((max_width, int(img.height * max_width / img.width)), Image.LANCZOS)
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def get_background_b64(image_path: str, max_width: int = 1400, quality: int = 72, brightness: float = 1.0) -> str:
    resolved_path = resolve_asset_path(image_path)
    if not os.path.exists(resolved_path):
        return ""
    try:
        return _background_b64(resolved_path, os.path.getmtime(resolved_path), max_width, quality, brightness)
    except Exception:
        return ""


def build_tab_background_css(target_env: str) -> str:
    if "Lunar" in target_env:
        tab2_img = TAB_IMAGES["tab2_lunar"]
    elif "Martian" in target_env:
        tab2_img = TAB_IMAGES["tab2_mars"]
    else:
        tab2_img = TAB_IMAGES["tab2_orbital"]
    images = {1: TAB_IMAGES["tab1"], 2: tab2_img, 3: TAB_IMAGES["tab3"], 4: TAB_IMAGES["tab4"]}

    rules = [".tabbg { display: none; }"]
    for n, path in images.items():
        s = TAB_STYLE[n]
        b64 = get_background_b64(path, IMG_SETTINGS["tab_bg_max_width"], brightness=s["brightness"])
        layers = f"linear-gradient(180deg, rgba(8,6,5,{s['overlay_top']}) 0%, rgba(14,8,4,{s['overlay_bottom']}) 100%)"
        if b64:
            layers += f', url("data:image/jpeg;base64,{b64}")'
        rules.append(
            f'div[role="tabpanel"]:has(.tabbg-{n}) {{ background-image: {layers}; '
            f"background-size: cover; background-position: center; background-repeat: no-repeat; "
            f"border-radius: 16px; border: 1px solid rgba(223,90,21,0.45); "
            f"box-shadow: 0 0 28px rgba(223,90,21,0.12) inset; "
            f"padding: 1.25rem 1.5rem 1.5rem 1.5rem; min-height: {IMG_SETTINGS['tab_min_height_vh']}vh; }}"
        )
    rules += [
        'div[role="tabpanel"] [data-testid="stMarkdownContainer"], div[role="tabpanel"] label { text-shadow: 0 1px 8px rgba(0,0,0,0.95); }',
        'div[role="tabpanel"] [data-testid="stPlotlyChart"] { background: rgba(8,5,3,0.55); border-radius: 12px; backdrop-filter: blur(4px); }',
        'div[role="tabpanel"] [data-testid="stDataFrame"] { background: rgba(8,5,3,0.70); border-radius: 10px; backdrop-filter: blur(4px); }',
        'div[role="tabpanel"] [data-testid="stAlert"] { backdrop-filter: blur(6px); }',
        'button[data-baseweb="tab"][aria-selected="true"], button[data-baseweb="tab"][aria-selected="true"] p { color: #ff752b !important; }',
        '[data-baseweb="tab-highlight"] { background-color: #ff752b !important; }',
        '[data-testid="stMultiSelect"] span[data-baseweb="tag"] { background-color: #c84b11 !important; border: 1px solid #ff7a2f !important; }',
    ]
    return "\n".join(rules)


def fireball_overlay_html(label: str = "Gemini is synthesizing your mission briefing...") -> str:
    b64 = get_processed_image_b64("assets/flame_emblem.jpg", key_black=True, opacity=1.0, max_width=500)
    ball_bg = f'url("data:image/png;base64,{b64}")' if b64 else "radial-gradient(circle, #ffe2a0 0%, #ff6a1a 45%, rgba(255,106,26,0) 70%)"
    size = IMG_SETTINGS["fireball_size_px"]
    radius = IMG_SETTINGS["fireball_orbit_radius_px"]
    secs = IMG_SETTINGS["fireball_orbit_seconds"]
    height = IMG_SETTINGS["fireball_stage_height_px"]
    return "\n".join([
        "<style>",
        "@keyframes fbOrbit { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }",
        "@keyframes fbSpin { from { transform: rotate(0deg); } to { transform: rotate(-720deg); } }",
        "@keyframes fbPulse { 0%, 100% { opacity: 0.55; } 50% { opacity: 1; } }",
        "@keyframes fbGlow { 0%, 100% { transform: scale(1); opacity: 0.75; } 50% { transform: scale(1.18); opacity: 1; } }",
        f".fb-stage {{ position: relative; width: 100%; height: {height}px; overflow: hidden; border-radius: 16px; "
        f"border: 1px solid rgba(255,122,47,0.5); margin: 10px 0 6px 0; "
        f"background: radial-gradient(ellipse at center, rgba(255,106,26,0.22) 0%, rgba(20,9,4,0.55) 55%, rgba(8,5,3,0.7) 100%); }}",
        f".fb-track {{ position: absolute; left: 50%; top: 50%; width: {radius * 2}px; height: {radius * 2}px; "
        f"margin: -{radius}px 0 0 -{radius}px; border: 1px dashed rgba(255,150,70,0.4); border-radius: 50%; }}",
        f".fb-core {{ position: absolute; left: 50%; top: 50%; width: 70px; height: 70px; margin: -35px 0 0 -35px; border-radius: 50%; "
        f"background: radial-gradient(circle, rgba(255,190,90,0.85) 0%, rgba(255,106,26,0.35) 55%, rgba(255,106,26,0) 75%); "
        f"animation: fbGlow 2s ease-in-out infinite; }}",
        f".fb-orbit {{ position: absolute; left: 50%; top: 50%; width: 0; height: 0; animation: fbOrbit {secs}s linear infinite; }}",
        f".fb-arm {{ position: absolute; left: {radius}px; top: 0; width: 0; height: 0; }}",
        f".fb-ball {{ position: absolute; width: {size}px; height: {size}px; left: -{size // 2}px; top: -{size // 2}px; "
        f"background-image: {ball_bg}; background-size: contain; background-repeat: no-repeat; background-position: center; "
        f"filter: drop-shadow(0 0 26px rgba(255,120,30,0.9)); animation: fbSpin {secs / 2:.1f}s linear infinite; }}",
        f".fb-label {{ position: absolute; left: 0; right: 0; bottom: 14px; text-align: center; color: #ffb27a; "
        f"font-size: 0.95rem; letter-spacing: 0.04em; text-shadow: 0 1px 8px rgba(0,0,0,0.95); animation: fbPulse 1.8s ease-in-out infinite; }}",
        "</style>",
        '<div class="fb-stage">',
        '<div class="fb-track"></div>',
        '<div class="fb-core"></div>',
        '<div class="fb-orbit"><div class="fb-arm"><div class="fb-ball"></div></div></div>',
        f'<div class="fb-label">🔥 {label}</div>',
        "</div>",
    ])


# --- COSMIC OBSIDIAN THEME ---
bg_b64 = get_processed_image_b64("assets/cosmic_banner.jpg", opacity=0.16, max_width=1600)
bg_css = (
    f'background-image: linear-gradient(180deg, rgba(8,6,5,0.82) 0%, rgba(16,8,4,0.88) 100%), url("data:image/png;base64,{bg_b64}");'
    if bg_b64
    else "background: radial-gradient(circle at 80% 10%, #260f04 0%, #090605 50%, #040406 100%);"
)

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        {bg_css}
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: #f5f5f7;
    }}
    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0);
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0e0805 0%, #170b05 100%) !important;
        border-right: 1px solid rgba(223, 90, 21, 0.45);
    }}
    span[data-baseweb="tag"] {{
        background-color: #c84b11 !important;
        border: 1px solid #ff7a2f !important;
    }}
    [data-testid="stMetric"] {{
        background: rgba(20, 11, 6, 0.72);
        border: 1px solid rgba(223, 90, 21, 0.4);
        padding: 12px 16px;
        border-radius: 10px;
    }}
    [data-testid="stMetricValue"] {{
        color: #ff752b !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #ff752b !important;
        border-bottom-color: #ff752b !important;
    }}
    .stButton > button[kind="primary"], .stDownloadButton > button {{
        background: linear-gradient(90deg, #df5a15 0%, #ff7a2f 100%) !important;
        border: none !important;
        color: #ffffff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- LOAD & NORMALIZE PSI DATASET + VERIFIED EVIDENCE LAYER ---
@st.cache_data
def load_psi_data(
    raw_filepath: str = "psi_data.json",
    verified_filepath: str = os.path.join("data", "verified_psi.json"),
):
    with open(raw_filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    verified = {}
    if os.path.exists(verified_filepath):
        with open(verified_filepath, "r", encoding="utf-8") as f:
            verified = json.load(f)

    records = []
    for psi_key, item in raw.items():
        v_rec = verified.get(psi_key, {})
        cond = v_rec.get("conditions", {})

        pillar = item.get("pillar", "unknown")
        parent_id = item.get("parent_investigation")
        if pillar == "unknown" and parent_id and parent_id in raw:
            pillar = f"{raw[parent_id].get('pillar', 'General')} (Ground Study)"
        elif pillar == "unknown":
            pillar = f"Non-Combustion ({item.get('research_area', 'Other')})"

        fire_fn = cond.get("fire_safety_function", "unknown")
        is_combustion = (item.get("research_area") == "Combustion Science") and (fire_fn != "out_of_scope")
        is_primary = bool(item.get("is_primary", False))
        pub_count = len(item.get("publications", []))

        def _val(field_name: str) -> str:
            entry = cond.get(field_name)
            if isinstance(entry, dict) and entry.get("value"):
                return str(entry["value"])
            return "Not specified"

        records.append({
            "psi_id": item.get("psi_id", psi_key),
            "acronym": item.get("acronym") if item.get("acronym") != "unknown" else "—",
            "name": item.get("name", ""),
            "pillar": pillar,
            "raw_pillar": item.get("pillar", "unknown"),
            "fire_safety_function": fire_fn,
            "environment_relevance": ", ".join(cond.get("environment_relevance", [])) or "—",
            "human_verified": bool(v_rec.get("human_verified", False)),
            "fuel_or_material": _val("fuel_type") if _val("fuel_type") != "Not specified" else _val("material_tested"),
            "o2_concentration": _val("o2_concentration"),
            "pressure": _val("pressure"),
            "flow_speed": _val("flow_speed"),
            "is_primary": is_primary,
            "is_combustion": is_combustion,
            "project_type": item.get("project_type", "unknown"),
            "research_area": item.get("research_area", "unknown"),
            "sub_research_area": item.get("sub_research_area", "unknown"),
            "flight_platform": item.get("flight_platform", "unknown"),
            "hardware": item.get("hardware", "unknown"),
            "managing_center": item.get("managing_center", "unknown"),
            "start_date": item.get("start_date", "unknown"),
            "end_date": item.get("end_date", "unknown"),
            "parent_investigation": parent_id or "None (Primary)",
            "related_ground_studies": ", ".join(item.get("related_ground_studies", [])) or "None",
            "pub_count": pub_count,
            "objective": item.get("objective", ""),
            "approach": item.get("approach", ""),
            "hypothesis": item.get("hypothesis", ""),
            "research_impacts": item.get("research_impacts", ""),
            "doi": item.get("doi", ""),
            "publications": item.get("publications", []),
            "contacts": item.get("contacts", []),
        })

    df = pd.DataFrame(records)
    df["psi_num"] = df["psi_id"].str.replace("PSI-", "", regex=False).astype(int)
    df = df.sort_values("psi_num").reset_index(drop=True)
    return df, raw, verified

def calculate_mission_score(row: pd.Series, env_profile: str) -> float:
    if not row["is_combustion"] or row["fire_safety_function"] == "out_of_scope":
        return 12.0

    text_blob = (
        f"{row['name']} {row['objective']} {row['hypothesis']} {row['research_impacts']} "
        f"{row['sub_research_area']} {row['o2_concentration']} {row['pressure']} {row['fuel_or_material']}"
    ).lower()
    pillar = row["pillar"].lower()

    score = 32.0
    if row["is_primary"]:
        score += 16.0
    if row["human_verified"]:
        score += 2.0
    score += min(row["pub_count"] * 0.45, 14.0)

    if "Lunar" in env_profile:
        if "lunar_base" in row["environment_relevance"]:
            score += 4.0
        if "solids" in pillar:
            score += 20.0
        elif "detection" in pillar:
            score += 14.0
        elif "gas flames" in pillar:
            score += 12.0
        elif "droplets" in pillar:
            score += 10.0

        for kw in ["oxygen", "30%", "34%", "10.2", "8.2", "flammability", "pmma", "sibal", "saffire", "bass"]:
            if kw in text_blob:
                score += 2.2

    elif "Martian" in env_profile:
        if "solids" in pillar:
            score += 18.0
        elif "gas flames" in pillar:
            score += 17.0
        elif "detection" in pillar:
            score += 15.0
        elif "droplets" in pillar:
            score += 11.0

        for kw in ["buoyancy", "concurrent", "opposed", "coflow", "airflow", "ventilation", "smoke", "scale"]:
            if kw in text_blob:
                score += 2.5

    else:
        if "droplets" in pillar:
            score += 20.0
        elif "detection" in pillar:
            score += 19.0
        elif "gas flames" in pillar:
            score += 16.0
        elif "solids" in pillar:
            score += 14.0

        for kw in ["cool flame", "extinguishment", "aerosol", "particulate", "quiescent", "spherical", "suppressant"]:
            if kw in text_blob:
                score += 2.5

    return round(min(score, 100.0), 1)

try:
    df, raw_dict, verified_dict = load_psi_data()
except Exception as e:
    st.error(f"Could not load PSI dataset files (`psi_data.json` / `data/verified_psi.json`): {e}")
    st.stop()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    flame_b64 = get_processed_image_b64("assets/flame_emblem.jpg", key_black=True, opacity=0.95, max_width=400)
    render_image(flame_b64, "width:135px; mix-blend-mode:screen; display:block; margin:0 auto -10px auto;", "TAARA flame emblem")
    st.title("🔥 Team TAARA")
    st.caption("NASA Space Apps Challenge | Flame in Freefall")
    st.divider()

    unicorn_b64 = get_processed_image_b64("assets/shadow_unicorn.jpg", opacity=1.0, vignette=True, max_width=500)
    render_image(
        unicorn_b64,
        f"width:{IMG_SETTINGS['sidebar_unicorn_width_pct']}%; display:block; margin:0 auto 4px auto; "
        "filter:drop-shadow(0 0 18px rgba(223,90,21,0.45));",
        "Shadow unicorn",
    )
    if unicorn_b64:
        st.markdown(
            '<div style="text-align:center; font-size:0.75rem; color:#c88a65; margin-bottom:6px;">'
            'Cross-Domain Anomaly Controls</div>',
            unsafe_allow_html=True,
        )
        st.divider()

    target_env = st.selectbox(
        "Target Mission Environment",
        [
            "Lunar Habitat (Moon — 1/6 g, ≥30% O₂ / ≤10.2 psi Exploration Atmosphere)",
            "Martian Habitat (Mars — 3/8 g, Partial Gravity Buoyancy Transition)",
            "Orbital Transit / ISS (Microgravity — 0 g, Forced Ventilation)",
        ],
    )

    include_non_combustion = st.checkbox(
        "Include Out-of-Scope Controls (PSI-108, PSI-181)",
        value=False,
        help="Shows Fluid Physics (PSI-108) & Materials Science/Soldering (PSI-181) records flagged as out_of_scope in verified_psi.json.",
    )

    study_filter = st.radio(
        "Investigation Tier",
        ["All Investigations", "Primary Flight Experiments Only", "Ground Validation Studies Only"],
    )

    available_pillars = sorted(df["pillar"].unique().tolist())
    selected_pillars = st.multiselect(
        "Combustion & Science Pillars",
        options=available_pillars,
        default=available_pillars,
    )

    st.divider()
    verified_count = int(df["human_verified"].sum())
    st.markdown(f"**Dataset Audit:** ✅ `{verified_count}/{len(df)}` Human-Verified")
    st.markdown("**API Status:** " + ("🟢 Gemini Connected" if client else "🔴 Missing `GEMINI_API_KEY` in `.env`"))

# --- COMPUTE DYNAMIC SCORES & APPLY FILTERS ---
df["readiness_score"] = df.apply(lambda r: calculate_mission_score(r, target_env), axis=1)

filtered_df = df.copy()
if not include_non_combustion:
    filtered_df = filtered_df[filtered_df["is_combustion"]]
if study_filter == "Primary Flight Experiments Only":
    filtered_df = filtered_df[filtered_df["is_primary"]]
elif study_filter == "Ground Validation Studies Only":
    filtered_df = filtered_df[~filtered_df["is_primary"]]
if selected_pillars:
    filtered_df = filtered_df[filtered_df["pillar"].isin(selected_pillars)]

# --- HEADER & KPI METRICS ---
hero_left, hero_right = st.columns([2.3, 1])
with hero_left:
    st.title("🔥 Flame in Freefall: Microgravity Combustion Intelligence Dashboard")
    st.markdown(
        f"**Active Mission Profile:** `{target_env}` — Bounding partial-gravity fire safety using audited NASA PSI $0g$ flight & $1g$ ground datasets."
    )
with hero_right:
    astro_b64 = get_processed_image_b64("assets/astronaut_fire.jpg", opacity=0.88, vignette=True)
    render_image(astro_b64, "width:100%; border-radius:14px;", "Astronaut observing a microgravity flame")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Filtered Investigations", len(filtered_df), f"of {len(df)} audited PSI records")
col2.metric("Primary Flight Studies", int(filtered_df["is_primary"].sum()))
col3.metric("Peer-Reviewed Papers", int(filtered_df["pub_count"].sum()))
top_row = filtered_df.sort_values(["readiness_score", "pub_count"], ascending=[False, False]).iloc[0] if not filtered_df.empty else None
col4.metric(
    "Top Ranked Dataset",
    f"{top_row['psi_id']} ({top_row['acronym']})" if top_row is not None else "N/A",
    f"Score: {top_row['readiness_score']}/100" if top_row is not None else "",
)

st.divider()

# --- TABS ---
st.markdown(f"<style>{build_tab_background_css(target_env)}</style>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Mission Ranking & Analytics",
    "🤖 AI Fire-Safety Synthesizer",
    "🔬 Investigation Deep-Dive & Evidence",
    "🔗 Flight-to-Ground Lineage",
])

# === TAB 1: RANKING & ANALYTICS ===
with tab1:
    st.markdown('<span class="tabbg tabbg-1"></span>', unsafe_allow_html=True)
    c_left, c_right = st.columns([1.3, 1])

    with c_left:
        st.subheader("Fire-Safety Relevance Ranking")
        ranked_df = filtered_df.sort_values(["readiness_score", "pub_count"], ascending=[True, True])
        fig_bar = px.bar(
            ranked_df,
            x="readiness_score",
            y="psi_id",
            color="pillar",
            orientation="h",
            hover_data=["acronym", "name", "fire_safety_function", "o2_concentration", "pressure", "pub_count"],
            labels={"readiness_score": "Mission Fire-Safety Score (0–100)", "psi_id": "PSI ID"},
            height=540,
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_right:
        st.subheader("Research Coverage by Pillar & Literature Output")
        fig_sun = px.treemap(
            filtered_df,
            path=["research_area", "pillar", "psi_id"],
            values="pub_count",
            color="readiness_score",
            color_continuous_scale="YlOrRd",
            hover_data=["acronym", "name"],
            height=540,
        )
        fig_sun.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_sun, use_container_width=True)

    header_col, btn_col = st.columns([3, 1])
    with header_col:
        st.subheader("Ranked PSI Investigation Matrix (with Audited Test Regimes)")
    with btn_col:
        export_cols = [
            "psi_id", "acronym", "name", "pillar", "fire_safety_function",
            "fuel_or_material", "o2_concentration", "pressure", "flow_speed",
            "pub_count", "readiness_score", "parent_investigation"
        ]
        ranked_table = filtered_df.sort_values(["readiness_score", "pub_count"], ascending=[False, False])[export_cols]
        st.download_button(
            label="📥 Export Ranked CSV",
            data=ranked_table.to_csv(index=False).encode("utf-8"),
            file_name="taara_psi_ranked.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.dataframe(ranked_table, use_container_width=True, hide_index=True)

# === TAB 2: AI FIRE-SAFETY SYNTHESIZER ===
with tab2:
    st.markdown('<span class="tabbg tabbg-2"></span>', unsafe_allow_html=True)
    t2_left, t2_right = st.columns([3, 1])
    with t2_left:
        st.subheader("🤖 Gemini-Powered Partial-Gravity Extrapolation Engine")
        st.markdown(
            "Select one or more PSI investigations to synthesize how $0g$ ISS findings and $1g$ ground models bound fire detection, material screening, and suppression for **Moon ($1/6g$)** and **Mars ($3/8g$)** habitats — backed by verbatim NASA evidence quotes."
        )
    with t2_right:
        astro_tab2 = get_processed_image_b64("assets/astronaut_fire.jpg", opacity=0.82, vignette=True, max_width=600)
        render_image(astro_tab2, "width:100%;", "Astronaut observing a microgravity flame")

    default_top4 = filtered_df.sort_values(["readiness_score", "pub_count"], ascending=[False, False])["psi_id"].head(4).tolist()

    selected_ids = st.multiselect(
        "Select PSI Investigations to Analyze (Pre-loaded with Top 4 for Active Environment)",
        options=df["psi_id"].tolist(),
        default=default_top4,
        format_func=lambda x: f"{x} ({raw_dict[x].get('acronym', '')}) — {raw_dict[x].get('name', '')[:65]}",
    )

    col_goal, col_mode = st.columns([2, 1.2])
    with col_goal:
        analysis_goal = st.selectbox(
            "Analysis Focus",
            [
                "Bound Moon (1/6 g) & Mars (3/8 g) Habitat Fire Safety Using 0g & 1g Data",
                "Compare Material Flammability Screening (NASA-STD-6001 1g vs Microgravity)",
                "Design Smoke Detection & Suppression Protocol for Low-Gravity Habitats",
                "Audit Out-of-Scope & Unspecified Experimental Parameters Across Selected Records",
            ],
        )
    with col_mode:
        ai_speed_mode = st.radio(
            "AI Inference Mode",
            [
                "⚡ Fast AI (Lite Tier — Instant Demo)",
                "🧠 Deep Research Mode (Flagship Tier — Full Synthesis)",
            ],
            help="Fast AI uses high-quota Lite models for rapid responses; Deep Research uses flagship models for deeper engineering reasoning.",
        )

    if st.button("🚀 Run AI Mission Synthesis", type="primary"):
        if not client:
            st.error("Gemini API key not found. Add `GEMINI_API_KEY=your_key` inside your `.env` file.")
        elif not selected_ids:
            st.warning("Please select at least one PSI investigation.")
        else:
            context_payload = []
            for pid in selected_ids:
                rec = raw_dict[pid]
                v_rec = verified_dict.get(pid, {})
                score_val = df.loc[df["psi_id"] == pid, "readiness_score"].values[0]
                context_payload.append({
                    "psi_id": pid,
                    "mission_relevance_score": float(score_val),
                    "name": rec.get("name"),
                    "acronym": rec.get("acronym"),
                    "research_area": rec.get("research_area"),
                    "pillar": rec.get("pillar"),
                    "project_type": rec.get("project_type"),
                    "human_verified": v_rec.get("human_verified", False),
                    "audited_conditions_with_evidence": v_rec.get("conditions", {}),
                    "objective": rec.get("objective"),
                    "approach": rec.get("approach"),
                    "hypothesis": rec.get("hypothesis"),
                    "research_impacts": rec.get("research_impacts"),
                    "sample_publications": [p.get("title") for p in rec.get("publications", [])[:5]],
                })

            is_deep = "Deep Research" in ai_speed_mode
            depth_instruction = (
                "Provide an exhaustive, publication-grade engineering analysis covering coupled heat/mass transport, boundary layer scaling, and cross-investigation trade-offs."
                if is_deep
                else "Provide a crisp, high-impact executive summary with concise bullet points optimized for rapid mission review."
            )

            prompt = f"""
You are a NASA Spacecraft Fire Safety & Microgravity Combustion Scientist supporting Team TAARA for the NASA Space Apps Challenge ('Flame in Freefall').

Target Mission Profile: {target_env}
Analysis Goal: {analysis_goal}
Response Style: {depth_instruction}

CRITICAL GROUNDING & SCIENTIFIC INTEGRITY RULES:
- Cite the exact PSI ID (e.g., [PSI-26]) for every experimental claim.
- Use ONLY experimental parameters, materials, concentrations, pressures, and metrics explicitly present in `audited_conditions_with_evidence` or the NASA metadata below.
- Where a field in `audited_conditions_with_evidence` has `"value": null`, explicitly state "not specified in PSI archive" — NEVER invent or extrapolate missing test parameters.
- Remember that NASA PSI contains 0g flight and 1g ground/modeling datasets—frame Moon (1/6g) and Mars (3/8g) conclusions as engineering bounds/extrapolations rather than direct partial-gravity flight measurements.

Supplied Audited NASA PSI Investigations:
{json.dumps(context_payload, indent=2)}

Provide a structured, rigorous engineering assessment with:
1. **Executive Risk Verdict** (Rank the selected studies by criticality for {target_env} with PSI citations).
2. **Physics Translation ($1g \\rightarrow 0g$ Bounding $1/6g$ & $3/8g$)**: Explain how buoyant convection suppression, radiative extinction, limiting oxygen index (LOI), soot/aerosol aggregation, or cool-flame regimes shift across gravity regimes based on the cited studies and their audited test conditions.
3. **Actionable Habitat Engineering Controls**: Specific recommendations for material selection, ventilation management, smoke detectors, or suppressants grounded in the supplied studies.
4. **Data Anomalies & Scope Caveats**: Explicitly flag any `out_of_scope` non-combustion controls (`PSI-108` Fluid Physics, `PSI-181` Soldering/Materials Science) or null test conditions.
"""
            if is_deep:
                models_to_try = [
                    "gemini-3.8-flash",
                    "gemini-3.7-flash",
                    "gemini-2.5-pro",
                    "gemini-3.6-flash",
                    "gemini-3.5-flash",
                    "gemini-3.5-flash-lite",
                    "gemini-3.1-flash-lite",
                    "gemini-2.5-flash-lite",
                ]
                spinner_label = "Running Deep Research synthesis with flagship Gemini models..."
            else:
                models_to_try = [
                    "gemini-3.5-flash-lite",
                    "gemini-3.1-flash-lite",
                    "gemini-2.5-flash-lite",
                    "gemini-3.5-flash",
                    "gemini-3.6-flash",
                    "gemini-3.7-flash",
                    "gemini-3.8-flash",
                    "gemini-2.5-pro",
                ]
                spinner_label = "Synthesizing rapid mission briefing with Fast AI (Lite tier)..."

            fire_slot = st.empty()
            fire_slot.markdown(fireball_overlay_html(spinner_label), unsafe_allow_html=True)
            with st.spinner(spinner_label):
                response_text = None
                active_model = None
                last_err = None

                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        response_text = response.text
                        active_model = model_name
                        break
                    except Exception as api_err:
                        last_err = api_err
                        time.sleep(2 if not is_deep else 3)
                        continue

                fire_slot.empty()

                if response_text:
                    st.caption(f"Mode: **{ai_speed_mode}** | Engine: `{active_model}` • Grounded strictly in human-verified NASA PSI evidence")
                    st.markdown(response_text)
                else:
                    st.error(f"Gemini API temporarily busy across all rotated models: {last_err}")

# === TAB 3: INVESTIGATION DEEP-DIVE & VERIFIED EVIDENCE ===
with tab3:
    st.markdown('<span class="tabbg tabbg-3"></span>', unsafe_allow_html=True)
    st.subheader("🔬 Investigation Explorer & Audited Evidence Trail")
    chosen_id = st.selectbox(
        "Inspect Investigation",
        options=df["psi_id"].tolist(),
        format_func=lambda x: f"{x} — {raw_dict[x].get('name', '')}",
    )
    item = raw_dict[chosen_id]
    v_item = verified_dict.get(chosen_id, {})
    v_cond = v_item.get("conditions", {})

    m1, m2, m3, m4 = st.columns(4)
    m1.info(f"**Acronym:** {item.get('acronym', 'unknown')}")
    m2.info(f"**Pillar:** {item.get('pillar', 'unknown')}")
    m3.info(f"**Function:** `{v_cond.get('fire_safety_function', 'unknown')}`")
    m4.info(f"**Audit Status:** {'✅ Human-Verified' if v_item.get('human_verified') else '⏳ Pending'}")

    st.markdown(f"### {item.get('name')}")
    st.caption(
        f"DOI: `{item.get('doi')}` | Platform: `{item.get('flight_platform')}` | "
        f"Managing Center: {item.get('managing_center')} | Dates: {item.get('start_date')} to {item.get('end_date')}"
    )

    st.markdown("#### ✅ Audited Experimental Conditions & Verbatim NASA Source Quotes")
    param_fields = [
        ("Fuel Type", "fuel_type"),
        ("Material Tested", "material_tested"),
        ("O₂ Concentration", "o2_concentration"),
        ("Ambient Pressure", "pressure"),
        ("Flow / Ventilation Speed", "flow_speed"),
        ("Sample Geometry / Size", "sample_geometry_size"),
        ("Diluents / Suppressants", "diluents_suppressants"),
        ("Sensors & Diagnostics", "sensors_measurements"),
        ("Test Variables", "test_variables"),
    ]
    evidence_rows = []
    for label, key in param_fields:
        entry = v_cond.get(key, {})
        val = entry.get("value") if isinstance(entry, dict) else None
        ev = entry.get("evidence") if isinstance(entry, dict) else None
        evidence_rows.append({
            "Experimental Parameter": label,
            "Verified Value": val if val is not None else "null (Not stated in PSI record)",
            "Verbatim NASA PSI Source Quote": ev if ev is not None else "—",
        })
    st.dataframe(pd.DataFrame(evidence_rows), use_container_width=True, hide_index=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🎯 Objective & Hypothesis")
        st.write("**Objective:**", item.get("objective"))
        st.write("**Hypothesis:**", item.get("hypothesis"))
    with col_b:
        st.markdown("#### 🧪 Experimental Approach & Hardware")
        st.write("**Hardware:**", item.get("hardware"))
        st.write("**Approach:**", item.get("approach"))

    st.markdown("#### 🚀 Spacecraft Fire Safety & Earth Research Impacts")
    st.success(item.get("research_impacts"))

    pubs = item.get("publications", [])
    st.markdown(f"#### 📚 Associated Publications ({len(pubs)})")
    if pubs:
        st.dataframe(pd.DataFrame(pubs), use_container_width=True, hide_index=True)
    else:
        st.write("No publications listed in this PSI record.")

# === TAB 4: FLIGHT-TO-GROUND LINEAGE ===
with tab4:
    st.markdown('<span class="tabbg tabbg-4"></span>', unsafe_allow_html=True)
    st.subheader("🔗 Flight-to-Ground Study Lineage & Cross-Domain Controls")
    st.markdown(
        "Shows how ISS/Cygnus primary flight experiments connect to follow-on ground CFD/modeling investigations in your dataset, plus `out_of_scope` non-combustion control records (`PSI-108`, `PSI-181`)."
    )

    lineage_rows = []
    for pid, rec in raw_dict.items():
        v_fn = verified_dict.get(pid, {}).get("conditions", {}).get("fire_safety_function", "unknown")
        if rec.get("parent_investigation") or rec.get("related_ground_studies") or v_fn == "out_of_scope":
            lineage_rows.append({
                "PSI ID": pid,
                "Acronym": rec.get("acronym"),
                "Name": rec.get("name"),
                "Research Area": rec.get("research_area"),
                "Fire Safety Function": v_fn,
                "Parent Flight Study": rec.get("parent_investigation") or "—",
                "Linked Ground Studies": ", ".join(rec.get("related_ground_studies", [])) or "—",
            })

    st.dataframe(pd.DataFrame(lineage_rows), use_container_width=True, hide_index=True)