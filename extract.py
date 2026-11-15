"""
Parses every PSI investigation's i_Investigation.txt (ISA-Tab format) into
one clean record. No AI involved -- this is a deterministic text parser,
because the source files are already structured.
"""
import os, json, csv, re

RAW_DIR = "psi_data/raw"
OUT_DIR = "build/output"
os.makedirs(OUT_DIR, exist_ok=True)

# Flight investigations we treat as primary dashboard entries.
PRIMARY = {
    "PSI-98": "Solids", "PSI-99": "Solids", "PSI-100": "Solids",
    "PSI-25": "Solids", "PSI-26": "Solids",
    "PSI-69": "Droplets", "PSI-68": "Droplets", "PSI-39": "Droplets",
    "PSI-159": "Gas flames", "PSI-10": "Gas flames", "PSI-21": "Gas flames",
    "PSI-22": "Gas flames", "PSI-23": "Gas flames", "PSI-20": "Gas flames",
    "PSI-107": "Gas flames", "PSI-106": "Gas flames",
    "PSI-102": "Detection", "PSI-101": "Detection", "PSI-47": "Detection",
}
# Ground / modeling studies -> which primary investigation they attach to.
GROUND_PARENT = {
    "PSI-117": "PSI-69",   # cool-flame CFD using FLEX data
    "PSI-142": "PSI-69",   # counterflow cool-flame extinction using FLEX data
    "PSI-62":  "PSI-25",   # flame-spread modeling compared to BASS/BASS-II
    "PSI-115": "PSI-102",  # DNS modeling of SAME smoke growth
    "PSI-60":  "PSI-107",  # soot modeling of SPICE data
    "PSI-181": None,       # Materials Science solder study -- not fire-related, kept only for completeness
    "PSI-108": None,       # Fluid Physics thermocapillary -- not fire-related, kept only for completeness
}

FIELD_MAP = {
    "id": "Study Identifier",
    "name": "Study Title",
    "acronym": "Comment[Investigation Acronym]",
    "objective": "Comment[Objective]",
    "approach": "Comment[Approach]",
    "hypothesis": "Comment[Hypothesis]",
    "research_impacts": "Comment[Research Impacts]",
    "hardware": "Comment[Experiment Hardware]",
    "flight_platform": "Comment[Flight Platform]",
    "start_date": "Comment[Investigation Start Date]",
    "end_date": "Comment[Investigation End Date]",
    "managing_center": "Comment[Managing NASA Center]",
    "research_area": "Comment[Research Area]",
    "sub_research_area": "Comment[SubResearch Area]",
    "doi": "Comment[DOI]",
    "project_type": "Comment[Project Type]",
}

def parse_tabfile(path):
    """Parse an ISA-Tab file into {row_label: [values...]}.

    ISA-Tab cells are quoted and can contain newlines (e.g. numbered objectives).
    Splitting on "\n" truncates them, so we use the csv module, which understands
    quoted multi-line cells.
    """
    rows = {}
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        for parts in csv.reader(f, delimiter="\t", quotechar='"'):
            if len(parts) < 2 or not parts[0].strip():
                continue
            key = parts[0].strip()
            vals = [" ".join(v.split()) for v in parts[1:] if v.strip() != ""]
            if key in rows:          # keep first occurrence (investigation-level)
                continue
            rows[key] = vals
    return rows

def first_or_unknown(rows, label):
    vals = rows.get(label, [])
    return vals[0] if vals else "unknown"

def all_or_empty(rows, label):
    return rows.get(label, [])

def parse_publications(rows):
    dois = all_or_empty(rows, "Study Publication DOI")
    authors = all_or_empty(rows, "Study Publication Author List")
    titles = all_or_empty(rows, "Study Publication Title")
    links = all_or_empty(rows, "Comment[Study Publication Link]")
    n = max(len(dois), len(authors), len(titles), len(links), 0)
    pubs = []
    for i in range(n):
        pubs.append({
            "title": titles[i] if i < len(titles) else "unknown",
            "authors": authors[i] if i < len(authors) else "unknown",
            "doi": dois[i] if i < len(dois) else "unknown",
            "link": links[i] if i < len(links) else "unknown",
        })
    return pubs

def parse_contacts(rows):
    last = all_or_empty(rows, "Study Person Last Name")
    first = all_or_empty(rows, "Study Person First Name")
    aff = all_or_empty(rows, "Study Person Affiliation")
    role = all_or_empty(rows, "Study Person Roles")
    n = len(last)
    people = []
    for i in range(n):
        people.append({
            "name": f"{first[i] if i < len(first) else ''} {last[i]}".strip(),
            "affiliation": aff[i] if i < len(aff) else "unknown",
            "role": role[i] if i < len(role) else "unknown",
        })
    return people

records = {}
errors = []

all_ids = sorted(
    [d for d in os.listdir(RAW_DIR) if d.startswith("PSI-")],
    key=lambda x: int(x.split("-")[1])
)

for pid in all_ids:
    path = os.path.join(RAW_DIR, pid, "i_Investigation.txt")
    if not os.path.exists(path):
        errors.append(f"{pid}: i_Investigation.txt not found")
        continue
    rows = parse_tabfile(path)
    rec = {k: first_or_unknown(rows, label) for k, label in FIELD_MAP.items()}
    rec["psi_id"] = pid  # the folder/ID is authoritative, not the parsed "Study Identifier" field
    rec["publications"] = parse_publications(rows)
    rec["contacts"] = parse_contacts(rows)
    rec["is_primary"] = pid in PRIMARY
    rec["pillar"] = PRIMARY.get(pid, "unknown")
    rec["parent_investigation"] = GROUND_PARENT.get(pid, None) if pid not in PRIMARY else None
    records[pid] = rec

# attach related/ground studies to their primary parent for easy lookup
for pid, rec in records.items():
    rec["related_ground_studies"] = [
        other for other, r in records.items()
        if r.get("parent_investigation") == pid
    ]

with open(os.path.join(OUT_DIR, "investigations.json"), "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

# Flattened CSV for quick filtering (publications/contacts collapsed to counts + first author)
csv_fields = [
    "psi_id", "name", "acronym", "is_primary", "pillar", "parent_investigation",
    "research_area", "sub_research_area", "project_type", "flight_platform",
    "hardware", "start_date", "end_date", "managing_center", "doi",
    "objective", "approach", "hypothesis", "research_impacts",
    "publication_count", "first_publication_title", "first_publication_doi",
    "related_ground_studies",
]
with open(os.path.join(OUT_DIR, "investigations.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=csv_fields)
    w.writeheader()
    for pid, rec in records.items():
        pubs = rec["publications"]
        w.writerow({
            "psi_id": rec["psi_id"], "name": rec["name"], "acronym": rec["acronym"],
            "is_primary": rec["is_primary"], "pillar": rec["pillar"],
            "parent_investigation": rec["parent_investigation"] or "",
            "research_area": rec["research_area"], "sub_research_area": rec["sub_research_area"],
            "project_type": rec["project_type"], "flight_platform": rec["flight_platform"],
            "hardware": rec["hardware"], "start_date": rec["start_date"], "end_date": rec["end_date"],
            "managing_center": rec["managing_center"], "doi": rec["doi"],
            "objective": rec["objective"], "approach": rec["approach"],
            "hypothesis": rec["hypothesis"], "research_impacts": rec["research_impacts"],
            "publication_count": len(pubs),
            "first_publication_title": pubs[0]["title"] if pubs else "unknown",
            "first_publication_doi": pubs[0]["doi"] if pubs else "unknown",
            "related_ground_studies": ";".join(rec["related_ground_studies"]),
        })

print(f"Parsed {len(records)} investigations.")
if errors:
    print("Errors:")
    for e in errors:
        print(" -", e)

# --- Quality report: catch truncated / empty fields before they reach the app ---
SUSPICIOUS = []
for pid, rec in records.items():
    for field in ("objective", "approach"):
        v = rec[field]
        if v == "unknown" or len(v) < 80 or v.rstrip().endswith(":"):
            SUSPICIOUS.append(f"{pid}.{field}: {len(v)} chars -> {v[:70]!r}")
print(f"\nField-quality check: {len(SUSPICIOUS)} suspicious field(s)")
for s in SUSPICIOUS:
    print(" -", s)
