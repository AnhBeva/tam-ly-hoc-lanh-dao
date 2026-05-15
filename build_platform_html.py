#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.strip().lower())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("đ", "d")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "section"


def inline_markdown(value: str) -> str:
    value = html.escape(value)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', value)
    return value


def close_blocks(out: list[str], state: dict[str, bool]) -> None:
    if state.get("list"):
        out.append("</ul>")
        state["list"] = False
    if state.get("table"):
        out.append("</table></div>")
        state["table"] = False


def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    state = {"code": False, "list": False, "table": False, "table_header": False}

    for raw in lines:
        line = raw.rstrip()

        if line.startswith("```"):
            if state["code"]:
                out.append("</code></pre>")
                state["code"] = False
            else:
                close_blocks(out, state)
                out.append("<pre><code>")
                state["code"] = True
            continue

        if state["code"]:
            out.append(html.escape(line) + "\n")
            continue

        if not line.strip():
            close_blocks(out, state)
            continue

        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r"[-: ]*", c) for c in cells):
                state["table_header"] = False
                continue
            if not state["table"]:
                close_blocks(out, state)
                out.append("<div class=\"table-wrap\"><table>")
                state["table"] = True
                state["table_header"] = True
            tag = "th" if state["table_header"] else "td"
            out.append("<tr>" + "".join(f"<{tag}>{inline_markdown(c)}</{tag}>" for c in cells) + "</tr>")
            state["table_header"] = False
            continue

        if line.startswith("- "):
            if state["table"]:
                out.append("</table></div>")
                state["table"] = False
            if not state["list"]:
                out.append("<ul>")
                state["list"] = True
            out.append(f"<li>{inline_markdown(line[2:].strip())}</li>")
            continue

        close_blocks(out, state)

        if line.startswith("# "):
            title = line[2:].strip()
            out.append(f"<h1 id=\"{slugify(title)}\">{inline_markdown(title)}</h1>")
        elif line.startswith("## "):
            title = line[3:].strip()
            out.append(f"<h2 id=\"{slugify(title)}\">{inline_markdown(title)}</h2>")
        elif line.startswith("### "):
            title = line[4:].strip()
            out.append(f"<h3 id=\"{slugify(title)}\">{inline_markdown(title)}</h3>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline_markdown(line[2:].strip())}</blockquote>")
        elif line == "---":
            out.append("<hr>")
        else:
            out.append(f"<p>{inline_markdown(line)}</p>")

    if state["code"]:
        out.append("</code></pre>")
    close_blocks(out, state)
    return "\n".join(out)


def first_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def collect_documents() -> list[Path]:
    ordered: list[Path] = []
    for pattern in ["README.md", "ban-do*.md", "giao-trinh*.md", "thuat-ngu*.md", "glossary.md"]:
        for path in sorted(ROOT.glob(pattern)):
            if path.exists() and path not in ordered:
                ordered.append(path)
    ordered.extend(sorted(ROOT.glob("Module-*.md")))
    return ordered


docs = collect_documents()
if not docs:
    raise SystemExit("No Markdown source files found.")

title = first_heading(ROOT / "README.md") if (ROOT / "README.md").exists() else "Nền tảng kiến thức"
modules = [p for p in docs if p.name.startswith("Module-")]
nav_items = [(path.stem, first_heading(path)) for path in docs]

sections = []
for path in docs:
    sections.append(
        f"<section class=\"lesson\" id=\"{path.stem}\">"
        f"<div class=\"source-label\">{html.escape(path.name)}</div>"
        + markdown_to_html(path.read_text(encoding="utf-8"))
        + "</section>"
    )

nav_html = "\n".join(
    f"<a href=\"#{html.escape(anchor)}\"><span>{i:02d}</span>{html.escape(label)}</a>"
    for i, (anchor, label) in enumerate(nav_items, start=1)
)

doc = f'''<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f5f5f7;
      --panel: rgba(255,255,255,.86);
      --text: #1d1d1f;
      --muted: #6e6e73;
      --line: #d8d8de;
      --accent: #0071e3;
      --accent-2: #34c759;
      --code: #f0f2f5;
      color-scheme: light;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
      color: var(--text);
      background: linear-gradient(180deg, #fbfbfd 0%, var(--bg) 42rem);
      line-height: 1.62;
    }}
    .hero {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 72px 24px 34px;
    }}
    .eyebrow {{
      color: var(--accent);
      font-weight: 700;
      letter-spacing: 0;
      margin-bottom: 12px;
    }}
    h1, h2, h3 {{ letter-spacing: 0; line-height: 1.12; }}
    .hero h1 {{
      max-width: 920px;
      margin: 0;
      font-size: 4.6rem;
      line-height: .98;
    }}
    .hero p {{
      max-width: 760px;
      color: var(--muted);
      font-size: 1.22rem;
      margin: 22px 0 0;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      max-width: 720px;
      margin-top: 32px;
    }}
    .stat {{
      background: var(--panel);
      border: 1px solid rgba(0,0,0,.08);
      border-radius: 8px;
      padding: 18px;
    }}
    .stat strong {{ display: block; font-size: 1.8rem; line-height: 1; }}
    .stat span {{ color: var(--muted); font-size: .92rem; }}
    .shell {{
      display: grid;
      grid-template-columns: 290px minmax(0, 1fr);
      gap: 28px;
      max-width: 1180px;
      margin: 0 auto;
      padding: 22px 24px 80px;
    }}
    nav {{
      position: sticky;
      top: 18px;
      align-self: start;
      max-height: calc(100vh - 36px);
      overflow: auto;
      padding: 10px;
      border: 1px solid rgba(0,0,0,.08);
      border-radius: 8px;
      background: var(--panel);
    }}
    nav a {{
      display: grid;
      grid-template-columns: 34px 1fr;
      gap: 10px;
      align-items: start;
      padding: 10px;
      color: var(--text);
      text-decoration: none;
      border-radius: 8px;
      font-size: .94rem;
    }}
    nav a:hover {{ background: rgba(0,113,227,.08); }}
    nav span {{
      color: var(--muted);
      font-variant-numeric: tabular-nums;
    }}
    main {{ min-width: 0; }}
    .lesson {{
      margin-bottom: 22px;
      padding: 34px 0;
      border-top: 1px solid var(--line);
    }}
    .source-label {{
      display: inline-flex;
      margin-bottom: 12px;
      padding: 5px 10px;
      border-radius: 8px;
      background: #eef5ff;
      color: #0057b8;
      font-size: .82rem;
      font-weight: 650;
    }}
    .lesson h1 {{ font-size: 2.65rem; margin: 0 0 18px; }}
    .lesson h2 {{ font-size: 1.65rem; margin-top: 38px; padding-top: 8px; }}
    .lesson h3 {{ font-size: 1.18rem; margin-top: 28px; }}
    p, li {{ font-size: 1rem; }}
    p {{ margin: 12px 0; }}
    ul {{ padding-left: 1.25rem; }}
    strong {{ font-weight: 760; }}
    blockquote {{
      margin: 18px 0;
      padding: 16px 18px;
      border-left: 4px solid var(--accent);
      background: #f3f8ff;
      border-radius: 8px;
      color: #24415f;
    }}
    .table-wrap {{ width: 100%; overflow-x: auto; margin: 18px 0; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 620px;
      background: #fff;
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 12px 13px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #f6f8fb; font-weight: 720; }}
    pre {{
      overflow: auto;
      padding: 16px;
      background: var(--code);
      border-radius: 8px;
      border: 1px solid #dfe3ea;
    }}
    a {{ color: var(--accent); text-decoration-thickness: .08em; text-underline-offset: .18em; }}
    code {{ font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace; font-size: .92em; }}
    hr {{ border: 0; border-top: 1px solid var(--line); margin: 28px 0; }}
    @media (max-width: 860px) {{
      .hero {{ padding-top: 46px; }}
      .hero h1 {{ font-size: 2.45rem; }}
      .stats {{ grid-template-columns: 1fr; }}
      .shell {{ grid-template-columns: 1fr; padding-inline: 14px; }}
      nav {{ position: relative; top: 0; max-height: 360px; }}
      .lesson {{ padding: 24px 0; }}
      .lesson h1 {{ font-size: 2rem; }}
    }}
    @media print {{
      body {{ background: #fff; }}
      nav, .stats, .source-label {{ display: none; }}
      .shell {{ display: block; padding: 0; }}
      .lesson {{ box-shadow: none; border: 0; page-break-after: always; }}
    }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="eyebrow">Nền tảng học tập</div>
    <h1>{html.escape(title)}</h1>
    <p>Một hệ thống học tập có cấu trúc, đi từ nền tảng, first principles, công cụ thực hành đến tài liệu tra cứu dễ đọc.</p>
    <div class="stats">
      <div class="stat"><strong>{len(modules)}</strong><span>module</span></div>
      <div class="stat"><strong>{len(docs)}</strong><span>tài liệu nguồn</span></div>
      <div class="stat"><strong>HTML</strong><span>sẵn sàng cho GitHub Pages</span></div>
    </div>
  </header>
  <div class="shell">
    <nav aria-label="Điều hướng giáo trình">
      {nav_html}
    </nav>
    <main>
      {''.join(sections)}
    </main>
  </div>
</body>
</html>
'''

(ROOT / "index.html").write_text(doc, encoding="utf-8")
print(f"Wrote {ROOT / 'index.html'}")
