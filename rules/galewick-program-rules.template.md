# Galewick Climate Systems — 2025 Channel Incentive Program Rules

**Version:** {{version}} · **Status:** {{status}} · **Program year:** January 1 – December 31, 2025

> Galewick Climate Systems is an invented company. These rules are invented for the Payout
> Math demonstration. No element mirrors any real program operator or client.

These rules are the truth Payout Math validates against. Every flag the tool raises cites a
rule number below and can be reproduced by hand from this document and the claim record.

Galewick runs two programs in 2025:

- **Part A — Contractor Install Bonus.** A per-unit bonus to enrolled contractors for each
  eligible unit they install.
- **Part B — Distributor Volume Rebate.** A quarterly tiered rebate to enrolled distributors on
  their purchases from Galewick.

---

## Part A — Contractor Install Bonus

### A1. Who can earn

A1.1 The claimant must be a contractor on the Galewick Certified Installer roster.

A1.2 The contractor's enrollment date must be on or before the install date, and the
contractor's status must be Active on the install date. Installs done before enrollment, or
while status is Suspended or Terminated, earn nothing.

### A2. What earns, and how much

A2.1 Only the models in **Table A1** earn a bonus. Models not listed earn nothing. Parts,
accessories, and thermostats never earn.

A2.2 The bonus is the Table A1 amount for the model installed, at the rate in effect on the
**install date**: the Spring Rate from {{spring_start}} through {{spring_end}}, 2025, and the Standard Rate on
every other day of the program year. The Spring Rate is a cooling-season promotion: furnaces
earn the same amount year-round.

> Every number in these rules is a seeded draw from a stated range. None was chosen by hand.
> The draws and their ranges are in `rules/parameters.json`. The basis for each range is in
> `DECISIONS.md`.

**Table A1 — Eligible models and bonus per unit**

| Model | Description | Standard Rate | Spring Rate ({{spring_short}}) |
|---|---|---|---|
{{table_a1}}

**Not eligible (common in the channel, listed for clarity):** GW-AC13 (13.4 SEER2 air
conditioner), GW-HP14 (14.3 SEER2 heat pump), GW-FG80 (80% AFUE furnace).

### A3. When the install must happen

A3.1 The install date on the invoice must fall between January 1 and December 31, 2025,
inclusive.

### A4. When the claim must be filed

A4.1 The claim must be received by Galewick within **{{deadline}} calendar days** of the install date.
Day 1 is the day after the install. A claim received on day {{deadline_plus_1}} or later earns nothing, except as
provided in A8.

### A5. What documentation is required

A5.1 Every claim needs both:

- (a) the **installation invoice**, showing the install date, the model, and the serial number;
  and
- (b) the **Galewick warranty registration confirmation** for that serial number.

A5.2 The model and serial on the invoice must match the model and serial on the claim.

A5.3 A claim missing either document, or whose invoice does not match the claim, earns
nothing, except as provided in A8.

### A6. One bonus per unit

A6.1 Each serial number earns one bonus, once, for the life of the program, regardless of which
contractor files it. The first valid claim received for a serial number is the one that earns.
Later claims on the same serial earn nothing.

A6.2 **Manufacturing serial collisions.** Galewick occasionally assigns the same serial number
to two physical units. Known collisions are listed in **Table A2** with the model and the
distributor each unit shipped to. A colliding serial identifies two different units. A claim
on either unit earns on its own merits, and must not be denied as a duplicate of the other.

### A7. Substitutions

A7.1 The bonus is paid on the model **actually installed**, as shown on the invoice. It is not
paid on the model ordered, promoted, or originally quoted.

A7.2 If a distributor ships a different model because the ordered model is out of stock, the
installed model must itself appear in Table A1 to earn. If it does, it earns its own Table A1
amount, not the amount of the model ordered.

### A8. Reduced payment for late documentation

A8.1 This is the only rule under which a claim may be paid less than its full Table A1 amount.

A8.2 If a claim was **filed on time** (A4.1) and **one** required document (A5.1 a or b) was
received after the {{deadline}}-day deadline but no more than **{{grace}} days** after it, the claim earns
**{{partial}}%** of its Table A1 amount.

A8.3 Any other partial payment has no basis in these rules.

### A9. Paying earned bonuses

A9.1 Every claim that meets A1 through A7 earns its full Table A1 amount, or {{partial}}% under A8.
Galewick owes that amount whether the claim was paid, denied, or left unprocessed.

A9.2 Bonuses are paid by check or ACH to the enrolled contractor of record.

---

## Part B — Distributor Volume Rebate

### B1. Who can earn

B1.1 The distributor must be enrolled in the Galewick Distributor Program for the full quarter.

### B2. Measurement period

B2.1 Each calendar quarter of 2025 is measured on its own. Q1 is Jan–Mar, Q2 is Apr–Jun, Q3 is
Jul–Sep, and Q4 is Oct–Dec.

### B3. Qualifying volume

B3.1 Qualifying volume is the distributor's invoiced purchases from Galewick, dated in the
quarter, of the **equipment SKUs in Table B1**,

B3.2 **minus** credits for returns of Table B1 SKUs issued in the same quarter.

B3.3 Parts, accessories, controls, freight, and any SKU not in Table B1 never count toward
qualifying volume.

**Table B1 — Rebate-eligible equipment SKUs**

All Table A1 models, plus GW-AC13, GW-HP14, and GW-FG80. These count toward distributor
volume even though they do not earn the contractor install bonus.

### B4. Tiers and rates

B4.1 The tier is set by the quarter's qualifying volume, compared to the thresholds in Table B2.
A distributor reaches a tier when qualifying volume is **equal to or greater than** the
threshold.

B4.2 The tier is recalculated every quarter. A tier reached in one quarter does not carry into
the next.

**Table B2 — Quarterly tiers**

| Tier | Qualifying volume | Rate | How the rate applies |
|---|---|---|---|
{{table_b2}}

### B5. Growth bonus

B5.1 A distributor earns an additional **{{growth_bonus}}%** on the quarter's qualifying volume if that
volume is at least **{{growth_threshold}}%** of its baseline.

B5.2 The **baseline** is the distributor's qualifying volume for the **same quarter of 2024**,
calculated under B3. Baselines are listed in Table B3. A distributor with no 2024 baseline
cannot earn the growth bonus.

### B6. Payment

B6.1 Rebate earned is the B4 amount plus any B5 amount.

B6.2 Galewick owes the rebate earned for each quarter. It is paid within 45 days after
quarter end to the enrolled distributor of record.

---

## Part C — How Payout Math applies these rules

C1. **Earned** is the amount these rules produce for a claim or a distributor-quarter.
**Paid** is the amount Galewick actually paid. Where paid exceeds earned, the difference is
an **overpayment**. Where earned exceeds paid, the difference is an **underpayment**. The two
are never netted against each other.

C2. **One primary defect per record.** A record can break more than one rule. Its dollars are
assigned to one primary defect, chosen in this fixed order:

1. **Eligibility:** A1, A7, A2.1, B1, B3.3
2. **Evidence:** A6, A3, A4, A5
3. **Math:** A2.2, A8, A9, B3.2, B4, B5

Within a group, the first-listed rule wins. Other defects on the record are still shown as
evidence.

### Defect classes and the rule each one breaks

| # | Defect class | Rule | Direction | Reproduce by hand |
|---|---|---|---|---|
| 1 | Duplicate serial, same contractor | A6.1 | Over | Serial appears on an earlier paid claim from the same contractor |
| 2 | Duplicate serial, two contractors | A6.1 | Over | Serial appears on an earlier paid claim from a different contractor |
| 3 | Factory serial collision denied as duplicate | A6.2 | Under | Serial + model is in Table A2; claim denied as a duplicate |
| 4 | Rain-check substitute paid | A7.2 | Over | Invoice model ≠ ordered model; invoice model not in Table A1 |
| 5 | Install outside program year | A3.1 | Over | Invoice install date before Jan 1 or after Dec 31, 2025 |
| 6 | Filed late, paid anyway | A4.1 | Over | Received date − install date > {{deadline}} days, and A8 doesn't apply |
| 7 | Ineligible model | A2.1 | Over | Invoice model not in Table A1 (no substitution involved) |
| 8 | Missing or mismatched documentation | A5 | Over | Document absent, or invoice model/serial ≠ claim |
| 9 | Wrong bonus amount | A2.2 | Over or under | Paid ≠ Table A1 amount at the install-date rate |
| 10 | Ineligible contractor | A1.2 | Over | Install date before enrollment, or status not Active |
| 11 | Valid claim denied or unprocessed | A9.1 | Under | Claim meets A1–A7; paid $0 |
| 12 | Wrong tier | B4.1 | Over or under | Tier implied by qualifying volume ≠ tier paid |
| 13 | Retroactive vs. incremental misapplied | B4 (Table B2) | Over or under | Tier 2–3 paid incrementally, or Tier 4 paid retroactively |
| 14 | Returns not netted | B3.2 | Over | Rebate computed on purchases before return credits |
| 15 | Wrong growth baseline | B5.2 | Over or under | Growth test run against a figure other than Table B3 |
| 16 | Ineligible SKUs in volume | B3.3 | Over | Non-Table B1 lines counted in qualifying volume |
| 17 | Earned tier paid at a lower tier | B4.2 | Under | Prior-quarter tier carried forward after the distributor moved up |
| 18 | Partial payment with no rule basis | A8.3 | Over or under | 0 < paid < full amount, and A8.2 does not apply |

**Note on #12 vs. #17:** #12 is a tier set from the wrong volume figure or the wrong threshold
comparison. #17 is a tier never recalculated: the prior quarter's lower tier was reused.

**Note on #4 vs. #7:** A7 is listed before A2.1, so an ineligible substitute is classed as #4,
not #7. #7 is for an ineligible model installed as ordered.

**Note on #9 vs. #18:** #9 is a payment equal to some *other* Table A1 amount: the wrong
model's rate, or the wrong period's rate. #18 is a payment between $0 and the full amount that
matches no Table A1 amount and does not qualify under A8.2.

---

## Tables to be generated with the universe

- **Table A2:** manufacturing serial collisions (serial, model, ship-to distributor, two rows
  per serial).
- **Table B3:** 2024 same-quarter baselines per distributor.

These are data, published alongside the rules. They are generated seed-locked with the universe.

---

## Changelog

{{changelog}}
