# HANDOFF — rebate-payout-validator (Payout Math)

**Phase:** LIVE, waiting on Max's audit of the live site. The repo stays private until that audit passes.

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

1. **Max audits the live site.** The judgment calls are J1–J8 in `docs/copy-freeze.md`. (V4 from the fifth review is moot after the V1 fix: overpaid, $17,597, again exceeds underpaid, $7,336.)
2. **Before the public flip:**
   - a name and trademark screen ("Galewick" and the generated member names);
   - the real README;
   - pre-ship checks.

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
