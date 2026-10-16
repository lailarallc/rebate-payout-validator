# Anchor research — raw findings (2026-10-15)

Input to the design gate. Not yet pinned. Every B2B figure below is a vendor or
consultancy claim; vendor-benchmark caveat applies to all rows unless marked independent.

## Aggregate leakage / validation failure (use as BOUND only, never divided into classes)

| Figure | Unit | Source | Type |
|---|---|---|---|
| 6–15% of claims fail basic validation | % of claims | [ProfitOptics, Apr 2026](https://www.profitoptics.com/insights/where-rebate-management-breaks-down-for-manufacturers) | Vendor |
| ~20% failed ≥1 validation step (single audit) | % of claims | same | Vendor |
| 3–5% of rebate margin lost to distributor claim errors | % of rebate margin | [ProfitOptics](https://www.profitoptics.com/rebate-audit) | Vendor |
| ~10% of channel incentive payouts over-claimed / wrong entity (high-tech) | % of payout $ | [IndustryWeek, Zyme founder](https://www.industryweek.com/supply-chain/article/22008178/how-to-lose-50-billion) | Vendor estimate |
| OEMs overpay incentives 10–15% (Forrester via Zyme PR) | % of incentive $ | [GlobeNewswire, 2013](https://www.globenewswire.com/news-release/2013/12/03/1088667/0/en/Zyme-Launches-ChannelView-Incentives-Suite-on-Salesforce-com-s-AppExchange-the-World-s-Leading-Business-Apps-Marketplace.html?print=1) | Vendor PR, second-hand |
| 1–9% of rebate spend fraudulent/non-compliant (appliance up to 9%, tires ~4%) | % of spend | [360insights](https://www.360insights.com/blog/three-ways-your-consumer-rebates-or-cashback-program-is-bleeding-money-and-how-to-stop-them) | Vendor, unsourced, consumer |

## Underpayment

| Figure | Unit | Source | Type |
|---|---|---|---|
| 0.75–1.25% of rebate income missed | % of rebate income | [Profectus via CFOtech, 2022](https://cfotech.com.au/story/profectus-group-serves-up-payment-analysis-for-barbeques-galore) | Vendor (recovery), buy-side |
| 3.5–4.5 errors per 10k supplier transactions | per 10k | same | Vendor |
| Longer redemption windows → lower redemption; deadline effects | qualitative | [UF / Silk, 2004](https://archive.news.ufl.edu/articles/2004/06/redemption-of-mail-in-rebates-declines-with-increased-time-allowance.html) | Independent, consumer |

## Duplicate analogue (AP duplicate payments, not claims — floor only)

| Figure | Source | Type |
|---|---|---|
| 0.1–2% of disbursements (estimate) | [Berkeley audit, 2010](https://berkeleyca.gov/sites/default/files/2022-01/2010-02-09_Item_10_Audit_Over__38_000_in_Duplicate_and_Over_Payments_Recovered.pdf) | Independent |
| Measured: 0.002–0.04% of $ | [Kansas City](https://kcmo.gov/home/showpublisheddocument/6404/637501981795270000), [Orange County](https://ocauditor.gov/wp-content/uploads/2017/08/2713-K-CAAT-May-2008.pdf), [Coventry](https://edemocracy.coventry.gov.uk/documents/s36157/Account%20Payable%20Recovery%20Audit%202016-2017.pdf) | Independent |

## Structural realism (CITE/DIRECTION)

- Claim window 30–60 days post-activity; documentation incompleteness = #1 rejection reason, late filing #3 ([ZINFI](https://www.zinfi.com/?p=65843), vendor, rank not rate).
- SPIFF runs 30–90 days; $25–$200/unit illustrative ([ZINFI](https://www.zinfi.com/glossary/what-is-spiff/), [Prospeo 2026](https://prospeo.io/s/spiff-program)).
- Tier examples 2%/3% or 2%/4% at $500k/$1M ([Hyperbots](https://www.hyperbots.com/glossary/volume-rebates)).
- Retro vs incremental gap ~12% in a $5M worked example ([SAP Community, 2023](https://answers.sap.com/t5/enterprise-resource-planning-q-a/sales-rebate-settlement-retroactive-accruals-update-field-option-on-display/qaq-p/12770977)).

## Gaps — no published per-class rate

All 17 taxonomy classes. Also: seasonality, industry/offer variation (beyond
360insights appliance-vs-tire split), claim volume per member. Not found: IRF,
Vistex, Model N, Big-4 rebate audit papers.

→ Per the gap rule, every class rate comes from the PRACTITIONER C/O/R call.

---

# Pass 2 — HVAC + warranty analogue (2026-10-15)

Figures from search summaries; primary sources NOT read unless noted.

## Warranty analogue
- Fraud = 5–15% of warranty cost; warranty cost = 1–4% of sales ("Warranty fraud management" book via [Corso](https://www.corso.com/post-purchase-resource-center/warranty-fraud-how-to-detect-prevent-and-manage-illegitimate-claims), vendor). Bound candidate.
- 8.1% of rejected claims rejected as fraud; 3.6% of approved later found fraudulent (IBM study via [ASIS](https://www.asisonline.org/security-management-magazine/latest-news/today-in-security/2020/march/Warranty-Fraud/), 2020, trade press citing vendor).
- 40% of claims contain inaccuracies (missing receipts, wrong serials) ([ClaimLane](https://www.claimlane.com/resources/blog/warranty-claim-denied), vendor, unsourced — upper-bound anecdote).
- Median 15% of rejected claims rejected for policy reasons, 604 cos ([APQC](https://www.apqc.org/what-we-do/benchmarking/open-standards-benchmarking/measures/percentage-total-rejected-claims-0), independent, denominator unclear).
- Non-warranty structural analogues: health claims duplicate/incomplete/coding 4.9% of claims ([HCI / MA report](https://www.hcinnovationgroup.com/population-health-management/payers-providers/news/55356286/massachusetts-report-20-of-claims-denied-in-2024)); 52% of flagged duplicates confirmed ([NY OSC](https://www.osc.ny.gov/files/audits/2017-11/bse-2016-05-09.pdf)); 1.4% paid incorrectly ([Nevada PEBP](https://www.pebp.nv.gov/siteassets/content/meetings/2020/september/4.4-audit-report-and-response-combined.pdf)).

## HVAC
- Contractor rebate approval ~70% baseline → 92–95% with processor ([Pipeline On](https://pipelineon.com/blog/hvac-utility-rebate-administration/), vendor, weak).
- Claim windows: 90 days from install ([SCI REMC 2026](https://www.sciremc.com/wp-content/uploads/2026_Residential_HVAC_Terms_Conditions.pdf), utility rules). Warranty registration 60–90 days by OEM ([Pipeline On](https://pipelineon.com/blog/hvac-warranty-registration/), unverified).
- Rejection reasons (qualitative): below SEER minimum, AHRI cert mismatch, used/rebuilt unit, unlicensed installer, invoice mismatch, incomplete form (utility applications: Chaska, Moreno Valley, CPS Energy).
- SPIFF $150–$600/unit attributed to ACHR News 2025 ([Pipeline On](https://pipelineon.com/blog/hvac-warranty-claims/), unverified).

## Volume rebate
- Nothing. PRGX marketing only, no rates.

## Gaps after pass 2
Still no per-class rate for any of the 17 classes. Not yet opened: utility EM&V
process evaluations (Duke Energy KY Smart $aver HVAC, Energy Trust of Oregon,
Focus on Energy, NYSERDA); AHRI, ACHR News, HARDI directly.

---

# Pass 3 — utility EM&V, READ IN PRIMARY (2026-10-15)

**Source:** Navigant Consulting, *Process Evaluation for Con Edison's and Orange & Rockland Utilities' Residential HVAC Programs*, Sept 20, 2013, pp. 48–49, Figs. 38–39. Independent evaluator, regulator-facing. Text extracted with pdftotext and read directly.

- **Overall rejection: ~13% of measure applications** (403 rejected vs 2,830 paid/in progress). Electric 11%, gas 20%.
- **Reason field blank on 53% of rejections** (211 of 403) — itself a realism note: real reject logs are dirty.
- Electric, reasons recorded (n=114): low SEER 31%, non-participating contractor 32%, low EER 20%, unit not a rated combination 14%, invalid purchase date 1%, other 1%.
- Gas, reasons recorded (n=76): non-participating contractor 47%, low AFUE 38%, other ineligible product/customer ~11%, invalid purchase date 1%, incomplete application 1%.
- File review (n=19 applicant files): 12 of 19 (63%) delayed for missing info — 9 missing invoice, 2 low EER; all 12 eventually paid. → missing documentation is mostly a *delay*, not a final reject.
- O&R checks for duplicate serial numbers against its own data and NYSERDA's (control exists; no rate given).

**Class mapping (direction only — utility consumer rebate, 2013, not manufacturer SPIFF):**
- Ineligible product (#7) dominates final rejections (efficiency-tier fails ≈ 50–65% of reasoned rejects).
- Ineligible member (#10) is the other major class (non-participating contractor).
- Out-of-window date (#5) and incomplete docs (#8) are rare as *final* rejects (~1%) but docs are common as *delays*.
- No rate for duplicates, rain checks, wrong rate, tier math.

Other three saved PDFs (Energy Trust 2023 impact eval, Cadmus Duke App. F, Black Hills EL18-043): no usable defect rates. Black Hills: 6 failed applications PY2017, no denominator.

---

# Rate mapping — PINNED (2026-10-15, owner-accepted)

**C = 2.0% · O = 0.75% · R = 0.2%.** Stated once, applied uniformly to every class whose
rate has no published source. Denominators: SPIFF classes = % of paid claims; tier
classes = % of member-periods. Mid-band beats edge-of-band for a judgment-mapped rate.

Resulting seeded defect share: SPIFF ≈ 10.4% of claims (≈8.2% over, ≈2.2% under) —
inside the cited 6–15% validation-failure band. Tier ≈ 9.5% of member-periods.

**Rejection-rate caveat:** Published numbers are rejection rates — defects caught before
payment. Payout Math seeds defects that got paid anyway, or were wrongly denied.
Research gives direction, not the rate itself.

**Bound check:** dollar-share bound (10–15% overpayment, vendor) checked AFTER generation.
No re-tuning if the verdict is undramatic. The verdict lands where it lands.

---

# Bound check — RESULT (2026-10-16, first generation, not re-tuned)

`scripts/bound_check.py` → `build/bound_check.json`.

| Bound | Measured | Cited range | Result |
|---|---|---|---|
| Paid install-bonus claims carrying a defect | 11.05% (1,306 of 11,818) | 6–15% (ProfitOptics, vendor) | **PASS** |
| Overpaid $ as share of all $ approved | 1.90% ($252,005 of $13,241,081) | 10–15% (Zyme/Forrester 2013, vendor PR) | **FAIL** |

**Re-run after realism fixes (rulebook v1.1, 2026-10-16):** claim share 11.14% PASS; overpaid-dollar share
2.54% ($332,822 of $13,088,044) FAIL. Same cause, same disposition: disclosed, not re-tuned.

**Why the dollar bound fails, stated plainly:** the pinned per-record rates (C 2.0 / O 0.75 / R 0.2)
put about 2–11% of *records* in defect. Distributor rebates are 91% of approved dollars, but only 60 of
640 distributor-quarters carry a defect, and a defect there moves a fraction of the rebate, not all of
it. A per-record frequency mapping cannot also produce a 10–15% *dollar* overpayment share unless
defects are concentrated in the largest payments. No published source supports that concentration.

**Not re-tuned** (pinned rule: no re-tuning if the verdict is undramatic). The failing bound is
disclosed, not hidden. The cited 10–15% is a 2013 vendor press-release figure for high-tech OEMs,
quoted second-hand. It is the weakest anchor in the file.
