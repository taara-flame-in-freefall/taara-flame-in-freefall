# Partial-Gravity Combustion Physics & Habitat Bounding Framework

**Author:** M. Shomail (Domain, Data & Dev — Team TAARA)  
**Challenge:** NASA Space Apps Challenge — *Flame in Freefall*

---

## 1. Scientific Scope & Partial-Gravity Caveat
The NASA Physical Sciences Informatics (PSI) archive contains **microgravity ($0g$) flight experiments** (conducted aboard the ISS and Cygnus spacecraft) paired with **normal-gravity ($1g$) ground validation and CFD modeling studies**. Because sustained partial-gravity combustion testbeds ($1/6g$ Lunar and $3/8g$ Martian) do not yet exist in the PSI repository, Team TAARA uses **$0g$ flight limits and $1g$ ground standards (NASA-STD-6001) as physical boundary conditions** to bracket fire hazards in extraterrestrial habitats.

---

## 2. Why Earth ($1g$) Flammability Tests Fail in Low Gravity
In normal Earth gravity ($1g$), hot combustion products rise rapidly via buoyant natural convection ($Gr \propto g \beta \Delta T L^3 / \nu^2$). This buoyant plume draws fresh oxygen into the flame base while stretching and convectively cooling the flame tip.

When gravity decreases toward $0g$ (ISS), $1/6g$ (Moon), or $3/8g$ (Mars):
1. **Buoyant Flow Suppression ($V_b \propto g^{1/2}$):** Natural convective velocities drop sharply, shifting heat and mass transport control to **forced cabin HVAC ventilation** ($5\text{–}20\text{ cm/s}$) and **molecular diffusion**.
2. **Low-Flow Flammability Expansion:** Polymeric and fabric materials that self-extinguish in $1g$ upward flame spread tests can sustain steady or slow-spreading flames in low-speed opposed flows because convective heat losses drop before radiative quenching occurs.
3. **Exploration Atmosphere Hazard ($\ge 30\%\text{ O}_2\text{ at }\le 10.2\text{ psi}$):** Future Lunar habitats and pressurized rovers operate at reduced total pressure with elevated oxygen fractions (e.g., Exploration Atmosphere regimes around $30\text{–}34\%\text{ O}_2$ and $8.2\text{–}10.2\text{ psi}$) to minimize EVA pre-breathe times. Elevated $O_2$ lowers ignition energy, shrinks quenching distances, and accelerates flame spread rates.

---

## 3. Bounding Across NASA PSI Fire-Safety Functions

| Fire-Safety Function | Representative PSI Studies | $0g$ & $1g$ Experimental Insights | Engineering Implications for Moon ($1/6g$) & Mars ($3/8g$) |
| :--- | :--- | :--- | :--- |
| **Prevention & Material Screening** | `PSI-25` (BASS-II), `PSI-26` (BASS), `PSI-98` (SAFFIRE-I), `PSI-99` (SAFFIRE-II), `PSI-100` (SAFFIRE-III), `PSI-39` (CFI-G) | `BASS`/`BASS-II` reveal opposed-flow burning below $1g$ oxygen limits; `SAFFIRE` scales solid flame spread (Sibal cotton-fiberglass, PMMA) to spacecraft duct dimensions; `CFI-G` explores elevated oxygen regimes up to $85\%\text{ O}_2$. | **Highest Lunar/Martian Priority:** Weak $1/6g$ and $3/8g$ buoyancy replenishes oxidizer in $\ge 30\%\text{ O}_2$ atmospheres without blowing flames off, requiring stricter material screening than $1g$ NASA-STD-6001 alone. |
| **Early Smoke Detection** | `PSI-102` (SAME), `PSI-101` (SAME-R), `PSI-47` | Longer flame residence times in $0g$ allow primary soot/smoke particles to coagulate into larger fractal aggregates, shifting light-scattering vs. ionization signatures. | Smoke detectors in $1/6g$ and $3/8g$ habitats must handle transitional buoyant plumes mixed with forced HVAC airflows without false alarms from lunar/martian regolith dust. |
| **Suppression & Extinguishment** | `PSI-69` (FLEX), `PSI-68` (FLEX-2), `PSI-10`–`PSI-23` (ACME) | `FLEX`/`FLEX-2` ($0.5\text{–}3\text{ atm}$, $0.1\text{–}0.4\text{ O}_2$ mole fraction) demonstrated radiative extinction of large fuel droplets followed by low-temperature **cool-flame combustion** ($500\text{–}800\text{ K}$). | Fire suppression protocols ($N_2$, $CO_2$, or water mist) must prevent reignition from invisible cool flames and account for reduced convective mixing in low gravity. |

---

## 4. Non-Combustion Archive Controls (`PSI-108` & `PSI-181`)
Two records included in the 26-dataset PSI extract fall outside Combustion Science:
* **`PSI-108` (Fluid Physics):** Investigates capillary/interfacial fluid transport rather than reactive oxidation.
* **`PSI-181` (Materials Science):** Investigates microgravity solder joint solidification for electronics manufacturing.

Both are retained in the repository as negative/cross-domain controls to verify dataset boundary filtering and are hidden by default from active combustion rankings.