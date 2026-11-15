# TAARA — Flame in Freefall

**NASA Space Apps Challenge 2026 · Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data**

An interactive dashboard that finds, ranks, compares and interprets NASA Physical Sciences Informatics (PSI) combustion investigations, so researchers and engineers can quickly see what microgravity fire research says about fire safety for spacecraft, stations, lunar and Martian habitats and pressurized rovers.

> **Live demo:** _add Streamlit URL_ · **Demo video:** _add link_ · **Team:** _add names_

## Why this matters
Fire is one of the most dangerous hazards in crewed spaceflight: Apollo 1 (pure-oxygen cabin fire), Apollo 13 (oxygen tank explosion), and the 1997 Mir fire (oxygen generator failure). Planned Moon habitats are expected to use higher oxygen concentrations (30% or more at 10.2 psi or less), which makes materials more flammable. The PSI archive holds decades of relevant data, but it is hard to find, compare and interpret.

## What the dashboard does
| Capability | Where |
|---|---|
| Rank investigations for a chosen habitat environment with a transparent, adjustable rubric | Ranking tab |
| Side-by-side comparison of investigations (fuels, O₂, pressure, flow, sensors, variables) | Compare tab |
| Model-ready conditions table, exportable as CSV, with DOI links | Data tab |
| SI-generated fire-safety synthesis, grounded in the selected records and citing PSI IDs | SI tab |
| Flight-to-ground study lineage | Lineage tab |
| Earth applications (firefighter air tanks, smoke detection, protective clothing) | Earth tab |

_Update this table to match what is actually shipped._

## Data
- 26 records from the PSI Data Repository search for "combustion" (flight investigations plus ground/modeling studies built on flight data; PSI-108 and PSI-181 are non-combustion controls and hidden by default).
- `extract.py` deterministically parses each `i_Investigation.txt` (ISA-Tab) into `psi_data.json`. No AI is involved in this step.
- `extract_conditions.py` uses Gemini **once, offline** to convert free text into structured test conditions (`data/verified_psi.json`). Each value carries a verbatim evidence sentence; anything not stated is `null`. Records are human-reviewed (`human_verified`).
- **Limitation:** PSI currently holds no partial-gravity (Moon/Mars) combustion data. The dashboard treats microgravity and normal-gravity results as bounding cases and labels any Moon/Mars interpretation as extrapolation.

## How the SI is used
See [`docs/si_usage_log.md`](docs/si_usage_log.md). In short: (1) offline structured extraction with evidence, (2) grounded synthesis restricted to supplied records, (3) cached results for reliable demos. Every SI output is labeled in the UI.

## Run locally
```bash
git clone <repo-url> && cd taara-flame-in-freefall
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then add your own GEMINI_API_KEY
streamlit run app.py
```
Rebuild the data:
```bash
python extract.py && cp build/output/investigations.json psi_data.json
python extract_conditions.py --dry-run               # preview prompt
python extract_conditions.py                         # needs GEMINI_API_KEY and GEMINI_MODEL
```
Never commit `.env`. For deployment use the host's secrets (e.g. Streamlit `st.secrets`).

## Repository layout
```
app.py                 dashboard (split into modules as it grows)
extract.py             ISA-Tab -> psi_data.json (deterministic)
extract_conditions.py  offline SI extraction -> data/verified_psi.json
psi_data/raw/          source ISA-Tab files from PSI
docs/                  decision log, SI usage log
```

## Sources and attribution
Data: NASA Physical Sciences Informatics (https://psi.nasa.gov). Cite each investigation by its DOI, as PSI requires. Background: NASA Combustion Science, Apollo 1, Apollo 13, the Mir fire article, the Researcher's Guide to Combustion Science, and NASA Spinoff pages. NASA does not endorse this project.

## Team
_List names and roles._

## License
_Choose one (e.g. MIT) and add a LICENSE file._
