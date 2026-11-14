import json
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load environment variables (.env locally, st.secrets on Streamlit Cloud)
load_dotenv()

st.set_page_config(
    page_title="TAARA | Flame in Freefall — Microgravity Fire Safety SI",
    page_icon="🔥",
    layout="wide",
)

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None
    return genai.Client(api_key=api_key) if api_key else None

client = get_gemini_client()

SYSTEM_PROMPT = """
You are an aerospace fire-safety research assistant built by Team TAARA for the 2026 NASA Space Apps Challenge (Flame in Freefall).
Analyze NASA Physical Sciences Informatics (PSI) microgravity combustion investigations for engineers, researchers, and students.
Always:
1. Contrast microgravity (0g) behavior against normal gravity (1g) buoyancy-driven combustion.
2. Reference specific experimental variables (fuel type, sample geometry, oxygen %, airflow speed in cm/s, diluents, sensors).
3. Translate findings into concrete spacecraft fire-safety rules (smoke detector thresholds, cabin ventilation shutoff rules, material flammability limits, suppression margins).
Keep outputs structured, quantitative, and grounded strictly in the provided NASA PSI dataset.
"""

def ask_gemini(prompt: str) -> str:
    if not client:
        return "⚠️ `GEMINI_API_KEY` not found. Check your `.env` file locally or Secrets in Streamlit Cloud."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
            ),
        )
        return response.text
    except Exception as e:
        return f"Gemini API Error: {e}"

# 2. Load data/verified_psi.json adaptively
@st.cache_data
def load_verified_data() -> pd.DataFrame:
    json_path = Path("data/verified_psi.json")
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, list):
                df = pd.DataFrame(raw)
            elif isinstance(raw, dict):
                # Support dict wrapped under a top-level key like {"investigations": [...]} or keyed by PSI ID
                list_candidates = [v for v in raw.values() if isinstance(v, list)]
                if list_candidates:
                    df = pd.DataFrame(list_candidates[0])
                else:
                    df = pd.DataFrame.from_dict(raw, orient="index").reset_index()
            else:
                df = pd.DataFrame()

            if not df.empty:
                return df
        except Exception as e:
            st.warning(f"Could not parse `data/verified_psi.json` automatically ({e}). Loading fallback baseline.")

    # Baseline fallback aligned with NASA PSI Flame in Freefall investigations
    return pd.DataFrame([
        {
            "psi_id": "PSI-FLEX",
            "acronym": "FLEX",
            "title": "Flame Extinguishment Experiment",
            "fuel_type": "Liquid Droplets (Heptane, Methanol)",
            "oxygen_pct": 21.0,
            "airflow_cm_s": 0.0,
            "sensors": "UV/Visible radiometers, high-speed cameras, GC",
            "objective": "Determine minimum suppressant concentrations and cool-flame extinction limits in 0g.",
            "fire_risk_score": 9.2,
        },
        {
            "psi_id": "PSI-BASS",
            "acronym": "BASS / BASS-II",
            "title": "Burning and Suppression of Solids",
            "fuel_type": "Solid Polymers & Fabrics (PMMA, Nomex, Cotton-Fiberglass)",
            "oxygen_pct": 18.0,
            "airflow_cm_s": 10.0,
            "sensors": "IR/HD video, thermocouples, radiometers",
            "objective": "Measure solid-fuel flame spread rates and extinction limits in low-speed cabin flows.",
            "fire_risk_score": 9.5,
        },
        {
            "psi_id": "PSI-SAME",
            "acronym": "SAME / SAME-R",
            "title": "Smoke and Aerosol Measurement Experiment",
            "fuel_type": "Spacecraft Wiring & Polymers (Kapton, Teflon, Silicone)",
            "oxygen_pct": 21.0,
            "airflow_cm_s": 5.0,
            "sensors": "Laser extinction, ionization/photoelectric smoke detectors",
            "objective": "Characterize smoke particle size distributions from overheated spacecraft materials.",
            "fire_risk_score": 8.9,
        },
        {
            "psi_id": "PSI-EFIELD",
            "acronym": "E-FIELD Flames (ACME)",
            "title": "Electric-Field Effects on Laminar Diffusion Flames",
            "fuel_type": "Gaseous Fuels (Methane, Ethylene)",
            "oxygen_pct": 21.0,
            "airflow_cm_s": 8.0,
            "sensors": "Ion current sensors, high-speed imaging, radiometers",
            "objective": "Use electric fields to mimic partial gravity (Moon/Mars) and actively control flames.",
            "fire_risk_score": 8.3,
        },
        {
            "psi_id": "PSI-181",
            "acronym": "PSI-181 (SOLDER)",
            "title": "Microgravity Soldering & Electronic Joint Reliability",
            "fuel_type": "Rosin/Polymer Flux & PCB Substrates",
            "oxygen_pct": 21.0,
            "airflow_cm_s": 2.0,
            "sensors": "Thermal imaging, optical microscopy, X-ray inspection",
            "objective": "Evaluate thermal behavior and flux outgassing during in-space electronics repair.",
            "fire_risk_score": 7.6,
        },
    ])

df = load_verified_data()

# --- Header ---
st.title("🔥 Flame in Freefall — Microgravity Fire Safety SI Dashboard")
st.caption("Team TAARA | NASA Space Apps Challenge 2026 | Powered by NASA PSI Data & Gemini")

# --- Sidebar Dynamic Filters ---
st.sidebar.header("🔬 Filter & Rank Experiments")
search_term = st.sidebar.text_input("Search keyword (fuel, sensor, PSI ID, acronym):", "")

filtered_df = df.copy()
if search_term.strip():
    mask = filtered_df.astype(str).apply(
        lambda col: col.str.contains(search_term, case=False, na=False)
    ).any(axis=1)
    filtered_df = filtered_df[mask]

numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()
text_cols = [c for c in filtered_df.columns if c not in numeric_cols]

# --- Top Metrics ---
m1, m2, m3 = st.columns(3)
m1.metric("Verified PSI Records Loaded", len(filtered_df))
m2.metric("Data Attributes Tracked", len(filtered_df.columns))
m3.metric("SI Engine Status", "Connected (Gemini 2.5 Flash)" if client else "Missing API Key")

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs([
    "📊 Rank & Compare PSI Experiments",
    "🧠 SI Fire-Safety Interpreter",
    "📂 Extracted / Raw PSI Files",
])

with tab1:
    st.subheader("Microgravity Combustion Parameter Comparison & Ranking")
    if filtered_df.empty:
        st.warning("No records match your search filter.")
    else:
        if numeric_cols and text_cols:
            c_left, c_right = st.columns([1.2, 1.3])
            with c_left:
                rank_metric = st.selectbox("Rank / Plot by Numeric Metric:", numeric_cols, index=len(numeric_cols) - 1)
                label_col = st.selectbox("Label Axis:", text_cols, index=0)
                sorted_df = filtered_df.sort_values(by=rank_metric, ascending=True)
                fig = px.bar(
                    sorted_df,
                    x=rank_metric,
                    y=label_col,
                    orientation="h",
                    text=rank_metric,
                    title=f"Comparison by {rank_metric}",
                )
                fig.update_layout(height=430)
                st.plotly_chart(fig, width="stretch")
            with c_right:
                st.dataframe(filtered_df, width="stretch", height=430)
        else:
            st.dataframe(filtered_df, width="stretch")

with tab2:
    st.subheader("SI-Powered Experiment Breakdown & Spacecraft Safety Insights")
    if filtered_df.empty:
        st.info("Clear the sidebar search filter to select an experiment.")
    else:
        label_col = text_cols[0] if text_cols else filtered_df.columns[0]
        options = [f"{i}: {row[label_col]}" for i, row in filtered_df.iterrows()]
        choice = st.selectbox("Choose a NASA PSI Investigation to Interpret:", options)
        selected_idx = int(choice.split(":")[0])
        record = filtered_df.loc[selected_idx].to_dict()

        with st.expander("📋 Verified Experiment Parameters", expanded=True):
            st.json(record)

        custom_q = st.text_input(
            "Ask a specific spacecraft engineering question (or leave blank for full synthesis):",
            placeholder="e.g., How does low-speed cabin ventilation affect flame spread and smoke detection here?",
        )

        if st.button("Generate SI Fire Safety Analysis", type="primary"):
            with st.spinner("Analyzing microgravity combustion parameters..."):
                question = custom_q.strip() or (
                    "1) Summarize the experimental objectives, fuel/sample geometry, oxygen %, airflow speed, and sensors.\n"
                    "2) Explain how 0g behavior diverges from 1g buoyancy-driven combustion.\n"
                    "3) Provide 3 concrete spacecraft fire-safety design or operational recommendations."
                )
                prompt = f"NASA PSI Record:\n{json.dumps(record, indent=2)}\n\nTask:\n{question}"
                st.markdown(ask_gemini(prompt))

with tab3:
    st.subheader("Inspect Local Files (`data/extracted` & `data/raw`) or Upload CSV")
    local_files = []
    for folder in ["data/extracted", "data/raw"]:
        p = Path(folder)
        if p.exists():
            local_files.extend(sorted(p.rglob("*.csv")))
            local_files.extend(sorted(p.rglob("*.json")))

    if local_files:
        selected_file = st.selectbox("Select a local file from your repo:", [str(f) for f in local_files])
        file_path = Path(selected_file)
        if file_path.suffix == ".csv":
            sub_df = pd.read_csv(file_path)
            st.write(f"**{file_path.name}** — {sub_df.shape[0]} rows × {sub_df.shape[1]} columns")
            st.dataframe(sub_df.head(30), width="stretch")
            num_cols = sub_df.select_dtypes(include="number").columns.tolist()
            if len(num_cols) >= 2:
                x_c = st.selectbox("X-Axis", num_cols, index=0, key="local_x")
                y_c = st.selectbox("Y-Axis", num_cols, index=1, key="local_y")
                st.plotly_chart(px.line(sub_df, x=x_c, y=y_c, title=f"{y_c} vs {x_c}"), width="stretch")
        elif file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as jf:
                st.json(json.load(jf))
    else:
        st.info("No `.csv` or `.json` files detected yet inside `data/extracted` or `data/raw`.")

    uploaded = st.file_uploader("Or upload any NASA PSI CSV file directly:", type=["csv"])
    if uploaded:
        up_df = pd.read_csv(uploaded)
        st.dataframe(up_df.head(30), width="stretch")
        if st.button("Interpret Uploaded CSV with SI"):
            with st.spinner("Analyzing sensor statistics..."):
                summary = up_df.describe().to_string()
                st.markdown(ask_gemini(f"File: {uploaded.name}\nColumns: {list(up_df.columns)}\nStats:\n{summary}"))