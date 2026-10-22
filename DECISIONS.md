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
