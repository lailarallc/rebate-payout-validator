"""Generate the Galewick universe: one program year of contractor install-bonus claims
and distributor volume-rebate statements, with defects seeded at the pinned rates.

Seed-locked and byte-stable. Money is integer cents. No wall-clock values.

Inputs:  rules/parameters.json (seeded program parameters)
Outputs: data/*.csv            (what Galewick's systems hold — the validator reads these)
         data/planted.csv      (the defects the generator planted — never read by the validator;
                                used only by tests to prove the validator recovers them exactly)

Rates (docs/anchors-research.md, pinned 2026-10-15): C 2.0% / O 0.75% / R 0.2%.
"""

import csv
import hashlib
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARAMS = json.loads((ROOT / "rules" / "parameters.json").read_text(encoding="utf-8"))
DATA = ROOT / "data"

SEED = int(hashlib.sha256(b"galewick-climate-systems/program-year-2025/universe").hexdigest(), 16) % (2**32)

RATE = {"C": 0.02, "O": 0.0075, "R": 0.002}

# Defect classes -> frequency tag (docs/clarify-log.md, owner calls + accepted guesses)
SPIFF_TAGS = {1: "R", 2: "R", 3: "R", 4: "O", 5: "O", 6: "C", 7: "C", 8: "O", 9: "O", 10: "O", 11: "C", 18: "O"}
TIER_TAGS = {12: "C", 13: "O", 14: "C", 15: "O", 16: "C", 17: "C"}

# Universe size (design gate, pinned)
N_CONTRACTORS = 350
N_SPIFF_BASE = 12_000          # clean paid claims before seeding; rate denominator
N_DISTRIBUTORS = 160
CORRECT_REJECT_SHARE = 0.115   # direction: ~13% rejection (Navigant 2013 Con Ed eval)

YEAR = PARAMS["program_year"]
DEADLINE = PARAMS["filing_deadline_days"]
GRACE = PARAMS["late_doc_grace_days"]
PARTIAL_PCT = PARAMS["late_doc_partial_pct"]
SPRING = range(PARAMS["spring_start_month"], PARAMS["spring_end_month"] + 1)
ELIGIBLE = {m["model"]: m for m in PARAMS["models"]}
INELIGIBLE = [m["model"] for m in PARAMS["not_eligible"]]
TIERS = PARAMS["tiers"]

# Install-month seasonality (DIRECTION: cooling peak spring/summer, heating bump fall/winter)
MONTH_WEIGHTS = [5, 4, 7, 9, 11, 12, 12, 11, 8, 7, 7, 7]
MODEL_WEIGHTS = {"GW-AC15": 22, "GW-HP16": 20, "GW-FG96": 15, "GW-AC17": 13,
                 "GW-HP18": 12, "GW-FG98M": 8, "GW-HP20V": 10}
FURNACE_MONTHS = {1, 2, 10, 11, 12}

# Distributor equipment list prices (cents) — invented, used only to build invoice lines
LIST_PRICE = {"GW-AC13": 210000, "GW-AC15": 265000, "GW-AC17": 340000, "GW-HP14": 280000,
              "GW-HP16": 335000, "GW-HP18": 420000, "GW-HP20V": 560000, "GW-FG80": 145000,
              "GW-FG96": 230000, "GW-FG98M": 330000}
NON_B1 = ["PARTS", "ACCESSORIES", "CONTROLS", "FREIGHT"]

PREFIX = ["Bren", "Cal", "Dun", "Ash", "Mar", "Hol", "Kel", "Lin", "Run", "Sal", "Tor", "Wex",
          "Ald", "Bray", "Cor", "Fen", "Gar", "Hart", "Lom", "Pell", "Quen", "Ros", "Strat", "Ul",
          "Vant", "Yar", "Ober", "Nesh", "Thorn", "Wil"]
SUFFIX = ["vale", "ford", "ton", "more", "field", "brook", "mont", "dale", "by", "stead", "well",
          "ridge", "port", "ley"]
CONTRACTOR_KIND = ["Heating & Air", "Comfort Co.", "Mechanical", "Climate Services", "Air & Heat",
                   "Home Comfort", "HVAC"]
DISTRIBUTOR_KIND = ["HVAC Supply", "Distribution", "Supply Co.", "Equipment Supply"]
DENIAL_TEXT = {
    "ineligible_model": "Model not eligible",
    "contractor_inactive": "Contractor not active",
    "late": "Received after deadline",
    "missing_docs": "Missing documentation",
    "out_of_window": "Install date outside program",
    "duplicate": "Duplicate serial",
}


def family(model):
    return model.split("-")[1][:2]  # AC / HP / FG


def is_spring(model, d):
    return family(model) != "FG" and d.year == YEAR and d.month in SPRING


def amount_cents(model, d):
    m = ELIGIBLE[model]
    return 100 * (m["spring_usd"] if is_spring(model, d) else m["standard_usd"])


def rand_date(rng, start, end):
    return start + timedelta(days=rng.randint(0, (end - start).days))


def place(rng, used):
    while True:
        name = rng.choice(PREFIX) + rng.choice(SUFFIX)
        if name not in used:
            used.add(name)
            return name


def n_for(tag, base):
    return round(RATE[tag] * base)


# ---------------------------------------------------------------- contractors / distributors

def make_distributors(rng):
    used = set()
    out = []
    for i in range(N_DISTRIBUTORS):
        out.append({
            "distributor_id": f"D{i + 1:03d}",
            "name": f"{place(rng, used)} {rng.choice(DISTRIBUTOR_KIND)}",
        })
    return out


def make_contractors(rng, distributors):
    used = set()
    out = []
    for i in range(N_CONTRACTORS):
        r = rng.random()
        if r < 0.08:      # enrolled during the program year
            enrolled = rand_date(rng, date(YEAR, 2, 1), date(YEAR, 9, 30))
        else:
            enrolled = rand_date(rng, date(2019, 1, 1), date(YEAR - 1, 12, 31))
        ended = ""
        if rng.random() < 0.045:  # terminated during the program year
            ended = rand_date(rng, max(enrolled + timedelta(days=60), date(YEAR, 4, 1)), date(YEAR, 11, 30))
        out.append({
            "contractor_id": f"C{i + 1:04d}",
            "name": f"{place(rng, used)} {rng.choice(CONTRACTOR_KIND)}",
            "enrollment_date": enrolled,
            "end_date": ended,
            "home_distributor_id": rng.choice(distributors)["distributor_id"],
            "size": rng.lognormvariate(0, 0.9),
        })
    return out


def active_on(c, d):
    return c["enrollment_date"] <= d and (c["end_date"] == "" or d <= c["end_date"])


# ---------------------------------------------------------------- claims

class Serials:
    def __init__(self, rng):
        self.rng = rng
        self.used = set()

    def new(self):
        while True:
            s = f"GW{self.rng.randint(0, 9_999_999):07d}"
            if s not in self.used:
                self.used.add(s)
                return s


def pick_model(rng, month):
    models = list(MODEL_WEIGHTS)
    w = [MODEL_WEIGHTS[m] * (2.0 if family(m) == "FG" and month in FURNACE_MONTHS else
                             0.3 if family(m) == "FG" else 1.0) for m in models]
    return rng.choices(models, w)[0]


def pick_install(rng, c):
    while True:
        month = rng.choices(range(1, 13), MONTH_WEIGHTS)[0]
        d = date(YEAR, month, rng.randint(1, 28 if month == 2 else 30))
        if active_on(c, d):
            return d


def clean_claim(rng, serials, c, model=None, install=None):
    install = install or pick_install(rng, c)
    model = model or pick_model(rng, install.month)
    while True:
        lag = max(1, int(rng.lognormvariate(math.log(16), 0.6)))
        if lag <= DEADLINE:
            break
    received = install + timedelta(days=lag)
    reg = install + timedelta(days=rng.randint(0, min(10, lag)))
    serial = serials.new()
    return {
        "contractor_id": c["contractor_id"],
        "distributor_id": c["home_distributor_id"],
        "serial": serial,
        "invoice_serial": serial,
        "ordered_model": model,
        "invoice_model": model,
        "claim_model": model,
        "install_date": install,
        "received_date": received,
        "invoice_doc_date": received,
        "registration_doc_date": reg,
        "status": "paid",
        "denial_reason": "",
        "paid_cents": amount_cents(model, install),
        "planted": [],
    }


def generate_claims(rng, contractors):
    serials = Serials(rng)
    weights = [c["size"] for c in contractors]
    by_id = {c["contractor_id"]: c for c in contractors}

    claims = [clean_claim(rng, serials, rng.choices(contractors, weights)[0]) for _ in range(N_SPIFF_BASE)]

    # Rule-consistent partial payments (A8): filed on time, registration within grace. Not defects.
    for cl in rng.sample(claims, round(0.0075 * N_SPIFF_BASE)):
        cl["registration_doc_date"] = cl["install_date"] + timedelta(days=DEADLINE + rng.randint(1, GRACE))
        cl["paid_cents"] = amount_cents(cl["claim_model"], cl["install_date"]) * PARTIAL_PCT // 100
        cl["rule_partial"] = True

    pool = [cl for cl in claims if not cl.get("rule_partial")]
    rng.shuffle(pool)
    # Under-direction classes and duplicate sources need otherwise-untouched claims: reserve them.
    reserved = {}
    cursor = 0
    for cls in (3, 11, 18, 1, 2):
        k = n_for(SPIFF_TAGS[cls], N_SPIFF_BASE)
        reserved[cls] = pool[cursor:cursor + k]
        cursor += k
    over_pool = pool[cursor:]

    # --- over classes: independent draws from the remaining pool (overlaps arise naturally)
    def draw(cls, exclude=()):
        cands = [cl for cl in over_pool if not (set(cl["planted"]) & set(exclude))]
        return rng.sample(cands, n_for(SPIFF_TAGS[cls], N_SPIFF_BASE))

    # #5 install outside program year (shift install, receipt and docs together). The new date
    # must keep the contractor active, and the payment is the amount a processor would compute
    # for that date, so the claim breaks A3 and nothing else.
    by_cid = {c["contractor_id"]: c for c in contractors}
    n5 = n_for(SPIFF_TAGS[5], N_SPIFF_BASE)
    cands5 = over_pool[:]
    rng.shuffle(cands5)
    for cl in cands5:
        if n5 == 0:
            break
        c = by_cid[cl["contractor_id"]]
        while True:
            if rng.random() < 0.6:
                new = rand_date(rng, date(YEAR - 1, 11, 15), date(YEAR - 1, 12, 31))
            else:
                new = rand_date(rng, date(YEAR + 1, 1, 1), date(YEAR + 1, 2, 10))
            if active_on(c, new):
                break
            if c["enrollment_date"].year == YEAR and c["end_date"] != "":
                new = None
                break
        if new is None:
            continue
        shift = new - cl["install_date"]
        for f in ("install_date", "received_date", "invoice_doc_date", "registration_doc_date"):
            cl[f] = cl[f] + shift
        cl["paid_cents"] = amount_cents(cl["claim_model"], cl["install_date"])
        cl["planted"].append(5)
        n5 -= 1
    assert n5 == 0

    # #6 filed after deadline, paid anyway
    for cl in draw(6):
        cl["received_date"] = cl["install_date"] + timedelta(days=DEADLINE + rng.randint(1, 45))
        cl["invoice_doc_date"] = cl["received_date"]
        cl["planted"].append(6)

    # #4 rain-check substitute: ordered an eligible model, installed the ineligible one, paid as ordered
    for cl in draw(4):
        sub = {"AC": "GW-AC13", "HP": "GW-HP14", "FG": "GW-FG80"}[family(cl["ordered_model"])]
        cl["invoice_model"] = cl["claim_model"] = sub
        cl["planted"].append(4)

    # #7 ineligible model installed as ordered, paid at the family's entry amount
    for cl in draw(7, exclude=(4,)):
        fam = family(cl["ordered_model"])
        bad = {"AC": "GW-AC13", "HP": "GW-HP14", "FG": "GW-FG80"}[fam]
        entry = {"AC": "GW-AC15", "HP": "GW-HP16", "FG": "GW-FG96"}[fam]
        cl["ordered_model"] = cl["invoice_model"] = cl["claim_model"] = bad
        cl["paid_cents"] = amount_cents(entry, cl["install_date"])
        cl["planted"].append(7)

    # #8 missing or mismatched documentation
    for cl in draw(8):
        v = rng.random()
        if v < 0.5:
            cl["registration_doc_date"] = ""
        elif v < 0.75:
            cl["registration_doc_date"] = cl["install_date"] + timedelta(days=DEADLINE + GRACE + rng.randint(1, 40))
        else:
            s = cl["serial"]
            cl["invoice_serial"] = s[:-2] + f"{(int(s[-2:]) + rng.randint(1, 98)) % 100:02d}"
        cl["planted"].append(8)

    # #10 ineligible contractor: claim belongs to a contractor not active on the install date
    candidates = [c for c in contractors if c["enrollment_date"].year == YEAR or c["end_date"] != ""]
    for cl in draw(10):
        options = [c for c in candidates if not active_on(c, cl["install_date"])]
        c = rng.choice(options)
        cl["contractor_id"] = c["contractor_id"]
        cl["distributor_id"] = c["home_distributor_id"]
        cl["planted"].append(10)

    # #9 wrong bonus amount (only on claims whose installed model is eligible)
    for cl in draw(9, exclude=(4, 7)):
        model, d = cl["claim_model"], cl["install_date"]
        right = amount_cents(model, d)
        if family(model) != "FG" and ELIGIBLE[model]["spring_usd"] != ELIGIBLE[model]["standard_usd"]:
            m = ELIGIBLE[model]
            wrong = 100 * (m["standard_usd"] if is_spring(model, d) else m["spring_usd"])
        else:
            others = [amount_cents(o, d) for o in ELIGIBLE if family(o) == family(model) and o != model]
            wrong = rng.choice(others)
        assert wrong != right
        cl["paid_cents"] = wrong
        cl["planted"].append(9)

    # --- under classes on reserved, otherwise-valid claims
    for cl in reserved[11]:
        if rng.random() < 0.7:
            cl["status"] = "denied"
            cl["denial_reason"] = rng.choice(["", "", DENIAL_TEXT["missing_docs"], DENIAL_TEXT["late"]])
        else:
            cl["status"] = "pending"
        cl["paid_cents"] = 0
        cl["planted"].append(11)

    for cl in reserved[18]:
        full = amount_cents(cl["claim_model"], cl["install_date"])
        bad = {full * PARTIAL_PCT // 100} | {100 * m[k] for m in ELIGIBLE.values()
                                              for k in ("standard_usd", "spring_usd")}
        while True:
            paid = 100 * round(full * rng.uniform(0.35, 0.9) / 100)
            if 0 < paid < full and paid not in bad:
                break
        cl["paid_cents"] = paid
        cl["planted"].append(18)

    extra = []
    # #1 / #2 duplicate serial paid again (same / different contractor)
    for cls in (1, 2):
        for src in reserved[cls]:
            if cls == 1:
                c = by_id[src["contractor_id"]]
            else:
                c = rng.choice([x for x in contractors if x["contractor_id"] != src["contractor_id"]
                                and active_on(x, src["install_date"])])
            dup = dict(src, planted=[cls], contractor_id=c["contractor_id"],
                       distributor_id=src["distributor_id"])
            dup["received_date"] = max(src["received_date"] + timedelta(days=rng.randint(1, 20)),
                                       dup["received_date"])
            dup["received_date"] = min(dup["received_date"], dup["install_date"] + timedelta(days=DEADLINE))
            if dup["received_date"] <= src["received_date"]:
                src["received_date"] = dup["received_date"] - timedelta(days=1)
                src["invoice_doc_date"] = src["received_date"]
                src["registration_doc_date"] = min(src["registration_doc_date"], src["received_date"])
            dup["invoice_doc_date"] = dup["received_date"]
            extra.append(dup)

    # #3 factory serial collision: a second physical unit with the same serial, denied as a duplicate
    collisions = []
    for src in reserved[3]:
        fam_models = [m for m in ELIGIBLE if m != src["claim_model"]]
        model2 = rng.choice(fam_models)
        # The second unit must be a fully valid claim received after the original.
        while True:
            c = rng.choice([x for x in contractors if x["home_distributor_id"] != src["distributor_id"]
                            and x["contractor_id"] != src["contractor_id"]])
            unit = clean_claim(rng, serials, c, model=model2, install=pick_install(rng, c))
            if unit["received_date"] > src["received_date"]:
                break
        unit["serial"] = unit["invoice_serial"] = src["serial"]
        unit["status"] = "denied"
        unit["denial_reason"] = DENIAL_TEXT["duplicate"]
        unit["paid_cents"] = 0
        unit["planted"] = [3]
        extra.append(unit)
        collisions.append((src["serial"], src["claim_model"], src["distributor_id"]))
        collisions.append((src["serial"], model2, unit["distributor_id"]))

    # Benign collisions: both units claimed and correctly paid (realism, not defects)
    benign_src = rng.sample([cl for cl in over_pool if not cl["planted"]], 10)
    for src in benign_src:
        model2 = rng.choice([m for m in ELIGIBLE if m != src["claim_model"]])
        c = rng.choice([x for x in contractors if x["home_distributor_id"] != src["distributor_id"]])
        unit = clean_claim(rng, serials, c, model=model2)
        unit["serial"] = unit["invoice_serial"] = src["serial"]
        unit["received_date"] = max(unit["received_date"], src["received_date"] + timedelta(days=1))
        if (unit["received_date"] - unit["install_date"]).days > DEADLINE:
            unit["install_date"] = unit["received_date"] - timedelta(days=DEADLINE - 1)
            unit["registration_doc_date"] = unit["install_date"]
            if unit["install_date"].year != YEAR or not active_on(c, unit["install_date"]):
                continue
            unit["paid_cents"] = amount_cents(model2, unit["install_date"])
        unit["invoice_doc_date"] = unit["received_date"]
        extra.append(unit)
        collisions.append((src["serial"], src["claim_model"], src["distributor_id"]))
        collisions.append((src["serial"], model2, unit["distributor_id"]))

    # Correctly denied claims (not defects): invalid submissions the program rightly rejected
    n_reject = round(CORRECT_REJECT_SHARE * N_SPIFF_BASE)
    reasons = rng.choices(["ineligible_model", "contractor_inactive", "late", "missing_docs",
                           "out_of_window", "duplicate"], [45, 25, 12, 10, 3, 5], k=n_reject)
    paid_valid = [cl for cl in claims if not cl["planted"] and cl["status"] == "paid" and not cl.get("rule_partial")]
    for why in reasons:
        c = rng.choices(contractors, weights)[0]
        cl = clean_claim(rng, serials, c)
        if why == "ineligible_model":
            m = rng.choice(INELIGIBLE)
            cl["ordered_model"] = cl["invoice_model"] = cl["claim_model"] = m
        elif why == "contractor_inactive":
            bad = [x for x in candidates if not active_on(x, cl["install_date"])]
            x = rng.choice(bad)
            cl["contractor_id"], cl["distributor_id"] = x["contractor_id"], x["home_distributor_id"]
        elif why == "late":
            cl["received_date"] = cl["install_date"] + timedelta(days=DEADLINE + rng.randint(1, 90))
            cl["invoice_doc_date"] = cl["received_date"]
        elif why == "missing_docs":
            cl["registration_doc_date"] = ""
        elif why == "out_of_window":
            shift = date(YEAR - 1, rng.randint(9, 12), 15) - cl["install_date"]
            for f in ("install_date", "received_date", "invoice_doc_date", "registration_doc_date"):
                cl[f] = cl[f] + shift
        elif why == "duplicate":
            src = rng.choice(paid_valid)
            for f in ("serial", "invoice_serial", "ordered_model", "invoice_model", "claim_model", "install_date"):
                cl[f] = src[f]
            cl["received_date"] = src["received_date"] + timedelta(days=rng.randint(1, 30))
            cl["invoice_doc_date"] = cl["received_date"]
            cl["registration_doc_date"] = src["registration_doc_date"]
        cl["status"] = "denied"
        cl["paid_cents"] = 0
        # Real reject logs are dirty: about half carry no reason (Navigant 2013: 53% blank)
        cl["denial_reason"] = "" if rng.random() < 0.5 else DENIAL_TEXT[why]
        extra.append(cl)

    allc = claims + extra
    allc.sort(key=lambda cl: (cl["received_date"], cl["serial"], cl["contractor_id"], cl["claim_model"]))
    for i, cl in enumerate(allc):
        cl["claim_id"] = f"A{i + 1:06d}"
    collisions = sorted(set(collisions))
    return allc, collisions


# ---------------------------------------------------------------- distributor volume rebate

def tier_for(volume):
    tier = 1
    for t in TIERS:
        if volume >= 100 * t["threshold_usd"]:
            tier = t["tier"]
    return tier


def rate_bp(tier):
    """Rate in basis points x 100 (so 1.75% -> 17500) to stay in integers."""
    return round(TIERS[tier - 1]["rate_pct"] * 10000)


def rebate_cents(volume, tier, method):
    """method: 'retroactive' (tier rate on all volume) or 'incremental' (graduated)."""
    if tier == 1:
        return 0
    if method == "retroactive":
        return volume * rate_bp(tier) // 1_000_000
    # incremental / graduated: each band at its own rate
    total = 0
    for t in TIERS[1:tier]:
        lo = 100 * t["threshold_usd"]
        nxt = TIERS[t["tier"]]["threshold_usd"] * 100 if t["tier"] < tier else None
        hi = volume if nxt is None else min(volume, nxt)
        if hi > lo:
            total += (hi - lo) * rate_bp(t["tier"]) // 1_000_000
    return total


def correct_rebate(volume, tier):
    if tier == 4:
        t4 = 100 * TIERS[3]["threshold_usd"]
        return t4 * rate_bp(3) // 1_000_000 + (volume - t4) * rate_bp(4) // 1_000_000
    return rebate_cents(volume, tier, "retroactive")


def correct_method(tier):
    return TIERS[tier - 1]["method"]


def paid_rebate(volume, tier, method):
    if tier == 4 and method == "incremental":
        return correct_rebate(volume, 4)
    if tier == 4 and method == "retroactive":
        return volume * rate_bp(4) // 1_000_000
    if method == "incremental":
        return rebate_cents(volume, tier, "incremental")
    return rebate_cents(volume, tier, "retroactive")


def growth_cents(volume, baseline):
    if baseline is None or baseline <= 0:
        return 0
    if volume * 100 >= baseline * PARAMS["growth_threshold_pct"]:
        return volume * round(PARAMS["growth_bonus_pct"] * 10000) // 1_000_000
    return 0


QUARTER_FACTOR = {1: 0.8, 2: 1.25, 3: 1.15, 4: 0.8}  # DIRECTION: cooling-season peak


def generate_volume(rng, distributors):
    skus = list(LIST_PRICE)
    lines, credits, baselines = [], [], []
    quarters = {}
    for d in distributors:
        did = d["distributor_id"]
        base = rng.lognormvariate(math.log(650_000), 0.75) * 100  # cents per quarter
        mix = [rng.uniform(0.5, 1.5) for _ in skus]
        has_baseline = rng.random() > 0.06
        nonb1_share = rng.uniform(0.08, 0.18)
        for q in (1, 2, 3, 4):
            target = base * QUARTER_FACTOR[q] * rng.uniform(0.85, 1.15)
            equip = 0
            for mi in range(3):
                month = 3 * (q - 1) + mi + 1
                for si, sku in enumerate(skus):
                    units = max(0, round(target / 3 * mix[si] / sum(mix) / LIST_PRICE[sku] * rng.uniform(0.7, 1.3)))
                    if units:
                        amt = units * LIST_PRICE[sku]
                        lines.append([did, date(YEAR, month, rng.randint(1, 28)), sku, units, amt])
                        equip += amt
                for sku in NON_B1:
                    amt = 100 * round(target / 3 * nonb1_share / len(NON_B1) * rng.uniform(0.6, 1.4) / 100)
                    lines.append([did, date(YEAR, month, rng.randint(1, 28)), sku, 0, amt])
            ret = 0
            if rng.random() < 0.7:
                for _ in range(rng.randint(1, 4)):
                    sku = rng.choice(skus)
                    units = rng.randint(1, 3)
                    amt = units * LIST_PRICE[sku]
                    if ret + amt > equip * 0.05:
                        break
                    credits.append([did, date(YEAR, 3 * (q - 1) + rng.randint(1, 3), rng.randint(1, 28)), sku, units, amt])
                    ret += amt
            nonb1 = sum(l[4] for l in lines if l[0] == did and l[2] in NON_B1 and (l[1].month - 1) // 3 + 1 == q)
            qual = equip - ret
            baseline = None
            if has_baseline:
                baseline = 100 * round(qual / rng.gauss(1.03, 0.09) / 100)
                baselines.append([did, q, baseline])
            quarters[(did, q)] = {"equip": equip, "returns": ret, "nonb1": nonb1, "qual": qual,
                                  "baseline": baseline}
    return lines, credits, baselines, quarters


def generate_statements(rng, distributors, quarters):
    stmts = {}
    for d in distributors:
        for q in (1, 2, 3, 4):
            k = (d["distributor_id"], q)
            v = quarters[k]
            tier = tier_for(v["qual"])
            stmts[k] = {
                "distributor_id": k[0], "quarter": q,
                "volume_basis_cents": v["qual"], "tier_applied": tier,
                "method_applied": correct_method(tier) if tier > 1 else "none",
                "baseline_used_cents": v["baseline"] if v["baseline"] is not None else "",
                "planted": [],
            }

    keys = sorted(stmts)
    base = len(keys)

    def recompute(s):
        v = quarters[(s["distributor_id"], s["quarter"])]
        rebate = paid_rebate(s["volume_basis_cents"], s["tier_applied"], s["method_applied"])
        bl = s["baseline_used_cents"]
        growth = growth_cents(s["volume_basis_cents"], bl if bl != "" else None)
        return rebate, growth

    def earned(k):
        v = quarters[k]
        return correct_rebate(v["qual"], tier_for(v["qual"])) + growth_cents(v["qual"], v["baseline"])

    # #16 ineligible SKUs counted; #14 returns not netted — both inflate the basis
    def seed_basis(cls, field):
        cands = [k for k in keys if quarters[k][field] > 0 and cls not in stmts[k]["planted"]]
        rng.shuffle(cands)
        n = n_for(TIER_TAGS[cls], base)
        done = 0
        for k in cands:
            if done == n:
                break
            s = stmts[k]
            before = sum(recompute(s))
            s2 = dict(s, volume_basis_cents=s["volume_basis_cents"] + quarters[k][field])
            s2["tier_applied"] = tier_for(s2["volume_basis_cents"])
            s2["method_applied"] = correct_method(s2["tier_applied"]) if s2["tier_applied"] > 1 else "none"
            if sum(recompute(s2)) != before:
                stmts[k] = dict(s2, planted=s["planted"] + [cls])
                done += 1
        assert done == n, cls

    seed_basis(16, "nonb1")
    seed_basis(14, "returns")

    # #17 prior quarter's lower tier carried forward
    true_tier = {k: tier_for(quarters[k]["qual"]) for k in keys}
    cands = [k for k in keys if k[1] > 1 and true_tier[(k[0], k[1] - 1)] < stmts[k]["tier_applied"]
             and not stmts[k]["planted"]]
    for k in rng.sample(cands, n_for(TIER_TAGS[17], base)):
        s = stmts[k]
        s["tier_applied"] = true_tier[(k[0], k[1] - 1)]
        s["method_applied"] = correct_method(s["tier_applied"]) if s["tier_applied"] > 1 else "none"
        s["planted"].append(17)

    # #12 wrong tier (one tier off, not explainable as a carried-forward tier)
    n = n_for(TIER_TAGS[12], base)
    cands = [k for k in keys if 17 not in stmts[k]["planted"]]
    rng.shuffle(cands)
    done = 0
    for k in cands:
        if done == n:
            break
        s = stmts[k]
        right = tier_for(s["volume_basis_cents"])
        opts = [t for t in (right - 1, right + 1) if 1 <= t <= 4]
        prior = true_tier.get((k[0], k[1] - 1))
        opts = [t for t in opts if not (prior is not None and t == prior and t < right)]
        if not opts:
            continue
        before = sum(recompute(s))
        t = rng.choice(opts)
        trial = dict(s, tier_applied=t, method_applied=correct_method(t) if t > 1 else "none")
        if sum(recompute(trial)) == before:
            continue
        stmts[k] = dict(trial, planted=s["planted"] + [12])
        done += 1
    assert done == n

    # #13 retroactive vs incremental misapplied
    n = n_for(TIER_TAGS[13], base)
    cands = [k for k in keys if stmts[k]["tier_applied"] in (2, 3, 4)]
    rng.shuffle(cands)
    done = 0
    for k in cands:
        if done == n:
            break
        s = stmts[k]
        wrong = "incremental" if s["tier_applied"] in (2, 3) else "retroactive"
        trial = dict(s, method_applied=wrong)
        if sum(recompute(trial)) == sum(recompute(s)):
            continue
        stmts[k] = dict(trial, planted=s["planted"] + [13])
        done += 1
    assert done == n

    # #15 growth test against the wrong baseline (prior quarter of this year, or 2024 incl. returns)
    n = n_for(TIER_TAGS[15], base)
    cands = [k for k in keys if quarters[k]["baseline"] is not None]
    rng.shuffle(cands)
    done = 0
    for k in cands:
        if done == n:
            break
        s = stmts[k]
        alts = []
        if k[1] > 1:
            alts.append(quarters[(k[0], k[1] - 1)]["qual"])
        alts.append(100 * round(quarters[k]["baseline"] * rng.uniform(0.85, 0.95) / 100))
        alts.append(100 * round(quarters[k]["baseline"] * rng.uniform(1.05, 1.2) / 100))
        rng.shuffle(alts)
        for alt in alts:
            trial = dict(s, baseline_used_cents=alt)
            if recompute(trial)[1] != recompute(s)[1]:
                stmts[k] = dict(trial, planted=s["planted"] + [15])
                done += 1
                break
    assert done == n

    out = []
    for k in keys:
        s = stmts[k]
        rebate, growth = recompute(s)
        s["rebate_paid_cents"] = rebate
        s["growth_paid_cents"] = growth
        s["total_paid_cents"] = rebate + growth
        out.append(s)
    return out


# ---------------------------------------------------------------- writing

def fmt(v):
    if isinstance(v, date):
        return v.isoformat()
    return v


def write_csv(name, header, rows):
    DATA.mkdir(exist_ok=True)
    with open(DATA / name, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow([fmt(x) for x in r])


def main():
    rng = random.Random(SEED)
    distributors = make_distributors(rng)
    contractors = make_contractors(rng, distributors)
    claims, collisions = generate_claims(rng, contractors)
    lines, credits, baselines, quarters = generate_volume(rng, distributors)
    stmts = generate_statements(rng, distributors, quarters)

    write_csv("distributors.csv", ["distributor_id", "name"],
              [[d["distributor_id"], d["name"]] for d in distributors])
    write_csv("contractors.csv", ["contractor_id", "name", "enrollment_date", "end_date", "home_distributor_id"],
              [[c["contractor_id"], c["name"], c["enrollment_date"], c["end_date"], c["home_distributor_id"]]
               for c in contractors])
    claim_cols = ["claim_id", "contractor_id", "distributor_id", "serial", "invoice_serial", "ordered_model",
                  "invoice_model", "claim_model", "install_date", "received_date", "invoice_doc_date",
                  "registration_doc_date", "status", "denial_reason", "paid_cents"]
    write_csv("claims.csv", claim_cols, [[cl[c] for c in claim_cols] for cl in claims])
    write_csv("serial_collisions.csv", ["serial", "model", "distributor_id"], collisions)
    lines.sort(key=lambda l: (l[0], l[1], l[2]))
    write_csv("purchase_lines.csv", ["distributor_id", "invoice_date", "sku", "units", "amount_cents"], lines)
    credits.sort(key=lambda l: (l[0], l[1], l[2]))
    write_csv("return_credits.csv", ["distributor_id", "credit_date", "sku", "units", "amount_cents"], credits)
    write_csv("baselines_2024.csv", ["distributor_id", "quarter", "qualifying_volume_cents"], baselines)
    stmt_cols = ["distributor_id", "quarter", "volume_basis_cents", "tier_applied", "method_applied",
                 "baseline_used_cents", "rebate_paid_cents", "growth_paid_cents", "total_paid_cents"]
    write_csv("rebate_statements.csv", stmt_cols, [[s[c] for c in stmt_cols] for s in stmts])

    planted = [["claim", cl["claim_id"], ";".join(str(x) for x in sorted(cl["planted"]))]
               for cl in claims if cl["planted"]]
    planted += [["statement", f"{s['distributor_id']}-Q{s['quarter']}", ";".join(str(x) for x in sorted(s["planted"]))]
                for s in stmts if s["planted"]]
    write_csv("planted.csv", ["record_type", "record_id", "classes"], planted)

    print(f"claims {len(claims)}  statements {len(stmts)}  planted records {len(planted)}")


if __name__ == "__main__":
    main()
