"""Generate the static site into ../public from cekat.ai/en/features.

Usage: python scripts/gen_html.py
"""
import sys, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scrape_lib import run, CATS

ROOT = os.path.dirname(HERE)
PUB = os.path.join(ROOT, "public")
os.makedirs(os.path.join(PUB, "features"), exist_ok=True)
os.makedirs(os.path.join(PUB, "assets"), exist_ok=True)
e = html.escape

CSS = """:root{--bg:#fafaf9;--card:#fff;--text:#1c1917;--muted:#57534e;--line:#e7e5e4;--accent:#0f766e}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1e1e1c;--text:#f5f5f4;--muted:#a8a29e;--line:#33312e;--accent:#2dd4bf}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.container{max-width:880px;margin:0 auto;padding:0 16px}

/* header */
.site-header{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line)}
.site-header .container{display:flex;align-items:center;justify-content:space-between;gap:16px;height:56px}
.brand{font-weight:700;color:var(--text)}
.site-nav{display:flex;gap:16px;overflow-x:auto;font-size:.9rem;white-space:nowrap}
.site-nav a{color:var(--muted)}.site-nav a:hover,.site-nav a.active{color:var(--accent)}

/* layout */
main{padding:40px 0 64px}
.hero{margin-bottom:32px}
.eyebrow{text-transform:uppercase;letter-spacing:.06em;font-size:.75rem;font-weight:600;color:var(--accent);margin:0 0 8px}
h1{font-size:2rem;line-height:1.2;margin:0 0 8px}
.lead{color:var(--muted);margin:0}
.section{margin-top:40px;scroll-margin-top:72px}
.section-title{font-size:1.3rem;margin:0 0 14px;display:flex;align-items:baseline;gap:8px}
.count{font-size:.85rem;font-weight:400;color:var(--muted)}
.breadcrumb{font-size:.85rem;color:var(--muted);margin-bottom:20px}

/* cards */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;color:var(--text)}
.card:hover{border-color:var(--accent);text-decoration:none}
.card-title{display:block;font-weight:600;margin-bottom:4px}
.card-text{display:block;color:var(--muted);font-size:.9rem;line-height:1.45}

/* feature page */
.intro{font-size:1.05rem;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:8px;padding:14px 16px;margin:0}
.items{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.items li{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 16px}
.items h3{font-size:1rem;margin:0 0 4px}.items p{margin:0;color:var(--muted)}
details{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 16px;margin-bottom:8px}
summary{cursor:pointer;font-weight:600}details p{margin:8px 0 2px;color:var(--muted)}
.source{margin-top:32px;font-size:.9rem;color:var(--muted);word-break:break-all}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:32px}
.pager a{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;font-size:.9rem}
.pager .next{text-align:right;grid-column:2}
.pager small{display:block;color:var(--muted)}

.site-footer{border-top:1px solid var(--line);padding:20px 0;font-size:.85rem;color:var(--muted)}"""
open(os.path.join(PUB, "assets", "style.css"), "w", encoding="utf-8").write(CSS)


ACTIVE = ' class="active"'


def slug_cat(c): return c.lower().replace(" & ", "-").replace(" ", "-")


def layout(title, body, active=None, description=""):
    nav = "".join(
        f'<a href="/#{slug_cat(c)}"{ACTIVE if c == active else ""}>{e(c)}</a>' for c, _ in CATS)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a class="brand" href="/">Cekat.AI Features</a>
      <nav class="site-nav">{nav}</nav>
    </div>
  </header>
  <main class="container">
{body}
  </main>
  <footer class="site-footer">
    <div class="container">Content summarized from <a href="https://cekat.ai/en/features">cekat.ai/en/features</a>.</div>
  </footer>
</body>
</html>
"""


def short(title): return title.split(",")[0].split(":")[0].strip()


res = run()
order = [s for _, g in CATS for s in g.split()]
cat_of = {s: c for c, g in CATS for s in g.split()}

# ---- index ----
b = ['    <section class="hero">',
     '      <p class="eyebrow">Feature overview</p>',
     '      <h1>Cekat.AI Features</h1>',
     f'      <p class="lead">All {len(order)} features, grouped by category. Open a feature for its full explanation.</p>',
     '    </section>']
for cat, g in CATS:
    sl = g.split()
    b.append(f'    <section class="section" id="{slug_cat(cat)}">')
    b.append(f'      <h2 class="section-title">{e(cat)} <span class="count">{len(sl)} features</span></h2>')
    b.append('      <div class="grid">')
    for s in sl:
        b.append(f'        <a class="card" href="/features/{s}"><span class="card-title">{e(short(res[s][2]))}</span>'
                 f'<span class="card-text">{e(res[s][3])}</span></a>')
    b.append('      </div>\n    </section>')
open(os.path.join(PUB, "index.html"), "w", encoding="utf-8").write(
    layout("Cekat.AI Features", "\n".join(b), description="All Cekat.AI features with detailed explanations."))

# ---- feature pages ----
for i, s in enumerate(order):
    _, url, title, h1, intro, sections, faqs = res[s]
    cat = cat_of[s]
    b = [f'    <nav class="breadcrumb"><a href="/">All features</a> / <a href="/#{slug_cat(cat)}">{e(cat)}</a> / {e(short(title))}</nav>',
         '    <section class="hero">',
         f'      <p class="eyebrow">{e(cat)}</p>',
         f'      <h1>{e(title)}</h1>',
         f'      <p class="lead">{e(h1)}</p>',
         '    </section>']
    if intro:
        b.append(f'    <p class="intro">{e(intro)}</p>')
    for h2, items in sections.items():
        b.append(f'    <section class="section">\n      <h2 class="section-title">{e(h2)}</h2>\n      <ul class="items">')
        b += [f'        <li><h3>{e(n)}</h3><p>{e(p)}</p></li>' for n, p in items]
        b.append('      </ul>\n    </section>')
    if faqs:
        b.append('    <section class="section">\n      <h2 class="section-title">FAQ</h2>')
        b += [f'      <details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faqs]
        b.append('    </section>')
    b.append(f'    <p class="source">Source: <a href="{url}">{e(url)}</a></p>')
    pager = ['    <nav class="pager">']
    if i:
        p = order[i - 1]
        pager.append(f'      <a class="prev" href="/features/{p}"><small>&larr; Previous</small>{e(short(res[p][2]))}</a>')
    if i + 1 < len(order):
        n = order[i + 1]
        pager.append(f'      <a class="next" href="/features/{n}"><small>Next &rarr;</small>{e(short(res[n][2]))}</a>')
    pager.append('    </nav>')
    b += pager
    open(os.path.join(PUB, "features", f"{s}.html"), "w", encoding="utf-8").write(
        layout(f"{short(title)} | Cekat.AI Features", "\n".join(b), active=cat, description=intro[:160]))

print("wrote", len(order) + 1, "pages to", PUB)
