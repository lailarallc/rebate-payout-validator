# Payout Math

**Live:** https://payoutmath.lailarallc.com

Incentive programs pay against rules, and almost nobody re-derives the payouts from those rules.
Payout Math re-derives every contractor install bonus and every distributor volume rebate in one
program year from the program's own published rulebook. It reports what was paid but never earned
and what was earned but never paid, at the same size, never netted.

## What it finds

<!-- Every number in this README sits inside a generated block written by scripts/build_readme.py
     from the build artifacts. No number is hand-entered; prose outside the blocks has no digits,
     and tests/test_pipeline.py enforces both. -->
<!-- generated:findings:begin -->
- **$17,597 of $521,804 approved for payout should never have been approved. $7,336 earned under the program's own rules was never paid.** The two are reported separately and never netted.
- Galewick paid 1,084 contractor install bonuses (from 1,235 claims) and issued 80 quarterly distributor rebate statements: $119,833 in bonuses and $401,971 in rebates.
- 129 payout decisions break a rule: 119 claims and 10 rebate statements. 16 break more than one.
- The validator recovers all 129 planted defects and flags nothing else. All 18 defect classes are present; 9 have enough cases to be ranked on the page, and the rest are grouped by program.
- The channel: 42 contractors, 20 distributors, $13,990,157 of equipment sell-in. Rulebook v1.1, with tiers at $50,700 / $163,800 / $327,600 a quarter.
- Defect share of paid install-bonus claims: 8.8%, inside the 6–15% a rebate-audit vendor reports. Overpaid dollars as a share of approved: 3.4%, outside the 10–15% of a 2013 vendor press release. The gap is disclosed; error rates were not tuned to close it.
<!-- generated:findings:end -->

Galewick Climate Systems is an invented HVAC manufacturer. Its contractors, distributors, claims,
statements, and rulebook are synthetic and seed-locked; the method is real. Every rule value is a
seeded draw from a range with a stated basis, and every flag on the page names the rule it breaks
and can be checked by hand against the [published rules](https://payoutmath.lailarallc.com/rules).

## How it works

- `scripts/roll_parameters.py` and `scripts/render_rules.py` draw the program parameters and render
  the rulebook.
- `scripts/generate_universe.py` builds the program year and plants defects at pinned rates.
- `scripts/validate.py` reads only what the program's systems would hold, plus the rules, and
  computes earned against paid for every claim and statement. It never reads the planted truth.
- `scripts/bound_check.py` compares the result with published ranges and reports pass or fail.
  It never adjusts anything.
- `scripts/build_site_data.py` and `web/` publish the verdict, the claims, and the program view.

Design decisions, realism reviews, and anchors: [DECISIONS.md](DECISIONS.md),
[docs/realism-review.md](docs/realism-review.md), [docs/anchors-research.md](docs/anchors-research.md).

## Machine-readable outputs

The live site serves its data as files, so the page is not the only way in:

- `/data/flagged.json`: every payout decision that breaks a rule. The keys are `id` (claim or
  statement), `t` (`c` claim, `s` statement), `m` and `n` (member id and name), `p` (paid cents),
  `e` (earned cents), `d` (difference in cents, positive when overpaid), `k` (every defect class
  broken), `pk` (the primary class), `ev` (evidence for each class in `k`, in order).
- `/rules/galewick-program-rules.md`: the published rulebook as plain text.
- In the repo: `build/results.json` (verdict, classes, every flagged record with full evidence),
  `build/bound_check.json`, and the program's system data in `data/`. The planted defects
  (`data/planted.csv`) exist for the tests; the validator never reads them.

## Stack

<!-- generated:stack:begin -->
- Python 3.13, standard library only: generator, validator, bound check, site data, tests.
- SvelteKit static site: `@sveltejs/kit` ^2.70.3, `svelte` ^5.56.10, `@sveltejs/adapter-static` ^3.0.10, `@sveltejs/vite-plugin-svelte` ^7.3.0, `vite` ^8.2.2.
- Lailara frame v1.5.1, vendored in `web/static/lailara/`.
- Cloudflare Pages, deployed by `lailarallc/reusable-workflows/.github/workflows/pages-deploy.yml@v1` after a CI job re-runs the pipeline and refuses stale artifacts.
<!-- generated:stack:end -->

## Run

```
python -I scripts/roll_parameters.py
python -I scripts/render_rules.py
python -I scripts/generate_universe.py
python -I scripts/validate.py
python -I scripts/bound_check.py
python -I scripts/build_site_data.py
python -I scripts/build_readme.py
python -I -m unittest discover -s tests
npm --prefix web ci
npm --prefix web run build
```

---

Built by [Lailara LLC](https://lailarallc.com) — data hygiene and analytics consulting for specialty
food brands scaling into national retail.
