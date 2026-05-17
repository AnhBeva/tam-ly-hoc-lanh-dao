#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOGO_REL = "assets/lumi-logo-2022.png"
LOGO_PATH = ROOT / LOGO_REL


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


def module_number(path: Path) -> int | None:
    match = re.match(r"Module-(\d{2})-", path.name)
    return int(match.group(1)) if match else None


def module_visual(path: Path) -> str:
    number = module_number(path)
    if number is None:
        return ""
    image_rel = f"assets/module-visuals/module-{number:02d}.jpg"
    image_path = ROOT / image_rel
    if not image_path.exists():
        return ""
    label = first_heading(path)
    return (
        '<figure class="module-visual">'
        f'<img src="{image_rel}" alt="Hình ảnh trực quan cho {html.escape(label)}" loading="lazy">'
        f'<figcaption>Trực quan hóa: {html.escape(label)}</figcaption>'
        '</figure>'
    )


def collect_documents() -> list[Path]:
    ordered: list[Path] = []
    for pattern in ["README.md", "ban-do*.md", "giao-trinh*.md", "thuat-ngu*.md", "cong-cu*.md", "glossary.md"]:
        for path in sorted(ROOT.glob(pattern)):
            if path.exists() and path not in ordered:
                ordered.append(path)
    ordered.extend(sorted(ROOT.glob("Module-*.md")))
    return ordered


docs = collect_documents()
if not docs:
    raise SystemExit("No Markdown source files found.")
if not LOGO_PATH.exists():
    raise SystemExit(f"Missing Lumi logo asset: {LOGO_PATH}")

title = first_heading(ROOT / "README.md") if (ROOT / "README.md").exists() else "Nền tảng kiến thức"
modules = [p for p in docs if p.name.startswith("Module-")]
nav_items = [(path.stem, first_heading(path)) for path in docs]

sections = []
for path in docs:
    sections.append(
        f"<section class=\"lesson\" id=\"{path.stem}\">"
        f"<div class=\"source-label\">{html.escape(path.name)}</div>"
        + module_visual(path)
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
      --lumi-green: #008B51;
      --lumi-green-deep: #006B3F;
      --lumi-mint: #E6F4EE;
      --lumi-pale: #F3FAF6;
      --text: #1F2933;
      --muted: #4B5563;
      --line: #DDE5E1;
      --surface: #FFFFFF;
      --code: #F3F7F5;
      --warning: #FFF7E6;
      color-scheme: light;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: Arial, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        linear-gradient(90deg, rgba(0,139,81,.06) 1px, transparent 1px),
        linear-gradient(180deg, #ffffff 0%, var(--lumi-pale) 34rem, #ffffff 70rem);
      background-size: 44px 44px, auto;
      line-height: 1.62;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 20;
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,.96);
    }}
    .topbar-inner {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 18px;
      min-width: 0;
    }}
    .brand-logo {{
      display: block;
      height: 42px;
      width: auto;
      object-fit: contain;
      flex: 0 0 auto;
    }}
    .brand-text {{
      display: grid;
      gap: 2px;
      min-width: 0;
    }}
    .brand-kicker {{
      color: var(--lumi-green);
      font-size: .78rem;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .brand-name {{
      color: var(--text);
      font-size: .96rem;
      font-weight: 700;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 44vw;
    }}
    .topbar-meta {{
      color: var(--muted);
      font-size: .88rem;
      white-space: nowrap;
    }}
    .hero {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 56px 24px 28px;
    }}
    .eyebrow {{
      color: var(--lumi-green);
      font-weight: 700;
      letter-spacing: 0;
      margin-bottom: 12px;
    }}
    h1, h2, h3 {{ letter-spacing: 0; line-height: 1.12; }}
    .hero h1 {{
      max-width: 980px;
      margin: 0;
      font-size: 4.1rem;
      line-height: 1.02;
    }}
    .hero p {{
      max-width: 820px;
      color: var(--muted);
      font-size: 1.18rem;
      margin: 22px 0 0;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
      gap: 28px;
      align-items: end;
    }}
    .promise-panel {{
      border: 1px solid var(--line);
      background: var(--surface);
      border-radius: 8px;
      padding: 20px;
    }}
    .promise-panel strong {{
      display: block;
      color: var(--lumi-green-deep);
      margin-bottom: 8px;
    }}
    .promise-panel p {{
      margin: 0;
      font-size: .96rem;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 32px;
    }}
    .stat {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .stat strong {{ display: block; font-size: 1.75rem; line-height: 1; color: var(--lumi-green-deep); }}
    .stat span {{ color: var(--muted); font-size: .92rem; }}
    .shell {{
      display: grid;
      grid-template-columns: 310px minmax(0, 1fr);
      gap: 34px;
      max-width: 1180px;
      margin: 0 auto;
      padding: 22px 24px 80px;
    }}
    nav {{
      position: sticky;
      top: 86px;
      align-self: start;
      max-height: calc(100vh - 104px);
      overflow: auto;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
    }}
    .nav-title {{
      padding: 10px 10px 8px;
      color: var(--lumi-green-deep);
      font-size: .82rem;
      font-weight: 700;
      text-transform: uppercase;
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
    nav a:hover {{ background: var(--lumi-mint); }}
    nav span {{
      color: var(--lumi-green);
      font-variant-numeric: tabular-nums;
    }}
    main {{ min-width: 0; }}
    .lesson {{
      margin-bottom: 22px;
      padding: 34px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,.96);
      border-radius: 8px;
    }}
    .source-label {{
      display: inline-flex;
      margin-bottom: 12px;
      padding: 5px 10px;
      border-radius: 8px;
      background: var(--lumi-mint);
      color: var(--lumi-green-deep);
      font-size: .82rem;
      font-weight: 650;
    }}
    .module-visual {{
      margin: 4px 0 26px;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: var(--surface);
    }}
    .module-visual img {{
      display: block;
      width: 100%;
      aspect-ratio: 16 / 9;
      object-fit: cover;
      object-position: center;
    }}
    .module-visual figcaption {{
      padding: 10px 14px;
      color: var(--muted);
      font-size: .88rem;
      border-top: 1px solid var(--line);
      background: var(--lumi-pale);
    }}
    .lesson h1 {{ font-size: 2.65rem; margin: 0 0 18px; }}
    .lesson h2 {{
      font-size: 1.55rem;
      margin-top: 38px;
      padding-top: 8px;
      color: var(--lumi-green-deep);
    }}
    .lesson h3 {{ font-size: 1.18rem; margin-top: 28px; }}
    p, li {{ font-size: 1rem; }}
    p {{ margin: 12px 0; }}
    ul {{ padding-left: 1.25rem; }}
    strong {{ font-weight: 760; }}
    blockquote {{
      margin: 18px 0;
      padding: 16px 18px;
      border-left: 4px solid var(--lumi-green);
      background: var(--lumi-mint);
      border-radius: 8px;
      color: var(--text);
    }}
    .table-wrap {{ width: 100%; overflow-x: auto; margin: 18px 0; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 620px;
      background: var(--surface);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 12px 13px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: var(--lumi-pale); font-weight: 720; color: var(--lumi-green-deep); }}
    pre {{
      overflow: auto;
      padding: 16px;
      background: var(--code);
      border-radius: 8px;
      border: 1px solid var(--line);
    }}
    a {{ color: var(--lumi-green); text-decoration-thickness: .08em; text-underline-offset: .18em; }}
    code {{ font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace; font-size: .92em; }}
    hr {{ border: 0; border-top: 1px solid var(--line); margin: 28px 0; }}
    .reading-note {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 0 24px 20px;
    }}
    .reading-note-inner {{
      border: 1px solid var(--line);
      border-left: 5px solid var(--lumi-green);
      background: var(--lumi-mint);
      border-radius: 8px;
      padding: 16px 18px;
      color: var(--text);
    }}
    @media (max-width: 860px) {{
      .topbar-inner {{ align-items: flex-start; }}
      .brand-logo {{ height: 34px; }}
      .brand-name {{ max-width: 62vw; white-space: normal; }}
      .topbar-meta {{ display: none; }}
      .hero {{ padding-top: 34px; }}
      .hero h1 {{ font-size: 2.45rem; }}
      .hero-grid {{ grid-template-columns: 1fr; }}
      .stats {{ grid-template-columns: 1fr; }}
      .shell {{ grid-template-columns: 1fr; padding-inline: 14px; }}
      nav {{ position: relative; top: 0; max-height: 360px; }}
      .lesson {{ padding: 24px 16px; }}
      .lesson h1 {{ font-size: 2rem; }}
      .module-visual {{ margin-bottom: 20px; }}
    }}
    @media print {{
      body {{ background: #fff; }}
      .topbar, nav, .stats, .source-label, .reading-note {{ display: none; }}
      .shell {{ display: block; padding: 0; }}
      .lesson {{ box-shadow: none; border: 0; page-break-after: always; }}
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <img class="brand-logo" src="{LOGO_REL}" alt="Lumi">
        <div class="brand-text">
          <div class="brand-kicker">Nền tảng học tập ứng dụng</div>
          <div class="brand-name">{html.escape(title)}</div>
        </div>
      </div>
      <div class="topbar-meta">Lumi learning system</div>
    </div>
  </header>
  <header class="hero">
    <div class="hero-grid">
      <div>
        <div class="eyebrow">Lumi-branded knowledge platform</div>
        <h1>{html.escape(title)}</h1>
        <p>Một hệ thống học tập sáng, kỹ thuật và có thể thực hành: đi từ vấn đề thật, cơ chế tâm lý, workflow lãnh đạo đến công cụ đo kết quả trong công việc.</p>
      </div>
      <aside class="promise-panel" aria-label="Lời hứa học tập">
        <strong>Chuẩn đầu ra</strong>
        <p>Người học biết gọi đúng vấn đề, chọn tầng can thiệp, hành động có đạo đức và đo tín hiệu sau áp dụng.</p>
      </aside>
    </div>
    <div class="stats">
      <div class="stat"><strong>{len(modules)}</strong><span>module</span></div>
      <div class="stat"><strong>{len(docs)}</strong><span>tài liệu nguồn</span></div>
      <div class="stat"><strong>#008B51</strong><span>Lumi green</span></div>
    </div>
  </header>
  <div class="reading-note">
    <div class="reading-note-inner">
      Học trực tiếp từ mục lục bên dưới. Website là HTML tĩnh, logo Lumi hiển thị bằng asset gốc, nội dung được build lại từ Markdown nguồn.
    </div>
  </div>
  <div class="shell">
    <nav aria-label="Điều hướng giáo trình">
      <div class="nav-title">Điều hướng nội dung</div>
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
