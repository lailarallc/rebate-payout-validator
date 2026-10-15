# /clarify log — rebate-payout-validator

Started 2026-10-15. Input: Max/owner brief (rebate-validator-brief.md). Running record of locked answers.

## Locked

| # | Question | Answer |
|---|---|---|
| Q1–3 | Defect taxonomy | 17 classes (below). Owner added factory dupe serials and rain-check substitution; struck "payout to wrong member entity". Rain check = ineligible substitute SKU paid (over). |
| Q4 | Frequency source | Rates vary by industry, offer, season. All 17 classes must exist. Frequencies from research, not practitioner first. |
| Q5 | Gap rule | Where research has no per-class rate: owner C/O/R call, labeled PRACTITIONER. C/O/R→rate mapping stated once, applied uniformly. Published aggregate leakage = sanity BOUND on total seeded leakage, never a divisor. |
| Q6 | Industry | HVAC. Manufacturer → distributors → installing contractors. Seasonal (cooling peak spring/summer, heating bump fall). |
| Q7 | Program scope | Both families: contractor SPIFF (per unit, by serial) + tiered volume rebate (distributors/dealers). |
| Q8 | Verdict framing | Gross both directions, never netted. **Corrected at confirmation:** verdict leads with overpaid ("$X of $Y approved for payout should never have been approved"); gross underpaid is the second number, full size, same grain, not a co-headline. |
| Q9 | Universe / sponsor | Universe: **Galewick**. Sponsor: **Galewick Climate Systems** (invented; web-screened, trademark check before launch). |
| Q10 | Tool name | **Payout Math** → payoutmath.lailarallc.com. Repo name unchanged. |

## Defect taxonomy (PRACTITIONER anchor — existence; owner's professional judgment)

SPIFF / claims family
1. Duplicate serial, same member (over)
2. Duplicate serial, two members (over)
3. Factory-created duplicate serial → legitimate claim wrongly rejected (under)
4. Rain-check substitution: ineligible substitute SKU paid (over)
5. Install/sale date outside program window (over)
6. Filed after deadline, paid anyway (over)
7. Ineligible product (over)
8. Missing / bad documentation (over)
9. Wrong payout rate for SKU (over or under)
10. Ineligible member (over)
11. Valid claim denied or never processed (under)

Volume / tier family
12. Wrong tier — threshold math (over or under)
13. Retro vs incremental applied wrong (over or under)
14. Gross not net — returns not netted (over)
15. Growth clause on wrong baseline (over or under)
16. Ineligible SKUs counted in volume (over)
17. Earned tier paid at lower tier (under)

## Frequency tags (Q11–12)

Labels: **P** = PRACTITIONER (owner's call). **A** = ASSUMED (Claude's best guess, owner-accepted "best guesses" — weaker than P, labeled separately). **D** = research direction (Navigant 2013 Con Edison eval; utility rebate, not SPIFF).

| # | Class | Tag | Basis |
|---|---|---|---|
| 1 | Dupe serial, same member | R | P |
| 2 | Dupe serial, two members | R | P |
| 3 | Factory dupe wrongly rejected | R | P |
| 4 | Rain-check substitute paid | O | P |
| 5 | Out-of-window date | O | A (D: rare as final reject) |
| 6 | Filed late, paid anyway | C | P |
| 7 | Ineligible product | C | D + A |
| 8 | Missing / bad docs | O | A (D: common as delay, rare as reject) |
| 9 | Wrong payout rate | O | P |
| 10 | Ineligible member | O | A (D: common in 2013 log, but that requirement was later dropped) |
| 11 | Valid claim denied / never processed | C | P |
| 12 | Wrong tier | C | P |
| 13 | Retro vs incremental | O | P |
| 14 | Gross not net | C | P |
| 15 | Growth baseline | O | P |
| 16 | Ineligible SKUs in volume | C | P |
| 17 | Earned tier paid lower | C | P |

Caveat: published rejection rates measure defects *caught* before payment. Seeded defects are ones that *slipped through* to payout (or were wrongly denied). Rejection data is direction, not rate.

## Design gate — pinned

- Rate mapping: C 2.0% / O 0.75% / R 0.2% (see anchors-research.md).
- Period: 1 program year (cooling + heating season).
- SPIFF: ~350 contractors, ~12,000 paid claims (~1,250 defects; R classes ~24 each).
- Tier: 160 distributors × 4 quarters = 640 member-periods (O classes ~5 each).
- Display floor: fleet 5-per-bucket minimum. Any class under 5 after generation is grouped into "other" in the program view, not ranked.

## Multi-defect + partial payment

- Multi-defect claims are expected. Generator seeds each class independently at its rate; overlaps arise naturally (no invented multi-defect rate).
- Attribution (a): one primary class per claim by fixed precedence **eligibility → evidence → math**, stated on the page. Primary dollars sum to the verdict exactly.
- Each class shows "primary on M claims / present on N". N column is informational and labeled as such.
- Multi-defect claim count reported at full size.
- **#18 (new, practitioner addition): ad-hoc partial payment with no rule basis.** Over if partial paid on a $0-earned claim; under if partial paid on a fully valid claim. Rule-consistent partials are not defects → Galewick rules must publish at least one explicit partial-pay rule. Tag: **O** (P). Owner typed "0"; read as O.

## Open
- Universe size (members, claims/period), program rules detail → design gate.
- Data home: brief lean = one repo, data generated in-repo.
