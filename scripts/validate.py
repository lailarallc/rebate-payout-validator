"""Validate every Galewick payout against the published rules.

Reads only what Galewick's systems hold (data/*.csv, never data/planted.csv) and the
rule parameters. For each claim and distributor-quarter it computes EARNED from the
rules, compares to PAID, and when they differ names every rule the record breaks.

Output: build/results.json (canonical: sorted keys, no floats, money in cents).
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from generate_universe import (  # noqa: E402  shared rule arithmetic, not shared data
    AS_OF, DEADLINE, ELIGIBLE, GRACE, NON_B1, PARTIAL_PCT, PROCESSING, YEAR, amount_cents, correct_method,
    correct_rebate, growth_cents, paid_rebate, tier_for,
)

DATA = ROOT / "data"
OUT = ROOT / "build" / "results.json"

CLASSES = {
    1: ("Duplicate serial, same contractor", "A6.1", "evidence", "spiff"),
    2: ("Duplicate serial, two contractors", "A6.1", "evidence", "spiff"),
    3: ("Factory serial collision denied as duplicate", "A6.2", "evidence", "spiff"),
    4: ("Rain-check substitute paid", "A7.2", "eligibility", "spiff"),
    5: ("Install outside program year", "A3.1", "evidence", "spiff"),
    6: ("Filed late, paid anyway", "A4.1", "evidence", "spiff"),
    7: ("Ineligible model", "A2.1", "eligibility", "spiff"),
    8: ("Missing or mismatched documentation", "A5", "evidence", "spiff"),
    9: ("Wrong bonus amount", "A2.2", "math", "spiff"),
    10: ("Ineligible contractor", "A1.2", "eligibility", "spiff"),
    11: ("Valid claim denied or unprocessed", "A9.1", "math", "spiff"),
    12: ("Wrong tier", "B4.1", "math", "tier"),
    13: ("Retroactive vs. incremental misapplied", "B4", "math", "tier"),
    14: ("Returns not netted", "B3.2", "math", "tier"),
    15: ("Wrong growth baseline", "B5.2", "math", "tier"),
    16: ("Ineligible SKUs in volume", "B3.3", "eligibility", "tier"),
    17: ("Earned tier paid at a lower tier", "B4.2", "math", "tier"),
    18: ("Partial payment with no rule basis", "A8.3", "math", "spiff"),
}
# Fixed precedence (rulebook Part C2): eligibility -> evidence -> math, rule order within group.
PRECEDENCE = [10, 4, 7, 16, 1, 2, 3, 5, 6, 8, 9, 18, 11, 14, 12, 17, 13, 15]

ALL_TABLE_AMOUNTS = {100 * m[k] for m in ELIGIBLE.values() for k in ("standard_usd", "spring_usd")}


def d(s):
    return date.fromisoformat(s) if s else None


def read(name):
    with open(DATA / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def money(c):
    sign = "-" if c < 0 else ""
    c = abs(c)
    return f"{sign}${c // 100:,}.{c % 100:02d}"


# ---------------------------------------------------------------- Part A

def validate_claims():
    contractors = {r["contractor_id"]: r for r in read("contractors.csv")}
    coll = read("serial_collisions.csv")
    coll_keys = {(r["serial"], r["model"]) for r in coll}
    coll_serials = {r["serial"] for r in coll}
    claims = read("claims.csv")
    claims.sort(key=lambda r: (r["received_date"], r["claim_id"]))

    earned_by = {}   # A6 key -> claim_id of the first valid claim
    out = []
    in_process = 0
    for r in claims:
        inst, recv = d(r["install_date"]), d(r["received_date"])
        inv, reg = d(r["invoice_doc_date"]), d(r["registration_doc_date"])
        paid = int(r["paid_cents"])
        c = contractors[r["contractor_id"]]
        # The invoice shows the unit installed. Without an invoice, only the claim says what it was.
        model = r["invoice_model"] or r["claim_model"]
        v = {}  # class -> evidence

        # A1 — contractor active on install date
        enr, end = d(c["enrollment_date"]), d(c["end_date"])
        if inst < enr or (end and inst > end):
            v[10] = (f"{c['name']} enrolled {enr}" + (f", ended {end}" if end else "")
                     + f"; install {inst}")
        # A7 — substitution: installed model must itself be eligible
        if model != r["ordered_model"] and model not in ELIGIBLE:
            v[4] = f"Ordered {r['ordered_model']}, installed {model} (not in Table A1)"
        # A2.1 — eligible model
        elif model not in ELIGIBLE:
            v[7] = f"{model} is not in Table A1"
        # A3 — install in program year
        if inst.year != YEAR:
            v[5] = f"Install date {inst} is outside {YEAR}"
        # A4 — filed within deadline
        lag = (recv - inst).days
        if lag > DEADLINE:
            v[6] = f"Received {recv}, installed {inst}: {lag} days > {DEADLINE}"
        # A5 — documentation. Both documents due within the A4.1 deadline (A5.3); a document up to
        # GRACE days late is "late" (A8), later is treated as missing. A late claim is judged
        # under A4.1 alone: only a missing document counts against it.
        on_time = lag <= DEADLINE

        def doc_state(dd):
            if dd is None:
                return "missing"
            if not on_time:
                return "ok"
            days = (dd - inst).days
            return "ok" if days <= DEADLINE else "late" if days <= DEADLINE + GRACE else "missing"

        states = {"Installation invoice": doc_state(inv), "Warranty registration": doc_state(reg)}
        doc_issue = None
        missing = [k for k, s in states.items() if s == "missing"]
        late = [k for k, s in states.items() if s == "late"]
        if missing:
            k = missing[0]
            dd = inv if k == "Installation invoice" else reg
            doc_issue = (f"{k} missing" if dd is None else
                         f"{k} received {dd}: {(dd - inst).days} days after install > {DEADLINE} + {GRACE}")
        elif len(late) == 2:
            doc_issue = "Both documents received after the deadline; A8 covers only one"
        elif inv is not None and r["invoice_serial"] != r["serial"]:
            doc_issue = f"Invoice serial {r['invoice_serial']} does not match claim serial {r['serial']}"
        elif inv is not None and r["invoice_model"] != r["claim_model"]:
            doc_issue = f"Invoice shows {r['invoice_model']}; claim names {r['claim_model']}"
        if doc_issue:
            v[8] = doc_issue
        partial = on_time and not doc_issue and len(late) == 1

        # A6 — one bonus per unit (collision serials are keyed by serial + model)
        key = (r["serial"], model) if r["serial"] in coll_serials else r["serial"]
        otherwise_valid = not v
        if otherwise_valid:
            if key in earned_by:
                first = earned_by[key]
                same = first[1] == r["contractor_id"]
                v[1 if same else 2] = f"Serial {r['serial']} already earned on {first[0]}" + (
                    "" if same else f" by {contractors[first[1]]['name']}")
            else:
                earned_by[key] = (r["claim_id"], r["contractor_id"])

        full = amount_cents(model, inst) if model in ELIGIBLE else 0
        earned = 0 if v else (full * PARTIAL_PCT // 100 if partial else full)

        # C0 / A9.3: pending and received within the last PROCESSING days = still in process
        if r["status"] == "pending" and (AS_OF - recv).days <= PROCESSING:
            in_process += 1
            continue
        if paid == earned:
            continue

        present = {}
        if paid > earned:
            present.update(v)
        if model in ELIGIBLE and paid > 0:
            if paid != full and paid != full * PARTIAL_PCT // 100:
                if paid in ALL_TABLE_AMOUNTS:
                    present[9] = f"Paid {money(paid)}; Table A1 amount for {model} on {inst} is {money(full)}"
                else:
                    present[18] = (f"Paid {money(paid)} of {money(full)}; matches no Table A1 amount "
                                   f"and A8.2 does not apply")
        if paid == 0 and earned > 0:
            if (r["serial"], model) in coll_keys and r["denial_reason"] == "Duplicate serial":
                present[3] = f"Serial {r['serial']} + {model} is a listed manufacturing collision (Table A2)"
            else:
                present[11] = (f"Meets A1-A7; status {r['status']}"
                               + (f" ({r['denial_reason']})" if r["denial_reason"] else " (no reason recorded)"))
        if not present:
            raise SystemExit(f"unexplained difference on {r['claim_id']}: paid {paid} earned {earned}")
        out.append({
            "record_type": "claim", "record_id": r["claim_id"], "family": "spiff",
            "member_id": r["contractor_id"], "member_name": c["name"],
            "paid_cents": paid, "earned_cents": earned, "delta_cents": paid - earned,
            "classes": sorted(present), "evidence": {str(k): present[k] for k in sorted(present)},
            "detail": {"serial": r["serial"], "model": model, "install_date": r["install_date"],
                       "received_date": r["received_date"], "status": r["status"]},
        })
    total_paid = sum(int(r["paid_cents"]) for r in claims)
    return out, total_paid, len(claims), sum(1 for r in claims if int(r["paid_cents"]) > 0), in_process


# ---------------------------------------------------------------- Part B

def validate_statements():
    dist = {r["distributor_id"]: r for r in read("distributors.csv")}
    names = {k: r["name"] for k, r in dist.items()}
    q_of = lambda s: (date.fromisoformat(s).month - 1) // 3 + 1  # noqa: E731
    equip, nonb1, ret = {}, {}, {}
    for r in read("purchase_lines.csv"):
        k = (r["distributor_id"], q_of(r["invoice_date"]))
        bucket = nonb1 if r["sku"] in NON_B1 else equip
        bucket[k] = bucket.get(k, 0) + int(r["amount_cents"])
    for r in read("return_credits.csv"):
        k = (r["distributor_id"], q_of(r["credit_date"]))
        ret[k] = ret.get(k, 0) + int(r["amount_cents"])
    baseline = {(r["distributor_id"], int(r["quarter"])): int(r["qualifying_volume_cents"])
                for r in read("baselines_2024.csv")}

    stmts = read("rebate_statements.csv")
    qual = {}
    for s in stmts:
        k = (s["distributor_id"], int(s["quarter"]))
        qual[k] = equip.get(k, 0) - ret.get(k, 0)

    out = []
    for s in stmts:
        k = (s["distributor_id"], int(s["quarter"]))
        basis, t_app, meth = int(s["volume_basis_cents"]), int(s["tier_applied"]), s["method_applied"]
        bl_used = int(s["baseline_used_cents"]) if s["baseline_used_cents"] else None
        paid = int(s["total_paid_cents"])
        # statement must be internally consistent: its fields reproduce its own amount
        assert paid_rebate(basis, t_app, meth if t_app > 1 else "retroactive") + growth_cents(basis, bl_used) == paid, k

        q = qual[k]
        tier = tier_for(q)
        bl = baseline.get(k)
        # B1: enrolled for the full quarter
        enrolled = date.fromisoformat(dist[k[0]]["enrollment_date"]) <= date(YEAR, 3 * (k[1] - 1) + 1, 1)
        earned = correct_rebate(q, tier) + growth_cents(q, bl) if enrolled else 0
        if paid == earned:
            continue

        present = {}
        extra = basis - q
        nb, rt = nonb1.get(k, 0), ret.get(k, 0)
        if extra in (nb, nb + rt) and nb > 0 and extra != 0:
            present[16] = f"Volume basis includes {money(nb)} of parts, accessories, controls and freight"
        if extra in (rt, nb + rt) and rt > 0 and extra != 0:
            present[14] = f"Volume basis {money(basis)} omits {money(rt)} of return credits"
        right_tier = tier_for(basis)
        prior = tier_for(qual[(k[0], k[1] - 1)]) if k[1] > 1 else None
        if t_app != right_tier:
            if prior is not None and t_app == prior and t_app < right_tier:
                present[17] = f"Paid at Tier {t_app} (Q{k[1] - 1} tier); Q{k[1]} volume reaches Tier {right_tier}"
            else:
                present[12] = f"Paid at Tier {t_app}; volume basis {money(basis)} sets Tier {right_tier}"
        if t_app > 1 and meth != correct_method(t_app):
            present[13] = f"Tier {t_app} paid {meth}; Table B2 says {correct_method(t_app)}"
        if bl_used != bl:
            present[15] = (f"Growth tested against {money(bl_used) if bl_used else 'no baseline'}; "
                           f"Table B3 baseline is {money(bl) if bl else 'none'}")
        if not present:
            raise SystemExit(f"unexplained difference on {k}: paid {paid} earned {earned}")
        out.append({
            "record_type": "statement", "record_id": f"{k[0]}-Q{k[1]}", "family": "tier",
            "member_id": k[0], "member_name": names[k[0]],
            "paid_cents": paid, "earned_cents": earned, "delta_cents": paid - earned,
            "classes": sorted(present), "evidence": {str(c): present[c] for c in sorted(present)},
            "detail": {"quarter": k[1], "qualifying_volume_cents": q, "tier_earned": tier,
                       "tier_applied": t_app},
        })
    total_paid = sum(int(s["total_paid_cents"]) for s in stmts)
    return out, total_paid, len(stmts)


# ---------------------------------------------------------------- summary

def primary(classes):
    return min(classes, key=PRECEDENCE.index)


def main():
    flagged_a, paid_a, n_claims, n_paid_claims, n_in_process = validate_claims()
    flagged_b, paid_b, n_stmts = validate_statements()
    flagged = flagged_a + flagged_b
    for f in flagged:
        f["primary"] = primary(f["classes"])

    over = sum(f["delta_cents"] for f in flagged if f["delta_cents"] > 0)
    under = -sum(f["delta_cents"] for f in flagged if f["delta_cents"] < 0)
    approved = paid_a + paid_b

    classes = []
    for c, (label, rule, group, fam) in CLASSES.items():
        prim = [f for f in flagged if f["primary"] == c]
        classes.append({
            "class": c, "label": label, "rule": rule, "group": group, "family": fam,
            "primary_count": len(prim),
            "present_count": sum(1 for f in flagged if c in f["classes"]),
            "over_cents": sum(f["delta_cents"] for f in prim if f["delta_cents"] > 0),
            "under_cents": -sum(f["delta_cents"] for f in prim if f["delta_cents"] < 0),
        })
    assert sum(x["over_cents"] for x in classes) == over
    assert sum(x["under_cents"] for x in classes) == under

    fam_totals = {}
    for fam, paid in (("spiff", paid_a), ("tier", paid_b)):
        fs = [f for f in flagged if f["family"] == fam]
        fam_totals[fam] = {
            "paid_cents": paid,
            "over_cents": sum(f["delta_cents"] for f in fs if f["delta_cents"] > 0),
            "under_cents": -sum(f["delta_cents"] for f in fs if f["delta_cents"] < 0),
            "flagged_records": len(fs),
        }

    result = {
        "schema_version": 1,
        "program_year": YEAR,
        "verdict": {
            "approved_cents": approved,
            "over_cents": over,
            "under_cents": under,
            "flagged_records": len(flagged),
            "multi_defect_records": sum(1 for f in flagged if len(f["classes"]) > 1),
        },
        "universe": {"claims": n_claims, "paid_claims": n_paid_claims, "in_process_claims": n_in_process,
                     "statements": n_stmts, "as_of": AS_OF.isoformat()},
        "families": fam_totals,
        "classes": classes,
        "precedence": PRECEDENCE,
        "flagged": sorted(flagged, key=lambda f: (f["record_type"], f["record_id"])),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n",
                   encoding="utf-8", newline="\n")
    v = result["verdict"]
    print(f"approved {money(approved)}  over {money(over)}  under {money(under)}  "
          f"flagged {v['flagged_records']}  multi {v['multi_defect_records']}")


if __name__ == "__main__":
    main()
