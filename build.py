#!/usr/bin/env python3
"""Static site generator for triadaadvisors.com.

Zero dependencies — run `python3 build.py` from the repo root and it
(re)writes every HTML page. All shared chrome (header, nav, footer,
regulatory disclosures) lives here so compliance text stays identical
on every page. Styles live in assets/css/styles.css.

URL scheme mirrors the original site: each page is written as
<path>/index.html so /about-us, /team/calvin-neeman, etc. resolve on
any static host (GitHub Pages, Netlify, S3).
"""

import os
import html

SITE_NAME = "Triada Advisors"
SITE_URL = "https://www.triadaadvisors.com"
PHONE_OFFICE = "(618) 281-3444"
PHONE_TOLLFREE = "(844) 894-9822"
EMAIL = "triada@lpl.com"
ADDRESS_LINES = ["1000 Eleven South, Suite 3D", "Columbia, IL 62236"]

LINKS = {
    "brokercheck": "https://brokercheck.finra.org/",
    "finra": "https://www.finra.org/",
    "sipc": "https://www.sipc.org/",
    "lpl": "https://www.lpl.com/",
    "lpl_crs": "https://www.lpl.com/crs",
    "cornerstone": "https://www.mycwmusa.com/",
    "linkedin": "https://www.linkedin.com/company/triada-advisors/",
    "facebook": "https://www.facebook.com/TriadaAdvisors/",
}

NAV = [
    ("Home", "/"),
    ("About Us", "/about-us/"),
    ("Our Solutions", "/our-solutions/"),
    ("Your Experience", "/your-experience/"),
    ("Team", "/team/"),
    ("Insights", "/blog/"),
    ("Events", "/events/"),
    ("Contact", "/contact-us/"),
]

# NOTE FOR SITE OWNER: the state list below must match the firm's current
# LPL registrations exactly. Replace the bracketed placeholder before
# publishing — this text is a regulatory requirement.
STATE_DISCLOSURE_PLACEHOLDER = (
    "[CONFIRM STATE LIST WITH LPL COMPLIANCE BEFORE PUBLISHING]"
)

# ---------------------------------------------------------------------------
# Brand assets — chunky rounded triad mark.
# ---------------------------------------------------------------------------

MARK_SVG = """<svg class="mark" viewBox="0 0 48 44" aria-hidden="true" focusable="false">
  <path d="M24 5 L43 39 H5 Z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>
  <path d="M24 21 L31 33.5 H17 Z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
</svg>"""

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 44'%3E"
    "%3Cpath d='M24 5 L43 39 H5 Z' fill='none' stroke='%230e7a4e' stroke-width='5' stroke-linejoin='round'/%3E"
    "%3Cpath d='M24 21 L31 33.5 H17 Z' fill='%23c9f25b' stroke='%23c9f25b' stroke-width='2'/%3E%3C/svg%3E"
)

# Chunky rounded line icons (48px grid, 3px stroke).
ICONS = {
    "map": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M24 42 C24 42 38 30.5 38 19.5 C38 11.5 31.7 6 24 6 C16.3 6 10 11.5 10 19.5 C10 30.5 24 42 24 42 Z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/>
  <circle cx="24" cy="19" r="5" fill="none" stroke="currentColor" stroke-width="3"/>
</svg>""",
    "chart": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M8 40 H40" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <path d="M10 32 L19 22 L26 27 L38 12" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M30 11 H39 V20" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "umbrella": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M24 7 C14 7 6.5 14.5 6 23.5 C9 21 13 21 16 23.5 C18.5 21 21.5 20.5 24 22 C26.5 20.5 29.5 21 32 23.5 C35 21 39 21 42 23.5 C41.5 14.5 34 7 24 7 Z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/>
  <path d="M24 22 V36 C24 39.5 21.5 41.5 18.5 41" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <path d="M24 5 V8" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
</svg>""",
    "calc": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <rect x="10" y="6" width="28" height="36" rx="5" fill="none" stroke="currentColor" stroke-width="3"/>
  <path d="M17 14 H31" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <path d="M17 24 H17.02 M24 24 H24.02 M31 24 H31.02 M17 33 H17.02 M24 33 H24.02 M31 33 H31.02" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
</svg>""",
    "heart": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M24 41 C24 41 6 30 6 17.5 C6 11 11 6.5 16.5 6.5 C20 6.5 22.8 8.4 24 11 C25.2 8.4 28 6.5 31.5 6.5 C37 6.5 42 11 42 17.5 C42 30 24 41 24 41 Z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/>
  <path d="M14 22 H20 L23 17 L26 27 L29 22 H34" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "spark": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M24 6 L27.5 18.5 L40 22 L27.5 25.5 L24 38 L20.5 25.5 L8 22 L20.5 18.5 Z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/>
  <circle cx="38" cy="9" r="2.4" fill="currentColor"/>
  <circle cx="10" cy="38" r="2.4" fill="currentColor"/>
</svg>""",
}

DISCLOSURES = f"""
      <div class="disclosures">
        <p>
          Check the background of your investment professionals on
          <a href="{LINKS['brokercheck']}" rel="noopener" target="_blank">FINRA&rsquo;s BrokerCheck</a>.
        </p>
        <p>
          Securities offered through LPL Financial, Member
          <a href="{LINKS['finra']}" rel="noopener" target="_blank">FINRA</a>/<a href="{LINKS['sipc']}" rel="noopener" target="_blank">SIPC</a>.
          Investment advice offered through Cornerstone Wealth Management, a
          registered investment advisor. Cornerstone Wealth Management and
          Triada Advisors are separate entities from
          <a href="{LINKS['lpl']}" rel="noopener" target="_blank">LPL Financial</a>.
        </p>
        <p>
          The LPL Financial registered representatives associated with this
          website may discuss and/or transact business only with residents of
          the states in which they are properly registered or licensed. No
          offers may be made or accepted from any resident of any other state.
          States currently registered: {STATE_DISCLOSURE_PLACEHOLDER}.
        </p>
        <p>
          For a copy of LPL Financial&rsquo;s Client Relationship Summary
          (Form CRS), please visit
          <a href="{LINKS['lpl_crs']}" rel="noopener" target="_blank">lpl.com/crs</a>.
        </p>
        <p>
          The information on this website is for general information only and
          is not intended to provide specific advice or recommendations for
          any individual. Consult your financial, tax, or legal professional
          regarding your unique situation.
        </p>
      </div>
"""

JSON_LD = f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FinancialService",
    "name": "Triada Advisors",
    "url": "{SITE_URL}/",
    "telephone": "+1-618-281-3444",
    "email": "{EMAIL}",
    "address": {{
      "@type": "PostalAddress",
      "streetAddress": "1000 Eleven South, Suite 3D",
      "addressLocality": "Columbia",
      "addressRegion": "IL",
      "postalCode": "62236",
      "addressCountry": "US"
    }},
    "sameAs": [
      "{LINKS['linkedin']}",
      "{LINKS['facebook']}"
    ]
  }}
  </script>
"""

_TICKER_SEQ = (
    '<span class="chip-t">Plan wisely</span>'
    '<span class="chip-t lime">Invest intently</span>'
    '<span class="chip-t mint">Live fully</span>'
) * 4
TICKER = f"""    <div class="ticker" aria-hidden="true">
      <div class="ticker-track">{_TICKER_SEQ}{_TICKER_SEQ}</div>
    </div>
"""


def nav_html(active_path):
    items = []
    for label, href in NAV:
        cls = ' class="active"' if href == active_path else ""
        items.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    return "\n            ".join(items)


def page_shell(*, title, description, active_path, body, canonical="", home=False):
    address = "<br>".join(ADDRESS_LINES)
    jsonld = JSON_LD if home else ""
    canonical_tag = (
        f'\n  <link rel="canonical" href="{SITE_URL}{canonical}">' if canonical else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">{canonical_tag}
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:type" content="website">
  <link rel="icon" href="{FAVICON}">
  <link rel="stylesheet" href="/assets/css/styles.css">
{jsonld}</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <div class="progress" aria-hidden="true"><i></i></div>

  <header class="masthead" id="site-header">
    <div class="shell masthead-inner">
      <a class="wordmark" href="/" aria-label="Triada Advisors home">
        {MARK_SVG}
        <span>triada<b>advisors</b></span>
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">
        <span class="sr-only">Menu</span>
        <span class="nav-toggle-bars" aria-hidden="true"><i></i><i></i></span>
      </button>
      <nav id="site-nav" class="site-nav" aria-label="Main navigation">
        <ul>
            {nav_html(active_path)}
        </ul>
      </nav>
      <a class="btn btn-sm masthead-cta" href="/contact-us/">Talk to us</a>
    </div>
  </header>

  <main id="main">
{body}
  </main>

  <footer class="foot">
    <div class="shell foot-grid">
      <div class="foot-brand">
        <a class="wordmark wordmark-foot" href="/">
          {MARK_SVG}
          <span>triada<b>advisors</b></span>
        </a>
        <p class="foot-tag">Plan wisely. Invest intently. Live fully.</p>
        <p class="social-links">
          <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
          <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>
        </p>
      </div>
      <div>
        <h2>Office</h2>
        <p>{address}</p>
        <p>
          Office <a href="tel:+16182813444">{PHONE_OFFICE}</a><br>
          Toll-Free <a href="tel:+18448949822">{PHONE_TOLLFREE}</a><br>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </p>
      </div>
      <nav aria-label="Footer">
        <h2>Explore</h2>
        <ul class="foot-links">
          <li><a href="/about-us/">About Us</a></li>
          <li><a href="/our-solutions/">Our Solutions</a></li>
          <li><a href="/your-experience/">Your Experience</a></li>
          <li><a href="/team/">Our Team</a></li>
          <li><a href="/blog/">Insights</a></li>
          <li><a href="/events/">Events</a></li>
          <li><a href="/contact-us/">Contact</a></li>
        </ul>
      </nav>
      <nav aria-label="Resources">
        <h2>Resources</h2>
        <ul class="foot-links">
          <li><a href="{LINKS['brokercheck']}" rel="noopener" target="_blank">FINRA BrokerCheck</a></li>
          <li><a href="{LINKS['lpl_crs']}" rel="noopener" target="_blank">LPL Relationship Summary (Form CRS)</a></li>
          <li><a href="{LINKS['lpl']}" rel="noopener" target="_blank">LPL Financial</a></li>
          <li><a href="{LINKS['cornerstone']}" rel="noopener" target="_blank">Cornerstone Wealth Management</a></li>
          <li><a href="{LINKS['finra']}" rel="noopener" target="_blank">FINRA</a></li>
          <li><a href="{LINKS['sipc']}" rel="noopener" target="_blank">SIPC</a></li>
        </ul>
      </nav>
    </div>
    <div class="shell">
{DISCLOSURES}
      <p class="copyright">&copy; 2026 Triada Advisors. All rights reserved.</p>
    </div>
  </footer>

  <script>
    (function () {{
      var btn = document.querySelector('.nav-toggle');
      var nav = document.getElementById('site-nav');
      btn.addEventListener('click', function () {{
        var open = nav.classList.toggle('open');
        btn.classList.toggle('is-open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      }});

      var header = document.getElementById('site-header');
      var bar = document.querySelector('.progress i');
      var onScroll = function () {{
        header.classList.toggle('is-scrolled', window.scrollY > 8);
        if (bar) {{
          var max = document.documentElement.scrollHeight - window.innerHeight;
          bar.style.setProperty('--p', max > 0 ? (window.scrollY / max) : 0);
        }}
      }};
      window.addEventListener('scroll', onScroll, {{ passive: true }});
      onScroll();

      var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var revealables = document.querySelectorAll('.reveal');
      if (!reduced && 'IntersectionObserver' in window) {{
        var io = new IntersectionObserver(function (entries) {{
          entries.forEach(function (e) {{
            if (e.isIntersecting) {{
              e.target.classList.add('is-visible');
              io.unobserve(e.target);
            }}
          }});
        }}, {{ threshold: 0.12, rootMargin: '0px 0px -30px 0px' }});
        revealables.forEach(function (el) {{ io.observe(el); }});
      }} else {{
        revealables.forEach(function (el) {{ el.classList.add('is-visible'); }});
      }}

      var counters = document.querySelectorAll('[data-count]');
      var animate = function (el) {{
        var target = parseInt(el.getAttribute('data-count'), 10);
        var suffix = el.getAttribute('data-suffix') || '';
        var start = null;
        var dur = 1200;
        var step = function (ts) {{
          if (!start) start = ts;
          var p = Math.min((ts - start) / dur, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(eased * target) + suffix;
          if (p < 1) requestAnimationFrame(step);
        }};
        requestAnimationFrame(step);
      }};
      if (!reduced && 'IntersectionObserver' in window) {{
        var cio = new IntersectionObserver(function (entries) {{
          entries.forEach(function (e) {{
            if (e.isIntersecting) {{ animate(e.target); cio.unobserve(e.target); }}
          }});
        }}, {{ threshold: 0.5 }});
        counters.forEach(function (el) {{ cio.observe(el); }});
      }} else {{
        counters.forEach(function (el) {{
          el.textContent = el.getAttribute('data-count') + (el.getAttribute('data-suffix') || '');
        }});
      }}
    }})();
  </script>
</body>
</html>
"""


def chip(label, tone=""):
    return f'<span class="chip {tone}">{label}</span>'


def section_head(label, heading, *, center=False):
    cls = "sec-head center" if center else "sec-head"
    return f"""        <div class="{cls} reveal">
          {chip(label)}
          <h2>{heading}</h2>
        </div>"""


def page_hero(label, heading, lede=""):
    lede_html = f'\n        <p class="lede reveal">{lede}</p>' if lede else ""
    return f"""    <section class="page-hero">
      <div class="blob blob-a" aria-hidden="true"></div>
      <div class="blob blob-b" aria-hidden="true"></div>
      <div class="shell">
        <div class="reveal">{chip(label, "lime")}</div>
        <h1 class="reveal">{heading}</h1>{lede_html}
      </div>
    </section>
"""


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------

TEAM = [
    {
        "slug": "calvin-neeman",
        "name": "Calvin Neeman",
        "title": "Financial Advisor",
        "group": "Advisors",
        "bio": (
            "Calvin works closely with family business owners, retirees, and "
            "wealth builders to design financial strategies around what "
            "matters most to them. He believes planning starts with "
            "listening, and he is committed to being a steady partner "
            "through every stage of a client&rsquo;s financial life."
        ),
    },
    {
        "slug": "aaron-thompson",
        "name": "Aaron Thompson, CPA",
        "title": "Financial Advisor",
        "group": "Advisors",
        "bio": (
            "Aaron brings extensive financial services industry experience "
            "to the team. He earned his master&rsquo;s degree in accounting "
            "from Butler University and holds the CPA license, giving "
            "clients the benefit of a tax-aware perspective on planning and "
            "investment decisions."
        ),
    },
    {
        "slug": "trevor-davis",
        "name": "Trevor Davis, CFP&reg;",
        "title": "Financial Advisor",
        "group": "Advisors",
        "bio": (
            "Trevor is a CERTIFIED FINANCIAL PLANNER&trade; professional who "
            "helps clients bring clarity and discipline to their long-term "
            "goals &mdash; from building careers and starting families to "
            "preparing for retirement."
        ),
    },
    {
        "slug": "lee-eggemeyer",
        "name": "Lee Eggemeyer, CPA",
        "title": "Triada Tax Services LLC",
        "group": "Tax Services",
        "bio": (
            "Lee is co-owner and manager of Triada Tax Services LLC. His "
            "background includes nine years with a Fortune 500 company and "
            "more than 35 years in public accounting, experience he draws on "
            "to help clients coordinate their tax and financial pictures."
        ),
    },
    {
        "slug": "karleigh-floarke",
        "name": "Karleigh Floarke, FPQP&reg;",
        "title": "Client Services",
        "group": "Client Services",
        "bio": (
            "Karleigh is a Financial Paraplanner Qualified Professional&trade; "
            "who supports clients and advisors alike, helping ensure every "
            "detail of the client experience is handled with care."
        ),
    },
    {
        "slug": "charlene-ahne",
        "name": "Charlene Ahne",
        "title": "Client Services",
        "group": "Client Services",
        "bio": (
            "Charlene helps keep the office running smoothly and is often "
            "the friendly first point of contact for clients visiting or "
            "calling our Columbia office."
        ),
    },
    {
        "slug": "kristina-davis",
        "name": "Kristina Davis",
        "title": "Client Services",
        "group": "Client Services",
        "bio": (
            "Kristina supports the advisory team and our clients with "
            "scheduling, service requests, and the day-to-day details that "
            "make for a seamless experience."
        ),
    },
    {
        "slug": "gregory-shoemaker",
        "name": "Gregory Shoemaker",
        "title": "Founder, Cornerstone Wealth Management",
        "group": "Cornerstone Wealth Management",
        "bio": (
            "Greg established Cornerstone Wealth Management in 2005 with a "
            "passion for objective guidance, transparent fees, and "
            "independent advice &mdash; values that continue to shape the "
            "resources available to Triada Advisors clients."
        ),
    },
    {
        "slug": "liyin-bao",
        "name": "Liyin Bao, CFA",
        "title": "Investment Team Lead, Cornerstone Wealth Portfolios",
        "group": "Cornerstone Wealth Management",
        "bio": (
            "Liyin leads the Cornerstone Wealth Portfolios investment team. "
            "Since joining the firm in 2012, she has managed a broad range "
            "of equity and fixed income portfolios on behalf of clients."
        ),
    },
    {
        "slug": "khurram-naveed",
        "name": "Khurram Naveed, CFA",
        "title": "Investment Team, Cornerstone Wealth Management",
        "group": "Cornerstone Wealth Management",
        "bio": (
            "Khurram is a CFA charterholder on the Cornerstone Wealth "
            "Management investment team, contributing research and portfolio "
            "analysis in support of client strategies."
        ),
    },
    {
        "slug": "elizabeth-yaekel",
        "name": "Elizabeth Yaekel",
        "title": "Cornerstone Wealth Management",
        "group": "Cornerstone Wealth Management",
        "bio": (
            "Elizabeth is part of the Cornerstone Wealth Management team "
            "that extends institutional-caliber resources to Triada "
            "Advisors clients."
        ),
    },
    {
        "slug": "sophia-mcwilliams",
        "name": "Sophia McWilliams",
        "title": "Cornerstone Wealth Management",
        "group": "Cornerstone Wealth Management",
        "bio": (
            "Sophia is part of the Cornerstone Wealth Management team that "
            "extends institutional-caliber resources to Triada Advisors "
            "clients."
        ),
    },
]

TEAM_GROUPS = [
    ("Advisors", "Your advisory team"),
    ("Tax Services", "Tax coordination"),
    ("Client Services", "Client experience"),
    ("Cornerstone Wealth Management", "Investment &amp; research partners"),
]

TINTS = ["mint", "lime", "sage", "leaf"]


def initials(m):
    return "".join(part[0] for part in m["slug"].split("-")[:2]).upper()


def team_card(m, i, delay):
    tint = TINTS[i % len(TINTS)]
    return f"""            <a class="person reveal" style="--d:{delay}ms" href="/team/{m['slug']}/">
              <span class="face {tint}" aria-hidden="true">{initials(m)}</span>
              <span class="person-name">{m['name']}</span>
              <span class="person-title">{m['title']}</span>
              <span class="person-go" aria-hidden="true">&#8599;</span>
            </a>"""


def team_index_body():
    out = [page_hero(
        "The people behind the plan",
        "Meet the <mark>team</mark> in your corner.",
        "A teamwork approach adds broader perspective &mdash; and greater "
        "benefit &mdash; to every client relationship.",
    )]
    i = 0
    for group, label in TEAM_GROUPS:
        cards, d = [], 0
        for m in TEAM:
            if m["group"] != group:
                continue
            cards.append(team_card(m, i, d))
            i += 1
            d += 70
        cards_html = "\n".join(cards)
        out.append(f"""    <section class="sec">
      <div class="shell">
{section_head(label, group)}
        <div class="person-grid">
{cards_html}
        </div>
      </div>
    </section>
""")
    return "\n".join(out)


def team_member_body(m, i):
    first = m["name"].split(",")[0].split()[0]
    tint = TINTS[i % len(TINTS)]
    return page_hero(m["group"], m["name"], m["title"]) + f"""
    <section class="sec">
      <div class="shell member-grid">
        <div class="face face-lg {tint} reveal" aria-hidden="true">{initials(m)}</div>
        <div class="reveal">
          <p class="lede">{m['bio']}</p>
          <p>
            To connect with {first} or any member of the Triada Advisors
            team, call our office at
            <a href="tel:+16182813444">{PHONE_OFFICE}</a> or
            <a href="/contact-us/">send us a message</a>.
          </p>
          <div class="btn-row">
            <a class="btn" href="/contact-us/">Start a conversation</a>
            <a class="btn btn-ghost" href="/team/">&larr; Back to the team</a>
          </div>
        </div>
      </div>
    </section>
"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

HOME_BODY = f"""    <section class="hero">
      <div class="blob blob-a" aria-hidden="true"></div>
      <div class="blob blob-b" aria-hidden="true"></div>
      <div class="shell hero-grid">
        <div class="hero-copy">
          <div class="reveal is-visible">{chip("Columbia, Illinois &middot; Serving clients nationwide", "lime")}</div>
          <h1 class="reveal is-visible" style="--d:80ms">Feel confident in your <mark>financial future.</mark></h1>
          <p class="lede reveal is-visible" style="--d:180ms">
            For more than two decades, Triada Advisors has helped family
            business owners, retirees, and wealth builders pursue their
            long-term goals through disciplined financial planning,
            investment management, and insurance consulting.
          </p>
          <div class="btn-row reveal is-visible" style="--d:280ms">
            <a class="btn" href="/contact-us/">Start the conversation</a>
            <a class="btn btn-ghost" href="/your-experience/">Discover your experience</a>
          </div>
        </div>
        <div class="hero-bento">
          <div class="bento tile-stat reveal is-visible" style="--d:200ms">
            <span class="stat-big"><span data-count="20" data-suffix="+">20+</span></span>
            <span class="stat-sub">years helping families pursue their goals</span>
          </div>
          <div class="bento tile-dark reveal is-visible" style="--d:300ms">
            <span class="tile-kicker">Our experience</span>
            <span class="tile-title">Living Intently&trade;</span>
            <p>Money in service of the life you actually want.</p>
            <a class="tile-link" href="/your-experience/">Explore &#8599;</a>
          </div>
          <div class="bento tile-team reveal is-visible" style="--d:400ms">
            <span class="face-row" aria-hidden="true">
              <span class="face mint">CN</span><span class="face lime">AT</span><span class="face sage">TD</span>
            </span>
            <span class="tile-sub">Three advisors. One coordinated team.</span>
            <a class="tile-link" href="/team/">Meet us &#8599;</a>
          </div>
          <div class="bento tile-quote reveal is-visible" style="--d:500ms">
            <p>&ldquo;It is never merely transactional &mdash; it is personal.&rdquo;</p>
          </div>
        </div>
      </div>
    </section>

{TICKER}

    <section class="sec">
      <div class="shell">
        <div class="sec-head-row">
{section_head("What we do", "Three disciplines.<br>One plan.")}
          <a class="btn btn-ghost reveal" href="/our-solutions/">All solutions</a>
        </div>
        <div class="card-grid">
          <a class="card mintbg reveal" style="--d:0ms" href="/our-solutions/">
            <span class="icon-pill">{ICONS['map']}</span>
            <h3>Financial Planning</h3>
            <p>A sound plan addresses every corner of your financial life
            &mdash; not just your portfolio.</p>
            <span class="card-go">Learn more &#8599;</span>
          </a>
          <a class="card sagebg reveal" style="--d:100ms" href="/our-solutions/">
            <span class="icon-pill">{ICONS['chart']}</span>
            <h3>Investment Management</h3>
            <p>No one-size-fits-all models. Every strategy is customized to
            your needs &mdash; and yours alone.</p>
            <span class="card-go">Learn more &#8599;</span>
          </a>
          <a class="card limebg reveal" style="--d:200ms" href="/our-solutions/">
            <span class="icon-pill">{ICONS['umbrella']}</span>
            <h3>Insurance Consulting</h3>
            <p>Experienced guidance to assess your coverage and address the
            risks that matter.</p>
            <span class="card-go">Learn more &#8599;</span>
          </a>
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="shell">
        <div class="panel-dark reveal">
          <div class="panel-grid">
            <div>
              {chip("Your experience", "onDark")}
              <h2>Wealth is a means,<br><mark class="mark-lime">not an end.</mark></h2>
              <p class="panel-lede">
                Our Living Intently experience is an interactive way to
                assess your total well-being and shape meaningful personal
                and financial life goals &mdash; so your money serves the
                life you actually want to live.
              </p>
              <a class="btn btn-lime" href="/your-experience/">Discover your experience</a>
            </div>
            <div class="panel-stats">
              <div class="pstat">
                <span class="pstat-num"><span data-count="20" data-suffix="+">20+</span></span>
                <span class="pstat-label">Years serving clients</span>
              </div>
              <div class="pstat">
                <span class="pstat-num"><span data-count="3">3</span></span>
                <span class="pstat-label">Advisors, one team</span>
              </div>
              <div class="pstat">
                <span class="pstat-num"><span data-count="1">1</span></span>
                <span class="pstat-label">Focus: your best interests</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="shell">
        <div class="sec-head-row">
{section_head("Your advisors", "A team in your corner.")}
          <a class="btn btn-ghost reveal" href="/team/">Meet everyone</a>
        </div>
        <div class="person-grid person-grid-3">
{team_card(TEAM[0], 0, 0)}
{team_card(TEAM[1], 1, 100)}
{team_card(TEAM[2], 2, 200)}
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="shell">
        <div class="cta-panel reveal">
          <div class="blob blob-c" aria-hidden="true"></div>
          <h2>Ready to take the next step?</h2>
          <p>Call us at <a href="tel:+16182813444">{PHONE_OFFICE}</a> or send
          a message &mdash; we&rsquo;d be glad to talk.</p>
          <a class="btn btn-dark" href="/contact-us/">Contact Triada Advisors</a>
        </div>
      </div>
    </section>
"""

ABOUT_BODY = page_hero(
    "More than 20 years of stewardship",
    "Built on trust. <mark>Focused on you.</mark>",
    "Supporting the financial success and wellness of our clients for more "
    "than two decades.",
) + f"""
    <section class="sec">
      <div class="shell two-col">
        <div class="reveal">
          <h2>Who we are</h2>
          <p>
            Based in Columbia, Illinois, Triada Advisors provides
            comprehensive investment management, insurance, and financial
            planning services. For more than two decades we have worked with
            family business owners, retirees, and wealth builders to help
            maximize their capital for long-term prosperity and growth.
          </p>
          <p>
            Establishing trust and caring about our clients&rsquo; best
            interests are of the utmost importance to us. That conviction
            shapes how we plan, how we invest, and how we communicate
            &mdash; in plain language, with your goals at the center.
          </p>
        </div>
        <div class="reveal">
          <h2>How we&rsquo;re built</h2>
          <p>
            Through our relationship with Cornerstone Wealth Management,
            LLC, our clients receive personalized, tailored service while
            enjoying access to the same caliber of resources as large
            institutions.
          </p>
          <p>
            And because we are aligned with LPL Financial &mdash; one of the
            nation&rsquo;s largest independent broker-dealers &mdash; we are
            free to provide truly objective, unbiased advice. No proprietary
            products. No hidden agendas.
          </p>
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="shell">
{section_head("Who we serve", "Clients at every stage.")}
        <div class="card-grid">
          <div class="card mintbg reveal" style="--d:0ms">
            <span class="icon-pill">{ICONS['spark']}</span>
            <h3>Family Business Owners</h3>
            <p>Coordinating business and personal wealth, succession, and
            the transition you&rsquo;ve worked a lifetime to earn.</p>
          </div>
          <div class="card sagebg reveal" style="--d:100ms">
            <span class="icon-pill">{ICONS['heart']}</span>
            <h3>Retirees</h3>
            <p>Turning savings into dependable income and protecting what
            you&rsquo;ve built for the people you love.</p>
          </div>
          <div class="card limebg reveal" style="--d:200ms">
            <span class="icon-pill">{ICONS['chart']}</span>
            <h3>Wealth Builders</h3>
            <p>Disciplined strategies for growing careers and growing
            families &mdash; compounding today into tomorrow&rsquo;s
            freedom.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="shell">
        <div class="cta-panel reveal">
          <div class="blob blob-c" aria-hidden="true"></div>
          <h2>See what working with us looks like.</h2>
          <a class="btn btn-dark" href="/your-experience/">Your experience</a>
        </div>
      </div>
    </section>
"""

SOLUTIONS_BODY = page_hero(
    "Comprehensive by design",
    "Solutions for your <mark>whole life.</mark>",
    "Expertise and guidance to help turn your life&rsquo;s goals into "
    "reality.",
) + f"""
    <section class="sec">
      <div class="shell solution-stack">
        <article class="solution mintbg reveal">
          <span class="icon-pill">{ICONS['map']}</span>
          <div>
            <h2>Financial Planning</h2>
            <p>
              A strong, sound financial plan encompasses many different
              aspects of your financial future &mdash; cash flow, retirement,
              taxes, education, estate considerations, and the goals that are
              uniquely yours. We build plans that connect those pieces into
              one clear picture, then revisit them as your life evolves.
            </p>
          </div>
        </article>
        <article class="solution sagebg reveal">
          <span class="icon-pill">{ICONS['chart']}</span>
          <div>
            <h2>Investment Management</h2>
            <p>
              Rather than relying on a single solution or a model portfolio,
              we customize each strategy based on your needs &mdash; and your
              needs alone. Portfolios are managed with discipline and
              supported by the Cornerstone Wealth Portfolios investment team,
              giving you institutional-caliber research with personal
              accountability.
            </p>
          </div>
        </article>
        <article class="solution limebg reveal">
          <span class="icon-pill">{ICONS['umbrella']}</span>
          <div>
            <h2>Insurance Consulting</h2>
            <p>
              With deep experience in the insurance marketplace and knowledge
              of the universe of options available, our advisors help you
              address insurance needs and assess appropriate coverage &mdash;
              protecting your income, your family, and your plan against the
              unexpected.
            </p>
          </div>
        </article>
        <article class="solution leafbg reveal">
          <span class="icon-pill">{ICONS['calc']}</span>
          <div>
            <h2>Tax Coordination</h2>
            <p>
              Through Triada Tax Services LLC and the CPA credentials on our
              team, we help clients keep their tax picture and financial plan
              working together instead of at cross purposes.
            </p>
          </div>
        </article>
      </div>
    </section>

    <section class="sec">
      <div class="shell">
        <div class="cta-panel reveal">
          <div class="blob blob-c" aria-hidden="true"></div>
          <h2>Not sure where to start?</h2>
          <p>Every engagement begins with a conversation about you.</p>
          <a class="btn btn-dark" href="/contact-us/">Talk with an advisor</a>
        </div>
      </div>
    </section>
"""

EXPERIENCE_BODY = page_hero(
    "Living Intently&trade;",
    "A plan with a <mark>&ldquo;why&rdquo;</mark> behind every number.",
    "An interactive approach to total well-being.",
) + f"""
    <section class="sec">
      <div class="shell two-col">
        <div class="reveal">
          <h2>More than money</h2>
          <p>
            Financial success and financial wellness are not the same thing.
            Our Living Intently experience invites you to step back and
            self-assess your total well-being &mdash; family, health, work,
            purpose, and finances &mdash; and then create meaningful personal
            and financial life goals from that fuller picture.
          </p>
        </div>
        <div class="reveal">
          <h2>Built around your life</h2>
          <p>
            The result is a plan with a &ldquo;why&rdquo; behind every
            number, and an advisor relationship built around the life you
            want to live &mdash; not just the assets you hold.
          </p>
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="shell">
{section_head("What to expect", "Four steps. One rhythm.")}
        <div class="step-grid">
          <div class="step reveal" style="--d:0ms">
            <span class="step-num mint">1</span>
            <h3>Discover</h3>
            <p>We listen first &mdash; your story, your values, your goals,
            and your concerns.</p>
          </div>
          <div class="step reveal" style="--d:100ms">
            <span class="step-num lime">2</span>
            <h3>Assess</h3>
            <p>Together we take stock of your total well-being and your
            complete financial picture.</p>
          </div>
          <div class="step reveal" style="--d:200ms">
            <span class="step-num sage">3</span>
            <h3>Design</h3>
            <p>We build a disciplined, personalized strategy across
            planning, investments, and protection.</p>
          </div>
          <div class="step reveal" style="--d:300ms">
            <span class="step-num leaf">4</span>
            <h3>Live</h3>
            <p>We meet regularly, adjust as life changes, and keep your plan
            pointed at what matters.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="shell">
        <div class="cta-panel reveal">
          <div class="blob blob-c" aria-hidden="true"></div>
          <h2>Begin living intently.</h2>
          <a class="btn btn-dark" href="/contact-us/">Schedule a conversation</a>
        </div>
      </div>
    </section>
"""

BLOG_BODY = page_hero(
    "Insights &amp; intellect",
    "Our <mark>perspective.</mark>",
    "Commentary on markets, planning, and living intently.",
) + f"""
    <section class="sec">
      <div class="shell narrow reveal">
        <p class="lede">
          Our team regularly shares market commentary, week-in-review notes,
          and planning insights. New posts will appear here &mdash; in the
          meantime, follow us on
          <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
          or <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>,
          or <a href="/contact-us/">contact us</a> to join our distribution
          list.
        </p>
      </div>
    </section>
"""

EVENTS_BODY = page_hero(
    "Calls, webinars &amp; gatherings",
    "Events &amp; <mark>webinars.</mark>",
    "Market update calls, webinars, and client events.",
) + f"""
    <section class="sec">
      <div class="shell narrow reveal">
        <p class="lede">
          Triada Advisors hosts periodic market update calls and client
          events. Upcoming events will be listed here. To be notified about
          the next one, call us at
          <a href="tel:+16182813444">{PHONE_OFFICE}</a>
          or <a href="/contact-us/">send us a message</a>.
        </p>
      </div>
    </section>
"""

CONTACT_BODY = page_hero(
    "We&rsquo;d be glad to talk",
    "Say <mark>hello.</mark>",
    "About markets, your plan, or what&rsquo;s next.",
) + f"""
    <section class="sec">
      <div class="shell contact-grid">
        <div class="contact-card reveal">
          <span class="icon-pill">{ICONS['map']}</span>
          <h2>Visit or call</h2>
          <p>
            <strong>Triada Advisors</strong><br>
            {ADDRESS_LINES[0]}<br>
            {ADDRESS_LINES[1]}
          </p>
          <p>
            Office <a href="tel:+16182813444">{PHONE_OFFICE}</a><br>
            Toll-Free <a href="tel:+18448949822">{PHONE_TOLLFREE}</a><br>
            <a href="mailto:{EMAIL}">{EMAIL}</a>
          </p>
          <p class="social-links">
            <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
            <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>
          </p>
        </div>
        <form class="contact-form reveal" action="mailto:{EMAIL}" method="get">
          <h2>Send a message</h2>
          <div class="field-row">
            <div class="field">
              <label for="cf-name">Name</label>
              <input id="cf-name" name="name" type="text" autocomplete="name" required>
            </div>
            <div class="field">
              <label for="cf-phone">Phone <span class="optional">(optional)</span></label>
              <input id="cf-phone" name="phone" type="tel" autocomplete="tel">
            </div>
          </div>
          <div class="field">
            <label for="cf-email">Email</label>
            <input id="cf-email" name="email" type="email" autocomplete="email" required>
          </div>
          <div class="field">
            <label for="cf-message">How can we help?</label>
            <textarea id="cf-message" name="body" rows="5" required></textarea>
          </div>
          <button class="btn" type="submit">Send message</button>
          <p class="form-note">Please do not include account numbers or
          other sensitive personal information in this form.</p>
        </form>
      </div>
    </section>
"""


def redirect_page(target):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={target}">
  <link rel="canonical" href="{target}">
  <title>Redirecting&hellip;</title>
</head>
<body>
  <p>This page has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""


PAGES = [
    ("", "Triada Advisors | Financial Planning & Investment Management, Columbia IL",
     "Triada Advisors provides comprehensive investment management, insurance and financial planning services from Columbia, Illinois.",
     "/", HOME_BODY),
    ("about-us", "About Us | Triada Advisors",
     "Based in Columbia, Illinois, Triada Advisors has supported the financial success of family business owners, retirees and wealth builders for more than 20 years.",
     "/about-us/", ABOUT_BODY),
    ("our-solutions", "Our Solutions | Triada Advisors",
     "Financial planning, investment management, insurance consulting and tax coordination from Triada Advisors in Columbia, Illinois.",
     "/our-solutions/", SOLUTIONS_BODY),
    ("your-experience", "Your Experience | Triada Advisors",
     "Living Intently — Triada Advisors' interactive approach to assessing total well-being and creating meaningful personal and financial life goals.",
     "/your-experience/", EXPERIENCE_BODY),
    ("team", "Our Team | Triada Advisors",
     "Meet the Triada Advisors team — advisors, tax and client service professionals, and the Cornerstone Wealth Management investment team.",
     "/team/", team_index_body()),
    ("blog", "Insights & Intellect | Triada Advisors",
     "Market commentary and planning insights from the Triada Advisors team.",
     "/blog/", BLOG_BODY),
    ("events", "Events & Webinars | Triada Advisors",
     "Market update calls, webinars and client events from Triada Advisors.",
     "/events/", EVENTS_BODY),
    ("contact-us", "Contact | Triada Advisors",
     "Contact Triada Advisors in Columbia, Illinois — (618) 281-3444, toll-free (844) 894-9822.",
     "/contact-us/", CONTACT_BODY),
]

# Legacy paths that existed on the original site.
REDIRECTS = [
    ("about", "/about-us/"),
    ("contact", "/contact-us/"),
]


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {path}")


def main():
    root = os.path.dirname(os.path.abspath(__file__))

    for slug, title, desc, active, body in PAGES:
        out = os.path.join(root, slug, "index.html") if slug else os.path.join(root, "index.html")
        write(out, page_shell(
            title=title, description=desc, active_path=active, body=body,
            canonical=active, home=(slug == ""),
        ))

    for i, m in enumerate(TEAM):
        plain_name = m["name"].replace("&reg;", "®").replace("&trade;", "™")
        write(
            os.path.join(root, "team", m["slug"], "index.html"),
            page_shell(
                title=f"{plain_name} | Triada Advisors",
                description=f"{plain_name} — {m['title']} at Triada Advisors in Columbia, Illinois.",
                active_path="/team/",
                canonical=f"/team/{m['slug']}/",
                body=team_member_body(m, i),
            ),
        )

    for slug, target in REDIRECTS:
        write(os.path.join(root, slug, "index.html"), redirect_page(target))


if __name__ == "__main__":
    main()
