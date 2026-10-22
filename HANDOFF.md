# HANDOFF — rebate-payout-validator (Payout Math)

**Phase:** LIVE, waiting on Max's audit of the live site. The repo stays private until that audit passes.

**Live:** https://payoutmath.lailarallc.com (also https://payoutmath.pages.dev)

## Where it stands (2026-10-22)

- **Universe:** resized by the owner (DECISIONS 2026-10-22).
  - 95 contractors, a 2,500-claim rate base, and 60 distributors × 4 quarters.
  - The tier-threshold range is scaled ×0.15 and base volume ×0.05.
  - The program-year payout is **$835,060**, inside the owner's $500K–$1M band. Sell-in is about $22.5M.
- **Rates:** all pinned rates are unchanged, and all 18 classes are present.
- **Validator:** recovers all 303 planted defects exactly. `python -I -m unittest discover -s tests` passes all 12 tests.
- **Bounds:** the claim-share bound passes (11.3%). The overpaid-dollar bound fails (3.5% against 10–15%); that is disclosed and was not re-tuned.
- **Realism reviews** (`docs/realism-review.md`):
  - First pass: FAIL, 17 findings, all fixed.
  - Second pass: PASS WITH FINDINGS, R1–R7 all fixed.
  - Third pass, after the resize: PASS WITH FINDINGS. T3, T4 and T5 are fixed.
- **Deploy:** `.github/workflows/deploy.yml` runs four jobs, with all actions SHA-pinned:
  - verify: the stdlib tests plus a check that committed artifacts are current;
  - build: `web/`;
  - deploy: the org `pages-deploy@v1`, project `payoutmath`;
  - domain: an idempotent attach plus the CNAME.
- **OG card:** `lailarallc.com/og/s/payoutmath.png` is live, from `lailara-website@f8890da`.

## Open

1. **Max audits the live site.** The judgment calls are J1–J8 in `docs/copy-freeze.md`.
2. **T1 and T2 need the owner's call** (third review):
   - sell-in tracks claims at r = 0.97;
   - micro-distributors that buy a unit a quarter.

   Both fixes raise sell-in, so they risk the $1M cap.
3. **Before the public flip:**
   - a name and trademark screen;
   - the real README from the template;
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
