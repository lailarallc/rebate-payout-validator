"""Pipeline tests. Run: python -m unittest discover -s tests

Intent, not letter: the validator must recover exactly the defects the generator planted,
reading only what Galewick's systems hold; and the whole pipeline must be byte-stable.
"""

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ["roll_parameters.py", "render_rules.py", "generate_universe.py", "validate.py", "bound_check.py"]
ARTIFACTS = sorted([*ROOT.glob("data/*.csv"), ROOT / "rules" / "parameters.json",
                    ROOT / "rules" / "galewick-program-rules.md", ROOT / "build" / "results.json",
                    ROOT / "build" / "bound_check.json"])


def run_pipeline():
    for s in SCRIPTS:
        subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / s)], check=True,
                       capture_output=True, cwd=ROOT)


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
        src = (ROOT / "scripts" / "validate.py").read_text(encoding="utf-8")
        self.assertNotIn("planted.csv\")", src.replace("never data/planted.csv", ""))
        self.assertNotIn("read(\"planted", src)

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

    def test_rulebook_has_no_unrendered_placeholder(self):
        self.assertNotIn("{{", (ROOT / "rules" / "galewick-program-rules.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
