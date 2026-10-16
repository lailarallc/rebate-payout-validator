"""Check the generated universe against the pinned aggregate bounds.

Bounds are sanity checks on the whole, never sources for the parts. Pinned 2026-10-15:
no re-tuning if a result is undramatic. This script reports PASS/FAIL. It never adjusts anything.

Output: build/bound_check.json
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "build" / "results.json"
OUT = ROOT / "build" / "bound_check.json"

# (low, high) in basis points of the denominator
BOUNDS = [
    {
        "id": "spiff_claim_share",
        "what": "Share of paid install-bonus claims carrying a defect",
        "low_bp": 600, "high_bp": 1500,
        "source": "ProfitOptics 2026: 6-15% of claims fail basic validation (vendor)",
    },
    {
        "id": "overpaid_dollar_share",
        "what": "Overpaid dollars as a share of all dollars approved for payout",
        "low_bp": 1000, "high_bp": 1500,
        "source": "Zyme/Forrester 2013: OEMs overpay incentives 10-15% (vendor PR, second-hand)",
    },
]


def main():
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    spiff_flagged = r["families"]["spiff"]["flagged_records"]
    measured = {
        "spiff_claim_share": (spiff_flagged, r["universe"]["paid_claims"]),
        "overpaid_dollar_share": (r["verdict"]["over_cents"], r["verdict"]["approved_cents"]),
    }
    out = []
    for b in BOUNDS:
        num, den = measured[b["id"]]
        bp = num * 10000 // den
        out.append(dict(b, numerator=num, denominator=den, measured_bp=bp,
                        result="PASS" if b["low_bp"] <= bp <= b["high_bp"] else "FAIL"))
        print(f"{out[-1]['result']}  {b['what']}: {bp / 100:.2f}% "
              f"(bound {b['low_bp'] / 100:g}-{b['high_bp'] / 100:g}%)")
    OUT.write_text(json.dumps({"bounds": out}, sort_keys=True, separators=(",", ":")) + "\n",
                   encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
