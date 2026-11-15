# Decision Log

| Date | Decision | Why | Alternatives | Owner |
|---|---|---|---|---|
| 2026-11-13 | Streamlit + Plotly + Gemini | Fast to build, web-based, interactive | _fill in_ | _name_ |
| 2026-11-14 | Parse PSI ISA-Tab deterministically (no AI) | Source is already structured | LLM parsing | _name_ |
| 2026-11-14 | Use `csv` module for ISA-Tab | Cells contain multi-line quoted text; newline splitting truncated 10+ objectives | Manual regex | _name_ |
| _date_ | Offline structured extraction with evidence + human review | Dashboard should show verified data, not runtime guesses | Runtime LLM answers only | _name_ |
| _date_ | Treat Moon/Mars output as extrapolation from bounding cases | PSI has no partial-gravity combustion data | Present as measured | _name_ |
| _date_ | Replace keyword score with transparent rubric (0-3 per criterion) | Defensible and adjustable | Keyword heuristic | _name_ |
| _date_ | Hide non-combustion controls (PSI-108, PSI-181) by default | Not combustion science | Include in ranking | _name_ |
