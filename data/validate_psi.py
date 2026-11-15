import json
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
PSI_DATA_PATH = BASE_DIR / "psi_data.json"
VERIFIED_PSI_PATH = BASE_DIR / "data" / "verified_psi.json"
EXPECTED_NON_COMBUSTION = {"PSI-108", "PSI-181"}
def main() -> int:
    if not PSI_DATA_PATH.exists() or not VERIFIED_PSI_PATH.exists():
        print("FAIL: Missing psi_data.json or data/verified_psi.json")
        return 1
    with open(PSI_DATA_PATH, "r", encoding="utf-8") as f:
        raw_psi = json.load(f)
    with open(VERIFIED_PSI_PATH, "r", encoding="utf-8") as f:
        verified_psi = json.load(f)
    errors = []
    if set(raw_psi.keys()) != set(verified_psi.keys()):
        missing = set(raw_psi.keys()) - set(verified_psi.keys())
        extra = set(verified_psi.keys()) - set(raw_psi.keys())
        errors.append(f"ID mismatch — missing: {sorted(missing)}, extra: {sorted(extra)}")
    verified_count = 0
    unreviewed_items = []
    for pid, entry in verified_psi.items():
        if entry.get("human_verified") is True:
            verified_count += 1
        else:
            errors.append(f"{pid}: human_verified is not True")
        if entry.get("needs_review"):
            unreviewed_items.append((pid, entry["needs_review"]))
        raw_rec = raw_psi.get(pid, {})
        parent_id = raw_rec.get("parent_investigation")
        if parent_id and parent_id not in raw_psi:
            errors.append(f"{pid}: parent_investigation '{parent_id}' missing from psi_data.json")
        for child_id in raw_rec.get("related_ground_studies", []):
            if child_id not in raw_psi:
                errors.append(f"{pid}: related ground study '{child_id}' missing from psi_data.json")
    for ctrl_id in EXPECTED_NON_COMBUSTION:
        area = raw_psi.get(ctrl_id, {}).get("research_area")
        if area == "Combustion Science":
            errors.append(f"{ctrl_id}: expected non-combustion control, found Combustion Science")
    if unreviewed_items:
        for pid, items in unreviewed_items:
            errors.append(f"{pid}: unresolved needs_review items -> {items}")
    print(f"Total PSI records checked : {len(verified_psi)}")
    print(f"Human-verified records    : {verified_count}/{len(verified_psi)}")
    print(f"Non-combustion controls   : {sorted(EXPECTED_NON_COMBUSTION)}")
    if errors:
        print("\nVALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("\nVALIDATION PASSED: All 26 PSI records verified, schema-valid, and lineage-consistent.")
    return 0
if __name__ == "__main__":
    sys.exit(main())
