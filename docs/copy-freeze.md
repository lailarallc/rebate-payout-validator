# Copy freeze — Payout Math (for Max's audit)

**Status:** FROZEN for audit. Nothing is deployed. No deploy workflow exists yet, so a push cannot ship the page.

**Run it locally:**

```
npm --prefix web ci
npm --prefix web run dev
```

Then open http://localhost:5173 (main page) and http://localhost:5173/rules (rulebook).

## What to audit

1. **Page copy:** `web/src/routes/+page.svelte`. These are the only user-facing words on the main page. Every number is computed from `web/src/lib/data/summary.json` or `web/static/data/flagged.json`, which the build writes from `build/results.json`. No dollar figure, count, or percentage is typed by hand. A grep for `$<digit>` in the page source returns nothing.
2. **Rulebook:** `rules/galewick-program-rules.md` v1.1, published at `/rules`. It is rendered from `rules/galewick-program-rules.template.md` + `rules/parameters.json`. Edit the template, not the rendered file.
3. **Meta and OG copy:** `web/src/app.html` (title, description, OG/Twitter text).
4. **Footer note:** `web/src/routes/+layout.svelte`.

## Judgment calls the audit should rule on

| # | Where | The call | Why it needs a second eye |
|---|---|---|---|
| J1 | Verdict | Leads with overpaid ("$X of $Y approved … should never have been approved"). Underpaid is the second number, same size, never netted. | Owner-pinned. Confirm the wording. |
| J2 | Method section | "The kinds of error come from nineteen years of incentive-program operations." | The only hand-stated fact on the page. It must match the owner's resume line exactly. |
| J3 | Method section | The dollar bound failure is disclosed in plain words: overpaid is 2.3% of approved, against 10–15% from "a 2013 Zyme press release quoting Forrester on high-tech manufacturers". The rates were not tuned to close the gap. | It is honest, but it hands a skeptic a line. Decide whether to keep it as is, cut the weak bound entirely, or move it to a footnote. (A pinned rule bans re-tuning; it does not require citing a weak source.) |
| J4 | Program view | Errors are split into "Submitted by members, approved by Galewick" and "Calculated by Galewick". The class-to-origin map is in `scripts/build_site_data.py` (ORIGIN). | Claude assigned this classification. It is a reading of the data, not a rule. |
| J5 | Program view | The headline sentence: 63.5% of wrong decisions start with members, but 85.3% of the dollars come from Galewick's calculations. | It is computed, but it is the page's editorial claim. Check that the phrasing does not overreach. |
| J6 | Throughout | "Payout decisions" is used rather than "payouts", because denied claims are decisions, not payouts. | Consistency. |
| J7 | Claims view | Evidence strings come from `scripts/validate.py`. They are terse, system-log register. | These are the strings a sponsor reads when checking a flag by hand. |
| J8 | Footer | "Galewick Climate Systems is invented. Every claim, contractor, distributor, and rule on this site is synthetic; the method is real." | Guardrail statement. |

## Pre-deploy checklist (not started; after audit sign-off)

- [ ] Run a trademark and name screen on "Galewick", "Galewick Climate Systems", and the generated contractor and distributor names, against real businesses.
- [ ] Add `.github/workflows/deploy.yml`, modeled on Slot Math: invariant → build → `lailarallc/reusable-workflows` pages-deploy with `project_name: payoutmath`. The CI build must run the Python pipeline, or check the committed artifacts.
- [ ] Create the Cloudflare Pages project `payoutmath` (Direct Upload, Git off), attach `payoutmath.lailarallc.com`, and wait for Active.
- [ ] Register the OG slug `payoutmath` in `reference/lailara-website/site/src/og/subdomain-manifest.ts`.
- [ ] Write the real README from `reference/README-TEMPLATE.md`, with artifact-fed numbers.
- [ ] Run the pre-ship checks, then flip the repo public.
