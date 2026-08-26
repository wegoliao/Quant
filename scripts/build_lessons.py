"""Turn the lesson markdown into artifacts an AI can actually swallow.

Three audiences, three shapes:

* An AI given a single URL -> ``lesson/<ai>/ALL.md``, everything concatenated,
  one fetch, no crawling.
* An AI that crawls -> ``llms.txt`` at the root, the emerging convention, with
  raw.githubusercontent.com URLs so nothing has to be un-rendered first.
* A human, or NotebookLM pointed at a website -> real HTML pages.

The markdown subset is small on purpose: front matter, headings, fenced code,
tables, lists, quotes, rules, and inline bold/code/links. Every source file in
this repo is written by hand against that subset, so a 150-line renderer is
enough and a dependency is not.

Pure standard library.
"""

from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lesson"
SITE_ORIGIN = "https://wegoliao.github.io/Quant"
RAW_ORIGIN = "https://raw.githubusercontent.com/wegoliao/Quant/main"

TRACK_LABEL = {
    "context": "脈絡",
    "block": "積木",
    "traps": "陷阱",
    "prompts": "提問法",
    "shared": "共用",
}


# ------------------------------------------------------------------ front matter


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip("[]")
    return meta, body


# --------------------------------------------------------------------- markdown


INLINE = (
    (re.compile(r"`([^`]+)`"), lambda m: f"<code>{html.escape(m.group(1))}</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: f"<strong>{m.group(1)}</strong>"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>'),
)


def inline(text: str) -> str:
    out = html.escape(text)
    for pattern, repl in INLINE:
        out = pattern.sub(repl, out)
    return out


def render_table(rows: list[str]) -> str:
    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    head = cells(rows[0])
    aligns = ["right" if col.strip().endswith(":") else "left" for col in cells(rows[1])]
    body = [cells(line) for line in rows[2:]]
    out = ['<div class="tw"><table><thead><tr>']
    for index, cell in enumerate(head):
        out.append(f'<th style="text-align:{aligns[index]}">{inline(cell)}</th>')
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        for index, cell in enumerate(row):
            align = aligns[index] if index < len(aligns) else "left"
            out.append(f'<td style="text-align:{align}">{inline(cell)}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def markdown(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]

        if line.startswith("```"):
            lang = line[3:].strip()
            index += 1
            block: list[str] = []
            while index < len(lines) and not lines[index].startswith("```"):
                block.append(lines[index])
                index += 1
            index += 1
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(block))}</code></pre>")
            continue

        if line.startswith("|") and index + 1 < len(lines) and set(lines[index + 1]) <= set("|-: "):
            table: list[str] = []
            while index < len(lines) and lines[index].startswith("|"):
                table.append(lines[index])
                index += 1
            out.append(render_table(table))
            continue

        if re.match(r"^#{1,6} ", line):
            level = len(line) - len(line.lstrip("#"))
            out.append(f"<h{level}>{inline(line[level:].strip())}</h{level}>")
            index += 1
            continue

        if line.strip() in {"---", "***", "___"}:
            out.append("<hr>")
            index += 1
            continue

        if line.startswith("> "):
            quote: list[str] = []
            while index < len(lines) and lines[index].startswith(">"):
                quote.append(lines[index].lstrip(">").strip())
                index += 1
            out.append(f"<blockquote>{inline(' '.join(quote))}</blockquote>")
            continue

        match = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", line)
        if match:
            ordered = match.group(2).endswith(".")
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            while index < len(lines):
                item = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", lines[index])
                if not item:
                    if lines[index].strip() == "" and index + 1 < len(lines) and re.match(
                        r"^(\s*)([-*]|\d+\.)\s+", lines[index + 1]
                    ):
                        index += 1
                        continue
                    break
                items.append(f"<li>{inline(item.group(3))}</li>")
                index += 1
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue

        if line.strip() == "":
            index += 1
            continue

        para: list[str] = []
        while index < len(lines) and lines[index].strip() and not re.match(
            r"^(#{1,6} |```|\||> |\s*([-*]|\d+\.)\s)", lines[index]
        ) and lines[index].strip() not in {"---", "***", "___"}:
            para.append(lines[index].strip())
            index += 1
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")

    return "\n".join(out)
