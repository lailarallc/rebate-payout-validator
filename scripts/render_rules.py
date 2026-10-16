"""Render rules/galewick-program-rules.md from the template and rules/parameters.json.

The rulebook never carries a hand-typed parameter value: every number comes from
parameters.json. Fails if any placeholder is left unfilled.
"""

import calendar
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "rules" / "galewick-program-rules.template.md"
PARAMS = ROOT / "rules" / "parameters.json"
OUT = ROOT / "rules" / "galewick-program-rules.md"

VERSION = "1.0"
STATUS = "Published — parameters drawn by seed, not by hand"
CHANGELOG = """- **1.0 (2026-10-16):** every program parameter re-drawn as a seeded draw from
  research-plausible ranges (distance by construction). Rules text unchanged from 0.1-draft.
- **0.1-draft (2026-10-15):** first draft; hand-drafted values, all since replaced."""


def usd(x):
    return f"${x:,.0f}"


def pct(x):
    return f"{x:g}"


def last_day(month):
    return calendar.monthrange(2025, month)[1]


def render(params):
    sm, em = params["spring_start_month"], params["spring_end_month"]
    rows = [
        f"| {m['model']} | {m['description']} | {usd(m['standard_usd'])} | {usd(m['spring_usd'])} |"
        for m in params["models"]
    ]
    t = params["tiers"]
    t2, t3, t4 = (t[i]["threshold_usd"] for i in (1, 2, 3))
    r2, r3, r4 = (t[i]["rate_pct"] for i in (1, 2, 3))
    retro = "Retroactive: applies to all qualifying volume from the first dollar"
    tier_rows = [
        f"| 1 | under {usd(t2)} | 0% | — |",
        f"| 2 | {usd(t2)} – {usd(t3 - 1)}.99 | {pct(r2)}% | {retro} |",
        f"| 3 | {usd(t3)} – {usd(t4 - 1)}.99 | {pct(r3)}% | {retro} |",
        f"| 4 | {usd(t4)} and over | {pct(r3)}% on the first {usd(t4)}, plus **{pct(r4)}%** on volume above {usd(t4)} | Incremental above the Tier 4 threshold only |",
    ]
    values = {
        "version": VERSION,
        "status": STATUS,
        "spring_start": f"{calendar.month_name[sm]} 1",
        "spring_end": f"{calendar.month_name[em]} {last_day(em)}",
        "spring_short": f"{calendar.month_abbr[sm]} 1 – {calendar.month_abbr[em]} {last_day(em)}",
        "table_a1": "\n".join(rows),
        "deadline": str(params["filing_deadline_days"]),
        "deadline_plus_1": str(params["filing_deadline_days"] + 1),
        "grace": str(params["late_doc_grace_days"]),
        "partial": str(params["late_doc_partial_pct"]),
        "table_b2": "\n".join(tier_rows),
        "growth_bonus": pct(params["growth_bonus_pct"]),
        "growth_threshold": str(params["growth_threshold_pct"]),
        "changelog": CHANGELOG,
    }
    text = TEMPLATE.read_text(encoding="utf-8")
    for key, val in values.items():
        text = text.replace("{{" + key + "}}", val)
    left = re.findall(r"\{\{\w+\}\}", text)
    if left:
        raise SystemExit(f"unfilled placeholders: {left}")
    return text


def main():
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    OUT.write_text(render(params), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
