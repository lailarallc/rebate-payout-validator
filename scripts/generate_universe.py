"""Generate the Galewick universe: one program year of contractor install-bonus claims
and distributor volume-rebate statements, with defects seeded at the pinned rates.

Seed-locked and byte-stable. Money is integer cents. No wall-clock values.

Inputs:  rules/parameters.json (seeded program parameters)
Outputs: data/*.csv            (what Galewick's systems hold — the validator reads these)
         data/planted.csv      (the defects the generator planted — never read by the validator;
                                used only by tests to prove the validator recovers them exactly)

Rates (docs/anchors-research.md, pinned 2026-10-15): C 2.0% / O 0.75% / R 0.2%.
Realism fixes F1-F17: docs/realism-review.md.
"""

import calendar
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
# Universe size: owner-sourced revision 2026-10-16 (DECISIONS) — program-year payout $500K-$1M.
N_CONTRACTORS = 95
N_SPIFF_BASE = 2_500           # clean claims before seeding; rate denominator
N_DISTRIBUTORS = 60
# Distributor sell-in is driven mostly by what enrolled contractors install (the claim floor
# below); BASE_VOLUME_SCALE sizes the rest. Together they land sell-in near the approved ~$20M,
# which is what the x0.15 tier-threshold scale (roll_parameters.py) is sized for.
BASE_VOLUME_SCALE = 0.05
CORRECT_REJECT_SHARE = 0.115   # direction: ~13% rejection (Navigant 2013 Con Ed eval)

YEAR = PARAMS["program_year"]
DEADLINE = PARAMS["filing_deadline_days"]
GRACE = PARAMS["late_doc_grace_days"]
PARTIAL_PCT = PARAMS["late_doc_partial_pct"]
PROCESSING = PARAMS["claim_processing_days"]
SPRING = range(PARAMS["spring_start_month"], PARAMS["spring_end_month"] + 1)
ELIGIBLE = {m["model"]: m for m in PARAMS["models"]}
INELIGIBLE = [m["model"] for m in PARAMS["not_eligible"]]
TIERS = PARAMS["tiers"]

AS_OF = date(YEAR + 1, 2, 27)                         # rulebook C0
DECIDED_BY = AS_OF - timedelta(days=PROCESSING + 1)   # received on/before this: decided (A9.3 "more than")

BASE_OF = {"AC": "GW-AC13", "HP": "GW-HP14", "FG": "GW-FG80"}   # ineligible builder grade
ENTRY_OF = {"AC": "GW-AC15", "HP": "GW-HP16", "FG": "GW-FG96"}  # lowest eligible step

# Install-month seasonality (DIRECTION: cooling peak spring/summer, heating bump fall/winter)
MONTH_WEIGHTS = [5, 4, 7, 9, 11, 12, 12, 11, 8, 7, 7, 7]
MODEL_WEIGHTS = {"GW-AC15": 22, "GW-HP16": 20, "GW-FG96": 15, "GW-AC17": 13,
                 "GW-HP18": 12, "GW-FG98M": 8, "GW-HP20V": 10}
FURNACE_MONTHS = {1, 2, 10, 11, 12}
# Weekday weights (Mon..Sun). Installs: residential work is mostly weekdays.
INSTALL_WEEKDAY = [1.0, 1.0, 1.0, 1.0, 1.0, 0.4, 0.1]

# Sell-in seasonality by family (DIRECTION): cooling stock ahead of summer, furnaces ahead of winter
QUARTER_FACTOR = {"AC": {1: 0.8, 2: 1.25, 3: 1.15, 4: 0.8},
                  "HP": {1: 0.8, 2: 1.25, 3: 1.15, 4: 0.8},
                  "FG": {1: 1.0, 2: 0.6, 3: 1.0, 4: 1.4}}

# Equipment list prices (cents) — invented. Distributors pay list x their own discount,
# with a mid-year price increase.
LIST_PRICE = {"GW-AC13": 210000, "GW-AC15": 265000, "GW-AC17": 340000, "GW-HP14": 280000,
              "GW-HP16": 335000, "GW-HP18": 420000, "GW-HP20V": 560000, "GW-FG80": 145000,
              "GW-FG96": 230000, "GW-FG98M": 330000}
PRICE_INCREASE_FROM = date(YEAR, 7, 1)
NON_B1 = ["PARTS", "ACCESSORIES", "CONTROLS", "FREIGHT"]

PREFIX = ["Bren", "Calv", "Dorn", "Marv", "Holv", "Kelv", "Lisk", "Torv", "Wexl", "Brayl",
          "Fenw", "Garv", "Lomb", "Quen", "Rosk", "Ulst", "Vant", "Ober", "Nesh", "Thrav",
          "Ilsk", "Sorv", "Tamb", "Alvan", "Corv", "Delm", "Esk", "Harv", "Jasp", "Kerl",
          "Morv", "Ostr", "Penn", "Rav", "Selb", "Tarv", "Varn", "Wend", "Yelv", "Brix"]
SUFFIX = ["vale", "rick", "mont", "dale", "stead", "wyn", "avel", "brook", "ridge", "mere",
          "holt", "crest", "gate", "worth", "combe", "hurst"]
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


# ---------------------------------------------------------------- calendar

def _nth_weekday(y, m, weekday, n):
    d = date(y, m, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def _last_weekday(y, m, weekday):
    d = date(y, m, calendar.monthrange(y, m)[1])
    return d - timedelta(days=(d.weekday() - weekday) % 7)


HOLIDAYS = set()
for _y in (YEAR - 1, YEAR, YEAR + 1):
    HOLIDAYS |= {date(_y, 1, 1), date(_y, 7, 4), date(_y, 12, 25), _last_weekday(_y, 5, 0),
                 _nth_weekday(_y, 9, 0, 1), _nth_weekday(_y, 11, 3, 4)}


def business_day(d):
    return d.weekday() < 5 and d not in HOLIDAYS


def next_business_day(d):
    while not business_day(d):
        d += timedelta(days=1)
    return d


def rand_business_day(rng, start, end):
    while True:
        d = start + timedelta(days=rng.randint(0, (end - start).days))
        if business_day(d):
            return d


def rand_date(rng, start, end):
    return start + timedelta(days=rng.randint(0, (end - start).days))


# ---------------------------------------------------------------- helpers

def family(model):
    return model.split("-")[1][:2]  # AC / HP / FG


def is_spring(model, d):
    return family(model) != "FG" and d.year == YEAR and d.month in SPRING


def amount_cents(model, d):
    m = ELIGIBLE[model]
    return 100 * (m["spring_usd"] if is_spring(model, d) else m["standard_usd"])


def n_for(tag, base):
    return round(RATE[tag] * base)


def place(rng, used):
    """An invented place-style name. Rejects machine-joined tells (review R2): a tripled letter,
    a doubled letter at the join, or a q without a u."""
    while True:
        pre, suf = rng.choice(PREFIX), rng.choice(SUFFIX)
        name = pre + suf
        low = name.lower()
        if (any(low[i] == low[i + 1] == low[i + 2] for i in range(len(low) - 2))
                or pre[-1].lower() == suf[0] or ("q" in low and "qu" not in low)):
            continue
        if name not in used:
            used.add(name)
            return name


def active_on(c, d):
    return c["enrollment_date"] <= d and (c["end_date"] == "" or d <= c["end_date"])


# ---------------------------------------------------------------- distributors / contractors

def make_distributors(rng):
    used = set()
    out = []
    eligible = list(ELIGIBLE)
    for i in range(N_DISTRIBUTORS):
        # Assortment: the three builder-grade units plus 3-6 eligible models (6-9 SKUs).
        carried = sorted(INELIGIBLE + rng.sample(eligible, rng.randint(3, 6)))
        new = rng.random() < 0.06   # joined in late 2024: no 2024 same-quarter baseline (review R3)
        out.append({
            "distributor_id": f"D{i + 1:03d}",
            "name": f"{place(rng, used)} {rng.choice(DISTRIBUTOR_KIND)}",
            "enrollment_date": (rand_date(rng, date(YEAR - 1, 10, 1), date(YEAR - 1, 12, 31)) if new
                                else rand_date(rng, date(2016, 1, 1), date(YEAR - 1, 9, 30))),
            "base": rng.lognormvariate(math.log(650_000 * BASE_VOLUME_SCALE), 0.75) * 100,   # cents per quarter
            "discount": rng.uniform(0.88, 0.97),
            "growth": rng.gauss(1.03, 0.08),
            "assortment": carried,
            "nonb1_share": rng.uniform(0.08, 0.18),
            "new_in_year": new,
        })
    return out


def make_contractors(rng, distributors):
    used = set()
    out = []
    weights = [d["base"] for d in distributors]
    for i in range(N_CONTRACTORS):
        if rng.random() < 0.08:      # enrolled during the program year
            enrolled = rand_date(rng, date(YEAR, 2, 1), date(YEAR, 9, 30))
        else:
            enrolled = rand_date(rng, date(2019, 1, 1), date(YEAR - 1, 12, 31))
        ended = ""
        if rng.random() < 0.045:     # terminated during the program year
            ended = rand_date(rng, max(enrolled + timedelta(days=60), date(YEAR, 4, 1)), date(YEAR, 11, 30))
        home = rng.choices(distributors, weights)[0]
        out.append({
            "contractor_id": f"C{i + 1:04d}",
            "name": f"{place(rng, used)} {rng.choice(CONTRACTOR_KIND)}",
            "enrollment_date": enrolled,
            "end_date": ended,
            "home": home,
            "home_distributor_id": home["distributor_id"],
            "size": rng.lognormvariate(0, 0.9),
        })
    return out


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


def pick_model(rng, month, carried):
    models = [m for m in MODEL_WEIGHTS if m in carried]
    w = [MODEL_WEIGHTS[m] * (2.0 if family(m) == "FG" and month in FURNACE_MONTHS else
                             0.3 if family(m) == "FG" else 1.0) for m in models]
    return rng.choices(models, w)[0]


def draw_install(rng, start, end):
    """A plausible install day: weekday-weighted, holidays rare."""
    while True:
        d = rand_date(rng, start, end)
        w = INSTALL_WEEKDAY[d.weekday()] * (0.1 if d in HOLIDAYS else 1.0)
        if rng.random() < w:
            return d


def pick_install(rng, c, model_family=None):
    while True:
        month = rng.choices(range(1, 13), MONTH_WEIGHTS)[0]
        d = draw_install(rng, date(YEAR, month, 1), date(YEAR, month, calendar.monthrange(YEAR, month)[1]))
        if active_on(c, d):
            return d


def spring_response(rng, model, d):
    """Cooling installs respond to the spring rate: some pulled into the window (F16)."""
    if family(model) == "FG" or d.year != YEAR:
        return d
    sm, em = SPRING.start, SPRING.stop - 1
    end = date(YEAR, em, calendar.monthrange(YEAR, em)[1])
    if d.month == em + 1 and d.day <= 7 and rng.random() < 0.25:
        return draw_install(rng, end - timedelta(days=6), end)
    if d.month not in SPRING and rng.random() < 0.06:
        return draw_install(rng, date(YEAR, sm, 1), end)
    return d


def clean_claim(rng, serials, c, model=None, install=None):
    """A claim that meets every rule. Documents trickle in, all inside the deadline."""
    while True:
        inst = install or pick_install(rng, c)
        m = model or pick_model(rng, inst.month, c["home"]["assortment"])
        if install is None:
            inst = spring_response(rng, m, inst)
            if not active_on(c, inst):
                continue
        lag = max(1, int(rng.lognormvariate(math.log(16), 0.6)))
        if lag > DEADLINE:
            continue
        received = next_business_day(inst + timedelta(days=lag))
        if (received - inst).days > DEADLINE:
            continue
        due = inst + timedelta(days=DEADLINE)
        inv = received
        if rng.random() < 0.15:
            inv = next_business_day(received + timedelta(days=rng.randint(1, 20)))
            if inv > due:          # re-draw, never clamp to the deadline (review R6)
                inv = received
        reg = inst + timedelta(days=int(rng.lognormvariate(math.log(3), 1.0)))
        if reg > due or inv > due:
            continue
        break
    serial = serials.new()
    return {
        "contractor_id": c["contractor_id"],
        "distributor_id": c["home_distributor_id"],
        "serial": serial, "invoice_serial": serial,
        "ordered_model": m, "invoice_model": m, "claim_model": m,
        "install_date": inst, "received_date": received,
        "invoice_doc_date": inv, "registration_doc_date": reg,
        "status": "paid", "denial_reason": "",
        "paid_cents": amount_cents(m, inst),
        "planted": [], "unit": True,
    }


def generate_claims(rng, contractors):
    serials = Serials(rng)
    weights = [c["size"] for c in contractors]
    by_id = {c["contractor_id"]: c for c in contractors}

    claims = [clean_claim(rng, serials, rng.choices(contractors, weights)[0]) for _ in range(N_SPIFF_BASE)]

    # Rule-consistent partial payments (A8): filed on time, registration inside the grace days,
    # invoice on time. Not defects.
    for cl in rng.sample(claims, round(0.0075 * N_SPIFF_BASE)):
        cl["registration_doc_date"] = cl["install_date"] + timedelta(days=DEADLINE + rng.randint(1, GRACE))
        cl["paid_cents"] = amount_cents(cl["claim_model"], cl["install_date"]) * PARTIAL_PCT // 100
        cl["rule_partial"] = True

    # Defects are seeded only on claims decided before the as-of date (C0).
    pool = [cl for cl in claims if not cl.get("rule_partial") and cl["received_date"] <= DECIDED_BY]
    rng.shuffle(pool)
    reserved = {}
    cursor = 0
    for cls in (3, 11, 18, 1, 2):
        k = n_for(SPIFF_TAGS[cls], N_SPIFF_BASE)
        reserved[cls] = pool[cursor:cursor + k]
        cursor += k
    over_pool = pool[cursor:]

    def draw(cls, exclude=(), where=lambda cl: True):
        cands = [cl for cl in over_pool if not (set(cl["planted"]) & set(exclude)) and where(cl)]
        return rng.sample(cands, n_for(SPIFF_TAGS[cls], N_SPIFF_BASE))

    # #5 install outside the program year. A late-December install filed in January, or a
    # January-2026 install filed into the closing program. Receipt always inside the program (F1).
    n5 = n_for(SPIFF_TAGS[5], N_SPIFF_BASE)
    cands5 = over_pool[:]
    rng.shuffle(cands5)
    for cl in cands5:
        if n5 == 0:
            break
        c = by_id[cl["contractor_id"]]
        if rng.random() < 0.6:
            inst = draw_install(rng, date(YEAR - 1, 12, 1), date(YEAR - 1, 12, 31))
            recv = rand_business_day(rng, date(YEAR, 1, 2), min(inst + timedelta(days=DEADLINE), date(YEAR, 2, 15)))
        else:
            inst = draw_install(rng, date(YEAR + 1, 1, 2), date(YEAR + 1, 1, 16))
            recv = next_business_day(inst + timedelta(days=rng.randint(3, 6)))
        if not active_on(c, inst) or (recv - inst).days > DEADLINE or recv > DECIDED_BY:
            continue
        reg = inst + timedelta(days=rng.randint(0, min(10, (recv - inst).days)))
        cl.update(install_date=inst, received_date=recv, invoice_doc_date=recv, registration_doc_date=reg,
                  paid_cents=amount_cents(cl["claim_model"], inst))
        cl["planted"].append(5)
        n5 -= 1
    assert n5 == 0

    # #6 filed after deadline, paid anyway
    # Late margin fits before the decided-by date, so Q4 installs can be late too (review R4).
    room = lambda cl: (DECIDED_BY - cl["install_date"]).days - DEADLINE - 4  # noqa: E731
    for cl in draw(6, where=lambda cl: room(cl) >= 1):
        cl["received_date"] = next_business_day(
            cl["install_date"] + timedelta(days=DEADLINE + rng.randint(1, min(40, room(cl)))))
        cl["invoice_doc_date"] = cl["received_date"]
        cl["planted"].append(6)

    # #4 rain-check substitute (F8, F9): an entry-level eligible model was ordered, the distributor
    # shipped the builder-grade unit, the contractor claimed the model ordered, and it was paid as ordered.
    entry = set(ENTRY_OF.values())
    for cl in draw(4, where=lambda cl: cl["ordered_model"] in entry):
        sub = BASE_OF[family(cl["ordered_model"])]
        cl["invoice_model"] = sub
        cl["planted"] += [4, 8]

    # #7 ineligible model installed as ordered and paid at the family's entry amount. About half
    # the claims name the entry model while the invoice shows the unit installed (F8).
    for cl in draw(7, exclude=(4,)):
        fam = family(cl["ordered_model"])
        bad = BASE_OF[fam]
        cl["ordered_model"] = cl["invoice_model"] = bad
        cl["paid_cents"] = amount_cents(ENTRY_OF[fam], cl["install_date"])
        if rng.random() < 0.5:
            cl["claim_model"] = ENTRY_OF[fam]
            cl["planted"] += [7, 8]
        else:
            cl["claim_model"] = bad
            cl["planted"].append(7)

    # #8 missing or mismatched documentation
    for cl in draw(8, exclude=(4, 7, 8)):
        v = rng.random()
        if v < 0.3:
            cl["registration_doc_date"] = ""
        elif v < 0.5:
            cl["invoice_doc_date"] = ""
            cl["invoice_model"] = cl["invoice_serial"] = ""
        elif v < 0.7 and 6 not in cl["planted"]:
            cl["registration_doc_date"] = cl["install_date"] + timedelta(days=DEADLINE + GRACE + rng.randint(1, 40))
        else:
            s = cl["serial"]
            cl["invoice_serial"] = s[:-2] + f"{(int(s[-2:]) + rng.randint(1, 98)) % 100:02d}"
        cl["planted"].append(8)

    # #10 ineligible contractor (F17): installs in the 30 days after termination or the 60 days
    # before enrollment, filed under that contractor.
    def inactive_fits(c, d):
        if c["end_date"] != "" and c["end_date"] < d <= c["end_date"] + timedelta(days=30):
            return True
        return c["enrollment_date"] - timedelta(days=60) <= d < c["enrollment_date"]

    lapsed = [c for c in contractors if c["enrollment_date"].year == YEAR or c["end_date"] != ""]
    n10 = n_for(SPIFF_TAGS[10], N_SPIFF_BASE)
    for cl in rng.sample(over_pool, len(over_pool)):
        if n10 == 0:
            break
        options = [c for c in lapsed if inactive_fits(c, cl["install_date"])
                   and cl["claim_model"] in c["home"]["assortment"]]
        if not options or cl["planted"]:
            continue
        c = rng.choice(options)
        cl["contractor_id"] = c["contractor_id"]
        cl["distributor_id"] = c["home_distributor_id"]
        cl["planted"].append(10)
        n10 -= 1
    assert n10 == 0

    # #9 wrong bonus amount (only on claims whose installed model is eligible and documented)
    for cl in draw(9, exclude=(4, 7), where=lambda cl: cl["invoice_model"] in ELIGIBLE):
        model, d = cl["claim_model"], cl["install_date"]
        right = amount_cents(model, d)
        m = ELIGIBLE[model]
        if family(model) != "FG" and m["spring_usd"] != m["standard_usd"] and d.year == YEAR:
            wrong = 100 * (m["standard_usd"] if is_spring(model, d) else m["spring_usd"])
        else:
            wrong = rng.choice([amount_cents(o, d) for o in ELIGIBLE if family(o) == family(model) and o != model])
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

    table_amounts = {100 * m[k] for m in ELIGIBLE.values() for k in ("standard_usd", "spring_usd")}
    for cl in reserved[18]:
        full = amount_cents(cl["claim_model"], cl["install_date"])
        bad = {full * PARTIAL_PCT // 100} | table_amounts
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
            recv = next_business_day(src["received_date"] + timedelta(days=rng.randint(1, 20)))
            if (recv - src["install_date"]).days > DEADLINE or recv > DECIDED_BY:
                recv = src["received_date"]
                src["received_date"] = recv - timedelta(days=1)
                while not business_day(src["received_date"]):
                    src["received_date"] -= timedelta(days=1)
                src["invoice_doc_date"] = min(src["invoice_doc_date"], src["received_date"]) \
                    if src["invoice_doc_date"] else src["invoice_doc_date"]
            dup = dict(src, planted=[cls], contractor_id=c["contractor_id"], unit=False,
                       received_date=recv, invoice_doc_date=recv)
            extra.append(dup)

    # #3 factory serial collision: a second physical unit with the same serial, denied as a duplicate
    collisions = []
    for src in reserved[3]:
        while True:
            c = rng.choice([x for x in contractors if x["home_distributor_id"] != src["distributor_id"]
                            and x["contractor_id"] != src["contractor_id"]])
            model2 = rng.choice([m for m in c["home"]["assortment"] if m in ELIGIBLE and m != src["claim_model"]])
            unit = clean_claim(rng, serials, c, model=model2, install=pick_install(rng, c))
            if src["received_date"] < unit["received_date"] <= DECIDED_BY:
                break
        unit["serial"] = unit["invoice_serial"] = src["serial"]
        unit.update(status="denied", denial_reason=DENIAL_TEXT["duplicate"], paid_cents=0, planted=[3])
        extra.append(unit)
        collisions += [(src["serial"], src["claim_model"], src["distributor_id"]),
                       (src["serial"], model2, unit["distributor_id"])]

    # Benign collisions: both units claimed and correctly paid (realism, not defects)
    for src in rng.sample([cl for cl in over_pool if not cl["planted"]], 3):
        while True:
            c = rng.choice([x for x in contractors if x["home_distributor_id"] != src["distributor_id"]])
            model2 = rng.choice([m for m in c["home"]["assortment"] if m in ELIGIBLE and m != src["claim_model"]])
            unit = clean_claim(rng, serials, c, model=model2)
            if src["received_date"] < unit["received_date"]:
                break
        unit["serial"] = unit["invoice_serial"] = src["serial"]
        extra.append(unit)
        collisions += [(src["serial"], src["claim_model"], src["distributor_id"]),
                       (src["serial"], model2, unit["distributor_id"])]

    # Correctly denied claims (not defects): invalid submissions the program rightly rejected
    n_reject = round(CORRECT_REJECT_SHARE * N_SPIFF_BASE)
    reasons = rng.choices(["ineligible_model", "contractor_inactive", "late", "missing_docs",
                           "out_of_window", "duplicate"], [48, 20, 12, 12, 3, 5], k=n_reject)
    paid_valid = [cl for cl in claims if not cl["planted"] and cl["status"] == "paid" and not cl.get("rule_partial")]
    for why in reasons:
        c = rng.choices(contractors, weights)[0]
        cl = clean_claim(rng, serials, c)
        if why == "ineligible_model":
            m = rng.choice([x for x in INELIGIBLE if x in c["home"]["assortment"]])
            cl["ordered_model"] = cl["invoice_model"] = cl["claim_model"] = m
        elif why == "contractor_inactive":
            while True:
                x = rng.choice(lapsed)
                if x["end_date"] != "" and rng.random() < 0.5:
                    d = draw_install(rng, x["end_date"] + timedelta(days=1), x["end_date"] + timedelta(days=30))
                else:
                    d = draw_install(rng, x["enrollment_date"] - timedelta(days=60), x["enrollment_date"] - timedelta(days=1))
                if d.year == YEAR and not active_on(x, d):
                    break
            cl = clean_claim(rng, serials, x, install=d)
        elif why == "late":
            cl["received_date"] = min(
                next_business_day(cl["install_date"] + timedelta(days=DEADLINE + rng.randint(1, 90))),
                next_business_day(max(cl["install_date"] + timedelta(days=DEADLINE + 1), AS_OF - timedelta(days=10))))
            cl["invoice_doc_date"] = cl["received_date"]
        elif why == "missing_docs":
            if rng.random() < 0.5:
                cl["registration_doc_date"] = ""
            else:
                cl["invoice_doc_date"] = cl["invoice_model"] = cl["invoice_serial"] = ""
        elif why == "out_of_window":
            inst = draw_install(rng, date(YEAR - 1, 11, 1), date(YEAR - 1, 12, 31))
            recv = rand_business_day(rng, date(YEAR, 1, 2), date(YEAR, 2, 28))
            cl.update(install_date=inst, received_date=recv, invoice_doc_date=recv,
                      registration_doc_date=inst + timedelta(days=rng.randint(0, 10)))
        elif why == "duplicate":
            src = rng.choice(paid_valid)
            for f in ("serial", "invoice_serial", "ordered_model", "invoice_model", "claim_model", "install_date",
                      "registration_doc_date", "distributor_id"):
                cl[f] = src[f]
            cl["received_date"] = cl["invoice_doc_date"] = next_business_day(
                src["received_date"] + timedelta(days=rng.randint(1, 30)))
            cl["unit"] = False
        cl["status"] = "denied"
        cl["paid_cents"] = 0
        # Real reject logs are dirty: about half carry no reason (Navigant 2013: 53% blank)
        cl["denial_reason"] = "" if rng.random() < 0.5 else DENIAL_TEXT[why]
        extra.append(cl)

    # Claims not yet received by the as-of date are not in the extract.
    for cl in claims + extra:
        if cl["received_date"] > AS_OF:
            assert not cl["planted"], cl["planted"]
    allc = [cl for cl in claims + extra if cl["received_date"] <= AS_OF]
    # Backlog (F6): claims received in the last processing window before the as-of date are
    # mostly still pending — not defects; the program has not decided them yet.
    for cl in allc:
        if cl["received_date"] > DECIDED_BY:
            assert not cl["planted"]
            age = (AS_OF - cl["received_date"]).days
            if rng.random() < 1 - age / PROCESSING:
                cl.update(status="pending", denial_reason="", paid_cents=0)
        assert cl["received_date"] <= AS_OF

    allc.sort(key=lambda cl: (cl["received_date"], cl["serial"], cl["contractor_id"], cl["claim_model"]))
    for i, cl in enumerate(allc):
        cl["claim_id"] = f"A{i + 1:06d}"
    return allc, sorted(set(collisions))


# ---------------------------------------------------------------- distributor volume rebate

def tier_for(volume):
    tier = 1
    for t in TIERS:
        if volume >= 100 * t["threshold_usd"]:
            tier = t["tier"]
    return tier


def rate_bp(tier):
    """Rate in millionths (1.75% -> 17500) to stay in integers."""
    return round(TIERS[tier - 1]["rate_pct"] * 10000)


def rebate_cents(volume, tier, method):
    """method: 'retroactive' (tier rate on all volume) or 'incremental' (graduated)."""
    if tier == 1:
        return 0
    if method == "retroactive":
        return volume * rate_bp(tier) // 1_000_000
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


def unit_price(d, sku, when):
    p = LIST_PRICE[sku] * d["discount"]
    if when >= PRICE_INCREASE_FROM:
        p *= 1.04
    return round(p)


def generate_volume(rng, distributors, claimed_units):
    lines, credits, baselines = [], [], []
    quarters = {}
    for d in distributors:
        did = d["distributor_id"]
        carried = d["assortment"]
        mix = {s: rng.uniform(0.5, 1.5) * (1.6 if s in INELIGIBLE else 1.0) for s in carried}
        total_mix = sum(mix.values())
        # Annual units per SKU from the distributor's size, never below what its contractors claimed
        annual = {}
        for s in carried:
            fam_avg = sum(QUARTER_FACTOR[family(s)].values()) / 4
            units = d["base"] * 4 * fam_avg * mix[s] / total_mix / LIST_PRICE[s]
            floor = math.ceil(claimed_units.get((did, s), 0) * rng.uniform(1.3, 2.5))
            annual[s] = max(round(units), floor)
        # Allocate each SKU's annual units to months exactly, by its family's seasonality.
        monthly = {}
        for s in carried:
            qf = QUARTER_FACTOR[family(s)]
            w = [qf[(m - 1) // 3 + 1] * rng.uniform(0.75, 1.25) for m in range(1, 13)]
            counts = [0] * 12
            for m in rng.choices(range(12), w, k=annual[s]):
                counts[m] += 1
            monthly[s] = counts
        for q in (1, 2, 3, 4):
            equip = 0
            nonb1 = 0
            for mi in range(3):
                month = 3 * (q - 1) + mi + 1
                last = calendar.monthrange(YEAR, month)[1]
                n_inv = rng.randint(3, 12)
                invoices = sorted(rand_business_day(rng, date(YEAR, month, 1), date(YEAR, month, last))
                                  for _ in range(n_inv))
                for s in carried:
                    units = monthly[s][month - 1]
                    # spread the month's units over a few of the month's invoices
                    while units > 0:
                        take = units if units <= 2 else rng.randint(1, max(1, units // 2))
                        when = rng.choice(invoices)
                        amt = take * unit_price(d, s, when)
                        lines.append([did, when, s, take, amt])
                        equip += amt
                        units -= take
                for when in invoices:
                    for s in rng.sample(NON_B1, rng.randint(1, 4)):
                        amt = round(d["base"] / 3 / n_inv * d["nonb1_share"] / 2.5 * rng.uniform(0.3, 1.7))
                        lines.append([did, when, s, 0, amt])
                        nonb1 += amt
            ret = 0
            if rng.random() < 0.7:
                for _ in range(rng.randint(1, 4)):
                    s = rng.choice(carried)
                    units = rng.randint(1, 3)
                    when = rand_business_day(rng, date(YEAR, 3 * (q - 1) + 1, 1),
                                             date(YEAR, 3 * q, calendar.monthrange(YEAR, 3 * q)[1]))
                    amt = units * unit_price(d, s, when)
                    if ret + amt > equip * 0.05:
                        break
                    credits.append([did, when, s, units, amt])
                    ret += amt
            qual = equip - ret
            baseline = None
            if not d["new_in_year"]:
                g = d["growth"] * rng.gauss(1.0, 0.04)
                baseline = round(qual / g)
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
        rebate = paid_rebate(s["volume_basis_cents"], s["tier_applied"], s["method_applied"])
        bl = s["baseline_used_cents"]
        return rebate, growth_cents(s["volume_basis_cents"], bl if bl != "" else None)

    def seed_basis(cls, field):
        cands = [k for k in keys if quarters[k][field] > 0 and cls not in stmts[k]["planted"]]
        rng.shuffle(cands)
        n, done = n_for(TIER_TAGS[cls], base), 0
        for k in cands:
            if done == n:
                break
            s = stmts[k]
            s2 = dict(s, volume_basis_cents=s["volume_basis_cents"] + quarters[k][field])
            s2["tier_applied"] = tier_for(s2["volume_basis_cents"])
            s2["method_applied"] = correct_method(s2["tier_applied"]) if s2["tier_applied"] > 1 else "none"
            if sum(recompute(s2)) != sum(recompute(s)):
                stmts[k] = dict(s2, planted=s["planted"] + [cls])
                done += 1
        assert done == n, cls

    seed_basis(16, "nonb1")
    seed_basis(14, "returns")
    basis_defect = lambda k: bool({14, 16} & set(stmts[k]["planted"]))  # noqa: E731  (F5: no stacking)

    # #17 prior quarter's lower tier carried forward
    true_tier = {k: tier_for(quarters[k]["qual"]) for k in keys}
    cands = [k for k in keys if k[1] > 1 and true_tier[(k[0], k[1] - 1)] < stmts[k]["tier_applied"]
             and not stmts[k]["planted"]]
    for k in rng.sample(cands, n_for(TIER_TAGS[17], base)):
        s = stmts[k]
        s["tier_applied"] = true_tier[(k[0], k[1] - 1)]
        s["method_applied"] = correct_method(s["tier_applied"]) if s["tier_applied"] > 1 else "none"
        s["planted"].append(17)

    # #12 wrong threshold comparison (F4): seeded on the statements whose volume sits closest
    # to a threshold, tier flipped across it. Closest-first rather than a fixed window, so a
    # small universe still has enough boundary cases.
    thresholds = [100 * t["threshold_usd"] for t in TIERS[1:]]
    n, done = n_for(TIER_TAGS[12], base), 0
    rel = lambda k: min(abs(stmts[k]["volume_basis_cents"] - th) / th for th in thresholds)  # noqa: E731
    cands = sorted((k for k in keys if not stmts[k]["planted"]), key=lambda k: (rel(k), k))
    for k in cands:
        if done == n:
            break
        s = stmts[k]
        vol = s["volume_basis_cents"]
        near = [min(range(len(thresholds)), key=lambda i: abs(vol - thresholds[i]) / thresholds[i])]
        th_tier = near[0] + 2                       # tier whose threshold this is
        t = th_tier - 1 if vol >= thresholds[near[0]] else th_tier
        prior = true_tier.get((k[0], k[1] - 1))
        if prior is not None and t == prior and t < s["tier_applied"]:
            continue
        trial = dict(s, tier_applied=t, method_applied=correct_method(t) if t > 1 else "none")
        if sum(recompute(trial)) == sum(recompute(s)):
            continue
        stmts[k] = dict(trial, planted=[12])
        done += 1
    assert done == n, done

    # #13 retroactive vs incremental misapplied
    n, done = n_for(TIER_TAGS[13], base), 0
    cands = [k for k in keys if stmts[k]["tier_applied"] in (2, 3, 4) and not basis_defect(k)]
    rng.shuffle(cands)
    for k in cands:
        if done == n:
            break
        s = stmts[k]
        trial = dict(s, method_applied="incremental" if s["tier_applied"] in (2, 3) else "retroactive")
        if sum(recompute(trial)) == sum(recompute(s)):
            continue
        stmts[k] = dict(trial, planted=s["planted"] + [13])
        done += 1
    assert done == n

    # #15 growth tested against the prior quarter instead of the 2024 same-quarter baseline
    n, done = n_for(TIER_TAGS[15], base), 0
    cands = [k for k in keys if quarters[k]["baseline"] is not None and k[1] > 1]
    rng.shuffle(cands)
    for k in cands:
        if done == n:
            break
        s = stmts[k]
        trial = dict(s, baseline_used_cents=quarters[(k[0], k[1] - 1)]["qual"])
        if recompute(trial)[1] != recompute(s)[1]:
            stmts[k] = dict(trial, planted=s["planted"] + [15])
            done += 1
    assert done == n

    out = []
    for k in keys:
        s = stmts[k]
        rebate, growth = recompute(s)
        s.update(rebate_paid_cents=rebate, growth_paid_cents=growth, total_paid_cents=rebate + growth)
        out.append(s)
    return out


# ---------------------------------------------------------------- writing

def fmt(v):
    return v.isoformat() if isinstance(v, date) else v


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

    claimed_units = {}
    for cl in claims:
        if cl["unit"] and cl["invoice_model"]:
            k = (cl["distributor_id"], cl["invoice_model"])
            claimed_units[k] = claimed_units.get(k, 0) + 1
    for d in distributors:   # a distributor ships what its contractors install
        for (did, s) in claimed_units:
            if did == d["distributor_id"] and s not in d["assortment"]:
                d["assortment"] = sorted(d["assortment"] + [s])

    lines, credits, baselines, quarters = generate_volume(rng, distributors, claimed_units)
    stmts = generate_statements(rng, distributors, quarters)

    write_csv("distributors.csv", ["distributor_id", "name", "enrollment_date"],
              [[d["distributor_id"], d["name"], d["enrollment_date"]] for d in distributors])
    write_csv("contractors.csv", ["contractor_id", "name", "enrollment_date", "end_date", "home_distributor_id"],
              [[c["contractor_id"], c["name"], c["enrollment_date"], c["end_date"], c["home_distributor_id"]]
               for c in contractors])
    claim_cols = ["claim_id", "contractor_id", "distributor_id", "serial", "invoice_serial", "ordered_model",
                  "invoice_model", "claim_model", "install_date", "received_date", "invoice_doc_date",
                  "registration_doc_date", "status", "denial_reason", "paid_cents"]
    write_csv("claims.csv", claim_cols, [[cl[c] for c in claim_cols] for cl in claims])
    write_csv("serial_collisions.csv", ["serial", "model", "distributor_id"], collisions)
    lines.sort(key=lambda l: (l[0], l[1], l[2], l[3], l[4]))
    write_csv("purchase_lines.csv", ["distributor_id", "invoice_date", "sku", "units", "amount_cents"], lines)
    credits.sort(key=lambda l: (l[0], l[1], l[2]))
    write_csv("return_credits.csv", ["distributor_id", "credit_date", "sku", "units", "amount_cents"], credits)
    write_csv("baselines_2024.csv", ["distributor_id", "quarter", "qualifying_volume_cents"], baselines)
    stmt_cols = ["distributor_id", "quarter", "volume_basis_cents", "tier_applied", "method_applied",
                 "baseline_used_cents", "rebate_paid_cents", "growth_paid_cents", "total_paid_cents"]
    write_csv("rebate_statements.csv", stmt_cols, [[s[c] for c in stmt_cols] for s in stmts])

    planted = [["claim", cl["claim_id"], ";".join(str(x) for x in sorted(set(cl["planted"])))]
               for cl in claims if cl["planted"]]
    planted += [["statement", f"{s['distributor_id']}-Q{s['quarter']}", ";".join(str(x) for x in sorted(s["planted"]))]
                for s in stmts if s["planted"]]
    write_csv("planted.csv", ["record_type", "record_id", "classes"], planted)
    print(f"claims {len(claims)}  statements {len(stmts)}  planted records {len(planted)}")


if __name__ == "__main__":
    main()
