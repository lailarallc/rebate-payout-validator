# PLAN — rebate-payout-validator (Payout Math)

Tier: Heavy.

## Goal

_Confirmed by owner 2026-10-15 via /clarify. Full record: [docs/clarify-log.md](docs/clarify-log.md); anchors: [docs/anchors-research.md](docs/anchors-research.md)._

- **What:** Payout Math (payoutmath.lailarallc.com) audits one program year of an invented HVAC manufacturer's incentive payouts against its own published rules. It is the flagship receipt for Lailara's rebate & incentive lane. Repo name stays `rebate-payout-validator`.
- **Verdict:** leads with overpaid — "$X of $Y approved for payout should never have been approved." Gross underpaid is the second number on the page: full size, same grain, never netted, not a co-headline.
- **Universe:** Galewick / Galewick Climate Systems (invented; trademark check before launch). Manufacturer → distributors → installing contractors. Two families: contractor SPIFF (42 contractors, 1,100-claim rate base) and tiered volume rebate (20 distributors × 4 quarters = 80 member-periods). Program-year payout is $500K–$1M (owner-sourced resize, 2026-10-22, DECISIONS). Seasonal. No element may mirror any real program operator or client the owner has worked with.
- **Defects:** 18 classes. Existence = PRACTITIONER anchor (owner's judgment). Rates: C 2.0% / O 0.75% / R 0.2%, applied uniformly; vendor aggregate leakage is a sanity bound only. Owner calls (P) and Claude's accepted guesses (A) labeled separately. Rejection-rate caveat recorded.
- **Validator rules:** multi-defect claims expected; one primary class per claim by fixed precedence eligibility → evidence → math (stated on page); per class "primary on M / present on N" (N informational); multi-defect count at full size; rule-based partial payments pass, ad-hoc partials are class #18; any displayed class under 5 groups into "other."
- **Out:** Cinderhaven entanglement, net-only verdict, tuning rates for drama, servers (static precompute).
- **Done:** criteria pinned → universe generated → dollar bound checked (no re-tuning) → **owner eyeballs 20 sampled claims (hard stop)** → three views (verdict, claims, program) on Lailara frame, checked at 1440 + 375 → deploy → flip public. ~2–2.5 weeks.

## Next

1. Galewick program rulebook (both families, incl. one explicit partial-pay rule) — owner guardrail review.
2. Universe generator (seed-locked, byte-stable) + defect seeding.
3. Dollar-share bound check.
4. **STOP:** 20-claim eyeball gate for the owner.
