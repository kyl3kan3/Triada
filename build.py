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
# Brand assets — the "triad" mark: three nested triangles.
# ---------------------------------------------------------------------------

MARK_SVG = """<svg class="mark" viewBox="0 0 44 40" aria-hidden="true" focusable="false">
  <path d="M22 3 L41 37 H3 Z" fill="none" stroke="currentColor" stroke-width="1.6"/>
  <path d="M22 13.5 L31.5 30.5 H12.5 Z" fill="currentColor" opacity=".28"/>
  <path d="M22 21 L26.8 30.5 H17.2 Z" fill="currentColor"/>
</svg>"""

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 44 40'%3E"
    "%3Cpath d='M22 3 L41 37 H3 Z' fill='none' stroke='%23c2a25c' stroke-width='2.4'/%3E"
    "%3Cpath d='M22 13.5 L31.5 30.5 H12.5 Z' fill='%23c2a25c' opacity='.35'/%3E"
    "%3Cpath d='M22 21 L26.8 30.5 H17.2 Z' fill='%23c2a25c'/%3E%3C/svg%3E"
)

# Custom line-icon set (48px grid, 1.5px stroke, drawn for this site).
ICONS = {
    "compass": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <circle cx="24" cy="24" r="19" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <path d="M31 17 L26.5 26.5 L17 31 L21.5 21.5 Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
  <circle cx="24" cy="24" r="1.6" fill="currentColor"/>
  <path d="M24 3.5 V7 M24 41 V44.5 M3.5 24 H7 M41 24 H44.5" stroke="currentColor" stroke-width="1.5"/>
</svg>""",
    "growth": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M6 40 H42" stroke="currentColor" stroke-width="1.5"/>
  <path d="M8 33 L18 23 L25 29 L40 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M32.5 11 H41 V19.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
  <circle cx="18" cy="23" r="1.8" fill="currentColor"/>
  <circle cx="25" cy="29" r="1.8" fill="currentColor"/>
</svg>""",
    "shield": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M24 5 L40 11 V23 C40 33.5 33.5 40.5 24 44 C14.5 40.5 8 33.5 8 23 V11 Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M17 24 L22 29 L31.5 18.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "ledger": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <rect x="10" y="6" width="28" height="36" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <path d="M17 15 H31 M17 22 H31 M17 29 H25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M28.5 33.5 L37 25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="29.5" cy="26" r="2" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <circle cx="36" cy="32.5" r="2" fill="none" stroke="currentColor" stroke-width="1.5"/>
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

  <div class="topbar">
    <div class="container topbar-inner">
      <span class="topbar-address">{ADDRESS_LINES[0]}, {ADDRESS_LINES[1]}</span>
      <span class="topbar-phones">
        <a href="tel:+16182813444">Office {PHONE_OFFICE}</a>
        <span class="dot" aria-hidden="true"></span>
        <a href="tel:+18448949822">Toll-Free {PHONE_TOLLFREE}</a>
      </span>
    </div>
  </div>

  <header class="site-header" id="site-header">
    <div class="container header-inner">
      <a class="brand" href="/" aria-label="Triada Advisors home">
        {MARK_SVG}
        <span class="brand-text">Triada<em>Advisors</em></span>
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">
        <span class="sr-only">Menu</span>
        <span class="nav-toggle-bars" aria-hidden="true"><i></i><i></i><i></i></span>
      </button>
      <nav id="site-nav" class="site-nav" aria-label="Main navigation">
        <ul>
            {nav_html(active_path)}
        </ul>
      </nav>
    </div>
  </header>

  <main id="main">
{body}
  </main>

  <footer class="site-footer">
    <div class="footer-rule" aria-hidden="true"></div>
    <div class="container footer-grid">
      <div class="footer-brand-col">
        <a class="brand brand-footer" href="/">
          {MARK_SVG}
          <span class="brand-text">Triada<em>Advisors</em></span>
        </a>
        <p class="footer-tagline">Plan wisely. Invest intently. Live fully.</p>
        <p>{address}</p>
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
      <nav aria-label="Footer">
        <h2>Explore</h2>
        <ul class="footer-links">
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
        <ul class="footer-links">
          <li><a href="{LINKS['brokercheck']}" rel="noopener" target="_blank">FINRA BrokerCheck</a></li>
          <li><a href="{LINKS['lpl_crs']}" rel="noopener" target="_blank">LPL Relationship Summary (Form CRS)</a></li>
          <li><a href="{LINKS['lpl']}" rel="noopener" target="_blank">LPL Financial</a></li>
          <li><a href="{LINKS['cornerstone']}" rel="noopener" target="_blank">Cornerstone Wealth Management</a></li>
          <li><a href="{LINKS['finra']}" rel="noopener" target="_blank">FINRA</a></li>
          <li><a href="{LINKS['sipc']}" rel="noopener" target="_blank">SIPC</a></li>
        </ul>
      </nav>
    </div>
    <div class="container">
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
      var onScroll = function () {{
        header.classList.toggle('is-scrolled', window.scrollY > 8);
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
        }}, {{ threshold: 0.15, rootMargin: '0px 0px -40px 0px' }});
        revealables.forEach(function (el) {{ io.observe(el); }});
      }} else {{
        revealables.forEach(function (el) {{ el.classList.add('is-visible'); }});
      }}

      var counters = document.querySelectorAll('[data-count]');
      var animate = function (el) {{
        var target = parseInt(el.getAttribute('data-count'), 10);
        var suffix = el.getAttribute('data-suffix') || '';
        var start = null;
        var dur = 1400;
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


def kicker_header(kicker, heading, *, light=False, center=False):
    cls = "section-head"
    if light:
        cls += " light"
    if center:
        cls += " center"
    return f"""        <div class="{cls} reveal">
          <p class="kicker"><span class="kicker-rule" aria-hidden="true"></span>{kicker}</p>
          <h2>{heading}</h2>
        </div>"""


def page_hero(kicker, heading, lede=""):
    lede_html = f'\n        <p class="lede reveal">{lede}</p>' if lede else ""
    return f"""    <section class="page-hero">
      <div class="hero-art" aria-hidden="true"></div>
      <div class="container">
        <p class="kicker reveal"><span class="kicker-rule" aria-hidden="true"></span>{kicker}</p>
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


def initials(m):
    return "".join(part[0] for part in m["slug"].split("-")[:2]).upper()


def team_card(m, delay):
    return f"""          <a class="team-card reveal" style="--d:{delay}ms" href="/team/{m['slug']}/">
            <span class="portrait" aria-hidden="true"><span>{initials(m)}</span></span>
            <span class="team-name">{m['name']}</span>
            <span class="team-title">{m['title']}</span>
            <span class="team-more">View profile <span aria-hidden="true">&rarr;</span></span>
          </a>"""


def team_index_body():
    sections = []
    for group, label in TEAM_GROUPS:
        cards = []
        d = 0
        for m in TEAM:
            if m["group"] != group:
                continue
            cards.append(team_card(m, d))
            d += 80
        cards_html = "\n".join(cards)
        sections.append(f"""    <section class="section">
      <div class="container">
{kicker_header(label, group)}
        <div class="team-grid">
{cards_html}
        </div>
      </div>
    </section>""")
    sections_html = "\n".join(sections)
    return page_hero(
        "The people behind the plan",
        "Our Team",
        "A teamwork approach adds broader perspective &mdash; and greater "
        "benefit &mdash; to every client relationship.",
    ) + f"""
{sections_html}
"""


def team_member_body(m):
    first = m["name"].split(",")[0].split()[0]
    return page_hero(m["group"], m["name"], m["title"]) + f"""
    <section class="section member">
      <div class="container member-grid">
        <div class="member-photo reveal" aria-hidden="true"><span>{initials(m)}</span></div>
        <div class="member-body reveal">
          <p class="member-lede">{m['bio']}</p>
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
      <div class="hero-art" aria-hidden="true"></div>
      <div class="hero-triad" aria-hidden="true">
        <svg viewBox="0 0 44 40">
          <path d="M22 3 L41 37 H3 Z" fill="none" stroke="currentColor" stroke-width=".7"/>
          <path d="M22 13.5 L31.5 30.5 H12.5 Z" fill="none" stroke="currentColor" stroke-width=".7"/>
          <path d="M22 21 L26.8 30.5 H17.2 Z" fill="currentColor" opacity=".5"/>
        </svg>
      </div>
      <div class="container hero-inner">
        <p class="kicker reveal is-visible"><span class="kicker-rule" aria-hidden="true"></span>Columbia, Illinois &middot; Serving clients nationwide</p>
        <h1 class="reveal is-visible">Feel confident in your <em>financial future.</em></h1>
        <p class="lede reveal is-visible">
          For more than two decades, Triada Advisors has helped family
          business owners, retirees, and wealth builders pursue their
          long-term goals through disciplined financial planning, investment
          management, and insurance consulting.
        </p>
        <div class="btn-row reveal is-visible">
          <a class="btn btn-gold" href="/contact-us/">Start the conversation</a>
          <a class="btn btn-ghost-light" href="/your-experience/">Discover your experience</a>
        </div>
      </div>
      <div class="hero-scroll" aria-hidden="true"><span></span></div>
    </section>

    <section class="section">
      <div class="container split">
        <div class="split-lead reveal">
          <p class="kicker"><span class="kicker-rule" aria-hidden="true"></span>Our philosophy</p>
          <h2 class="display">Built on trust.<br><em>Focused on you.</em></h2>
        </div>
        <div class="split-body">
          <p class="reveal">
            Our firm is rooted in a simple belief: earning your trust and
            caring about your best interests come before everything else.
            When we work with clients, it is never merely transactional
            &mdash; it is personal. We are proud to walk alongside you
            through life&rsquo;s biggest milestones, from building a career
            and starting a family to selling a business and stepping into
            retirement.
          </p>
          <p class="reveal">
            Based in the heart of Columbia, Illinois, we serve neighbors here
            at home and clients across the country. Through our relationship
            with Cornerstone Wealth Management and our alignment with LPL
            Financial, we combine the personal service of a local firm with
            the resources of a large institution &mdash; and the freedom to
            offer objective, unbiased advice.
          </p>
        </div>
      </div>
    </section>

    <section class="section band">
      <div class="container">
        <div class="section-head-row">
{kicker_header("What we do", "Three disciplines. One plan.")}
          <a class="text-link reveal" href="/our-solutions/">All solutions <span aria-hidden="true">&rarr;</span></a>
        </div>
        <div class="card-grid">
          <a class="card reveal" style="--d:0ms" href="/our-solutions/">
            {ICONS['compass']}
            <h3>Financial Planning</h3>
            <p>A sound plan addresses every corner of your financial life
            &mdash; not just your portfolio.</p>
            <span class="card-link">Learn more <span aria-hidden="true">&rarr;</span></span>
          </a>
          <a class="card reveal" style="--d:120ms" href="/our-solutions/">
            {ICONS['growth']}
            <h3>Investment Management</h3>
            <p>No one-size-fits-all models. Every strategy is customized to
            your needs &mdash; and yours alone.</p>
            <span class="card-link">Learn more <span aria-hidden="true">&rarr;</span></span>
          </a>
          <a class="card reveal" style="--d:240ms" href="/our-solutions/">
            {ICONS['shield']}
            <h3>Insurance Consulting</h3>
            <p>Experienced guidance to assess your coverage and address the
            risks that matter.</p>
            <span class="card-link">Learn more <span aria-hidden="true">&rarr;</span></span>
          </a>
        </div>
      </div>
    </section>

    <section class="section panel-dark">
      <div class="hero-art" aria-hidden="true"></div>
      <div class="container split align-center">
        <div class="reveal">
          <p class="kicker light"><span class="kicker-rule" aria-hidden="true"></span>Your experience</p>
          <h2 class="display light">Living <em>Intently</em>&trade;</h2>
          <p class="lede-sm">
            Wealth is a means, not an end. Our Living Intently experience is
            an interactive way to assess your total well-being and shape
            meaningful personal and financial life goals &mdash; so your
            money serves the life you actually want to live.
          </p>
          <a class="btn btn-gold" href="/your-experience/">Discover your experience</a>
        </div>
        <div class="stat-stack reveal">
          <div class="stat">
            <span class="stat-num"><span data-count="20" data-suffix="+">20+</span></span>
            <span class="stat-label">Years serving clients</span>
          </div>
          <div class="stat">
            <span class="stat-num"><span data-count="3">3</span></span>
            <span class="stat-label">Advisors, one coordinated team</span>
          </div>
          <div class="stat">
            <span class="stat-num"><span data-count="1">1</span></span>
            <span class="stat-label">Focus: your best interests</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head-row">
{kicker_header("Your advisors", "A team in your corner")}
          <a class="text-link reveal" href="/team/">Meet everyone <span aria-hidden="true">&rarr;</span></a>
        </div>
        <div class="team-grid team-grid-3">
{team_card(TEAM[0], 0)}
{team_card(TEAM[1], 120)}
{team_card(TEAM[2], 240)}
        </div>
      </div>
    </section>

    <section class="quote-band">
      <div class="container reveal">
        <div class="quote-mark" aria-hidden="true">{MARK_SVG}</div>
        <blockquote>
          Establishing trust and caring about our clients&rsquo; best
          interests are of the utmost importance to us. It is never merely
          transactional &mdash; it is personal.
        </blockquote>
        <p class="quote-attr">The Triada Advisors philosophy</p>
      </div>
    </section>

    <section class="cta-band">
      <div class="hero-art" aria-hidden="true"></div>
      <div class="container reveal">
        <h2 class="display light">Ready to take <em>the next step?</em></h2>
        <p>Call us at <a href="tel:+16182813444">{PHONE_OFFICE}</a> or send a
        message &mdash; we&rsquo;d be glad to talk.</p>
        <a class="btn btn-gold" href="/contact-us/">Contact Triada Advisors</a>
      </div>
    </section>
"""

ABOUT_BODY = page_hero(
    "More than 20 years of stewardship",
    "About <em>Us</em>",
    "Supporting the financial success and wellness of our clients for more "
    "than two decades.",
) + f"""
    <section class="section">
      <div class="container split">
        <div class="split-lead reveal">
          <p class="kicker"><span class="kicker-rule" aria-hidden="true"></span>Who we are</p>
          <h2 class="display">Rooted in Columbia.<br><em>Reaching nationwide.</em></h2>
        </div>
        <div class="split-body">
          <p class="reveal">
            Based in Columbia, Illinois, Triada Advisors provides
            comprehensive investment management, insurance, and financial
            planning services. For more than two decades we have worked with
            family business owners, retirees, and wealth builders to help
            maximize their capital for long-term prosperity and growth.
          </p>
          <p class="reveal">
            Establishing trust and caring about our clients&rsquo; best
            interests are of the utmost importance to us. That conviction
            shapes how we plan, how we invest, and how we communicate
            &mdash; in plain language, with your goals at the center.
          </p>
        </div>
      </div>
    </section>

    <section class="section band">
      <div class="container">
{kicker_header("How we're built", "Independent by design")}
        <div class="pillar-grid">
          <div class="pillar reveal" style="--d:0ms">
            <span class="pillar-num" aria-hidden="true">01</span>
            <h3>A local firm, personally invested</h3>
            <p>You work directly with advisors who know you, your family,
            and your goals &mdash; neighbors, not a call center.</p>
          </div>
          <div class="pillar reveal" style="--d:120ms">
            <span class="pillar-num" aria-hidden="true">02</span>
            <h3>Institutional resources</h3>
            <p>Through our relationship with Cornerstone Wealth Management,
            LLC, clients receive tailored service with access to the same
            caliber of resources as large institutions.</p>
          </div>
          <div class="pillar reveal" style="--d:240ms">
            <span class="pillar-num" aria-hidden="true">03</span>
            <h3>Objective, unbiased advice</h3>
            <p>Aligned with LPL Financial &mdash; one of the nation&rsquo;s
            largest independent broker-dealers &mdash; we are free to
            recommend what serves you. No proprietary products. No hidden
            agendas.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
{kicker_header("Who we serve", "Clients at every stage")}
        <div class="card-grid">
          <div class="card reveal" style="--d:0ms">
            <h3>Family Business Owners</h3>
            <p>Coordinating business and personal wealth, succession, and
            the transition you&rsquo;ve worked a lifetime to earn.</p>
          </div>
          <div class="card reveal" style="--d:120ms">
            <h3>Retirees</h3>
            <p>Turning savings into dependable income and protecting what
            you&rsquo;ve built for the people you love.</p>
          </div>
          <div class="card reveal" style="--d:240ms">
            <h3>Wealth Builders</h3>
            <p>Disciplined strategies for growing careers and growing
            families &mdash; so today&rsquo;s decisions compound into
            tomorrow&rsquo;s freedom.</p>
          </div>
        </div>
        <div class="btn-row reveal">
          <a class="btn" href="/your-experience/">See what working with us looks like</a>
        </div>
      </div>
    </section>
"""

SOLUTIONS_BODY = page_hero(
    "Comprehensive by design",
    "Our <em>Solutions</em>",
    "Expertise and guidance to help turn your life&rsquo;s goals into "
    "reality.",
) + f"""
    <section class="section">
      <div class="container solutions-list">
        <article class="solution reveal">
          <span class="solution-num" aria-hidden="true">01</span>
          <div class="solution-icon">{ICONS['compass']}</div>
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
        <article class="solution reveal">
          <span class="solution-num" aria-hidden="true">02</span>
          <div class="solution-icon">{ICONS['growth']}</div>
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
        <article class="solution reveal">
          <span class="solution-num" aria-hidden="true">03</span>
          <div class="solution-icon">{ICONS['shield']}</div>
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
        <article class="solution reveal">
          <span class="solution-num" aria-hidden="true">04</span>
          <div class="solution-icon">{ICONS['ledger']}</div>
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

    <section class="cta-band">
      <div class="hero-art" aria-hidden="true"></div>
      <div class="container reveal">
        <h2 class="display light">Not sure <em>where to start?</em></h2>
        <p>Every engagement begins with a conversation about you.</p>
        <a class="btn btn-gold" href="/contact-us/">Talk with an advisor</a>
      </div>
    </section>
"""

EXPERIENCE_BODY = page_hero(
    "Living Intently&trade;",
    "Your <em>Experience</em>",
    "An interactive approach to total well-being &mdash; and a plan with a "
    "&ldquo;why&rdquo; behind every number.",
) + """
    <section class="section">
      <div class="container split">
        <div class="split-lead reveal">
          <p class="kicker"><span class="kicker-rule" aria-hidden="true"></span>More than money</p>
          <h2 class="display">Wealth is a means,<br><em>not an end.</em></h2>
        </div>
        <div class="split-body">
          <p class="reveal">
            Financial success and financial wellness are not the same thing.
            Our Living Intently experience invites you to step back and
            self-assess your total well-being &mdash; family, health, work,
            purpose, and finances &mdash; and then create meaningful personal
            and financial life goals from that fuller picture.
          </p>
          <p class="reveal">
            The result is a plan with a &ldquo;why&rdquo; behind every
            number, and an advisor relationship built around the life you
            want to live &mdash; not just the assets you hold.
          </p>
        </div>
      </div>
    </section>

    <section class="section band">
      <div class="container">
""" + kicker_header("What to expect", "Four movements, one rhythm") + """
        <ol class="process-grid">
          <li class="process reveal" style="--d:0ms">
            <span class="pillar-num" aria-hidden="true">01</span>
            <h3>Discover</h3>
            <p>We listen first &mdash; your story, your values, your goals,
            and your concerns.</p>
          </li>
          <li class="process reveal" style="--d:120ms">
            <span class="pillar-num" aria-hidden="true">02</span>
            <h3>Assess</h3>
            <p>Together we take stock of your total well-being and your
            complete financial picture.</p>
          </li>
          <li class="process reveal" style="--d:240ms">
            <span class="pillar-num" aria-hidden="true">03</span>
            <h3>Design</h3>
            <p>We build a disciplined, personalized strategy across
            planning, investments, and protection.</p>
          </li>
          <li class="process reveal" style="--d:360ms">
            <span class="pillar-num" aria-hidden="true">04</span>
            <h3>Live</h3>
            <p>We meet regularly, adjust as life changes, and keep your plan
            pointed at what matters.</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="cta-band">
      <div class="hero-art" aria-hidden="true"></div>
      <div class="container reveal">
        <h2 class="display light">Begin <em>living intently.</em></h2>
        <a class="btn btn-gold" href="/contact-us/">Schedule a conversation</a>
      </div>
    </section>
"""

BLOG_BODY = page_hero(
    "Insights &amp; intellect",
    "Our <em>Perspective</em>",
    "Commentary on markets, planning, and living intently.",
) + f"""
    <section class="section">
      <div class="container narrow reveal">
        <p>
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
    "Events &amp; <em>Webinars</em>",
    "Market update calls, webinars, and client events.",
) + f"""
    <section class="section">
      <div class="container narrow reveal">
        <p>
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
    "Contact <em>Us</em>",
    "About markets, your plan, or what&rsquo;s next.",
) + f"""
    <section class="section">
      <div class="container contact-grid">
        <div class="contact-card reveal">
          <h2>Visit or call</h2>
          <p class="contact-lines">
            <strong>Triada Advisors</strong><br>
            {ADDRESS_LINES[0]}<br>
            {ADDRESS_LINES[1]}
          </p>
          <p class="contact-lines">
            Office <a href="tel:+16182813444">{PHONE_OFFICE}</a><br>
            Toll-Free <a href="tel:+18448949822">{PHONE_TOLLFREE}</a><br>
            <a href="mailto:{EMAIL}">{EMAIL}</a>
          </p>
          <p class="social-links">
            <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
            <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>
          </p>
        </div>
        <div class="reveal">
          <h2>Send a message</h2>
          <form class="contact-form" action="mailto:{EMAIL}" method="get">
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
            <button class="btn btn-gold" type="submit">Send message</button>
            <p class="form-note">Please do not include account numbers or
            other sensitive personal information in this form.</p>
          </form>
        </div>
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

    for m in TEAM:
        plain_name = m["name"].replace("&reg;", "®").replace("&trade;", "™")
        write(
            os.path.join(root, "team", m["slug"], "index.html"),
            page_shell(
                title=f"{plain_name} | Triada Advisors",
                description=f"{plain_name} — {m['title']} at Triada Advisors in Columbia, Illinois.",
                active_path="/team/",
                canonical=f"/team/{m['slug']}/",
                body=team_member_body(m),
            ),
        )

    for slug, target in REDIRECTS:
        write(os.path.join(root, slug, "index.html"), redirect_page(target))


if __name__ == "__main__":
    main()
