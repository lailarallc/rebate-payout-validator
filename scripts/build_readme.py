"""Write the figures into README.md from the build artifacts.

README.md holds two generated blocks, `findings` and `stack`, between
<!-- generated:NAME:begin --> and <!-- generated:NAME:end --> markers. This script replaces their
contents. Every number in the README lives inside a generated block. The prose outside them carries
no digits at all, and tests/test_pipeline.py enforces both rules.

Inputs: build/results.json, build/bound_check.json, web/src/lib/data/summary.json,
        data/planted.csv, data/purchase_lines.csv, data/contractors.csv, data/distributors.csv,
        rules/parameters.json, web/package.json, web/static/lailara/lailara-frame.css
"""

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from render_rules import VERSION as RULES_VERSION  # noqa: E402


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def rows(rel):
    with open(ROOT / rel, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def usd(cents):
    return f"${round(cents / 100):,}"


def findings():
    r, b, s, p = load("build/results.json"), load("build/bound_check.json"), load("web/src/lib/data/summary.json"), load("rules/parameters.json")
    v, u, fam = r["verdict"], r["universe"], r["families"]
    planted = len(rows("data/planted.csv"))
    sellin = sum(int(x["amount_cents"]) for x in rows("data/purchase_lines.csv") if x["sku"].startswith("GW-"))
    shown = sum(1 for c in s["classes"] if c["shown"])
    bounds = {x["id"]: x for x in b["bounds"]}
    cs, ds = bounds["spiff_claim_share"], bounds["overpaid_dollar_share"]
    t = p["tiers"]
    return "\n".join([
        f"- **{usd(v['over_cents'])} of {usd(v['approved_cents'])} approved for payout should never have been approved. "
        f"{usd(v['under_cents'])} earned under the program's own rules was never paid.** The two are reported "
        "separately and never netted.",
        f"- Galewick paid {u['paid_claims']:,} contractor install bonuses (from {u['claims']:,} claims) and issued "
        f"{u['statements']} quarterly distributor rebate statements: {usd(fam['spiff']['paid_cents'])} in bonuses and "
        f"{usd(fam['tier']['paid_cents'])} in rebates.",
        f"- {v['flagged_records']} payout decisions break a rule: {fam['spiff']['flagged_records']} claims and "
        f"{fam['tier']['flagged_records']} rebate statements. {v['multi_defect_records']} break more than one.",
        f"- The validator recovers all {planted} planted defects and flags nothing else. All "
        f"{len(r['classes'])} defect classes are present; {shown} have enough cases to be ranked on the page, "
        "and the rest are grouped by program.",
        f"- The channel: {len(rows('data/contractors.csv'))} contractors, {len(rows('data/distributors.csv'))} "
        f"distributors, {usd(sellin)} of equipment sell-in. Rulebook v{RULES_VERSION}, with tiers at "
        f"{usd(100 * t[1]['threshold_usd'])} / {usd(100 * t[2]['threshold_usd'])} / {usd(100 * t[3]['threshold_usd'])} a quarter.",
        f"- Defect share of paid install-bonus claims: {cs['measured_bp'] / 100:.1f}%, inside the "
        f"{cs['low_bp'] // 100}–{cs['high_bp'] // 100}% a rebate-audit vendor reports. Overpaid dollars as a share of "
        f"approved: {ds['measured_bp'] / 100:.1f}%, outside the {ds['low_bp'] // 100}–{ds['high_bp'] // 100}% of a "
        "2013 vendor press release. The gap is disclosed; error rates were not tuned to close it.",
    ])


def stack():
    pkg = load("web/package.json")["devDependencies"]
    frame = re.search(r"lailara-frame\.css — v([\d.]+)", (ROOT / "web/static/lailara/lailara-frame.css").read_text(encoding="utf-8")).group(1)
    wf = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
    py = re.search(r'python-version: "([\d.]+)"', wf).group(1)
    reusable = re.search(r"uses: (lailarallc/reusable-workflows/\S+)", wf).group(1)
    return "\n".join([
        f"- Python {py}, standard library only: generator, validator, bound check, site data, tests.",
        f"- SvelteKit static site: `@sveltejs/kit` {pkg['@sveltejs/kit']}, `svelte` {pkg['svelte']}, "
        f"`@sveltejs/adapter-static` {pkg['@sveltejs/adapter-static']}, `vite` {pkg['vite']}.",
        f"- Lailara frame v{frame}, vendored in `web/static/lailara/`.",
        f"- Cloudflare Pages, deployed by `{reusable}` after a CI job re-runs the pipeline and refuses stale artifacts.",
    ])


def main():
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    for name, body in (("findings", findings()), ("stack", stack())):
        pat = re.compile(rf"(<!-- generated:{name}:begin -->\n)(?:.*?\n)?(<!-- generated:{name}:end -->)", re.S)
        if not pat.search(text):
            raise SystemExit(f"README.md is missing the generated:{name} block")
        text = pat.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("README.md generated blocks written")


if __name__ == "__main__":
    main()
