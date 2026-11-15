# Contributor Log — Ayesha
**Project:** Team TAARA | *Flame in Freefall: Microgravity Combustion Intelligence Dashboard*  
**Challenge:** NASA Space Apps Challenge — *Flame in Freefall*  
**Primary Focus Areas:** UI/UX Architecture, Custom Visual Asset Design, Frontend Asset Pipeline & Visual QA

---

## 1. Summary of Contributions
Designed and integrated the complete visual identity, custom mission imagery, and high-contrast Cosmic Obsidian user interface for Team TAARA's Streamlit dashboard (`app.py`), transforming raw NASA Physical Sciences Informatics (PSI) datasets into an intuitive, mission-control experience for evaluating fire safety across **$0g$ (ISS/Orbital)**, **$1/6g$ (Lunar)**, and **$3/8g$ (Martian)** environments.

---

## 2. Custom Visual Assets Created & Integrated (`assets/`)
Created and mapped **9 bespoke mission-themed visual assets** inside the `assets/` directory, pairing each graphic with a specific scientific and navigational role in the application:

| Asset File | Dashboard Placement | Functional & Scientific Purpose |
| :--- | :--- | :--- |
| `shadow_unicorn.jpg` | Top of Left Sidebar | Serves as the **Cross-Domain Anomaly Guard** emblem, visually anchoring the sidebar controls that filter out-of-scope non-combustion records (`PSI-108` Fluid Physics, `PSI-181` Soldering/Materials Science). |
| `astronaut_fire.jpg` | Hero Header (Top-Right) | Illustrates microgravity combustion behavior in human spaceflight alongside the active mission profile selector and KPI telemetry strip. |
| `flame_emblem.jpg` | Tab 2 Header & AI Spinner | Represents the **$0g$ Spherical Flame Kernel** in the *AI Fire-Safety Synthesizer* header and drives the animated orbital fireball loader during Gemini synthesis. |
| `cosmic_banner.jpg` | Global App Backdrop | Provides an atmospheric deep-space obsidian-and-amber backdrop across the entire application viewport. |
| `flame_comparison_1g_vs_0g.jpg` | Tab 1 Background | Visually contrasts buoyant **$1g$** teardrop flames against diffusion-controlled **$0g$** spherical flames behind the *Mission Ranking & Analytics* charts. |
| `moon_habitat.jpg` | Tab 2 Dynamic Background | Dynamically loads behind the AI Synthesizer when the **Lunar Habitat ($1/6g$, $\ge 30\%\ \text{O}_2$)** mission profile is active. |
| `mars_habitat.jpg` | Tab 2 Dynamic Background | Dynamically loads behind the AI Synthesizer when the **Martian Habitat ($3/8g$)** mission profile is active. |
| `detection_suppression.jpg` | Tab 3 Background | Anchors the *Investigation Deep-Dive & Audited Evidence Trail* view with spacecraft fire detection and suppression context. |
| `iss_cygnus_orbit.jpg` | Tab 2 (Orbital) & Tab 4 Background | Sets the orbital flight context for **$0g$ ISS/Cygnus** synthesis and *Flight-to-Ground Study Lineage* mapping. |

---

## 3. Frontend & UI/UX Engineering (`app.py`)
* **Resilient Asset Resolution Pipeline (`resolve_asset_path`):** Implemented automatic directory (`assets/`) and file-extension resolution (`.jpg`, `.jpeg`, `.png`, `.webp`) so all visual assets load reliably across Windows, macOS, and Linux deployments without silent path failures.
* **True-Alpha Image Processing & Radial Feathering:** Built PIL/NumPy image preprocessing (`_process_image_b64`) featuring luminance-based black-background keying for flame graphics and Gaussian radial vignette masks so sidebar and hero visuals blend seamlessly into the dark obsidian layout without hard rectangular borders.
* **High-Contrast Frosted Glass Readability System:** Styled translucent cosmic-obsidian glass containers (`.glass-card`, `.ai-output-card`, and frosted Plotly/DataFrame wrappers with `backdrop-filter: blur`) to guarantee crisp legibility over full-bleed habitat and flame backgrounds.
* **Aerospace Mission-Control Typography & Hierarchy:** Configured **Space Grotesk** display headings, **Inter** body text, and **JetBrains Mono** telemetry readouts alongside a unified Cosmic Amber (`#FF752B`) and Plasma Blue (`#38BDF8`) color palette.
* **Sidebar & Tab Visual Re-Architecture:** Elevated the **Cross-Domain Anomaly Guard** (`shadow_unicorn.jpg`) to the primary top slot of the sidebar and relocated the **$0g$ Spherical Flame Kernel** (`flame_emblem.jpg`) directly into Tab 2's AI synthesis workspace.

---

## 4. Quality Assurance & Debugging Milestones
* Diagnosed and fixed missing dashboard graphics caused by root-vs-`assets/` relative path mismatches and hidden OS file extensions.
* Audited text contrast across all four tabs and dynamic environment states (Lunar, Martian, Orbital) to ensure all metrics, evidence tables, and Gemini synthesis reports remain sharp and accessible.