# HANDOFF — rebate-payout-validator (Payout Math)

**Phase:** copy freeze. The project is waiting on Max's audit before any deploy work starts.

## Where it stands (2026-10-16)

- **Rulebook v1.1** (`rules/`). Every parameter is a seeded draw from a stated range (distance by construction, see DECISIONS).
- **Universe:** `scripts/generate_universe.py` produces one program year of Galewick data: 13,461 claims and 640 distributor-quarters. Generation is seed-locked and byte-stable.
- **Validator:** `scripts/validate.py` reads only system data and recovers all 1,378 planted defects exactly.
- **Bound check:** the claim-share bound passes at 11.2%. The overpaid-dollar bound fails at 2.3% against 10–15%; that is disclosed and was not re-tuned.
- **Realism review:** an independent session wrote `docs/realism-review.md`. The first pass was FAIL with 17 findings, all fixed. The re-review was PASS WITH FINDINGS (R1–R7), all addressed.
- **Web:** `web/` (SvelteKit static, frame v1.5.1) has three views: verdict, claims and program, plus a method section and the `/rules` page. It was checked at 1440px and 375px.
- **Tests:** `python -I -m unittest discover -s tests` runs 12 tests, all passing.

## Pipeline

```
python -I scripts/roll_parameters.py
python -I scripts/render_rules.py
python -I scripts/generate_universe.py
python -I scripts/validate.py
python -I scripts/bound_check.py
python -I scripts/build_site_data.py
npm --prefix web run build
```

## Next

1. Max audits the copy (`docs/copy-freeze.md`, judgment calls J1–J8).
2. Apply the audit edits.
3. Work the pre-deploy checklist in `docs/copy-freeze.md`.
