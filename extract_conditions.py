"""
Offline, one-time SI step: turn each investigation's free-text objective/approach
into a STRUCTURED test-conditions record, saved to data/verified_psi.json.

Why offline: the dashboard should read verified data, not ask Gemini to guess at
runtime. Every extracted value must quote the sentence it came from, and anything
not stated in the text must be null. A human then reviews the file (see
`needs_review`) before it is committed.

Usage:
    python extract_conditions.py --dry-run          # print one prompt, no API call
    python extract_conditions.py                    # extract all, resume-safe
    python extract_conditions.py --only PSI-69 PSI-98
Env:
    GEMINI_API_KEY   (from .env or the shell)
    GEMINI_MODEL     (set to a current model id from the Gemini docs)
"""
import argparse, json, os, sys, time

from dotenv import load_dotenv

load_dotenv()

SRC = "psi_data.json"
OUT = "data/verified_psi.json"
MODELS = [m.strip() for m in (os.getenv("GEMINI_MODELS") or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash").split(",") if m.strip()]
MODEL = MODELS[0]

FUNCTIONS = ["prevention_flammability", "detection", "suppression",
             "fundamental_combustion", "ground_modeling", "out_of_scope"]
ENVIRONMENTS = ["spacecraft", "space_station", "lunar_base", "mars_base",
                "pressurized_rover", "earth_applications"]

# Plain JSON-schema-style dict (Gemini structured output accepts this shape).
FIELD = {"type": "object", "properties": {
    "value": {"type": "string", "nullable": True},
    "evidence": {"type": "string", "nullable": True,
                 "description": "Exact sentence or phrase copied from the input that supports value."},
}, "required": ["value", "evidence"]}

SCHEMA = {
    "type": "object",
    "properties": {
        "fuel_type": FIELD,
        "sample_geometry_size": FIELD,
        "o2_concentration": FIELD,
        "pressure": FIELD,
        "flow_speed": FIELD,
        "diluents_suppressants": FIELD,
        "sensors_measurements": FIELD,
        "test_variables": FIELD,
        "fire_safety_function": {"type": "string", "enum": FUNCTIONS},
        "function_evidence": {"type": "string", "nullable": True},
        "environment_relevance": {"type": "array", "items": {"type": "string", "enum": ENVIRONMENTS}},
        "earth_application": FIELD,
    },
    "required": ["fuel_type", "sample_geometry_size", "o2_concentration", "pressure",
                 "flow_speed", "diluents_suppressants", "sensors_measurements",
                 "test_variables", "fire_safety_function", "function_evidence",
                 "environment_relevance", "earth_application"],
}

INSTRUCTIONS = """You extract structured test-condition metadata from NASA PSI
investigation records for a fire-safety dashboard.

RULES (strict):
1. Use ONLY the text provided below. Do not use outside knowledge.
2. If a field is not explicitly stated, set value to null and evidence to null.
   Never estimate, infer numbers, or fill in typical values.
3. For every non-null value, `evidence` must be a verbatim excerpt from the input.
4. Keep numbers and units exactly as written (e.g. "0.1 to 0.4 mole fraction").
5. fire_safety_function: pick the best single label. Use `ground_modeling` for
   computational/ground studies built on flight data, and `out_of_scope` for
   records that are not about combustion/fire.
6. environment_relevance: list only environments the text clearly supports;
   an empty list is fine. Rocket/propellant combustion is out of scope.
"""


def build_prompt(rec):
    body = {k: rec.get(k) for k in
            ("psi_id", "name", "acronym", "objective", "approach", "hypothesis",
             "research_impacts", "hardware", "flight_platform", "project_type")}
    return INSTRUCTIONS + "\nINVESTIGATION RECORD:\n" + json.dumps(body, indent=2, ensure_ascii=False)


def needs_review(result):
    """Flag records a human must check: weak/missing evidence or empty extraction."""
    problems = []
    for k, v in result.items():
        if isinstance(v, dict) and v.get("value") and not v.get("evidence"):
            problems.append(f"{k}: value without evidence")
    n_filled = sum(1 for v in result.values() if isinstance(v, dict) and v.get("value"))
    if n_filled < 2:
        problems.append("fewer than 2 conditions extracted")
    return problems


def evidence_in_source(rec, result):
    """Cheap hallucination check: every evidence string must appear in the source text."""
    haystack = " ".join(str(rec.get(k, "")) for k in
                        ("objective", "approach", "hypothesis", "research_impacts")).lower()
    haystack = " ".join(haystack.split())
    bad = []
    for k, v in result.items():
        if isinstance(v, dict) and v.get("evidence"):
            ev = " ".join(v["evidence"].lower().split())
            if ev not in haystack:
                bad.append(f"{k}: evidence not found verbatim in source")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--list-models", action="store_true", help="print models your key can use")
    args = ap.parse_args()

    data = json.load(open(SRC, encoding="utf-8"))
    ids = args.only or list(data)

    if args.dry_run:
        print(f"Model: {MODEL}\n\n{build_prompt(data[ids[0]])}\n\nSCHEMA keys: {list(SCHEMA['properties'])}")
        return

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY missing")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)

    if args.list_models:
        for m in client.models.list():
            acts = getattr(m, "supported_actions", None) or []
            if not acts or "generateContent" in acts:
                print(m.name.replace("models/", ""))
        return

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) and os.path.getsize(OUT) else {}
    # drop failed entries from earlier runs so they are retried
    out = {k: v for k, v in out.items() if "error" not in v}

    for pid in ids:
        MODELS[:] = MODELS or [MODEL]
        if pid in out and not args.only:
            continue  # resume-safe
        rec = data[pid]
        done = False
        for attempt in range(6):
            model = MODELS[attempt % len(MODELS)]   # rotate models on each retry
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=build_prompt(rec),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=SCHEMA,
                        temperature=0,
                    ),
                )
                result = json.loads(resp.text)
                problems = needs_review(result) + evidence_in_source(rec, result)
                out[pid] = {"psi_id": pid, "acronym": rec.get("acronym"),
                            "conditions": result,
                            "needs_review": problems,
                            "human_verified": False,
                            "model": model}
                print(f"{pid}: ok ({model})" + (f"  REVIEW: {problems}" if problems else ""))
                done = True
                break
            except Exception as e:
                msg = str(e)
                if "API key" in msg or "403" in msg or "PERMISSION" in msg:
                    sys.exit(f"Stopping: {msg[:300]}\nCheck GEMINI_API_KEY in .env")
                if ("404" in msg or "NOT_FOUND" in msg) and len(MODELS) > 1:
                    print(f"{pid}: model '{model}' does not exist - removing it from the list")
                    MODELS.remove(model)
                    continue
                if "404" in msg or "NOT_FOUND" in msg:
                    sys.exit(f"Stopping: model '{model}' not found. Run: python extract_conditions.py --list-models")
                transient = any(c in msg for c in ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "500"))
                wait = min(60, 5 * 2 ** attempt) if transient else 3
                print(f"{pid}: {model} failed ({msg[:90]}...) - waiting {wait}s")
                time.sleep(wait)
        if not done:
            print(f"{pid}: FAILED - will retry on next run")
            continue
        time.sleep(4)   # gentle pacing to stay inside free-tier rate limits
        json.dump(out, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    print(f"\nWrote {OUT}. Review every entry, then set human_verified=true.")


if __name__ == "__main__":
    main()
