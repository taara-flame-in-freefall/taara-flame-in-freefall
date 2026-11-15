# Contributor Report — Nimra Pervez

**Team:** TAARA (Ghulam Ishaq Khan Institute of Engineering Sciences and Technology — GIKI, Topi)  
**Challenge:** NASA Space Apps Challenge 2026 — *Flame in Freefall*  
**Role:** Dataset Verification Completion & Verified Evidence Dashboard Integration  

---

## 1. What Was Contributed

1. **Completed 26/26 Human Verification of the NASA PSI Dataset (`data/verified_psi.json`):**
   * Audited and finalized the remaining gaseous combustion records (`PSI-10`, `PSI-20`, and `PSI-21`) against raw NASA Physical Sciences Informatics (PSI) source text in `psi_data.json`, bringing dataset verification from `23/26` to **`26/26` passing** under `python data/validate_psi.py`.
2. **Integrated the Audited Evidence Layer into the Dashboard (`app.py`):**
   * Updated `load_psi_data()` in `app.py` to load and merge `data/verified_psi.json` alongside `psi_data.json`, exposing human-verified experimental conditions (`fire_safety_function`, `environment_relevance`, `fuel_type`, `material_tested`, `o2_concentration`, `pressure`, `flow_speed`, `sensors_measurements`, `sample_geometry_size`, and `test_variables`) and verbatim NASA `"evidence"` quotes across the UI.
3. **Scientific Integrity (SI) Guardrails & Out-of-Scope Filtering:**
   * Enforced automatic exclusion of `out_of_scope` non-combustion control records (`PSI-108` Fluid Physics and `PSI-181` Materials Science/Soldering) from default fire-safety rankings while preserving a sidebar toggle to inspect them as cross-domain negative controls.
   * Added an **"Audited Experimental Conditions & Verbatim NASA Source Quotes"** table in Tab 3 (*Investigation Deep-Dive & Evidence*) and grounded the Tab 2 Gemini AI Synthesizer prompt in `audited_conditions_with_evidence` so missing parameters (`null`) are explicitly flagged rather than extrapolated.

---

## 2. How It Was Done

* **Cross-Audit of ACME Gaseous Flame Investigations:**
  * **`PSI-10` (ACME / Flame Design):** Verified fuel types (`C2H4 and CH4`), diluents (`N2 or CO2`), and diagnostic instruments (`cameras, radiometers, photomultiplier tubes, and thermocouples`) against verbatim NASA quotes and flipped `"human_verified": true`.
  * **`PSI-20` (ACME BRE):** Verified elevated-oxygen exploration test conditions (`21 % oxygen, 26.5 %, 34 % oxygen` at `14.7 psia, 10.2 psia, 8.2 psia` in `quiescent` flow on `25 and 50 mm` porous circular burners) and flipped `"human_verified": true`.
  * **`PSI-21` (ACME CLD Flame):** Verified gaseous fuels (`methane and ethylene`), measured diagnostics (`flame shape, lift-off heights, temperatures and extinction limits`), and independent test variables (`velocity and fuel dilution`), then flipped `"human_verified": true`.
* **Automated Validation Check:**
  * Executed `python data/validate_psi.py` to confirm `26/26` human-verified records, zero remaining `needs_review` items, 1-to-1 key parity with `psi_data.json`, and valid flight-to-ground lineage links.
* **Dashboard & Prompt Grounding (`app.py`):**
  * Bound mission scoring, ranked CSV exports, deep-dive parameter tables, and Gemini synthesis payloads directly to the verified JSON schema so every quantitative metric displayed in the interface is traceable to an exact NASA PSI quote.

---

## 3. How It Solves NASA's Challenge

Spacecraft and lunar/martian habitat designers rely on microgravity ($0g$) ISS experiments and $1g$ ground tests to bound fire risk in partial-gravity ($1/6g$ Moon, $3/8g$ Mars) exploration atmospheres (such as `8.2 psia` / `34% O₂`). By achieving **100% (26/26) human-verified schema compliance** and binding every UI parameter and AI synthesis output to verbatim NASA PSI source quotes, this layer prevents AI hallucinations of unstated experimental conditions and ensures non-combustion control records do not distort mission fire-safety rankings.