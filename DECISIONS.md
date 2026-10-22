# DECISIONS

- **2026-10-16 — History rewritten before first publication, never after.** An early commit named the owner's employer in the PLAN.md guardrail. The repo was a day old, private, unpinned, and had no collaborators, so history was rewritten and force-pushed. Old SHAs are deliberately not recorded here, because GitHub keeps orphaned commits reachable by SHA until it garbage-collects them. Do not: rewrite history once the repo is public or has any collaborator, fork, or pin. After publication, a fix goes in a new commit.
- **2026-10-16 — One orphaned commit accepted. No purge, no deletion, no recreation.** GitHub still serves the pre-rewrite commit to anyone who has its SHA. The owner accepts this because the content isn't sensitive: the owner's employment is public, and the line was a guardrail, not a disclosure. It also can't be reached without a SHA that is recorded nowhere. Deleting and recreating the repo was considered and dropped.
- **2026-10-16 — No further practitioner gates. Distance by construction replaces owner distance review.** The owner wants Payout Math demonstrated on research-backed realism, without ongoing owner review. The practitioner taxonomy recorded on 2026-10-15 stands, because defect *classes* are generic industry knowledge. Every specific program *value* is now a seeded draw, so none came from the memory of anyone who has administered real programs.
  - **Mechanism:** `scripts/roll_parameters.py` draws each parameter uniformly on a stepped range.
    - The seed is SHA-256 of the fixed string `galewick-climate-systems/program-year-2025/parameters`, mod 2^32. It is derived, not chosen.
    - Output goes to `rules/parameters.json`, which is byte-stable on re-run.
    - `scripts/render_rules.py` renders `rules/galewick-program-rules.md` from the template. The rulebook carries no hand-typed parameter.
  - **Ranges and basis.** Basis labels:
    - CITE: a published figure, recorded in `docs/anchors-research.md`.
    - DIRECTION: a published qualitative pattern.
    - STRUCTURAL: no published figure. Claude set the range for internal coherence; the owner did not.

    | Parameter | Range (step) | Basis | Drawn |
    |---|---|---|---|
    | Filing deadline | 30–90 days (15) | CITE: 30–60 (ZINFI), 60–90 (utility/OEM) | 60 |
    | Late-doc grace | 15–45 days (15) | STRUCTURAL | 15 |
    | Late-doc partial pay | 25–75% (25) | STRUCTURAL | 25% |
    | Spring rate start month | Feb–Apr | DIRECTION: cooling-season peak | Mar |
    | Spring rate length | 2–3 months | DIRECTION: SPIFF runs 30–90 days (ZINFI) | 2 (Mar–Apr) |
    | Spring uplift | 20–60% (5) | STRUCTURAL | 50% |
    | Per-unit floor | $25–60 ($5) | CITE: $25–100 (Prospeo), $100–200 (ZINFI) | $50 |
    | Per-unit ceiling | $150–300 ($5) | CITE: $150–600 HVAC (Pipeline On; unverified) | $175 |
    | Tier 2 threshold (quarterly) | $150k–400k ($25k) | DIRECTION: $500k/$1M examples (Hyperbots), scaled to a quarter | $325k |
    | Tier 3 = T2 × | 2.5–3.5 (0.25) | STRUCTURAL | $1.05M |
    | Tier 4 = T3 × | 1.8–2.2 (0.1) | STRUCTURAL | $2.1M |
    | Tier 2 rate | 1.5–2.5% (0.25) | CITE: 2–4% (Hyperbots) | 1.75% |
    | Tier 3 step | +0.5–1.5 pts (0.25) | CITE: 2–4% (Hyperbots) | 3.25% |
    | Tier 4 incremental step | +1.0–2.0 pts (0.25) | STRUCTURAL | 5.25% |
    | Growth threshold | 105–115% (1) | STRUCTURAL | 113% |
    | Growth bonus | 0.5–1.5% (0.25) | STRUCTURAL | 0.75% |

  - **Per-unit amounts by model:** interpolated from floor to ceiling by efficiency rank, with seeded ±8% jitter, rounded to $5. Spring amounts apply to cooling equipment only.
  - **Disclosed and kept:** the Tier 4 incremental rate (5.25%) lands above the cited 2–4% band, because its step range is STRUCTURAL. It was kept, not re-drawn. Re-drawing after seeing a result is tuning for looks.
  - **Not drawn:** model codes (invented) and their efficiency labels. The ineligible SEER2/AFUE levels sit at generic federal-minimum levels. These are product attributes, not program parameters.
  - **Do not:** hand-edit `rules/galewick-program-rules.md` or `rules/parameters.json`. Change a range here first, then re-run both scripts, and log the change.
- **2026-10-16 — The 20-claim owner eyeball gate is replaced by an independent adversarial realism review.** A fresh session with no stake in the build reviews the generated universe against the pinned criteria, following the fleet's blind-review pattern. Its findings are recorded in-repo. Owner sampling is optional, not required.
- **2026-10-16 — Realism review FAIL answered in the generator and the rule text; rates and v1.0 parameters untouched.** The independent review (`docs/realism-review.md`, 17 findings) found the payout math exact, but the data showed synthetic tells. Every finding is addressed or explicitly kept (response table appended to the review).
  - **New parameters in rulebook v1.1.** They come from a separate seeded stream, so every v1.0 draw is unchanged:
    - claim processing window: 21–42 days (7), STRUCTURAL, drawn 35;
    - rebate payment window: 30–60 days (15), STRUCTURAL, drawn 60.
  - **As-of date** of the extract is 2026-02-27. That is a data choice, not a program parameter. It is close enough to year-end that December's heating-season claims form a real in-process backlog.
  - **New DIRECTION labels:**
    - Furnace sell-in seasonality is Q1 1.0 / Q2 0.6 / Q3 1.0 / Q4 1.4, with distributors stocking ahead of winter.
    - Install weekday weights are Sat 0.4, Sun 0.1, holidays 0.1, because residential installs are mostly weekday work.
    - A mid-year list-price increase of +4% applies from Jul 1. It is STRUCTURAL.
  - **Do not:** seed a defect that the channel structure makes impossible. Contractor claims never exceed their distributor's sell-in, and a test enforces this.
- **2026-10-22 — Universe size revised. This is an owner-sourced (PRACTITIONER) realism-scale correction, not verdict tuning.**
  - **Owner's rationale:** a ~$13M program-year payout is unrealistic for a program of this shape. The demo sponsor has to read like the buyer, a smaller program, without spooking them with scale. The owner set the band: program-year payout of **$500K–$1M at most**.
  - **Diagnosis:** the distributor side modeled a $488M sell-in channel, while the contractor side implied a far smaller one. Only 6% of units sold were claimed.
  - **Shapes proposed:**
    1. $3–4M (×0.2), rejected as too large.
    2. $2.5–3M (×0.12), rejected.
    3. 120 contractors / 3,200 claims / 60 distributors / ×0.10, approved, but it landed at $1.22M. The distributor floor (sell-in ≥ 1.3–2.5× claimed units) lifted sell-in to $27M, and the ×0.10 thresholds then tipped 43 of 240 quarters into Tier 4.
    4. **95 contractors / 2,500 claims / 60 distributors × 4 quarters / tier-threshold range ×0.15 / base volume ×0.05**, approved as a band.
  - **Actual result:** **$819,580**, which is $548,126 of rebates plus $271,454 of install bonuses.
    - Sell-in is $22.0M, and payout is 3.7% of sell-in. Rebates are 2.49%, inside the cited 2–4%.
    - Tier occupancy is T1 113 / T2 83 / T3 33 / T4 11.
    - Claimed units are 35% of units sold.
  - **Unchanged:** every pinned rate (C 2.0 / O 0.75 / R 0.2), every program parameter except the threshold range, and the rule text. The threshold draw index is the same as before; only the range is scaled.
  - **Defect coverage:** all 18 classes are still present. The R classes have exactly 5 each, so they clear the display floor. The tier O classes (#13, #15) have 2 each and group into "Other".
  - **Generator change forced by the size:** #12 is now seeded on the statements closest to a threshold, rather than within a fixed 3% window. That window held only 3 statements out of 240.
  - **Cited band check:** total payout as a share of sell-in (3.7%) sits below the only published whole-program figures:
    - Zinfi (vendor): 8–20% for commissions, rebates, MDF and SPIFFs combined.
    - The Channel Company/IPED 2019: 15–24% of the total channel budget.

    Those figures cover instruments Galewick does not run. The rebate share is inside its cited band.
  - **Do not:** re-scale the universe to move the verdict. Sizes move only on an owner realism call, and rates never move.
- **2026-10-22 — Pin deviation: #12 ("Wrong tier") seeding rule changed twice.**
  - **Original rule (realism review F4):** seed #12 only on statements whose volume sits within 3% of a tier threshold, then flip the tier across it.
  - **Deviation 1, forced by the owner-sourced resize:** at 240 statements, only 3 sat inside the 3% window, and the pinned rate needs 5 cases (C 2.0% × 240). The rule became "closest-to-threshold first".
  - **Deviation 2 (third review, T3):** closest-first made every boundary statement wrong and none right, a "perfect wall" an auditor would spot. #12 is now drawn from the 4n statements nearest a threshold (20 for n = 5), weighted 1/rank, without replacement. Clean boundary statements stay interleaved with the defective ones.
  - **What did not change:** the count (rate × base) and the defect's meaning, a tier flipped across the nearest threshold.
  - **Do not:** go back to a fixed-percentage window without checking that it holds at least 4n candidates at the current universe size.
- **2026-10-22 — Second channel resize, so the realism tells T1/T2 can be fixed under the owner's $1M cap. Owner-approved; tier rates unchanged.**
  - **Why the owner ruled:** Payout Math's audience is program sponsors, and both tells show within 30 seconds:
    - T1: plotting sell-in against claims gives a straight line (r = 0.97);
    - T2: 17 of 60 "stocking distributors" earn $0 all year.
  - **Conflict found on paper:** fixing T1 adds sell-in, and every distributor above Tier 1 earns at least 1.75% of it. With 60 distributors, no threshold setting met ≤ $1M and zero $0-earners at the same time. Raising thresholds only created more $0-earners.

    The owner chose a smaller channel over bent rates or a raised cap. Option 2, raising the cap, was rejected.
  - **Solved by a dry-run projection**, using the generator's own arithmetic with nothing written, before the single regeneration.
  - **Shape:**
    - 1,100-claim rate base;
    - 42 contractors;
    - 20 distributors × 4 quarters;
    - tier-threshold range ×1.3 (cumulative ×0.195 of v1.0, same draw index), giving T2 $63,375 / T3 $204,750 / T4 $409,500.
  - **T1 fix:** the claim floor is now a distributor-level multiple of claims (lognormal, median 3, σ 0.7), with mild per-SKU noise. The first attempt used per-SKU noise only; it averaged out (projected r = 0.90–0.98) and was replaced.
  - **T2 fix:** a stocking distributor's base quarter is at least $40K, with re-draws below that. Late-2024 joiners are drawn only from below-median distributors.
  - **Result:** matches the projection to the cent.
    - **$888,574.65 total**: $768,742 of rebates and $119,833 of install bonuses.
    - Sell-in is $22.1M. The effective rebate rate is 3.48%.
    - Correlation of sell-in with claims is r = 0.41; claimed units are 16% of units sold.
    - 0 of 20 distributors earn $0. Tier occupancy is 13 / 36 / 25 / 6.
    - Exact recovery, 129 of 129.
  - **Class floor learned:** below 17 distributors (68 quarters), the O-rate tier classes (#13, #15) round to 0 cases. 20 distributors is the floor.
  - **Owner-accepted cost:** 10 of 18 classes have fewer than 5 cases: the three R install-bonus classes and all six rebate classes. They exist in the data and the claims table, and the program view groups them under "Other".
  - **Do not:** re-roll tier rates after seeing results. They are the original v1.0 draws.
- **2026-10-22 — Fourth review (U1–U8) answered; thresholds ×0.8 (owner-approved).**
  - **U1, one distributor was the program.** D012 accounted for 38% of sell-in and 53% of rebates, from an extreme draw of the new T1 multiplier (24× claims). Its parts, freight and returns stayed flat instead of scaling with volume.
    - **Fixes:** the distributor-level claim multiple is truncated at ≤ 8× (re-drawn above that). Non-equipment lines scale with each month's equipment volume. Returns are 0.5–4% of each quarter's equipment volume.
    - **Effect:** sell-in fell from $22.1M to $14.0M. At the approved thresholds, the projected total fell to $489,095, below the owner's $500K floor.
  - **Thresholds ×0.8.** This is the sanctioned lever: thresholds follow the channel. Same draw index; the cumulative range is now ×0.156 of v1.0, giving T2 $50,700 / T3 $163,800 / T4 $327,600. The owner approved it from the dry-run projection.
  - **Result:** matches the projection to the cent.
    - **$514,807.41** total: $394,974 of rebates plus $119,833 of install bonuses.
    - The effective rebate rate is 2.82%. Tier occupancy as paid is 3 / 46 / 22 / 9.
    - 0 distributors earn $0. The largest distributor is 10.5% of sell-in. Sell-in vs claims is r = 0.67.
    - Exact recovery, 129 of 129.
  - **U7:** two correct denials (missing documents) are left stale-pending. They owe $0, so "pending" alone no longer singles out #11.
  - **U2–U5, page copy:**
    - U2: "Other" is now split by program, on the charts and in the program view.
    - U3: duplicate rule numbers are removed from the "Other" cells.
    - U4: the lede says "issued … rebate statements".
    - U5: the method line says counts are "rounded to a whole case (at least one)".
  - **U6:** accepted as taste. About 11% of lognormal draws fall under the 1.3× floor.
  - **U8, corrections to the previous entry:**
    - "10 of 18 classes" should read **9 of 18**: the three R install-bonus classes plus the six rebate classes.
    - Its tier occupancy (13 / 36 / 25 / 6) was **as paid**. As earned it was 12 / 38 / 24 / 6.
    - Its r = 0.41 was driven by the D012 outlier. Without D012 it was 0.73.
    - At this pass, 9 classes are ranked on the page and 9 are grouped.
- **2026-10-22 — Fifth review (V1–V5) answered. Equipment, claims and statements are byte-identical to the reviewed universe.**
  - **V1, generator bug.** The return-credit loop stopped at the first oversized draw, so only 11 of 80 quarters carried returns. The loop now skips an overshooting draw and stops once it reaches 60% of the target. 47 of 80 quarters now carry returns.
  - **V5.** The four non-equipment categories had come out equal in dollars. They are now weighted: parts 1.5, freight 1.1, accessories 0.8, controls 0.6 (STRUCTURAL).
  - **How the fixes were isolated:** returns and non-equipment values come from a side seeded stream (`SEED + 1`). The main stream still consumes the legacy draws but discards their values (`_burn_legacy_return_draws`), so `claims.csv` and every equipment line are byte-identical to 563b5c6.
    - The first attempt, without the burn, reshuffled the universe: sell-in vs claims went to r = 0.79. It was replaced before any regeneration.
  - **Result:** matches the projection to the cent.
    - **$521,804.21** total: $401,971 of rebates plus $119,833 of install bonuses.
    - Sell-in is $13.99M, and r = 0.67.
    - 0 distributors earn $0. Tier occupancy as paid is 2 / 46 / 23 / 9.
    - Exact recovery, 129 of 129.
  - **V2, accepted.** The entry tier is a stocking hurdle that every enrolled distributor is expected to clear: T2 is $50,700 against a $40K minimum base quarter, so Tier 1 holds only the odd slow quarter. Lowering the minimum base would cost payout margin against the $500K floor.
  - **V3.** The verdict footnote now points readers to the claims table, filtered to the rebate program, to see the grouped rebate rules one by one.
  - **V4, noted for the owner.** Underpaid ($7,336) and overpaid ($17,597) have traded places over the resizes. The headline still leads with overpaid, as pinned.
