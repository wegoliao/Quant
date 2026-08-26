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


# ------------------------------------------------------------------------ shell


SHELL = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<style>
:root{{--bg:#0d1117;--panel:#161b22;--raise:#1c2430;--ink:#e6edf3;--muted:#8b949e;
--line:#26303b;--accent:#58a6ff;--gold:#d29922;--green:#3fb950}}
:root[data-theme="light"]{{--bg:#f6f8fa;--panel:#fff;--raise:#f0f3f6;--ink:#1f2328;--muted:#59636e;
--line:#d8dee4;--accent:#0969da;--gold:#9a6700;--green:#1a7f37}}
@media (prefers-color-scheme:light){{:root:not([data-theme="dark"]){{--bg:#f6f8fa;--panel:#fff;
--raise:#f0f3f6;--ink:#1f2328;--muted:#59636e;--line:#d8dee4;--accent:#0969da;--gold:#9a6700;--green:#1a7f37}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);line-height:1.75;
font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,-apple-system,"Segoe UI",sans-serif;
-webkit-font-smoothing:antialiased}}
.wrap{{max-width:840px;margin:0 auto;padding:28px 20px 90px}}
.wide{{max-width:1080px}}
a{{color:var(--accent)}}
.crumb{{font-size:13px;color:var(--muted);margin-bottom:20px}}
.crumb a{{text-decoration:none}}
.badge{{display:inline-block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;
background:var(--raise);border:1px solid var(--line);border-radius:99px;padding:3px 11px;
color:var(--muted);margin-right:6px;font-weight:700}}
.badge.ai{{color:var(--accent);border-color:var(--accent)}}
.badge.ok{{color:var(--green);border-color:var(--green)}}
h1{{font-size:clamp(25px,4vw,36px);letter-spacing:-.02em;line-height:1.25;margin:14px 0 8px}}
h2{{font-size:22px;margin:42px 0 12px;padding-top:10px;border-top:1px solid var(--line);letter-spacing:-.01em}}
h3{{font-size:17px;margin:30px 0 8px;color:var(--ink)}}
p{{margin:0 0 15px}}
code{{background:var(--raise);padding:1.5px 6px;border-radius:5px;font-size:.87em;
font-family:ui-monospace,"Cascadia Code",Consolas,monospace}}
pre{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:15px 17px;
overflow-x:auto;margin:0 0 18px}}
pre code{{background:none;padding:0;font-size:12.7px;line-height:1.65}}
blockquote{{margin:0 0 18px;padding:12px 18px;border-left:3px solid var(--gold);
background:rgba(210,153,34,.07);border-radius:0 8px 8px 0;color:var(--ink)}}
ul,ol{{margin:0 0 16px;padding-left:23px}}
li{{margin-bottom:7px}}
hr{{border:0;border-top:1px solid var(--line);margin:34px 0}}
.tw{{overflow-x:auto;margin:0 0 18px;-webkit-overflow-scrolling:touch}}
table{{width:100%;border-collapse:collapse;font-size:14px;min-width:420px}}
th{{text-align:left;color:var(--muted);font-size:12px;letter-spacing:.04em;font-weight:700;
border-bottom:1px solid var(--line);padding:9px 10px;white-space:nowrap}}
td{{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:13px;margin:20px 0}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;
text-decoration:none;color:inherit;display:block}}
.card:hover{{border-color:var(--accent)}}
.card .id{{font-size:11px;color:var(--accent);font-weight:800;letter-spacing:.08em}}
.card .t{{font-size:15.5px;font-weight:650;margin:5px 0 6px;line-height:1.4}}
.card .d{{font-size:12.5px;color:var(--muted);line-height:1.55}}
.ingest{{background:var(--panel);border:1px solid var(--accent);border-radius:12px;padding:18px 20px;margin:24px 0}}
.ingest h3{{margin:0 0 10px;font-size:15px;color:var(--accent)}}
.ingest p{{font-size:13.5px;margin-bottom:9px}}
.ingest code{{word-break:break-all}}
footer{{margin-top:52px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:12.5px}}
</style>
</head>
<body><div class="wrap{wide}">
{crumb}
{body}
<footer>{footer}</footer>
</div></body>
</html>
"""


def page(title, description, body, crumb="", wide=False, footer="") -> str:
    return SHELL.format(
        title=html.escape(title),
        description=html.escape(description),
        body=body,
        crumb=crumb,
        wide=" wide" if wide else "",
        footer=footer,
    )


# -------------------------------------------------------------------- discovery


def collect() -> list[dict]:
    docs: list[dict] = []
    for path in sorted(LESSON.rglob("*.md")):
        if path.name == "ALL.md":
            continue  # generated bundle; never fold it back into itself
        meta, body = split_front_matter(path.read_text(encoding="utf-8"))
        rel = path.relative_to(LESSON).as_posix()
        parts = rel.split("/")
        docs.append(
            {
                "path": rel,
                "dir": parts[0] if len(parts) > 1 else "",
                "depth": rel.count("/"),
                "id": meta.get("id", path.stem),
                "title": meta.get("title", path.stem),
                "author_ai": meta.get("author_ai", "—"),
                "track": meta.get("track", "context"),
                "status": meta.get("status", "draft"),
                "verified_by": meta.get("verified_by", ""),
                "updated": meta.get("updated", ""),
                "body": body,
                "html_path": rel[:-3] + ".html",
                "site_url": f"{SITE_ORIGIN}/lesson/{rel[:-3]}.html",
                "raw_url": f"{RAW_ORIGIN}/lesson/{rel}",
            }
        )
    return docs


def subtitle(doc: dict) -> str:
    for line in doc["body"].split("\n"):
        stripped = line.strip().lstrip("*").strip()
        if stripped and not stripped.startswith(("#", "|", "[", "-", ">", "`")):
            return stripped[:120]
    return ""


def author_of(group: list[dict], fallback: str) -> str:
    for doc in group:
        if doc["author_ai"] not in {"—", ""}:
            return doc["author_ai"]
    return fallback


# ------------------------------------------------------------------------ build


def build() -> dict:
    docs = collect()
    if not docs:
        raise SystemExit("no lesson markdown found")

    root_docs = [d for d in docs if d["dir"] == ""]
    by_dir: dict[str, list[dict]] = {}
    for doc in docs:
        if doc["dir"]:
            by_dir.setdefault(doc["dir"], []).append(doc)

    # 1. one HTML page per markdown file -- every directory, same treatment.
    #    INDEX.md is skipped: it becomes lesson/index.html in step 3. Emitting
    #    INDEX.html too would collide with it on a case-insensitive filesystem,
    #    and the survivor is the one Pages does NOT serve for a directory URL.
    for doc in docs:
        if doc["path"] == "INDEX.md":
            continue
        up = "../" * doc["depth"]
        trail = f' / {html.escape(doc["dir"])}' if doc["dir"] else ""
        crumb = (
            f'<div class="crumb"><a href="{up}../index.html">Quant</a>'
            f' / <a href="{up}index.html">lesson</a>{trail} / {html.escape(doc["id"])}</div>'
        )
        badges = (
            f'<span class="badge ai">{html.escape(doc["author_ai"])}</span>'
            f'<span class="badge">{html.escape(TRACK_LABEL.get(doc["track"], doc["track"]))}</span>'
            f'<span class="badge {"ok" if doc["status"] == "verified" else ""}">'
            f'{html.escape(doc["status"])}</span>'
        )
        verified = (
            f'<p class="crumb">驗證：<code>{html.escape(doc["verified_by"])}</code></p>'
            if doc["verified_by"]
            else ""
        )
        footer = (
            f'原始 Markdown：<a href="{doc["raw_url"]}">{doc["path"]}</a> · '
            f'作者 AI：{html.escape(doc["author_ai"])}'
            + (f' · 更新 {html.escape(doc["updated"])}' if doc["updated"] else "")
        )
        target = LESSON / doc["html_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            page(
                f'{doc["id"]} · {doc["title"]}',
                subtitle(doc),
                badges + verified + markdown(doc["body"]),
                crumb,
                wide=doc["path"] in {"INDEX.md", "README.md"},
                footer=footer,
            ),
            encoding="utf-8",
            newline="\n",
        )

    # 2. per-directory bundle + index (skip nothing; _shared gets one too)
    for name, group in sorted(by_dir.items()):
        author = author_of(group, name)
        bundle = [
            f"# lesson/{name} · 完整合輯",
            "",
            f"作者 AI：**{author}**　·　檔案 {len(group)} 份　·　產生於 {date.today().isoformat()}",
            "",
            "這份檔案把整個目錄串成一份，給只能吃一個 URL 的 AI 用。",
            "每一節開頭的 `## [id] title` 對應一個獨立檔案，可以單獨抽走使用。",
            "",
            "---",
            "",
        ]
        for doc in group:
            bundle += [
                f"## [{doc['id']}] {doc['title']}",
                "",
                f"*track: {doc['track']} · status: {doc['status']}"
                + (f" · verified_by: {doc['verified_by']}" if doc["verified_by"] else "")
                + f" · source: lesson/{doc['path']}*",
                "",
                doc["body"].strip(),
                "",
                "---",
                "",
            ]
        (LESSON / name / "ALL.md").write_text(
            "\n".join(bundle), encoding="utf-8", newline="\n"
        )
        # a web-readable twin of the bundle: one URL, whole directory
        (LESSON / name / "ALL.html").write_text(
            page(
                f"lesson / {name} · 完整合輯",
                f"{author} 撰寫的全部內容，串成單一頁面供 NotebookLM 或 AI 一次讀取。",
                markdown("\n".join(bundle)),
                f'<div class="crumb"><a href="../../index.html">Quant</a> / '
                f'<a href="../index.html">lesson</a> / '
                f'<a href="index.html">{html.escape(name)}</a> / 合輯</div>',
                footer=f'Markdown 版：<a href="{RAW_ORIGIN}/lesson/{name}/ALL.md">ALL.md</a>',
            ),
            encoding="utf-8",
            newline="\n",
        )

        cards = "".join(
            f'<a class="card" href="{d["path"].split("/", 1)[1][:-3]}.html">'
            f'<div class="id">{html.escape(d["id"])} · '
            f'{html.escape(TRACK_LABEL.get(d["track"], d["track"]))}</div>'
            f'<div class="t">{html.escape(d["title"])}</div>'
            f'<div class="d">{html.escape(subtitle(d))}</div></a>'
            for d in group
        )
        ingest = (
            '<div class="ingest"><h3>丟給 AI / NotebookLM</h3>'
            f"<p>整個目錄一份檔案（推薦，一次吃完）：<br>"
            f"<code>{RAW_ORIGIN}/lesson/{name}/ALL.md</code></p>"
            f"<p>網頁版索引：<br><code>{SITE_ORIGIN}/lesson/{name}/</code></p>"
            f"<p>全站機器可讀清單：<br><code>{SITE_ORIGIN}/llms.txt</code></p></div>"
        )
        blocks = sum(1 for d in group if d["track"] == "block")
        (LESSON / name / "index.html").write_text(
            page(
                f"lesson / {name}",
                f"{author} 撰寫的量化系統教學：積木、陷阱、提問法。",
                f'<span class="badge ai">{html.escape(author)}</span>'
                f"<h1>lesson / {html.escape(name)}</h1>"
                f"<p>由 <b>{html.escape(author)}</b> 撰寫，共 {len(group)} 份"
                + (f"，其中 {blocks} 個可獨立抽用的積木" if blocks else "")
                + "。</p>" + ingest + f'<div class="grid">{cards}</div>',
                f'<div class="crumb"><a href="../../index.html">Quant</a> / '
                f'<a href="../index.html">lesson</a> / {html.escape(name)}</div>',
                wide=True,
                footer=f'完整 Markdown：<a href="{RAW_ORIGIN}/lesson/{name}/ALL.md">ALL.md</a>',
            ),
            encoding="utf-8",
            newline="\n",
        )

    # 3. lesson hub -- INDEX.md is hand-written, so render it and append a
    #    generated catalog underneath. The narrative stays human; the roster
    #    stays correct.
    hub = next((d for d in root_docs if d["path"] == "INDEX.md"), None)
    dir_cards = "".join(
        f'<a class="card" href="{name}/index.html">'
        f'<div class="id">{html.escape(name)}</div>'
        f'<div class="t">{html.escape(author_of(group, name))}</div>'
        f'<div class="d">{len(group)} 份'
        + (f" · {sum(1 for d in group if d['track'] == 'block')} 個積木" if any(
            d["track"] == "block" for d in group) else "")
        + "</div></a>"
        for name, group in sorted(by_dir.items())
    )
    catalog = (
        "<h2>目錄現況（自動產生）</h2>"
        "<p>下面這份清單由建置程序掃描實際檔案產生，不會和上面的手寫導覽一起腐爛。</p>"
        f'<div class="grid">{dir_cards}</div>'
        '<div class="ingest"><h3>丟給 AI / NotebookLM</h3>'
        f"<p>全站機器可讀索引：<br><code>{SITE_ORIGIN}/llms.txt</code></p>"
        f"<p>結構化清單：<br><code>{SITE_ORIGIN}/lesson/MANIFEST.json</code></p>"
        "<p>各 AI 的單檔合輯：<br>"
        + "<br>".join(
            f"<code>{RAW_ORIGIN}/lesson/{name}/ALL.md</code>" for name in sorted(by_dir)
        )
        + "</p></div>"
    )
    hub_body = (markdown(hub["body"]) if hub else "<h1>lesson</h1>") + catalog
    (LESSON / "index.html").write_text(
        page(
            "lesson · 跨 AI 量化系統課程",
            "Gemini、Claude、Codex 各自寫下的台股量化系統教學與可獨立抽用的積木庫。",
            hub_body,
            '<div class="crumb"><a href="../index.html">Quant</a> / lesson</div>',
            wide=True,
            footer=f'原始 Markdown：<a href="{RAW_ORIGIN}/lesson/INDEX.md">INDEX.md</a>',
        ),
        encoding="utf-8",
        newline="\n",
    )

    # 4. llms.txt -- the machine entry point
    lines = [
        "# Quant · lesson",
        "",
        "> 台股四策略量化系統的拆解教學。每個 AI 一個目錄，各自寫下驗證過的積木、",
        "> 踩過的陷阱、以及有效的提問法。純技術教學，不含投資建議、不含買賣訊號。",
        "",
        "來源系統: https://github.com/wegoliao/performance-accumulation-dashboard",
        "公開儀表板: https://wegoliao.github.io/performance-accumulation-dashboard/",
        f"結構化索引: {SITE_ORIGIN}/lesson/MANIFEST.json",
        "",
        "## 建議吃法",
        "",
        "只想吃一份：挑一個目錄的 ALL.md。想吃全部：把每個 ALL.md 都加進來。",
        "",
    ]
    for name, group in sorted(by_dir.items()):
        lines.append(f"## lesson/{name} — {author_of(group, name)}")
        lines.append("")
        lines.append(f"- [整份合輯（推薦）]({RAW_ORIGIN}/lesson/{name}/ALL.md)")
        for doc in group:
            lines.append(
                f"- [{doc['id']} {doc['title']}]({doc['raw_url']}): "
                f"{TRACK_LABEL.get(doc['track'], doc['track'])} · {doc['status']}"
            )
        lines.append("")
    if root_docs:
        lines.append("## 站台文件")
        lines.append("")
        for doc in root_docs:
            lines.append(f"- [{doc['title']}]({doc['raw_url']})")
        lines.append("")
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8", newline="\n")

    # 5. MANIFEST.json
    manifest = {
        "name": "Quant lesson",
        "generated": date.today().isoformat(),
        "site": SITE_ORIGIN,
        "raw": RAW_ORIGIN,
        "source_system": "https://github.com/wegoliao/performance-accumulation-dashboard",
        "disclaimer": "技術教學文件，不含投資建議、不含買賣訊號、不含委託路徑。",
        "directories": [
            {
                "dir": name,
                "author_ai": author_of(group, name),
                "bundle": f"{RAW_ORIGIN}/lesson/{name}/ALL.md",
                "index": f"{SITE_ORIGIN}/lesson/{name}/",
                "documents": [
                    {
                        "id": d["id"],
                        "title": d["title"],
                        "track": d["track"],
                        "status": d["status"],
                        "verified_by": d["verified_by"],
                        "updated": d["updated"],
                        "raw": d["raw_url"],
                        "html": d["site_url"],
                    }
                    for d in group
                ],
            }
            for name, group in sorted(by_dir.items())
        ],
    }
    (LESSON / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


    # 6. repo-root landing page
    ai_rows = "".join(
        f'<a class="card" href="lesson/{name}/index.html">'
        f'<div class="id">lesson / {html.escape(name)}</div>'
        f'<div class="t">{html.escape(author_of(group, name))}</div>'
        f'<div class="d">{len(group)} 份'
        + (
            f" · {sum(1 for d in group if d['track'] == 'block')} 個積木"
            if any(d["track"] == "block" for d in group)
            else ""
        )
        + "</div></a>"
        for name, group in sorted(by_dir.items())
    )
    bundles = "<br>".join(
        f"<code>{RAW_ORIGIN}/lesson/{name}/ALL.md</code>" for name in sorted(by_dir)
    )
    (ROOT / "index.html").write_text(
        page(
            "Quant · 跨 AI 量化系統課程",
            "台股四策略績效系統的拆解教學：驗證過的積木、踩過的陷阱、有效的提問法。",
            "<h1>Quant</h1>"
            "<p>台股四策略績效系統的拆解教學。每個 AI 一個目錄，各自寫下"
            "<b>驗證過的積木、踩過的陷阱、有效的提問法</b>，可以互相讀、互相補、互相挑錯。</p>"
            "<p>純技術教學文件。不含投資建議、不含買賣訊號、不含委託路徑。</p>"
            f'<div class="grid">{ai_rows}</div>'
            '<div class="ingest"><h3>丟給 AI / NotebookLM</h3>'
            f"<p>機器可讀索引：<br><code>{SITE_ORIGIN}/llms.txt</code></p>"
            f"<p>結構化清單：<br><code>{SITE_ORIGIN}/lesson/MANIFEST.json</code></p>"
            "<p>各 AI 單檔合輯（把這幾份加進 NotebookLM 就是完整知識庫）：<br>"
            f"{bundles}</p></div>"
            "<h2>來源系統</h2>"
            "<ul>"
            '<li>程式碼：<a href="https://github.com/wegoliao/performance-accumulation-dashboard">'
            "performance-accumulation-dashboard</a></li>"
            '<li>公開儀表板：<a href="https://wegoliao.github.io/performance-accumulation-dashboard/">'
            "四策略實際績效</a></li>"
            '<li>主線二追蹤：<a href="https://wegoliao.github.io/performance-accumulation-dashboard/mainline2/">'
            "未持有訊號的分價與落點</a></li>"
            "</ul>",
            wide=True,
            footer=f'由 <code>scripts/build_lessons.py</code> 產生 · {date.today().isoformat()}',
        ),
        encoding="utf-8",
        newline="\n",
    )

    return {
        "documents": len(docs),
        "directories": sorted(by_dir),
        "blocks": sum(1 for d in docs if d["track"] == "block"),
        "by_dir": {name: len(group) for name, group in sorted(by_dir.items())},
    }


def main() -> int:
    result = build()
    print(f"SUCCESS: {result['documents']} docs, {result['blocks']} blocks")
    for name, count in result["by_dir"].items():
        print(f"  lesson/{name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
