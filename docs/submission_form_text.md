# Space Apps Project Form: Ready-to-Paste Text

Challenge: **Flame in Freefall: Microgravity Combustion Intelligence Dashboard**
Team: **Team TAARA (GIKI)**
Live app: https://spaceapps-taara-flame-in-freefall.streamlit.app/
Demo: https://drive.google.com/file/d/10s2lhf4rXUMcbocrBxwwq22Y9h4eAK5F/view?usp=drive_link
Code: https://github.com/taara-flame-in-freefall/taara-flame-in-freefall

---

## Project summary (short)
TAARA is an interactive dashboard that ranks, compares and synthesizes NASA Physical Sciences Informatics (PSI) combustion experiments to help bound fire-safety risk for Orbital (0g), Lunar (1/6g) and Martian (3/8g) habitats.

## Detailed description
Fire is one of the most serious hazards in crewed spaceflight. In microgravity, buoyancy disappears, so flames behave very differently from flames on Earth: they can form spherical flame balls, show radiative extinction limits, and change how materials burn and how smoke spreads. NASA's PSI archive holds many of these experiments, but the data is spread across separate records and no permanent partial-gravity fire laboratory exists yet for the Moon or Mars.

TAARA turns 26 PSI investigations (0g flight studies on the ISS and Cygnus, plus 1g and ground modeling studies) into one dashboard. It has four parts:

1. **Mission Ranking & Analytics.** Scores each investigation from 0 to 100 for a chosen environment (Orbital 0g, Lunar 1/6g or Martian 3/8g), with a pillar coverage treemap and a one-click CSV export.
2. **AI Fire-Safety Synthesizer.** Uses Gemini to combine the investigations a user selects into material-screening, detection and suppression bounds. It cites exact PSI IDs, flags missing parameters as null, and labels its output as AI-generated.
3. **Evidence & Verbatim Quote Explorer.** Shows each investigation's fuel or material, oxygen percentage, pressure, flow speed and hardware next to the verbatim NASA sentences they came from.
4. **Flight-to-Ground Lineage.** Links primary flight experiments to the ground and modeling studies that build on them, and isolates two non-combustion records (PSI-108 fluid physics and PSI-181 soldering) so they do not distort the results.

Because PSI contains 0g and 1g data but no direct 1/6g or 3/8g flight tests, every Moon and Mars output is framed as an engineering bound or extrapolation, not a measurement. Structured test conditions were extracted offline with Gemini, every non-null value carries a verbatim NASA quote, unstated values stay null, and a validation script checks the schema and evidence integrity of all 26 records.

## How we used SI (AI)
- **Gemini in the app:** the AI Fire-Safety Synthesizer sends only the selected PSI records to Gemini. The prompt forbids numbers that are not in those records, falls back to "not in PSI metadata", and labels all output as AI-generated.
- **Gemini for data extraction:** an offline script uses Gemini to extract structured test conditions from each record's text. A verbatim evidence quote is required for each non-null value, and a validation script checks the result.
- **Claude (Anthropic) during development:** used for code review, a parser fix, the extraction script, and drafts of the README, documentation and this submission text. The team reviewed and edited the output.
- Full details are in `docs/si_usage_log.md`.

## NASA data used
- NASA Physical Sciences Informatics (PSI) Data Repository, https://psi.nasa.gov: ISA-Tab investigation files for 26 combustion and fire-safety investigations (for example ACME, BASS, SAFFIRE, SAME, FLEX, SPICE, SLICE, CFI), each cited by its NASA PSI ID. PSI-108 and PSI-181 are included only as flagged non-combustion controls.

## Other references
- NASA Combustion Science Program materials and the *Researcher's Guide to Combustion Science*
- Case studies: Apollo 1, Apollo 13 and the 1997 Mir oxygen-generator fire
- NASA Spinoff publications
- Software: Streamlit, Plotly, pandas, python-dotenv, Google Gen AI SDK (Gemini)

NASA does not endorse this project.
