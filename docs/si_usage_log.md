# SI (AI) Usage Log

Purpose: record every place AI is used in this project, what it was asked to do, and how a human checked the result. Keep this honest and current; check the challenge's rules on AI-use disclosure and make sure this log satisfies them.

## In the product
| # | Feature | Model / tool | Input | Output | Safeguards | Human check |
|---|---|---|---|---|---|---|
| 1 | Fire-safety synthesis (SI tab) | Gemini (`GEMINI_MODEL`) | Selected PSI records only | Structured assessment with PSI-ID citations | Prompt forbids numbers not in records; "not in PSI metadata" fallback; output labeled as AI-generated | _who/when_ |
| 2 | Conditions extraction (offline) | Gemini | `objective`, `approach`, etc. per record | `data/verified_psi.json` | Verbatim evidence required; `needs_review` flags; `human_verified` flag | _who reviewed which records_ |
| 3 | _Ask-the-dataset chat (if built)_ | | | | | |

## In development (tools used to build the project)
| Date | Tool | Used for | What the team changed/verified |
|---|---|---|---|
| 2026-11-14 | Claude (Anthropic) | Code review of the repo, parser fix, extraction script, README/doc drafts | _record what was accepted, edited or rejected_ |
| _date_ | _Gemini/other_ | _e.g. app scaffolding_ | |

## Known SI limitations
- No partial-gravity (Moon/Mars) combustion data exists in PSI; any Moon/Mars statement is extrapolation and must be labeled.
- LLM output can contain errors; it is never shown as a measured result.
- Extraction quality depends on the text in the PSI record; missing conditions stay `null`.

## Prompt versions
Keep copies of final prompts here (or link to the file) so results are reproducible.
