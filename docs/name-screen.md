# Name and trademark screen — 2026-10-27

**Verdict: CLEAR WITH NEAR-MISSES.** No real HVAC, plumbing, mechanical or building-supply business, product or trademark uses any screened name.

**Screened:** 63 names: "Galewick", "Galewick Climate Systems", and all 62 generated member names (20 distributors, 42 contractors).

**Galewick: clear.**
- **USPTO wordmark search:** via the tmsearch backend API. The endpoint was validated first: "carrier" returned more than 10,000 hits. "galewick", "galewick*" and "gale*wick" each returned 0.
- **Web exact-phrase search:** no business named Galewick, Galewick Climate Systems, Galewick HVAC, Galewick Inc or Galewick LLC. Near-spellings only: Galew, a village in Poland, plus Gatwick and Colwick.

**Findings — owner decides; naming is owner-class:**

| Name | File | Found | Severity |
|---|---|---|---|
| Pennridge HVAC | `data/contractors.csv` | Three live USPTO marks "PENNRIDGE RANCH" (cattle breeding, Texas). Pennridge is also a real place (Bucks County, PA) where local businesses could use the name. No Pennridge HVAC or heating company was found. | MED |
| Brenwyn Heating & Air | `data/contractors.csv` | "BRANWYN" (merino activewear, Oregon) and "Brangwyn Limited" (UK) are one letter off, in unrelated industries. | LOW |

**Not checked, or checked weakly — this is not a clearance search:**
- USPTO coverage is exact and wildcard wordmarks only. It has no phonetic or similar-mark analysis and does not cover design marks, state marks or common-law use.
- Justia was blocked (403).
- Member names were screened by stem, mostly in grouped queries.
- Not checked at all: state business registries, contractor-license databases, Companies House, Canadian registries, and domain names.

## Rename (2026-11-02)

- **What changed:** "Pennridge HVAC" (C0030) became **"Alvandale HVAC"**. The owner ruled that distance is free and keeping a flagged name buys nothing.
- **How the replacement was drawn:** from the generator's own stem pool, via a separate seeded stream (`SEED + 2`). Any candidate within one edit of a screened name (Pennridge, Brenwyn, Branwyn, Brangwyn) was rejected.
- **Screen of "Alvandale": CLEAR.**
  - USPTO wordmark search: "alvandale", "alvandale*" and "alvandal" each returned 0.
  - Web exact phrase: no business or place by the name. The nearest are Avondale (AZ) and Annandale (MN), two edits away and no name match.
- **Rebuild:** diff-clean apart from the name. `build/results.json` and `flagged.json` are identical to the previous build except for the two Pennridge occurrences, and every total is unchanged.
