"""Pipeline tests. Run: python -m unittest discover -s tests

Intent, not letter: the validator must recover exactly the defects the generator planted,
reading only what Galewick's systems hold; and the whole pipeline must be byte-stable.
"""

import csv
import re
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ["roll_parameters.py", "render_rules.py", "generate_universe.py", "validate.py", "bound_check.py",
           "build_site_data.py", "build_readme.py"]
ARTIFACTS = sorted([*ROOT.glob("data/*.csv"), ROOT / "rules" / "parameters.json",
                    ROOT / "rules" / "galewick-program-rules.md", ROOT / "build" / "results.json",
                    ROOT / "build" / "bound_check.json", ROOT / "web" / "src" / "lib" / "data" / "summary.json",
                    ROOT / "web" / "src" / "lib" / "data" / "rules.html", ROOT / "web" / "static" / "data" / "flagged.json",
                    ROOT / "README.md"])


def run_script(s):
    r = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / s)], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        raise AssertionError(f"{s} failed:\n{r.stdout}\n{r.stderr}")


def run_pipeline():
    for s in SCRIPTS:
        run_script(s)


def digest():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in ARTIFACTS}


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_pipeline()
        cls.first = digest()
        run_pipeline()
        cls.second = digest()
        cls.results = json.loads((ROOT / "build" / "results.json").read_text(encoding="utf-8"))

    def test_byte_identical_rebuild(self):
        self.assertEqual(self.first, self.second)

    def test_validator_never_reads_planted_truth(self):
        """Behavioural: with the planted truth file absent, the validator's output is byte-identical."""
        planted = ROOT / "data" / "planted.csv"
        hidden = ROOT / "data" / "planted.csv.hidden"
        results = ROOT / "build" / "results.json"
        before = results.read_bytes()
        planted.rename(hidden)
        try:
            run_script("validate.py")
            after = results.read_bytes()
        finally:
            hidden.rename(planted)
            run_script("validate.py")
        self.assertEqual(before, after)

    def test_validator_recovers_every_planted_defect_exactly(self):
        got = {f["record_id"]: ";".join(map(str, f["classes"])) for f in self.results["flagged"]}
        with open(ROOT / "data" / "planted.csv", encoding="utf-8", newline="") as f:
            want = {r["record_id"]: r["classes"] for r in csv.DictReader(f)}
        self.assertEqual(got, want)

    def test_every_class_is_planted(self):
        present = {c["class"] for c in self.results["classes"] if c["present_count"] > 0}
        self.assertEqual(present, set(range(1, 19)))

    def test_primary_dollars_sum_to_verdict(self):
        v, cls = self.results["verdict"], self.results["classes"]
        self.assertEqual(sum(c["over_cents"] for c in cls), v["over_cents"])
        self.assertEqual(sum(c["under_cents"] for c in cls), v["under_cents"])
        self.assertEqual(sum(f["delta_cents"] for f in self.results["flagged"] if f["delta_cents"] > 0),
                         v["over_cents"])

    def test_over_and_under_are_never_netted(self):
        v = self.results["verdict"]
        self.assertGreater(v["over_cents"], 0)
        self.assertGreater(v["under_cents"], 0)
        self.assertNotIn("net_cents", v)

    def test_no_floats_in_results(self):
        def walk(x):
            if isinstance(x, float):
                raise AssertionError(f"float in results: {x}")
            if isinstance(x, dict):
                for y in x.values():
                    walk(y)
            if isinstance(x, list):
                for y in x:
                    walk(y)
        walk(self.results)

    def test_primary_class_direction_matches_rulebook(self):
        over_only = {1, 2, 4, 5, 6, 7, 8, 10, 14, 16}
        under_only = {3, 11, 17}
        for f in self.results["flagged"]:
            if f["primary"] in over_only:
                self.assertGreater(f["delta_cents"], 0, f["record_id"])
            if f["primary"] in under_only:
                self.assertLess(f["delta_cents"], 0, f["record_id"])

    def test_distributor_sell_in_covers_contractor_claims(self):
        bought = {}
        with open(ROOT / "data" / "purchase_lines.csv", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                k = (r["distributor_id"], r["sku"])
                bought[k] = bought.get(k, 0) + int(r["units"])
        claimed = {}
        with open(ROOT / "data" / "claims.csv", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["invoice_model"]:
                    k = (r["distributor_id"], r["invoice_model"])
                    claimed[k] = claimed.get(k, 0) + 1
        over = {k: (v, bought.get(k, 0)) for k, v in claimed.items() if v > bought.get(k, 0)}
        self.assertEqual(over, {})

    def test_no_claim_received_outside_program_operation(self):
        with open(ROOT / "data" / "claims.csv", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertTrue(all("2025-01-01" < r["received_date"] <= self.results["universe"]["as_of"] for r in rows))

    def test_site_data_matches_validator(self):
        s = json.loads((ROOT / "web" / "src" / "lib" / "data" / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(s["verdict"], self.results["verdict"])
        flagged = json.loads((ROOT / "web" / "static" / "data" / "flagged.json").read_text(encoding="utf-8"))
        self.assertEqual(len(flagged), self.results["verdict"]["flagged_records"])
        self.assertEqual(sum(f["d"] for f in flagged if f["d"] > 0), self.results["verdict"]["over_cents"])

    def test_readme_has_no_hand_entered_numbers(self):
        """Every digit in README.md sits inside a generated block (scripts/build_readme.py)."""
        import re
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        blocks = re.findall(r"<!-- generated:(\w+):begin -->", text)
        self.assertEqual(sorted(blocks), ["findings", "stack"])
        outside = re.sub(r"<!-- generated:(\w+):begin -->.*?<!-- generated:\1:end -->", "", text, flags=re.S)
        self.assertEqual(re.findall(r"\d", outside), [])

    def test_readme_verdict_matches_results(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        v = self.results["verdict"]
        for cents in (v["over_cents"], v["under_cents"], v["approved_cents"]):
            amount = re.escape(f"${round(cents / 100):,}")
            self.assertRegex(text, rf"(?<![\d,]){amount}(?![\d,])")

    def test_rulebook_has_no_unrendered_placeholder(self):
        self.assertNotIn("{{", (ROOT / "rules" / "galewick-program-rules.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()


class RuleArithmetic(unittest.TestCase):
    """Golden values computed by hand from rulebook v1.1 (rules/galewick-program-rules.md), not from code.

    The validator borrows its rule arithmetic from the generator, so exact recovery of planted defects
    cannot catch a bug in that shared arithmetic. These values are the independent oracle. If a re-roll
    changes a rulebook parameter, re-derive them from the rendered rulebook.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "scripts"))
        import generate_universe as g
        cls.g = g

    def test_rulebook_parameters_are_the_ones_these_values_assume(self):
        tiers = [(t["threshold_usd"], t["rate_pct"]) for t in self.g.TIERS]
        self.assertEqual(tiers, [(0, 0.0), (50700, 1.75), (163800, 3.25), (327600, 5.25)])
        self.assertEqual((self.g.PARAMS["growth_threshold_pct"], self.g.PARAMS["growth_bonus_pct"]), (113, 0.75))

    def test_b4_1_threshold_is_equal_to_or_greater_than(self):
        self.assertEqual(self.g.tier_for(5_069_999), 1)
        self.assertEqual(self.g.tier_for(5_070_000), 2)    # exactly $50,700 reaches Tier 2
        self.assertEqual(self.g.tier_for(16_380_000), 3)
        self.assertEqual(self.g.tier_for(32_760_000), 4)

    def test_b4_tier_rebates(self):
        self.assertEqual(self.g.correct_rebate(5_070_000, 2), 88_725)        # $50,700 x 1.75% = $887.25
        self.assertEqual(self.g.correct_rebate(16_380_000, 3), 532_350)      # $163,800 x 3.25% = $5,323.50
        # Tier 4: 3.25% on the first $327,600 ($10,647.00) + 5.25% on $72,400 above it ($3,801.00)
        self.assertEqual(self.g.correct_rebate(40_000_000, 4), 1_444_800)

    def test_b5_growth_bonus_at_exactly_the_threshold(self):
        self.assertEqual(self.g.growth_cents(11_300_000, 10_000_000), 84_750)   # 113% earns 0.75% = $847.50
        self.assertEqual(self.g.growth_cents(11_299_999, 10_000_000), 0)
        self.assertEqual(self.g.growth_cents(11_300_000, None), 0)               # no baseline, no bonus

    def test_a2_2_spring_rate_is_cooling_only_and_ends_april_30(self):
        from datetime import date
        self.assertEqual(self.g.amount_cents("GW-AC17", date(2025, 4, 30)), 18_000)
        self.assertEqual(self.g.amount_cents("GW-AC17", date(2025, 5, 1)), 12_000)
        self.assertEqual(self.g.amount_cents("GW-FG96", date(2025, 3, 15)), 9_000)   # furnaces: no spring rate

    def test_a8_partial_is_a_quarter_of_the_bonus(self):
        self.assertEqual(self.g.PARTIAL_PCT, 25)
        self.assertEqual(self.g.amount_cents("GW-AC17", date_(2025, 6, 2)) * self.g.PARTIAL_PCT // 100, 3_000)


def date_(y, m, d):
    from datetime import date
    return date(y, m, d)
