# Realism review — Galewick 2025 universe (commit 632c00a)

**Verdict: FAIL.** The dollar math is sound: every flag reproduces by hand from the rulebook. The
data does not yet pass as a real program year. A program sponsor would spot five problems within
minutes: no installs ever happen on the 31st; claims were received and paid before the program
existed; every distributor buys every SKU every month at one fleet-wide list price; contractor
claims cannot be reconciled with their distributors' purchases; and the volume rebate has no
heating season. Every fix is local to `scripts/generate_universe.py`, and none needs a change
to rates, rules, or parameters.

Reviewer: independent session, no stake in the build. Read-only on everything except this file.
Python `-I`, stdlib only. Inputs: `data/*.csv`, `build/results.json`, `data/planted.csv`, plus
the generator source (read to explain the tells, not to grade them).

## What holds up

- **Hand reproduction: exact.** An independent re-implementation of Parts A and B, written from the
  rulebook text alone, reproduces all of the following with zero disagreements on any record:
  1,306 SPIFF records (over $86,260.00, under $31,751.00) and 60 tier records (over $165,745.38,
  under $274,746.60). The SPIFF result needs one inference the rulebook does not state (see F7).
- **Pinned sizes and rates hold.** 350 contractors, 11,818 paid claims, 640 statements. R classes
  have 24 records each, O classes 90 (SPIFF) or 5 (tier), and C classes 240 or 13.
- **Blank denial reasons are 49.6%** (776 of 1,564), against 53% in Navigant 2013. The recorded
  reasons are led by ineligible model (40%) and inactive contractor (21%), which matches the
  Navigant direction.
- **Filing lag looks right.** It is lognormal with a median of 16 days and a tail past 60 (382 claims).
- **Claims per contractor look right:** median 28, p90 73, max 475; the top 10 contractors file 16%.
  This skew is believable.
- **Model mix looks right.** HP leads AC, the entry tiers dominate, and furnace claims peak in
  Q4 and Q1 (1,060 in Q4 vs 388 in Q3).
- **Tier occupancy is plausible:** T1 25%, T2 54%, T3 17%, T4 4%. Returns are 1.15% of equipment
  dollars, and 32% of quarters have no returns.
- **Guardrail holds.** A web search for "Galewick" returns no company. Model codes (`GW-AC15`…)
  and rule shapes are generic. See F14 for the one residual risk.
- **Multi-defect combinations are plausible:** 27 records. The most common pairs are 5+6, 6+10, 6+8,
  7+8 and 7+10, each a claim that broke two cheap checks at once.

## Findings — breaks a pinned criterion or the rulebook

Ranked by severity.

### F1 (High): claims received and paid before the program year existed
- **What:** 79 claims have a received date before 2025-01-01. Of these, 38 were **paid** under
  the 2025 program, and the earliest receipt is 2024-09-24.
- **Evidence:** A000021 (installed 2024-11-17, received 2024-11-20, paid $70) and A000038 (installed
  2024-11-21, received 2024-12-02, paid $135). The 41 correct denials go back to September 2024
  (A000001–A000003).
- **Why it breaks:** a 2025 program cannot receive claims in September 2024. A real class #5
  claim is a late-December install filed in January, or a January-2026 install filed into the
  closing 2025 program. Only the second of these is present. The current data also implies impossible
  date order against the rulebook's own year (A3.1, program year Jan 1 – Dec 31).
- **Smallest fix:** in #5 and in the correctly denied `out_of_window` branch, draw the shifted
  install date so that `received_date >= 2025-01-02`. For 2024 installs, use Dec 1–31 with a lag
  that crosses the year boundary.

### F2 (High): distributor purchases cannot support the contractor claims routed through them
- **What:** the two program families are statistically independent, although the universe is
  pinned as one channel (Manufacturer → distributors → installing contractors, clarify-log Q6).
- **Evidence:**
  - In 44 distributor×model pairs, contractors claimed more units than the distributor bought all
    year. For example, D152/GW-HP16 shows 102 claimed against 47 purchased, and D106/GW-HP18
    shows 19 against 1.
  - D106's contractors claimed 2.3× its total equipment units for the year.
  - 19 distributors have zero contractors and zero claims, despite annual equipment purchases of
    $609k–$1.5M+.
  - Distributor dollar volume and claim count correlate at r = −0.07.
- **Why it breaks:** this is the first cross-check a sponsor's auditor runs, because units
  installed per channel cannot exceed sell-in. A planted defect that the channel structure makes
  impossible undermines every flag next to it.
- **Smallest fix:** assign each contractor a `home_distributor_id` with probability proportional
  to distributor `base`, and scale contractor `size` by the same draw. Then assert
  `claimed_units(d, model) <= purchased_units(d, model)` for every pair, and re-draw any pair that
  fails the assertion.

### F3 (High): no heating season in distributor sell-in
- **What:** one `QUARTER_FACTOR` applies to every SKU, so furnace sell-in peaks in Q2.
- **Evidence:** furnace units purchased by quarter: Q1 14,074, Q2 21,906, Q3 20,692, Q4 13,973.
  Furnace installs claimed: Q1 531, Q2 393, Q3 388, Q4 1,060. AC sell-in has the same shape as
  furnace sell-in.
- **Why it breaks:** clarify-log Q6 pins a seasonal year with a "heating bump fall". The claim
  family honours this; the volume family does not. Distributors stock furnaces ahead of Q4, not Q2.
- **Smallest fix:** use a per-family quarter factor, for example FG `{1: 1.0, 2: 0.6, 3: 1.0, 4: 1.4}`
  and keep the current factor for AC and HP. The values are DIRECTION and need a label in
  DECISIONS.

### F4 (Medium-High): #12 "Wrong tier" records match neither mechanism the rulebook names
- **What:** the rulebook's note on #12 says the cause is "the wrong volume figure or the wrong
  threshold comparison". In every planted #12, the volume basis is correct and the tier is moved
  one step at random, wherever the volume sits.
- **Evidence:** 8 of the 13 records sit more than 10% from any threshold.
  - D132-Q1: $497,900 paid at Tier 3, which needs $1,050,000. That is 53% from the nearest
    threshold.
  - D056-Q4: $543,200 paid at Tier 1, 48% above the Tier 2 threshold.
  - D057-Q1: $645,650 paid at Tier 3.

  No volume equals a threshold exactly, so the `>=` vs `>` boundary error never appears.
- **Why it breaks:** an auditor reading the evidence cannot say *how* a $498k distributor got a
  rate meant for $1.05M. Real wrong-tier errors cluster at boundaries, or come from a visibly
  wrong basis.
- **Smallest fix:** seed #12 only where volume is within about 3% of a threshold (there are 42
  candidate statements), and flip the tier across that boundary. Alternatively, also plant 2–3
  volumes exactly at a threshold and pay them one tier low.

### F5 (Medium-High): "Returns not netted" displays underpaid dollars
- **What:** D049-Q4 carries classes 12 and 14. Its primary is #14 (B3.2 precedes B4), but its delta is an
  **underpayment** of $6,871.37, because the wrong tier (T1) zeroed the rebate.
- **Evidence:** in `results.json`, class 14 shows under_cents of 687,137. The rulebook's class
  table lists #14 as direction "Over" only.
- **Why it breaks:** a published page will show "Returns not netted: $6,871 underpaid". A reader
  checking the rulebook sees a contradiction.
- **Smallest fix:** either exclude #12 from #14 records when seeding (as #12 already excludes #17),
  or make primary attribution direction-aware and say so in C2. The first fix is one line.

### F6 (Medium): "pending" is a perfect oracle for defect #11
- **What:** all 80 pending claims are planted #11, and no claim is legitimately in process.
- **Evidence:** pending receipts run evenly from Jan 2025 (4 claims) to Jan 2026 (4 claims). Claims
  received up to 2026-05-06 exist, and none is pending.
- **Why it breaks:** any real extract has a backlog of recent claims in process. With no backlog,
  a reader can find #11 by filtering on status, and the 15-month-old pending claims carry no
  contrast.
- **Smallest fix:** set an explicit extract date, for example 2026-05-15, and state it in the rules
  or README. Mark claims received in the last 2–3 weeks before it as `pending`, as non-defects.
  The validator must then treat "pending and inside the processing window" as not-yet-owed.

### F7 (Medium): the rulebook never states a deadline for documents
- **What:** A5 requires two documents but sets no date for them. A8.2 implies a deadline ("received
  after the 60-day deadline but no more than 15 days after it"). A document received on day 90 is
  never defined as missing.
- **Evidence:** 18 planted #8 records (the "registration beyond grace" variant) and all 90 A8
  partials depend on reading A8 as if it set a document deadline. My hand re-derivation matched only
  after I made that inference.
- **Why it breaks:** the rules promise that every flag can be reproduced by hand from the
  rulebook. This flag can be reproduced only by inference.
- **Smallest fix:** add one sentence to A5 in the template: "Both documents must be received
  within the A4.1 deadline; a document received later is treated as missing, except as provided
  in A8." Re-render the rulebook. This is a text change, not a parameter change.

### F8 (Medium): rain-check and ineligible-model claims put the ineligible model on the claim itself
- **What:** `invoice_model == claim_model` on 13,462 of 13,462 rows. Every #4 and #7 claim was
  paid with an ineligible model code (GW-AC13 / HP14 / FG80) printed on the claim.
- **Evidence:** A000744 is a claim for GW-FG80 paid $90. A001028 shows GW-FG96 ordered, GW-FG80 on
  both the invoice and the claim, paid $90.
- **Why it breaks:** a rain-check substitution shows up as a contractor claiming the *promoted*
  model while the invoice shows the substitute. That is the reason invoice review exists. Under
  the current shape, a one-line lookup against the model list catches 330 overpayments, which
  makes the program look negligent rather than fooled. The A5.2 model-mismatch path never occurs
  anywhere in the data, so an auditor would also ask where it went.
- **Smallest fix:**
  - For #4, set `claim_model = ordered_model` and keep `invoice_model = substitute`. Precedence
    already classes it as #4, and it is also present as #8.
  - For about half of #7, set `claim_model` to the family's entry model and leave the invoice
    showing the ineligible one.

### F9 (Medium): #4 substitutions are always a downgrade to the bottom of the family
- **What:** every rain-check substitute is the ineligible base model, whatever was ordered.
- **Evidence:** 8 of the 90 substitutions turn a GW-HP20V (variable-speed, $5,600 list) into a
  GW-HP14 ($2,800).
- **Why it breaks:** an out-of-stock substitution is like-for-like, or one step either side. No
  distributor substitutes a variable-speed premium unit with a builder-grade unit, and no
  contractor installs one without a re-quote.
- **Smallest fix:** draw #4 only from ordered models in the bottom two efficiency steps of each
  family (AC15, HP16, FG96). That pool has ample candidates.

## Findings — synthetic-generation tells (realism, not a pinned criterion)

### F10 (High tell): day-of-month and weekday artifacts
- **What:** installs never fall on the 31st, and purchases and credits never fall after the 28th.
  Weekends, Christmas and July 4th behave like any other day.
- **Evidence:**
  - Installs on the 31st: **1** of 13,462. Expected count is about 258.
  - Purchase lines and return credits use days 1–28 only.
  - Install, receipt and invoice weekdays are flat: Sunday installs 1,917 vs Monday 1,924, and
    purchase lines on Sunday 3,795.
  - 122 claims were "received" on Dec 25, Jan 1 or Jul 4.
- **Why it breaks:** a 30-second pivot by day finds this. Residential installs run about 85–90% on
  weekdays, and distributor invoicing is close to 100% on business days.
- **Smallest fix:**
  - Draw the day from `calendar.monthrange`.
  - Weight weekdays (for example Sat 0.4, Sun 0.1 for installs; 0 for invoices and credits).
  - Roll weekend and holiday receipts to the next business day, or accept portal receipts but not
    invoice dates.

### F11 (High tell): purchase ledger is a perfect grid
- **What:** the purchase data looks generated, not transacted.
- **Evidence:**
  - Each SKU has exactly **one unit price** across 160 distributors and 12 months (GW-AC15 is
    always $2,650.00).
  - 1,894 of 1,920 distributor-months contain all 14 SKUs, with exactly one line per SKU per month.
  - 627 of 640 statement volumes end in $00 or $50.
  - Non-equipment lines have 0 units and whole-dollar amounts.
  - All 604 baselines are whole dollars.
- **Why it breaks:** real sell-in has many invoices a month, distributor-specific net pricing
  (programs, freight terms, price increases mid-year), ragged cents, and SKUs a given distributor
  never carries.
- **Smallest fix:**
  - Price per line = list × distributor discount (fixed per distributor, about 0.88–0.97) × a
    mid-year increase (+3–5% from Jul 1), rounded to cents.
  - Split each month into 3–12 invoices.
  - Give each distributor a 6–9 SKU assortment.
  - Draw baselines to the cent.

### F12 (Medium tell): claim documents arrive like clockwork
- **What:** document dates follow fixed rules, with no variation.
- **Evidence:**
  - `invoice_doc_date == received_date` on 13,462 of 13,462 rows.
  - No claim lacks an invoice.
  - Registration lag is uniform from 0 to 10 days (about 1,000–1,400 per day), then nothing until
    the planted 61+ cases.
  - Apart from planted and A8 cases, the registration document never trails the claim.
- **Why it breaks:** Navigant (anchors pass 3) found that missing information delayed 63% of
  files, and that **missing invoice** was the most common gap. Docs trickling in after the claim
  but inside the deadline are the norm. This data has none.
- **Smallest fix:**
  - Draw registration lag from a skewed distribution with a tail to about 45 days, so some
    registrations arrive after the claim but inside the deadline.
  - Give about 15% of claims an invoice document received 1–20 days after the claim, still within
    the deadline.
  - Add a missing-invoice variant to #8 and to the correctly denied `missing_docs`.

### F13 (Medium tell): out-of-window correct denials sit on the 15th
- **What:** all 47 correctly denied out-of-window claims have an install date of 2024-09-15,
  10-15, 11-15 or 12-15.
- **Evidence:** 13 claims on 10-15, 13 on 11-15, 11 on 09-15 and 10 on 12-15. This is the first
  screen of `claims.csv`.
- **Smallest fix:** draw the day at random (this is part of the F1 fix).

### F14 (Low, guardrail): contractor and distributor names include real place names
- **What:** the name generator joins a prefix and a suffix, which reproduces real towns.
- **Evidence:**
  - 17 of 160 distributor names are real place names, including Hartford HVAC Supply, Stratford
    Supply Co., Wexford HVAC Supply and Ashton Distribution.
  - At least 43 of 350 contractor names are real place names, including Hartford Mechanical,
    Thornton Air & Heat, Salford Climate Services and Aldridge Home Comfort.
- **Why it matters:** none mirrors a known program operator, but "Hartford HVAC Supply" style
  names have a real chance of matching an operating business.
- **Smallest fix:** drop the suffixes that produce towns ("ford", "ton", "ley") or keep a
  stop-list of real place names, then re-screen the names before launch together with the
  Galewick trademark check.

### F15 (Low tell): no distributor-level persistence in growth
- **What:** growth vs baseline is drawn fresh each quarter. Q1 and Q2 growth ratios correlate at
  r = −0.02.
- **Why it breaks:** real distributors that grow keep growing, because of a new branch, a lost
  line, or a competitor's exit.
- **Smallest fix:** give each distributor a growth draw, gauss(1.03, 0.08), and add per-quarter
  noise of about 0.04.

### F16 (Low tell): the spring promotion moves no units
- **What:** a 50% bonus uplift for Mar 1–Apr 30 produces no response in install volume.
- **Evidence:**
  - Feb 23–28 has 93 installs and Mar 1–6 has 175. The jump comes from the month weights
    (4 → 7), not from the promotion.
  - Cooling installs on Apr 25–30 (233) are fewer than on May 1–6 (267). There is no Apr 30
    pull-forward.
- **Why it matters:** an incentive analyst expects some pull-forward, and some install dates
  pushed into the window. This is taste, but it is the first thing a channel-program person
  looks for.
- **Smallest fix:** multiply cooling install weight by about 1.15 inside the window, and move
  about 2% of May 1–7 cooling installs to Apr 24–30.

### F17 (Low tell): terminated contractors keep installing at full rate
- **What:** contractors whose enrollment ended keep claiming installs as if nothing changed.
- **Evidence:**
  - C0063, terminated 2025-04-16, has 26 claims for installs after termination, out of 32 total.
  - C0319, enrolled 2025-09-09, has 27 of its 49 claims for installs before enrollment.
  - 39 contractors carry all 453 inactive-date claims.
- **Why it matters:** a terminated contractor loses portal access, and filing tails off quickly.
  The concentration on a few contractors is believable; the volume is not.
- **Smallest fix:** cap post-termination claims at about 30 days of the contractor's normal rate,
  and cap pre-enrollment backfiles at about 60 days.

## Things a real auditor would expect that never appear

- **Model mismatch between invoice and claim (A5.2):** 0 records (F8).
- **Missing invoice:** 0 records (F12).
- **Near-duplicates.** Every duplicate (#1, #2, correct-denied) is an exact copy of serial, model
  and install date. None is a re-keyed serial with one digit off on the *claim* serial.
- **Serials that carry a manufacture date.** Real HVAC serials encode year and week, so a
  "manufactured after install" check exists; `GW` + 7 random digits supports no such check.
  This is taste. If kept, say on the page that serials are opaque.
- **Distributor enrollment.** B1 sits in the precedence list, but `distributors.csv` has no
  enrollment date, so B1 can neither be tested nor violated.
- **Rounding rule.** Part B never states how fractional cents round. The validator floors, and I
  matched it by flooring. Add one clause to B6.

## Sample — 20 claims

**Method:** `random.Random(20261016)`. I drew 8 from clean paid claims (not in `planted.csv`), 4 from
correctly denied claims (denied, not planted), and 8 from planted claims, then sorted the 20 by
claim_id. Script: `scratchpad/samp.py`, available on request.

| Claim | Kind | Reads real? | Why not |
|---|---|---|---|
| A000038 | #5 | **No** | Received 2024-12-02 and paid under the 2025 program (F1). |
| A000744 | #7 | **No** | Claim says GW-FG80 and was paid $90; the ineligible model is on the claim's face (F8). |
| A001028 | #4 | **No** | Claim says GW-FG80 (F8). The FG96 → FG80 substitution is plausible. |
| A001741 | correct deny | Yes | HP14, denied with a blank reason. Matches a real reject log. |
| A002744 | clean | Mostly | Spring AC17 paid $180. The invoice date equals the received date exactly (F12). |
| A003557 | clean | Mostly | FG98M installed in May. The invoice date equals the received date (F12). |
| A003700 | #7 | **No** | FG80 on the claim and paid; a 36-day lag is fine (F8). |
| A004540 | correct deny | Yes | Duplicate filed 48 days after install, reason recorded. |
| A006024 | clean | Mostly | Same pattern as A003557. |
| A006166 | #7+#8 | Partly | Missing registration plus GW-AC13 on the claim. The pair is plausible; the claim model is not (F8). |
| A008300 | clean | Mostly | Registration 2 days after install, every document on time. |
| A008988 | clean | Yes | Labor Day install, which is fine, but weekday never matters anywhere in the data (F10). |
| A010414 | clean | Mostly | — |
| A010846 | correct deny | Yes | Install 4 months after termination, reason recorded. |
| A011083 | clean | Yes | 36-day lag for a contractor enrolled Jul 16 and terminated Oct 22. Odd, but legal. |
| A011355 | clean | Mostly | — |
| A011862 | #11 pending | Partly | Pending for months while 30 sibling claims were paid. Plausible, but status alone gives it away (F6). |
| A011985 | correct deny | Yes | AC13, "Model not eligible". |
| A013428 | #6 | Yes | 102 days late and paid anyway. A believable processor miss. |
| A013445 | #6 | Yes | 94 days late, filed over the holidays. Believable. |

**Result:** 8 of 20 read as real (Yes), 6 read as Mostly, 2 as Partly, and 4 fail outright. Of the
4 failures, 3 are F8 (ineligible model on the claim) and 1 is F1 (receipt before the program).
The 8 marked "Mostly" or "Partly" pass alone, but show the doc-date grid (F12) as soon as a
second one is read next to them.

## Sample — 10 distributor-quarters

**Method:** the same RNG continued. I drew 6 clean and 4 planted statements.

| Statement | Kind | Reads real? | Note |
|---|---|---|---|
| D023-Q4 | #14 | Yes | $376,250 basis includes returns. Tier 2, a small over. Volume ends in $50 (F11). |
| D077-Q2 | #15 | Yes | Growth tested against the Q1 2025 basis ($2.07M) instead of the 2024 baseline ($3.44M). A textbook wrong baseline. |
| D080-Q2 | #13 | Yes | Tier 2 paid incrementally. A believable system misconfiguration. |
| D102-Q2 | clean | Mostly | $709,100.00. Round to the dollar again (F11). |
| D102-Q4 | clean | Mostly | Q4 volume about half of Q2, with no furnace lift (F3). |
| D103-Q3 | #16 | Yes | New distributor (no baseline), with parts and freight counted. |
| D112-Q2 | clean | Mostly | — |
| D117-Q1 | clean | Mostly | — |
| D134-Q4 | clean | Mostly | Tier 3 in Q4 for a distributor whose Q4 should be furnace-heavy (F3). |
| D159-Q4 | clean | Yes | Tier 1 at $154k. Believable. |

**Result:** the defects read well. 4 of 4 planted statements look like real failures. The clean
statements fail only in aggregate (F3, F11). Note that 1 of 5 #15 records (D094-Q4) uses a
scaled baseline (×0.897) that exists nowhere in the data; the other 4 use the prior quarter,
which is the realistic form.

## Scope note

The 1.9% overpaid-dollar bound miss is disclosed in `anchors-research.md`, and I do not re-litigate
it. None of the fixes above changes a pinned rate or a rulebook parameter. F7 and the B6 rounding
clause are template text changes, and every other fix is in the generator. After the fixes, re-run
the bound check, `validate.py` and the tests.

---

## Builder response (2026-10-16, rulebook v1.1)

Each finding was fixed in the generator, the rule text or the validator, or kept on purpose. Verified by re-running the checks listed and by `tests/test_pipeline.py` (11 tests).

| # | Disposition | Check after fix |
|---|---|---|
| F1 | Fixed. #5 installs are late Dec 2024 (received Jan 2025) or early Jan 2026 (received before the as-of cut-off). Correct out-of-window denials are received in 2025. | 0 claims received before 2025 (test) |
| F2 | Fixed. Contractors are assigned to distributors in proportion to distributor size. Annual SKU units are floored at 1.3–2.5× claimed units and allocated to months exactly. Duplicates keep the unit's real ship-to. | 0 distributor×model pairs claimed > bought (test). 36 small distributors have no enrolled contractors, which is kept as plausible. |
| F3 | Fixed. Seasonality is set per family; furnaces peak in Q4. | Furnace units by quarter: Q1 20k / Q2 12k / Q3 21k / Q4 28k |
| F4 | Fixed. #12 is seeded only within 3% of a threshold, and the tier flips across it. | — |
| F5 | Fixed. #12, #13 and #17 never stack on #14/#16 records. | Primary-class direction matches the rulebook on every record (test) |
| F6 | Fixed. A9.3 sets a 35-day processing window and C0 sets a 2026-02-27 as-of date. In-process claims are pending and not flagged. | 46 in process vs 79 stale pending (#11) |
| F7 | Fixed. A5.3 now states the document deadline, and adds that a late claim is judged under A4.1 alone. | — |
| F8 | Fixed. #4 claims name the ordered model while the invoice shows the substitute (4+8). Half of #7 claims name the entry model (7+8). A5.2 mismatches now occur. | — |
| F9 | Fixed. #4 is drawn only from entry-level ordered models. | — |
| F10 | Fixed. Install days use the full month with weekday and holiday weights. Receipts, invoices and credits fall on business days. | 245 installs on the 31st; 0 weekend invoice lines |
| F11 | Fixed. Prices use the distributor's discount plus the mid-year increase, rounded to the cent. Each month has 3–12 invoices, each distributor has a 6–9 SKU assortment, and baselines are to the cent. | 174–320 distinct unit prices per SKU |
| F12 | Fixed. Registration lag is skewed with a tail. 15% of invoices trail the claim. A missing-invoice variant now exists in #8 and in correct denials. | — |
| F13 | Fixed (via F1). | 0 out-of-window installs on the 15th |
| F14 | Fixed. The suffixes that produce real towns are removed and the prefixes are invented. Names will be re-screened before launch with the trademark check. | — |
| F15 | Fixed. Each distributor gets a persistent growth draw, plus quarterly noise. | — |
| F16 | Fixed. A share of cooling installs is pulled into the spring window, including from early May. | — |
| F17 | Fixed. #10 and inactive-contractor denials use installs within 30 days after termination or 60 days before enrollment. | — |
| Auditor items | B1 is now testable (distributor enrollment dates). B6.3 is the rounding clause. A6.1 says serials are opaque. Near-duplicates (re-keyed serials) are kept out as taste. | — |

---

# Re-review (793e9d1)

**Verdict: PASS WITH FINDINGS.** The 17 original findings are fixed, and I checked each one in the
data rather than taking the response table's word for it. The universe now reads like a real
program year:

- The channel reconciles.
- The calendar is ragged.
- Sell-in has a heating season.
- Defects show up the way real ones do.
- A fresh 20-claim sample reads real on content, 20 of 20.

One record still cannot be reproduced from the rulebook text (R1), which is a one-line fix. The
other findings are new tells that the fixes introduced, and none of them is a blocker.

Same constraints as the first review: read-only except this file, Python `-I` and stdlib only.
Rulebook: v1.1.

## Hand re-derivation against rulebook v1.1

I wrote the re-derivation from the rule text alone, including the new clauses:

- A5.3: document deadline; a late document counts as missing except under A8.
- A9.3 and C0: as-of date 2026-02-27, with a 35-day processing window.
- B1: enrolled for the full quarter.
- B6.3: round down to the cent, B4 and B5 separately.

| Family | Records off | Over | Under | Agreement with `results.json` |
|---|---|---|---|---|
| Tier | 60 | $243,551.71 | $151,075.65 | Exact. 0 disagreements. |
| SPIFF | 1,313 | $89,270.00 | $35,415.00 | 1 disagreement: **A013347** (R1). The validator reports 1,314 records, $89,270.00 over and $35,575.00 under. |

The F7 inference is gone, because A5.3 now states the deadline. B6.3 matches the validator's
flooring. B1 can be computed, but no distributor ever breaks it: the latest enrollment is
2024-09-20.

## Dispositions checked against the data

| # | Builder says | Data says | Status |
|---|---|---|---|
| F1 | No receipts before 2025 | 0 receipts before 2025-01-02. The 42 paid 2024 installs are all Dec 2024, received Jan–Feb 2025. | Fixed |
| F2 | 0 pairs claimed > bought | 0 by **installed** model and unique serial. The 18 pairs over by *claim* model are all #7+8 claims naming the entry model, which is correct by design. Volume vs claims r = 0.62 (was −0.07). | Fixed |
| F3 | Furnaces peak in Q4 | Furnace sell-in by quarter: 20.7k / 12.3k / 20.3k / 28.4k units. Furnace installs: 489 / 396 / 425 / 1,140. | Fixed |
| F4 | #12 within 3% | All 13 within 0.47–2.56% of a threshold | Fixed |
| F5 | Direction matches | Every class's primary dollars match the rulebook's direction column. #14 is now over only. | Fixed |
| F6 | 46 in process, 79 stale | **47 in process and 78 stale** by the rule text. The difference is A013347 (R1). | Fixed, except for R1 |
| F7 | A5.3 added | Reproduces | Fixed |
| F8 | A5.2 mismatches occur | invoice_model ≠ claim_model on 317 rows. All 90 #4 claims name the ordered model. | Fixed |
| F9 | Entry-level only | All #4 claims ordered AC15, HP16 or FG96 | Fixed |
| F10 | 245 installs on the 31st; 0 weekend invoices | Confirmed. Saturday installs are 1,019 and Sunday 260, against about 2,400 on weekdays. 0 receipts on holidays. | Fixed |
| F11 | 174–320 prices per SKU | Confirmed. Statement volumes are ragged to the cent, 1–20 invoices per SKU per month, and distributor-months carry 7–13 SKUs. | Fixed |
| F12 | Docs trail | About 14% of invoice documents trail the claim. Registration lag tails out past 19 days. There are 99 missing invoices and 94 missing registrations. | Fixed (see R6) |
| F13 | No pile on the 15th | Out-of-window installs fall on random days | Fixed |
| F14 | Town suffixes removed | No real place names remain, but the replacement names are malformed (R2) | Fixed, but it introduced R2 |
| F15 | Persistent growth | Q1 vs Q2 growth r = 0.71 (was −0.02) | Fixed |
| F16 | Spring pull | Mar 1,083 vs Feb 455; Apr 1,449 > May 1,249 | Fixed |
| F17 | 30/60-day windows | 384 inactive-date claims across 51 contractors. The maximum per contractor is 20 (was 27). | Fixed |

## Findings — breaks the rulebook

### R1 (Medium): day 35 is in process by the rule text, but the data flags it
- **What:** A013347 was received on 2026-01-23, exactly 35 days before the as-of date, and it is
  pending.
  - A9.3 counts a claim as unprocessed only when it is pending "**more than** 35 days after
    receipt".
  - C0 says a claim received "**within** the previous 35 days" is in process.

  By both, this claim is in process and must not be flagged. The data flags it anyway.
- **Evidence:** `results.json` flags A013347 as #11, $160.00 underpaid. The cause is in two scripts:
  - `validate.py:155` uses `(AS_OF - recv).days < PROCESSING`.
  - The generator's `DECIDED_BY = AS_OF - 35` is inclusive, so it planted #11 on the boundary
    day.
- **Why it breaks:** this is the only flag in 1,374 that cannot be reproduced by hand from the
  rulebook.
- **Smallest fix:** choose one side and make all three places agree.
  - Either change the text to "35 days or more" and "fewer than 35 days".
  - Or use `<=` in the validator and seed defects only on `received_date < DECIDED_BY` in the
    generator.

## Findings — new tells introduced by the fixes

### R2 (Medium tell): invented names are visibly machine-joined
- **What:** the new prefixes join to the suffixes without any phonetic check.
- **Evidence:**
  - 10 names have a tripled letter: Corrrick Climate Services, Corrridge Heating & Air,
    Merrrick HVAC Supply, Yarrrick Climate Services, Odddale HVAC Supply, and others.
  - Joins double a letter: Calvvale, Garvvale, Holvvale, Sorvvale.
  - 15 names start "Linq-" (Linqholt, Linqdale).
  - Clusters such as Dunrmere, Dunrridge and Thravholt read unnatural.
  - Three of the 20 sampled claims carry one of these names (Dunrmere ×2, Holvvale).
- **Why it matters:** on the claims page, a reviewer sees "Corrrick" before they see any number.
  This replaces the F14 risk (real towns) with a synthetic tell.
- **Smallest fix:**
  - In `place()`, reject any name with a tripled letter, a doubled letter at the join, or a `q`
    not followed by `u`.
  - Drop the "Linq" and "Dunr" prefixes.

  A hand-screened list of about 60 invented stems would be cleaner still. Keep the pre-launch
  re-screen.

### R3 (Medium): long-enrolled distributors with no 2024 volume
- **What:** 12 distributors have no Table B3 baseline, so B5.2 bars them from the growth bonus.
  All 12 have been enrolled since 2016–2023, yet they show zero 2024 purchases and normal 2025
  purchases.
- **Evidence:**
  - D094 enrolled 2016-04-16 and D010 enrolled 2017-01-01; in total 12 such distributors.
  - D016 (enrolled 2021-03-26) appears in the sample at $815,049 in Q1 with a blank baseline.
- **Why it breaks:** B5.2 describes a distributor that is new in 2025. A distributor enrolled for
  eight years with no 2024 business would be the first question in a rebate audit. The
  `new_in_year` flag is drawn separately from the enrollment date.
- **Smallest fix:** give `new_in_year` distributors an enrollment date of 2024-10-01 to 2024-12-31.
  B1 still passes for 2025 Q1. Alternatively, draw `new_in_year` from the enrollment date.

### R4 (Low-Medium tell): no defects at year-end
- **What:** two generator constraints empty the year-end of defects:
  - Defects are seeded only on claims received on or before 2026-01-23.
  - #6 requires install + 106 days ≤ 2026-01-23.
- **Evidence:**
  - None of the 240 #6 claims has an install after 2025-10-09, against 3,057 Q4 installs and the
    furnace peak.
  - The 62 claims received after 2026-01-23 that were already decided carry 0 defects.
  - The by-month #6 counts fall from 39 in July to 8 in October, then to 0.
- **Why it matters:** late filing clusters at year-end, around holiday backlogs and the heating
  rush. A defect-rate-by-month chart, which a program view invites, shows a cliff.
- **Smallest fix:**
  - For #6, draw the late margin as 1 to `min(40, (DECIDED_BY - install).days - 60)`, so Q4
    installs qualify.
  - Allow over-class defects on claims already decided inside the final window. Only *pending*
    claims there are exempt.

### R5 (Low, page copy): the multi-defect count is now mostly single acts
- **What:** multi-defect records went from 27 to 232. Of these, 212 are the forced pairs
  7+8 (124) and 4+8 (88).
- **Evidence:** #8 is present on 308 claims and primary on 88.
- **Why it matters:** the pairs are correct under A5.2, because a rain check always also
  mismatches the invoice. But the page pins "multi-defect count at full size", and a reader will
  take 232 to mean 232 independent double failures.
- **Smallest fix:** no data change. Add one line on the page: "Rain-check and model-swap claims
  always also break A5.2."

### R6 (Low tell): clamps leave pile-ups on the deadline
- **What:** documents are clamped to the deadline instead of re-drawn.
- **Evidence:**
  - 47 invoice documents and 19 registrations land exactly on day 60, the deadline, because of
    `min(..., due)`.
  - 10 invoice documents fall on weekends while every other business date is a weekday, because
    `due` itself can be a weekend.
- **Smallest fix:** re-draw instead of clamping, and roll back to the prior business day.

### R7 (Low, taste): Monday intake is 2.5× the other weekdays
- **What:** Monday receipts are 5,545, against 1,804–2,216 on Tuesday to Friday.
- **Why it's acceptable:** weekend portal submissions roll to Monday. That is a defensible intake
  log, provided the page says that received dates are business-day intake dates.
- **Fix:** none needed. One line of documentation is enough.

## Not changed and accepted
- B1 is computable but never broken, because every distributor enrolled by 2024-09-20. This is
  fine as a demo path, and the page should not list B1 as a class.
- The overpaid-dollar bound is now 2.54% against the 10–15% bound. It is disclosed and not
  re-tuned, and I do not re-litigate it.
- **36 distributors with no enrolled contractors.** Plausible, since not every distributor's
  installer base is enrolled.
- **#12 records just below a threshold, paid the higher tier.** 11 of 13 sit just below a
  threshold and were paid the tier above it. That reads as a basis or comparison slip at the
  boundary. Accepted.

## Fresh sample — 20 claims

**Method:** `random.Random(20261017)`. I drew 8 clean paid, 4 correctly denied and 8 planted
claims, then sorted them by claim_id.

| Claim | Kind | Reads real? | Note |
|---|---|---|---|
| A000707 | clean | Yes | HP20V installed Feb 5. The invoice document arrived with the claim. |
| A001744 | #11 pending | Yes | FG98M received Apr 7 and still pending at the as-of date. A lost claim. |
| A002557 | clean | Yes | Spring HP20V paid $260. The registration trails the claim by 2 days. Name: "Dunrmere" (R2). |
| A003766 | clean | Yes | — |
| A003817 | #9 | Yes | Installed May 7 and paid the spring rate ($260 vs $175). A believable boundary slip. |
| A005713 | clean | Yes | — |
| A006670 | correct deny | Yes | Invoice missing, reason recorded. |
| A008564 | #18 | Yes | $139 of $175 with no rule basis. |
| A008954 | clean | Yes | — |
| A009876 | clean | Yes | Invoice document arrived 6 days after the claim, inside the deadline. |
| A010177 | #6 | Yes | 92 days late and paid. |
| A010679 | clean | Yes | — |
| A010744 | #6 | Yes | 65 days late and paid. |
| A010815 | clean | Yes | Contractor enrolled Jun 2025, install in Oct. |
| A010835 | correct deny | Yes | 137 days late. Name: "Holvvale" (R2). |
| A011467 | correct deny | Yes | 124 days late. "Dunrmere" again. |
| A011477 | correct deny | Yes | Duplicate, reason recorded. |
| A011602 | #6 | Yes | 68 days late and paid. |
| A012036 | #11 denied | Yes | Denied as "Missing documentation" although both documents are on file. This is exactly how the defect looks in a real log. |
| A012505 | #7+8 | Yes | Claim says GW-FG96, invoice shows GW-FG80. A textbook model swap. |

**Result:** 20 of 20 read real on content, against 8 of 20 in the first review. 3 of the 20 carry
a malformed name (R2).

## Fresh sample — 10 distributor-quarters

**Method:** the same RNG continued. I drew 6 clean and 4 planted statements.

| Statement | Kind | Reads real? | Note |
|---|---|---|---|
| D016-Q1 | #16 | Yes, except the data behind it | Non-equipment lines counted. The blank baseline on a distributor enrolled since 2021 is R3. |
| D047-Q3 | clean | Yes | $339,238.28 at Tier 2, just over the threshold. |
| D051-Q2 | clean | Yes | — |
| D053-Q1 | clean | Yes | $255,999.99 at Tier 1. |
| D071-Q2 | clean | Yes | 121% of baseline, growth bonus paid. |
| D088-Q4 | clean | Yes | Down 10% on 2024. |
| D107-Q1 | #12 | Yes | $321,915 paid Tier 2. That is 0.95% under the threshold, a boundary slip. |
| D117-Q3 | #17 | Yes | $408k paid Tier 1, carried over from Q2. |
| D124-Q2 | #16 | Yes | Non-equipment lines counted, which inflates the basis on which growth is paid. |
| D128-Q3 | clean | Yes | $4.26M at Tier 4, incremental. |

**Result:** 10 of 10 read real. D016 is the only one with a data contradiction behind it (R3).

---

## Builder response to the re-review (2026-10-16)

| # | Disposition |
|---|---|
| R1 | Fixed: the validator treats a claim as in process when (as-of − received) ≤ 35 days, and the generator seeds defects only on claims more than 35 days old. Rule text, validator and generator now agree. Exact recovery: 1,378 of 1,378. |
| R2 | Fixed: `place()` rejects tripled letters, a doubled letter at the join, and q without u. The stems were replaced (612 valid combinations). 0 tripled letters remain. Names will be re-screened before launch. |
| R3 | Fixed: distributors without a 2024 baseline now enrolled Oct–Dec 2024. |
| R4 | Fixed: the #6 late margin fits before the decided-by date, and late filings now run through installs of 2025-11-18. The final 35-day window stays defect-free, because those claims are undecided. |
| R5 | Page line added beside the multi-defect count. |
| R6 | Fixed: trailing invoice dates are re-drawn rather than clamped, and the registration lag is re-drawn past the deadline. 21 invoices land on day 60 naturally (a claim filed on day 60 with its invoice attached). |
| R7 | Page line added: received dates are business-day intake dates. |
