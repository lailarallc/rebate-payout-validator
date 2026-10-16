"""Draw every specific Galewick program parameter from research-plausible ranges.

Distance by construction: no rule value is hand-picked. Each value is a seeded draw
from a range whose basis is stated beside it. The seed is derived from a fixed
string, not chosen. Re-running produces byte-identical output.

Output: rules/parameters.json
"""

import hashlib
import json
import random
from pathlib import Path

SEED_STRING = "galewick-climate-systems/program-year-2025/parameters"
SEED = int(hashlib.sha256(SEED_STRING.encode()).hexdigest(), 16) % (2**32)

OUT = Path(__file__).resolve().parent.parent / "rules" / "parameters.json"

# Each range: (low, high, step) plus basis. Basis labels:
#   CITE      published figure (see docs/anchors-research.md)
#   DIRECTION published qualitative pattern, no rate
#   STRUCTURAL no published figure; range set by Claude for internal coherence,
#              never by anyone who has administered a real program
RANGES = {
    "filing_deadline_days": {
        "low": 30, "high": 90, "step": 15,
        "basis": "CITE: claim windows 30-60 days (ZINFI), 60-90 days (utility rules, OEM warranty registration)",
    },
    "late_doc_grace_days": {
        "low": 15, "high": 45, "step": 15,
        "basis": "STRUCTURAL",
    },
    "late_doc_partial_pct": {
        "low": 25, "high": 75, "step": 25,
        "basis": "STRUCTURAL",
    },
    "spring_start_month": {
        "low": 2, "high": 4, "step": 1,
        "basis": "DIRECTION: cooling-season demand peaks spring/summer",
    },
    "spring_length_months": {
        "low": 2, "high": 3, "step": 1,
        "basis": "DIRECTION: SPIFF runs 30-90 days (ZINFI)",
    },
    "spring_uplift_pct": {
        "low": 20, "high": 60, "step": 5,
        "basis": "STRUCTURAL",
    },
    "bonus_floor_usd": {
        "low": 25, "high": 60, "step": 5,
        "basis": "CITE: per-unit SPIFF $25-$100 (Prospeo), $100-$200 (ZINFI); vendor, illustrative",
    },
    "bonus_ceiling_usd": {
        "low": 150, "high": 300, "step": 5,
        "basis": "CITE: per-unit HVAC $150-$600 (Pipeline On, attributed ACHR News; unverified)",
    },
    "tier2_threshold_usd": {
        "low": 150_000, "high": 400_000, "step": 25_000,
        "basis": "DIRECTION: tier examples at $500k / $1M (Hyperbots), scaled to a quarter",
    },
    "tier3_multiple": {
        "low": 2.5, "high": 3.5, "step": 0.25,
        "basis": "STRUCTURAL",
    },
    "tier4_multiple": {
        "low": 1.8, "high": 2.2, "step": 0.1,
        "basis": "STRUCTURAL",
    },
    "tier2_rate_pct": {
        "low": 1.5, "high": 2.5, "step": 0.25,
        "basis": "CITE: tier rates 2-4% (Hyperbots); vendor, illustrative",
    },
    "tier3_step_pct": {
        "low": 0.5, "high": 1.5, "step": 0.25,
        "basis": "CITE: tier rates 2-4% (Hyperbots); vendor, illustrative",
    },
    "tier4_step_pct": {
        "low": 1.0, "high": 2.0, "step": 0.25,
        "basis": "STRUCTURAL: incremental top tier above Tier 3 rate",
    },
    "growth_threshold_pct": {
        "low": 105, "high": 115, "step": 1,
        "basis": "STRUCTURAL",
    },
    "growth_bonus_pct": {
        "low": 0.5, "high": 1.5, "step": 0.25,
        "basis": "STRUCTURAL",
    },
}

# Added in rulebook v1.1 (realism review F6 / B6). Drawn from a separate seeded stream so
# the v1.0 draws above are unchanged.
SEED_STRING_V11 = "galewick-climate-systems/program-year-2025/parameters/v1.1"
RANGES_V11 = {
    "claim_processing_days": {
        "low": 21, "high": 42, "step": 7,
        "basis": "STRUCTURAL",
    },
    "rebate_payment_days": {
        "low": 30, "high": 60, "step": 15,
        "basis": "STRUCTURAL",
    },
}

# Models ordered by efficiency within each family. Rank 0 = lowest eligible.
# Model codes and efficiency labels are invented. Furnaces get no spring rate
# (spring promotion is a cooling-season promotion).
MODELS = [
    ("GW-AC15", "Air conditioner, 15 SEER2", True),
    ("GW-HP16", "Heat pump, 16 SEER2", True),
    ("GW-FG96", "Gas furnace, 96% AFUE", False),
    ("GW-AC17", "Air conditioner, 17 SEER2", True),
    ("GW-HP18", "Heat pump, 18 SEER2", True),
    ("GW-FG98M", "Gas furnace, 98% AFUE, modulating", False),
    ("GW-HP20V", "Heat pump, variable speed", True),
]
NOT_ELIGIBLE = [
    ("GW-AC13", "Air conditioner, 13.4 SEER2"),
    ("GW-HP14", "Heat pump, 14.3 SEER2"),
    ("GW-FG80", "Gas furnace, 80% AFUE"),
]


def draw(rng, spec):
    n_steps = round((spec["high"] - spec["low"]) / spec["step"])
    value = spec["low"] + rng.randint(0, n_steps) * spec["step"]
    return round(value, 4)


def round_to(x, step):
    return int(round(x / step) * step)


def main():
    rng = random.Random(SEED)
    drawn = {name: draw(rng, spec) for name, spec in RANGES.items()}

    # Per-unit amounts: interpolate floor -> ceiling across efficiency rank,
    # with a seeded jitter so the ladder isn't perfectly linear. Rounded to $5.
    floor, ceiling = drawn["bonus_floor_usd"], drawn["bonus_ceiling_usd"]
    uplift = 1 + drawn["spring_uplift_pct"] / 100
    models = []
    for rank, (code, desc, spring) in enumerate(MODELS):
        base = floor + (ceiling - floor) * rank / (len(MODELS) - 1)
        base *= 1 + rng.uniform(-0.08, 0.08)
        standard = round_to(base, 5)
        models.append({
            "model": code,
            "description": desc,
            "standard_usd": standard,
            "spring_usd": round_to(standard * uplift, 5) if spring else standard,
        })

    t2 = drawn["tier2_threshold_usd"]
    t3 = round_to(t2 * drawn["tier3_multiple"], 50_000)
    t4 = round_to(t3 * drawn["tier4_multiple"], 50_000)
    r2 = drawn["tier2_rate_pct"]
    r3 = r2 + drawn["tier3_step_pct"]
    r4 = r3 + drawn["tier4_step_pct"]

    rng11 = random.Random(int(hashlib.sha256(SEED_STRING_V11.encode()).hexdigest(), 16) % (2**32))
    drawn11 = {name: draw(rng11, spec) for name, spec in RANGES_V11.items()}

    start = int(drawn["spring_start_month"])
    end = start + int(drawn["spring_length_months"]) - 1

    params = {
        "seed_string": SEED_STRING,
        "seed": SEED,
        "program_year": 2025,
        "filing_deadline_days": int(drawn["filing_deadline_days"]),
        "late_doc_grace_days": int(drawn["late_doc_grace_days"]),
        "late_doc_partial_pct": int(drawn["late_doc_partial_pct"]),
        "spring_start_month": start,
        "spring_end_month": end,
        "spring_uplift_pct": int(drawn["spring_uplift_pct"]),
        "models": models,
        "not_eligible": [{"model": m, "description": d} for m, d in NOT_ELIGIBLE],
        "tiers": [
            {"tier": 1, "threshold_usd": 0, "rate_pct": 0.0, "method": "none"},
            {"tier": 2, "threshold_usd": t2, "rate_pct": r2, "method": "retroactive"},
            {"tier": 3, "threshold_usd": t3, "rate_pct": r3, "method": "retroactive"},
            {"tier": 4, "threshold_usd": t4, "rate_pct": r4, "method": "incremental"},
        ],
        "growth_threshold_pct": int(drawn["growth_threshold_pct"]),
        "growth_bonus_pct": drawn["growth_bonus_pct"],
        "claim_processing_days": int(drawn11["claim_processing_days"]),
        "rebate_payment_days": int(drawn11["rebate_payment_days"]),
        "ranges": {**RANGES, **RANGES_V11},
        "draws": {**drawn, **drawn11},
        "seed_string_v11": SEED_STRING_V11,
    }
    OUT.write_text(json.dumps(params, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in params.items() if k not in ("ranges", "draws")}, indent=2))


if __name__ == "__main__":
    main()
