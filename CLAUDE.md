# rebate-payout-validator (Payout Math)

Static demo, live at https://payoutmath.lailarallc.com. It validates an invented HVAC manufacturer's
(Galewick) program-year incentive payouts against its own published rulebook. Install bonuses and
distributor rebates are reported as gross overpaid and gross underpaid, never netted. State files:
PLAN.md, HANDOFF.md, DECISIONS.md. Realism record: docs/realism-review.md.

## Pipeline (run in order; all Python is stdlib, run with `-I`)

roll_parameters → render_rules → generate_universe → validate → bound_check → build_site_data →
build_readme. Then `npm --prefix web run build`. Tests: `python -I -m unittest discover -s tests`.

Commit every regenerated artifact. CI re-runs the pipeline and refuses to deploy if anything differs
or is left uncommitted.

## Never hand-edit (generated)

`rules/parameters.json`, `rules/galewick-program-rules.md`, `data/*.csv`, `build/*.json`,
`web/src/lib/data/*`, `web/static/data/*`, `web/static/rules/*.md`, and the generated blocks in
`README.md`. Edit the script or the template, then re-run.

## Integrity rules (from DECISIONS; do not relitigate)

- Pinned defect rates (C 2.0 / O 0.75 / R 0.2) and the tier rates never move. Universe size moves
  only on an owner realism call, after a dry-run projection, with a single regeneration.
- Bounds are disclosed, never tuned. A definition fix is recorded as one, with the population it
  changes.
- The validator never reads `data/planted.csv`. A behavioural test enforces this.
- Exact recovery of planted defects is necessary but not sufficient. The rule arithmetic is pinned
  by hand-computed golden values (`RuleArithmetic`). Re-derive them from the rendered rulebook if a
  parameter ever changes.
- Change data surgically. To fix one generated surface, draw from a side seeded stream and keep the
  main stream's consumption identical (see `_burn_legacy_return_draws`, `SCREENED_OUT`). Then confirm
  the rebuild is otherwise byte-identical.
- Every README number sits inside a generated block. Prose outside the blocks carries no digits
  (tested).
- Names are owner-class. Screen new names against real businesses (`docs/name-screen.md`).
