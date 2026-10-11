"""Generate the service, about and contact pages (English + Spanish) and the sitemap.

The two homepages (index.html, es/index.html) are edited by hand. This script reads
shared pieces from them (footer, icons, About and Contact sections) so every page
stays consistent, and it rewrites the homepage header so the menu matches.

Run from anywhere:  python3 _build/build.py
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from content import UI, SERVICES, PAGES, PHONE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://110pestcontrol.com"
TEL = "tel:+17863683883"
HOME = {"en": "/", "es": "/es/"}


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def write(p, s):
    full = os.path.join(ROOT, p.lstrip("/"))
    if full.endswith("/"):
        full += "index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(s)


def grab(pattern, s, flags=re.S):
    m = re.search(pattern, s, flags)
    if not m:
        raise SystemExit(f"Could not find {pattern!r} on a homepage")
    return m.group(0)


def absolute(s):
    """Homepage markup uses relative asset paths; generated pages live in subfolders."""
    return re.sub(r'(src|href)="(?:\.\./)?(images/|favicon\.ico|styles\.css)', r'\1="/\2', s)


# ---------- pieces shared with the homepages ----------
SRC = {"en": read("index.html"), "es": read("es/index.html")}
CSS_VERSION = re.search(r'styles\.css\?v=(\d+)', SRC["en"]).group(1)
DEFS = grab(r'<svg width="0" height="0".*?</svg>', SRC["en"])
PHONE_SVG = grab(r'<svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18">.*?</svg>', SRC["en"])
SCRIPTS = grab(r"<script>document\.getElementById\('year'\).*?</script>\s*<script>.*?</script>", SRC["en"])


def lang_pieces(lang):
    s = SRC[lang]
    footer = absolute(grab(r'<footer class="site-footer">.*?</footer>', s))
    icons = re.findall(r'<div class="card-icon" aria-hidden="true">.*?</div>', s, re.S)
    cards = re.findall(r'<article class="card">.*?<h3>(.*?)</h3>\s*<p>(.*?)</p>', s, re.S)
    assert len(icons) == 6 and len(cards) == 6, (lang, len(icons), len(cards))
    about = s[s.index('<section id="about"'):]
    about = about[about.index("<h2>"):about.index('<a class="btn btn-primary" href="#contact">')]
    contact = s[s.index('<section id="contact"'):]
    contact = contact[contact.index('<ul class="contact-list">'):contact.index("</form>") + len("</form>")]
    return dict(footer=footer, icons=icons, cards=cards, about=absolute(about), contact=absolute(contact))


PIECES = {l: lang_pieces(l) for l in ("en", "es")}


# ---------- urls ----------
def service_path(i, lang):
    base = PAGES["services"][lang]["path"]
    return f"{base}{SERVICES[i][lang]['slug']}/"


def page_path(key, lang):
    return PAGES[key][lang]["path"]


# ---------- layout ----------
def header(lang, other_url, home_page=False):
    t = UI[lang]
    en_url, es_url = (other_url, None) if lang == "es" else (None, other_url)
    cur = 'aria-current="page"'
    toggle = (f'<a href="{en_url or "#"}" lang="en" hreflang="en"{" " + cur if lang == "en" else ""}>EN</a>\n'
              f'      <a href="{es_url or "#"}" lang="es" hreflang="es"{" " + cur if lang == "es" else ""}>ES</a>')
    if lang == "en":
        toggle = toggle.replace('href="#" lang="en"', 'href="./" lang="en"' if home_page else 'href="#" lang="en"')
    return f'''<header class="site-header">
  <div class="wrap header-inner">
    <a href="{HOME[lang]}" class="brand" aria-label="110 Pest Control Services">
      <img src="/images/logo-mark.png" alt="" width="60" height="48">
      <span class="brand-text">
        <span class="brand-name">110 Pest</span>
        <span class="brand-sub">Control Services</span>
      </span>
    </a>
    <nav class="nav" aria-label="Main">
      <a href="{page_path('services', lang)}">{t['services']}</a>
      <a href="{page_path('about', lang)}">{t['about']}</a>
      <a href="{page_path('contact', lang)}">{t['contact']}</a>
    </nav>
    <div class="lang-toggle" role="group" aria-label="Language">
      {toggle}
    </div>
    <a class="btn btn-primary header-call" href="{TEL}">
      {PHONE_SVG}
      <span>{PHONE}</span>
    </a>
  </div>
</header>'''


def fix_toggle(h, lang, en_url, es_url):
    """Point both language links at the right pages and mark the current one."""
    h = re.sub(r'<a href="[^"]*" lang="en" hreflang="en"( aria-current="page")?>EN</a>',
               f'<a href="{en_url}" lang="en" hreflang="en"{" aria-current=\"page\"" if lang == "en" else ""}>EN</a>', h)
    h = re.sub(r'<a href="[^"]*" lang="es" hreflang="es"( aria-current="page")?>ES</a>',
               f'<a href="{es_url}" lang="es" hreflang="es"{" aria-current=\"page\"" if lang == "es" else ""}>ES</a>', h)
    return h


def page(lang, en_url, es_url, title, desc, body, jsonld=None):
    t = UI[lang]
    url = en_url if lang == "en" else es_url
    ld = f'\n  <script type="application/ld+json">\n  {json.dumps(jsonld, ensure_ascii=False)}\n  </script>' if jsonld else ""
    head_html = header(lang, None)
    head_html = fix_toggle(head_html, lang, en_url, es_url)
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="theme-color" content="#c4161c">

  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE}{url}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:image" content="{SITE}/images/og-image.jpg">

  <link rel="canonical" href="{SITE}{url}">
  <link rel="alternate" hreflang="en" href="{SITE}{en_url}">
  <link rel="alternate" hreflang="es" href="{SITE}{es_url}">
  <link rel="alternate" hreflang="x-default" href="{SITE}{en_url}">

  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="48x48" href="/images/icon-48.png">
  <link rel="icon" type="image/png" sizes="96x96" href="/images/icon-96.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/images/icon-192.png">
  <link rel="apple-touch-icon" href="/images/apple-touch-icon.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css?v={CSS_VERSION}">
  <script>document.documentElement.classList.add('js');</script>{ld}
</head>
<body>
{DEFS}

{head_html}

<main id="top">
{body}
</main>

{PIECES[lang]['footer']}

<div class="mobile-bar">
  <a href="{TEL}" class="mb-call">{t['mb_call']}</a>
  <a href="{page_path('contact', lang)}" class="mb-quote">{t['mb_quote']}</a>
</div>

{SCRIPTS}
</body>
</html>
'''


def page_hero(lang, crumbs, h1, lead, icon=""):
    t = UI[lang]
    trail = " <span>/</span> ".join(f'<a href="{u}">{n}</a>' if u else f'<span aria-current="page">{n}</span>' for n, u in crumbs)
    side = f'\n      <div class="page-hero-icon">{icon}</div>' if icon else ""
    return f'''  <section class="page-hero">
    <div class="wrap page-hero-inner">
      <div class="page-hero-copy">
        <nav class="crumbs" aria-label="Breadcrumb">{trail}</nav>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
        <div class="cta-row">
          <a class="btn btn-primary btn-lg" href="{TEL}">{t['call_now']}</a>
          <a class="btn btn-outline btn-lg" href="{page_path('contact', lang)}">{t['free_quote']}</a>
        </div>
      </div>{side}
    </div>
  </section>'''


def band(lang):
    t = UI[lang]
    return f'''      <div class="band">
        <p>{t['band']}</p>
        <a class="btn btn-light" href="{TEL}">{t['band_btn']}</a>
      </div>'''


def service_cards(lang, skip=None):
    out = []
    for i, (name, desc) in enumerate(PIECES[lang]["cards"]):
        if i == skip:
            continue
        out.append(f'''        <article class="card">
          {PIECES[lang]['icons'][i]}
          <h3>{name}</h3>
          <p>{desc}</p>
          <a class="card-more" href="{service_path(i, lang)}">{UI[lang]['learn_more']} <span aria-hidden="true">→</span></a>
        </article>''')
    return "\n".join(out)


# ---------- pages ----------
def build_service(i, lang):
    s, t = SERVICES[i][lang], UI[lang]
    icon = PIECES[lang]["icons"][i].replace('class="card-icon" aria-hidden="true"', 'aria-hidden="true"')
    crumbs = [(t["home"], HOME[lang]), (t["services"], page_path("services", lang)), (s["name"], None)]
    li = lambda items: "\n".join(f"            <li>{x}</li>" for x in items)
    steps = "\n".join(f'''          <li class="step"><span class="step-num">{n}</span><h3>{a}</h3><p>{b}</p></li>'''
                      for n, (a, b) in enumerate(t["steps"], 1))
    body = f'''{page_hero(lang, crumbs, s['h1'], s['intro'], icon)}

  <section class="section">
    <div class="wrap two-col">
      <div class="panel">
        <h2>{s.get('signs_title', t['signs'])}</h2>
        <ul class="checklist">
{li(s['signs'])}
        </ul>
      </div>
      <div class="panel">
        <h2>{s.get('tips_title', t['tips'])}</h2>
        <ul class="checklist checklist-tips">
{li(s['tips'])}
        </ul>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap">
      <p class="eyebrow">{t['how_eyebrow']}</p>
      <h2>{t['how_title']}</h2>
      <ol class="steps">
{steps}
      </ol>
{band(lang)}
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <h2>{t['other']}</h2>
      <div class="cards">
{service_cards(lang, skip=i)}
      </div>
    </div>
  </section>'''
    en, es = service_path(i, "en"), service_path(i, "es")
    ld = {"@context": "https://schema.org", "@type": "Service", "name": s["name"], "serviceType": "Pest control",
          "url": SITE + service_path(i, lang),
          "areaServed": ["Broward County, FL", "Miami-Dade County, FL", "South Florida"],
          "provider": {"@type": "HomeAndConstructionBusiness", "name": "110 Pest Control Services",
                       "telephone": "+1-786-368-3883", "url": SITE + "/"}}
    title = f"{s['h1']} | 110 Pest Control"
    desc = s["intro"].split(". ")[0].rstrip(".") + f". Free estimates. Call {PHONE}."
    write(service_path(i, lang), page(lang, en, es, title, desc, body, ld))


def build_services(lang):
    p, t = PAGES["services"][lang], UI[lang]
    crumbs = [(t["home"], HOME[lang]), (t["services"], None)]
    body = f'''{page_hero(lang, crumbs, p['h1'], p['lead'])}

  <section class="section">
    <div class="wrap">
      <div class="cards">
{service_cards(lang)}
      </div>
{band(lang)}
    </div>
  </section>'''
    write(p["path"], page(lang, PAGES["services"]["en"]["path"], PAGES["services"]["es"]["path"], p["title"], p["desc"], body))


def build_about(lang):  # unused: About lives on the homepage (#about)
    p, t = PAGES["about"][lang], UI[lang]
    crumbs = [(t["home"], HOME[lang]), (t["about"], None)]
    body = f'''{page_hero(lang, crumbs, p['h1'], p['lead'])}

  <section class="section section-alt">
    <div class="wrap about">
      <div class="about-copy">
        {PIECES[lang]['about'].strip()}
      </div>
    </div>
  </section>'''
    write(p["path"], page(lang, PAGES["about"]["en"]["path"], PAGES["about"]["es"]["path"], p["title"], p["desc"], body))


def build_contact(lang):
    p, t = PAGES["contact"][lang], UI[lang]
    crumbs = [(t["home"], HOME[lang]), (t["contact"], None)]
    body = f'''  <section class="page-hero page-hero-slim">
    <div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="{HOME[lang]}">{t['home']}</a> <span>/</span> <span aria-current="page">{t['contact']}</span></nav>
      <h1>{p['h1']}</h1>
      <p class="lead">{p['lead']}</p>
    </div>
  </section>

  <section class="section section-tight" id="contact">
    <div class="wrap contact">
      <div class="contact-info">
        {PIECES[lang]['contact']}
    </div>
  </section>'''
    write(p["path"], page(lang, PAGES["contact"]["en"]["path"], PAGES["contact"]["es"]["path"], p["title"], p["desc"], body))


# ---------- homepages: menu + card links ----------
def update_home(lang):
    path = "index.html" if lang == "en" else "es/index.html"
    s = SRC[lang]
    h = header(lang, None, home_page=True)
    h = fix_toggle(h, lang, "/", "/es/")
    s = re.sub(r'<header class="site-header">.*?</header>', lambda m: h, s, count=1, flags=re.S)
    s = re.sub(r'\s*<a class="card-more"[^>]*>.*?</a>', "", s)  # idempotent
    n = 0

    def add_link(m):
        nonlocal n
        link = f'\n          <a class="card-more" href="{service_path(n, lang)}">{UI[lang]["learn_more"]} <span aria-hidden="true">→</span></a>'
        n += 1
        return m.group(0) + link
    s = re.sub(r'(<article class="card">.*?<p>.*?</p>)', add_link, s, flags=re.S)
    assert n == 6
    s = s.replace('<a href="#contact" class="mb-quote">', '<a href="#contact" class="mb-quote">')
    write("/" + path, s)


def build_sitemap():
    pairs = [("/", "/es/")]
    pairs += [(PAGES[k]["en"]["path"], PAGES[k]["es"]["path"]) for k in ("services", "contact")]
    pairs += [(service_path(i, "en"), service_path(i, "es")) for i in range(len(SERVICES))]
    urls = []
    for en, es in pairs:
        alt = (f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/>\n'
               f'    <xhtml:link rel="alternate" hreflang="es" href="{SITE}{es}"/>\n')
        for u in (en, es):
            urls.append(f"  <url>\n    <loc>{SITE}{u}</loc>\n{alt}  </url>")
    write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    return len(urls)


if __name__ == "__main__":
    for lang in ("en", "es"):
        for i in range(len(SERVICES)):
            build_service(i, lang)
        build_services(lang)
        build_contact(lang)
        update_home(lang)
    print("pages in sitemap:", build_sitemap())
