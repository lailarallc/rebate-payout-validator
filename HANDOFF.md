# HANDOFF — rebate-payout-validator (Payout Math)

**Phase:** LIVE. **Max's audit signed off 2026-10-27:** the arithmetic is exact, the bounds are disclosed honestly, and his three audit fixes (68d2275: three-lane footer, engagement section, per-page canonicals) are verified live. Pre-flip items are in progress. The public flip remains the owner's word.

**Live:** https://payoutmath.lailarallc.com (also https://payoutmath.pages.dev)

## Where it stands (2026-10-22, ccdcea3)

- **Universe** (owner-approved channel; DECISIONS):
  - 42 contractors, a 1,100-claim rate base, and 20 distributors × 4 quarters.
  - Tier thresholds are T2 $50,700 / T3 $163,800 / T4 $327,600. The rates are unchanged original draws.
  - **Payout $521,804**: $401,971 of rebates plus $119,833 of install bonuses.
  - Sell-in is $13.99M, and the effective rebate rate is 2.87%.
  - 0 distributors earn $0, and the largest distributor is 10.5% of sell-in.
- **Validator:** recovers all 129 planted defects exactly. All 18 classes exist; 9 are ranked on the page and 9 are grouped as "Other", by program. `python -I -m unittest discover -s tests` passes all 12 tests.
- **Bounds:** the claim-share bound passes (11.0%). The overpaid-dollar bound fails (3.4% against 10–15%); that is disclosed and was not re-tuned.
- **Realism reviews** (`docs/realism-review.md`): five passes. The fourth and fifth were PASS WITH FINDINGS; every finding is fixed or recorded as accepted (U6 and V2 accepted, V4 noted).
- **Deploy:** live at https://payoutmath.lailarallc.com, with all four CI jobs green. The OG card is live.

## Open

1. ~~Max audits the live site~~: **signed off 2026-10-27.**
2. **Pre-flip items, done 2026-10-27:**
   - Name screen: CLEAR WITH NEAR-MISSES (`docs/name-screen.md`). Galewick is clear. **Owner call:** keep or rename "Pennridge HVAC" (MED: real place name, and an unrelated USPTO mark exists). Brenwyn is a LOW near-miss.
   - Real README: done. Numbers are artifact-fed, enforced by tests and CI.
   - Pre-ship: READY. A fresh clone runs the full pipeline with zero diff, all 14 tests pass, `npm ci` and the build succeed, no secrets appear in tracked files or history, and `.gitignore` covers secrets.
3. **Public flip:** the owner's word.

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

Commit the regenerated artifacts. CI refuses to deploy if they are stale.
