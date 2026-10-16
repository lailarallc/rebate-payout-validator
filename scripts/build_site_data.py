"""Shape build/results.json into what the web page reads, and render the rulebook to HTML.

Outputs:
  web/src/lib/data/summary.json   (small; prerendered into the page)
  web/static/data/flagged.json    (every flagged record; fetched by the claims view)
  web/src/lib/data/rules.html     (the published rulebook body, rendered from rules/*.md)
  web/static/rules/galewick-program-rules.md

Canonical JSON, no floats. Rulebook rendering is a minimal Markdown subset (headings,
paragraphs, lists, tables, blockquotes, bold, code) — stdlib only.
"""

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = json.loads((ROOT / "build" / "results.json").read_text(encoding="utf-8"))
BOUNDS = json.loads((ROOT / "build" / "bound_check.json").read_text(encoding="utf-8"))
PARAMS = json.loads((ROOT / "rules" / "parameters.json").read_text(encoding="utf-8"))
WEB = ROOT / "web"

MIN_DISPLAY = 5  # fleet 5-per-bucket floor: smaller classes are grouped into "other"

# Where a defect starts: in what a member submitted, or in Galewick's own calculation.
ORIGIN = {c: "submitted" for c in (1, 2, 4, 5, 6, 7, 8, 10)}
ORIGIN.update({c: "calculated" for c in (3, 9, 11, 12, 13, 14, 15, 16, 17, 18)})


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


def summary():
    classes = []
    for c in RESULTS["classes"]:
        classes.append(dict(c, origin=ORIGIN[c["class"]], shown=c["primary_count"] >= MIN_DISPLAY))
    return {
        "verdict": RESULTS["verdict"],
        "universe": RESULTS["universe"],
        "families": RESULTS["families"],
        "classes": classes,
        "precedence": RESULTS["precedence"],
        "bounds": BOUNDS["bounds"],
        "min_display": MIN_DISPLAY,
        "rules_version": "1.1",
        "params": {k: PARAMS[k] for k in ("filing_deadline_days", "late_doc_grace_days", "late_doc_partial_pct",
                                          "claim_processing_days", "program_year")},
    }


def flagged():
    rows = []
    for f in RESULTS["flagged"]:
        rows.append({
            "id": f["record_id"], "t": "c" if f["record_type"] == "claim" else "s",
            "m": f["member_id"], "n": f["member_name"],
            "p": f["paid_cents"], "e": f["earned_cents"], "d": f["delta_cents"],
            "k": f["classes"], "pk": f["primary"],
            "ev": [f["evidence"][str(k)] for k in f["classes"]],
        })
    return rows


# ---------------------------------------------------------------- tiny markdown

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def render_md(md):
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        m = re.match(r"^(#{1,4}) (.*)", ln)
        if m:
            lvl = len(m.group(1))
            text = m.group(2)
            slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h{lvl} id="{slug}">{inline(text)}</h{lvl}>')
            i += 1
            continue
        if ln.strip() == "---":
            out.append("<hr>")
            i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            t = ["<div class=\"table-wrap\"><table><thead><tr>"] + [f"<th>{inline(c)}</th>" for c in head] + ["</tr></thead><tbody>"]
            for r in body:
                t += ["<tr>"] + [f"<td>{inline(c)}</td>" for c in r] + ["</tr>"]
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> "))
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(buf))}</p></blockquote>")
            continue
        if re.match(r"^(- |\d+\. )", ln):
            ordered = bool(re.match(r"^\d+\. ", ln))
            items = []
            while i < len(lines) and (re.match(r"^(- |\d+\. )", lines[i]) or lines[i].startswith("  ")):
                if lines[i].startswith("  ") and items:
                    items[-1] += " " + lines[i].strip()
                else:
                    items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||>|- |\d+\. |---)", lines[i]):
            buf.append(lines[i])
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)


def main():
    dump(WEB / "src" / "lib" / "data" / "summary.json", summary())
    dump(WEB / "static" / "data" / "flagged.json", flagged())
    md = (ROOT / "rules" / "galewick-program-rules.md").read_text(encoding="utf-8")
    (WEB / "src" / "lib" / "data" / "rules.html").write_text(render_md(md) + "\n", encoding="utf-8", newline="\n")
    rules_dir = WEB / "static" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "rules" / "galewick-program-rules.md", rules_dir / "galewick-program-rules.md")
    print("site data written")


if __name__ == "__main__":
    main()
