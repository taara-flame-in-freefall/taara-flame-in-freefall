# Contributor Report: Muhammad Yasin
**Team:** TAARA (Ghulam Ishaq Khan Institute of Engineering Sciences and Technology — GIKI, Topi, Pakistan)  
**Challenge:** NASA Space Apps Challenge 2026 — *Flame in Freefall*  
**Role:** Data Engineering, Scientific Integrity (SI) & Development  

---

## 1. Executive Summary: What I Contributed
I was responsible for the human-in-the-loop verification, scientific auditing, and automated schema validation of the upper half of Team TAARA's NASA Physical Sciences Informatics (PSI) dataset (`PSI-98` through `PSI-181`, covering 13 investigations)[cite: 5].

Specifically, I delivered:
1. **Audited & Verified Dataset (`data/verified_psi.json`):** Completed full parameter-by-parameter verification and evidence grounding for 13 NASA PSI investigations (`PSI-98`, `PSI-99`, `PSI-100`, `PSI-101`, `PSI-102`, `PSI-106`, `PSI-107`, `PSI-108`, `PSI-115`, `PSI-117`, `PSI-142`, `PSI-159`, and `PSI-181`), resolving all automated review flags (`needs_review: []`) and certifying every record with `"human_verified": true`[cite: 5].
2. **Automated Schema & Lineage Validator (`data/validate_psi.py`):** Built a zero-dependency Python validation suite to enforce 1-to-1 key parity between raw NASA PSI metadata (`psi_data.json`) and our extracted schema (`data/verified_psi.json`), verify parent-child study lineage, ensure zero unresolved review flags, and isolate non-combustion control records.
3. **Zero-Conflict Git Integration:** Executed isolated branch/file commits so downstream dashboard developers (Nimra, Zain, Shomail, Ayesha, and Tahoora) could ingest verified, hallucination-free JSON records directly into `app.py`.

---

## 2. Technical Methodology: How I Did It

### A. Ground-Truth Evidence Auditing (`PSI-98` to `PSI-181`)
Initial LLM extraction (`gemini-3.5-flash-lite`) pre-populated experimental parameters from NASA PSI abstracts, leaving several records flagged in `needs_review`[cite: 5]. I performed a side-by-side audit comparing every extracted field in `data/verified_psi.json` against the verbatim NASA text in `psi_data.json`:
* **Strict Anti-Hallucination Rule:** Every extracted condition (`fuel_type`, `sample_geometry_size`, `o2_concentration`, `pressure`, `flow_speed`, `diluents_suppressants`, `sensors_measurements`, `test_variables`, and `earth_application`) was required to map directly to an explicit `"evidence"` quote from the NASA record[cite: 5]. Any unstated parameter was strictly set to `null` rather than inferred[cite: 5].
* **Resolution of Flagged Combustion Investigations:**
  * **`PSI-102` (SAME):** Verified aerosol/smoke diagnostic instrumentation (`smoke detectors`, `thermophoretic soot samplers`, `Transmission Electron Microscope (TEM)`, and `mass loss`) directly against flight hardware descriptions[cite: 5].
  * **`PSI-106` (SLICE):** Grounded laminar diffusion flame diagnostics (`integrated sensors to measure flow rates and temperature`, `high resolution camera`) and terrestrial combustor efficiency impacts[cite: 5].
  * **`PSI-107` (SPICE):** Verified parametric test variables (`burner diameter`, `co-flow velocity`, `air and fuel flow rate variations`) across 0.41 mm, 0.76 mm, and 1.6 mm burners at co-flow velocities from 5.4 to 65 cm/s[cite: 5].

### B. Handling Non-Combustion Control Records (`PSI-108` & `PSI-181`)
Two records in my assigned range were non-combustion experiments that triggered automated "fewer than 2 conditions extracted" flags:
* **`PSI-108` (STDCE-1):** Surface Tension Driven Convection Experiment (Fluid Physics / thermocapillary flow)[cite: 5].
* **`PSI-181`:** Microgravity soldering / electronics materials science (relevant to lunar base repair, but not fire combustion)[cite: 5].

Rather than forcing irrelevant combustion tags onto these records, I classified both as `"fire_safety_function": "out_of_scope"`, preserved their null combustion fields, and cleared their review flags[cite: 5]. This gives our dashboard an explicit negative-control benchmark to prove our ranking engine filters out non-fire PSI studies.

### C. Automated Quality Gate (`data/validate_psi.py`)
To prevent silent JSON corruption or missing lineage links before deployment, I wrote `data/validate_psi.py` using Python's standard library (`json`, `sys`, `pathlib`) to check:
1. **Key Parity:** `set(raw_psi.keys()) == set(verified_psi.keys())` so no investigation is dropped or duplicated.
2. **Verification Completeness:** Confirms `human_verified is True` and `needs_review` is empty across all entries.
3. **Study Lineage Integrity:** Validates that every `parent_investigation` and `related_ground_studies` reference exists inside `psi_data.json` (for example, linking ground CFD/modeling studies like `PSI-115` and `PSI-117` back to their parent ISS flight experiments `SAME` and `FLEX`)[cite: 5].
4. **Control Verification:** Confirms non-combustion controls (`PSI-108`, `PSI-181`) are never misclassified under `Combustion Science`.

---

## 3. Impact on Team TAARA & NASA's Fire Safety Challenge
NASA's *Flame in Freefall* challenge requires translating decades of microgravity combustion data into actionable fire safety insights for spacecraft and future Moon/Mars habitats—where low gravity eliminates buoyancy-driven convection and elevated $O_2$ / reduced-pressure atmospheres alter flammability limits.

My contribution directly addresses three core NASA engineering needs:
1. **Separating Material Flammability from Detection & Modeling:** By verifying large-scale spacecraft material burn tests (`SAFFIRE-I`, `SAFFIRE-II`, `SAFFIRE-III` in `PSI-98`–`PSI-100` testing SIBAL, Nomex, silicone, and PMMA at 20–30 cm/s airflow)[cite: 5], smoke aerosol detection baselines (`SAME` and `SAME-R` in `PSI-101`–`PSI-102`)[cite: 5], and high-pressure/cool-flame numerical models (`PSI-115`, `PSI-117`, `PSI-142`, `PSI-159`)[cite: 5], engineers can query exact operational regimes instead of reading unstructured PDFs.
2. **Preventing False Positives in Habitat Risk Ranking:** By isolating out-of-scope studies (`PSI-108` and `PSI-181`)[cite: 5], Team TAARA's dashboard avoids contaminating spacecraft fire-prevention rankings with fluid physics or soldering datasets.
3. **Auditability for Safety-Critical Decisions:** In aerospace engineering, unverified AI summaries are a safety liability. Attaching verbatim NASA source quotes (`"evidence"`) and a programmatic `validate_psi.py` check ensures every data point displayed on the TAARA dashboard is 100% traceable back to NASA's Physical Sciences Informatics repository[cite: 5].