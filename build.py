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
]

# NOTE FOR SITE OWNER: the state list below must match the firm's current
# LPL registrations exactly. Replace the bracketed placeholder before
# publishing — this text is a regulatory requirement.
STATE_DISCLOSURE_PLACEHOLDER = (
    "[CONFIRM STATE LIST WITH LPL COMPLIANCE BEFORE PUBLISHING]"
)

MARK_SVG = """<svg class="mark" viewBox="0 0 44 40" aria-hidden="true" focusable="false">
  <path d="M22 3 L41 37 H3 Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/>
  <path d="M22 19 L28.5 31 H15.5 Z" fill="currentColor"/>
</svg>"""

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 44 40'%3E"
    "%3Cpath d='M22 3 L41 37 H3 Z' fill='none' stroke='%23123a5f' stroke-width='3'/%3E"
    "%3Cpath d='M22 19 L28.5 31 H15.5 Z' fill='%23b98a2f'/%3E%3C/svg%3E"
)

# Simple, professional line icons (48px grid, 2.5px stroke).
ICONS = {
    "compass": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <circle cx="24" cy="24" r="18" fill="none" stroke="currentColor" stroke-width="2.5"/>
  <path d="M30.5 17.5 L26.5 26.5 L17.5 30.5 L21.5 21.5 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
</svg>""",
    "chart": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M8 40 H40" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M10 32 L19 22 L26 27 L38 13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M31 12 H39 V20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "shield": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M24 5 L39 11 V23 C39 33 33 39.5 24 43 C15 39.5 9 33 9 23 V11 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M17.5 24 L22 28.5 L30.5 19.5" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "ledger": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <rect x="11" y="6" width="26" height="36" rx="3" fill="none" stroke="currentColor" stroke-width="2.5"/>
  <path d="M17 15 H31 M17 22 H31 M17 29 H25" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
</svg>""",
    "people": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <circle cx="18" cy="17" r="6" fill="none" stroke="currentColor" stroke-width="2.5"/>
  <path d="M7 38 C7 31 12 27 18 27 C24 27 29 31 29 38" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="33" cy="18" r="4.5" fill="none" stroke="currentColor" stroke-width="2.5"/>
  <path d="M32 26.5 C37.5 26.5 41 30 41 36" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
</svg>""",
    "home": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M8 22 L24 8 L40 22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 20 V40 H36 V20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M20 40 V29 H28 V40" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
</svg>""",
    "handshake": """<svg class="icon" viewBox="0 0 48 48" aria-hidden="true">
  <path d="M4 16 H12 V32 H4 M44 16 H36 V32 H44" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M12 28 L20 34 C22 35.5 24.5 35 26 33.5 L36 24 M12 18 L20 14 L28 18 L23 23 C21.5 24.5 19 24.5 17.5 23 L12 18 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
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
    items.append('<li><a class="btn btn-gold nav-cta" href="/contact-us/">Schedule a conversation</a></li>')
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

  <div class="utility">
    <div class="wrap utility-inner">
      <span>{ADDRESS_LINES[0]}, {ADDRESS_LINES[1]}</span>
      <span>
        <a href="tel:+16182813444">Office {PHONE_OFFICE}</a>
        &nbsp;&middot;&nbsp;
        <a href="tel:+18448949822">Toll-Free {PHONE_TOLLFREE}</a>
      </span>
    </div>
  </div>

  <header class="masthead" id="site-header">
    <div class="wrap masthead-inner">
      <a class="wordmark" href="/" aria-label="Triada Advisors home">
        {MARK_SVG}
        <span>Triada Advisors<small>Columbia, Illinois</small></span>
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
    </div>
  </header>

  <main id="main">
{body}
  </main>

  <footer class="colophon">
    <div class="wrap colophon-grid">
      <div>
        <a class="wordmark" href="/">
          {MARK_SVG}
          <span>Triada Advisors<small>Columbia, Illinois</small></span>
        </a>
        <p class="colophon-tag">Plan wisely. Invest intently. Live fully.</p>
        <p class="social-links">
          <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
          <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>
        </p>
      </div>
      <div>
        <h2>Contact</h2>
        <p>{address}</p>
        <p>
          Office <a href="tel:+16182813444">{PHONE_OFFICE}</a><br>
          Toll-Free <a href="tel:+18448949822">{PHONE_TOLLFREE}</a><br>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </p>
      </div>
      <nav aria-label="Footer">
        <h2>Explore</h2>
        <ul class="colophon-links">
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
        <ul class="colophon-links">
          <li><a href="{LINKS['brokercheck']}" rel="noopener" target="_blank">FINRA BrokerCheck</a></li>
          <li><a href="{LINKS['lpl_crs']}" rel="noopener" target="_blank">LPL Relationship Summary (Form CRS)</a></li>
          <li><a href="{LINKS['lpl']}" rel="noopener" target="_blank">LPL Financial</a></li>
          <li><a href="{LINKS['cornerstone']}" rel="noopener" target="_blank">Cornerstone Wealth Management</a></li>
          <li><a href="{LINKS['finra']}" rel="noopener" target="_blank">FINRA</a></li>
          <li><a href="{LINKS['sipc']}" rel="noopener" target="_blank">SIPC</a></li>
        </ul>
      </nav>
    </div>
    <div class="wrap">
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
        }}, {{ threshold: 0.12, rootMargin: '0px 0px -30px 0px' }});
        revealables.forEach(function (el) {{ io.observe(el); }});
      }} else {{
        revealables.forEach(function (el) {{ el.classList.add('is-visible'); }});
      }}
    }})();
  </script>
</body>
</html>
"""


def page_hero(eyebrow, heading, lede=""):
    lede_html = f'\n        <p class="lede reveal">{lede}</p>' if lede else ""
    return f"""    <section class="hero">
      <div class="wrap" style="padding-top:clamp(2.6rem,6vh,4rem);padding-bottom:clamp(2.2rem,5vh,3.2rem);">
        <span class="eyebrow reveal">{eyebrow}</span>
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
    ("Client Services", "Here for you, every day"),
    ("Cornerstone Wealth Management", "Investment &amp; research partners"),
]


def initials(m):
    return "".join(part[0] for part in m["slug"].split("-")[:2]).upper()


def person_card(m, delay):
    return f"""            <a class="person reveal" style="--d:{delay}ms" href="/team/{m['slug']}/">
              <span class="portrait" aria-hidden="true">{initials(m)}</span>
              <span class="person-name">{m['name']}</span>
              <span class="person-title">{m['title']}</span>
              <span class="person-link">View profile &rarr;</span>
            </a>"""


def team_index_body():
    out = [page_hero(
        "Our Team",
        "Experienced professionals,<br>invested in you.",
        "A teamwork approach adds broader perspective &mdash; and greater "
        "benefit &mdash; to every client relationship.",
    )]
    for i, (group, label) in enumerate(TEAM_GROUPS):
        wash = " wash" if i % 2 == 1 else ""
        cards, d = [], 0
        for m in TEAM:
            if m["group"] != group:
                continue
            cards.append(person_card(m, d))
            d += 70
        cards_html = "\n".join(cards)
        out.append(f"""    <section class="sec{wash}">
      <div class="wrap">
        <div class="sec-head reveal">
          <span class="eyebrow">{label}</span>
          <h2>{group}</h2>
        </div>
        <div class="person-grid">
{cards_html}
        </div>
      </div>
    </section>
""")
    return "\n".join(out)


def team_member_body(m):
    first = m["name"].split(",")[0].split()[0]
    return page_hero(m["group"], m["name"], m["title"]) + f"""
    <section class="sec">
      <div class="wrap member-grid">
        <div class="portrait portrait-lg reveal" aria-hidden="true">{initials(m)}</div>
        <div class="reveal">
          <p class="lede">{m['bio']}</p>
          <p>
            To connect with {first} or any member of the Triada Advisors
            team, call our office at
            <a href="tel:+16182813444">{PHONE_OFFICE}</a> or
            <a href="/contact-us/">send us a message</a>.
          </p>
          <div class="btn-row">
            <a class="btn" href="/contact-us/">Schedule a conversation</a>
            <a class="btn btn-ghost" href="/team/">&larr; Back to the team</a>
          </div>
        </div>
      </div>
    </section>
"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

CTA_BAND = f"""    <section class="cta-band">
      <div class="wrap cta-inner">
        <div class="reveal">
          <h2>Let&rsquo;s talk about your future.</h2>
          <p>Call <a href="tel:+16182813444">{PHONE_OFFICE}</a> or request a
          time that works for you. No pressure, no obligation &mdash; just a
          conversation about your goals.</p>
        </div>
        <div class="cta-actions reveal">
          <a class="btn btn-gold" href="/contact-us/">Schedule a conversation</a>
        </div>
      </div>
    </section>
"""

TRUSTBAR = f"""    <div class="trustbar">
      <div class="wrap trustbar-inner">
        <div class="trust reveal" style="--d:0ms">{ICONS['handshake']}<span><b>20+ years</b> serving families like yours</span></div>
        <div class="trust reveal" style="--d:80ms">{ICONS['people']}<span><b>CFP&reg;, CPA, CFA</b> credentials on your team</span></div>
        <div class="trust reveal" style="--d:160ms">{ICONS['shield']}<span><b>Objective advice</b> &mdash; no proprietary products</span></div>
        <div class="trust reveal" style="--d:240ms">{ICONS['home']}<span><b>Locally owned</b> in Columbia, Illinois</span></div>
      </div>
    </div>
"""

HOME_BODY = f"""    <section class="hero">
      <div class="wrap hero-inner">
        <div>
          <span class="eyebrow reveal is-visible">Financial planning &middot; Investments &middot; Insurance</span>
          <h1 class="reveal is-visible">Feel confident in your financial future.</h1>
          <p class="lede reveal is-visible" style="--d:100ms">
            For more than 20 years, families in Columbia, Illinois and across
            the country have trusted Triada Advisors to help them plan
            wisely, invest intently, and live fully. Wherever you are on
            your journey, we&rsquo;ll meet you there.
          </p>
          <div class="btn-row reveal is-visible" style="--d:200ms">
            <a class="btn btn-gold" href="/contact-us/">Schedule a conversation</a>
            <a class="btn btn-ghost" href="/your-experience/">See how we work</a>
          </div>
          <p class="hero-note reveal is-visible" style="--d:300ms">
            {MARK_SVG} Independent guidance through Cornerstone Wealth
            Management and LPL Financial.
          </p>
        </div>
        <div class="hero-visual reveal is-visible" style="--d:150ms" aria-hidden="true">
          {MARK_SVG}
          <div class="visual-caption">
            <strong>Plan wisely. Invest intently. Live fully.</strong>
            Serving Columbia, Illinois and clients nationwide.
          </div>
        </div>
      </div>
    </section>

{TRUSTBAR}

    <section class="sec">
      <div class="wrap">
        <div class="sec-head-row">
          <div class="sec-head reveal">
            <span class="eyebrow">What we do</span>
            <h2>Guidance for every part of your financial life.</h2>
          </div>
          <a class="text-link reveal" href="/our-solutions/">View all solutions &rarr;</a>
        </div>
        <div class="card-grid">
          <a class="card reveal" style="--d:0ms" href="/our-solutions/">
            {ICONS['compass']}
            <h3>Financial Planning</h3>
            <p>A sound plan connects every corner of your financial life
            &mdash; cash flow, retirement, taxes, education, and estate
            considerations &mdash; into one clear picture.</p>
            <span class="card-link">Learn more &rarr;</span>
          </a>
          <a class="card reveal" style="--d:100ms" href="/our-solutions/">
            {ICONS['chart']}
            <h3>Investment Management</h3>
            <p>Your strategy is customized to your needs &mdash; and your
            needs alone &mdash; backed by institutional-caliber research.</p>
            <span class="card-link">Learn more &rarr;</span>
          </a>
          <a class="card reveal" style="--d:200ms" href="/our-solutions/">
            {ICONS['shield']}
            <h3>Insurance Consulting</h3>
            <p>Experienced guidance to assess your coverage and protect
            your income, your family, and your plan.</p>
            <span class="card-link">Learn more &rarr;</span>
          </a>
        </div>
      </div>
    </section>

    <section class="sec wash">
      <div class="wrap">
        <div class="sec-head center reveal">
          <span class="eyebrow">Who we serve</span>
          <h2>Wherever you are on your journey.</h2>
        </div>
        <div class="card-grid">
          <div class="card reveal" style="--d:0ms">
            {ICONS['home']}
            <h3>Family Business Owners</h3>
            <p>You&rsquo;ve built something that matters. We help you
            coordinate business and personal wealth, plan succession, and
            protect the transition you&rsquo;ve earned.</p>
          </div>
          <div class="card reveal" style="--d:100ms">
            {ICONS['handshake']}
            <h3>Retirees</h3>
            <p>You&rsquo;ve saved for decades. We help you turn those
            savings into dependable income &mdash; and protect what
            you&rsquo;ve built for the people you love.</p>
          </div>
          <div class="card reveal" style="--d:200ms">
            {ICONS['chart']}
            <h3>Wealth Builders</h3>
            <p>Your career and family are growing. We bring discipline to
            the decisions that compound into tomorrow&rsquo;s freedom.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="stats">
      <div class="wrap stats-inner">
        <div class="stat reveal" style="--d:0ms"><b>20+</b><span>Years serving clients</span><i></i></div>
        <div class="stat reveal" style="--d:80ms"><b>3</b><span>Advisors on your team</span><i></i></div>
        <div class="stat reveal" style="--d:160ms"><b>2</b><span>Decades of client relationships</span><i></i></div>
        <div class="stat reveal" style="--d:240ms"><b>1</b><span>Focus: your best interests</span><i></i></div>
      </div>
    </section>

    <section class="sec">
      <div class="wrap">
        <div class="sec-head-row">
          <div class="sec-head reveal">
            <span class="eyebrow">Your team</span>
            <h2>Advisors who know your name &mdash; and your goals.</h2>
          </div>
          <a class="text-link reveal" href="/team/">Meet the whole team &rarr;</a>
        </div>
        <div class="person-grid person-grid-3">
{person_card(TEAM[0], 0)}
{person_card(TEAM[1], 100)}
{person_card(TEAM[2], 200)}
        </div>
      </div>
    </section>

    <section class="sec wash quote">
      <div class="wrap reveal">
        {MARK_SVG}
        <blockquote>
          Establishing trust and caring about our clients&rsquo; best
          interests are of the utmost importance to us. It is never merely
          transactional &mdash; it is personal.
        </blockquote>
        <p class="quote-attr">The Triada Advisors philosophy</p>
      </div>
    </section>

{CTA_BAND}"""

ABOUT_BODY = page_hero(
    "About Us",
    "A firm built on trust,<br>focused on you.",
    "Based in the heart of Columbia, Illinois, Triada Advisors has "
    "supported the financial success and wellness of family business "
    "owners, retirees, and wealth builders for more than two decades.",
) + f"""
    <section class="sec">
      <div class="wrap">
        <div class="card-grid">
          <div class="card reveal" style="--d:0ms">
            {ICONS['people']}
            <h3>Personal by principle</h3>
            <p>When we work with you, it&rsquo;s never merely transactional
            &mdash; it&rsquo;s personal. We&rsquo;re proud to walk alongside
            you through life&rsquo;s biggest milestones, from building a
            career and starting a family to selling a business and stepping
            into retirement.</p>
          </div>
          <div class="card reveal" style="--d:100ms">
            {ICONS['chart']}
            <h3>Institutional resources</h3>
            <p>Through our relationship with Cornerstone Wealth Management,
            LLC, you receive personalized, tailored service with access to
            the same caliber of resources as large institutions.</p>
          </div>
          <div class="card reveal" style="--d:200ms">
            {ICONS['shield']}
            <h3>Objective advice</h3>
            <p>Because we&rsquo;re aligned with LPL Financial &mdash; one of
            the nation&rsquo;s largest independent broker-dealers &mdash;
            we&rsquo;re free to recommend what serves you. No proprietary
            products. No hidden agendas.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="stats">
      <div class="wrap stats-inner">
        <div class="stat reveal" style="--d:0ms"><b>20+</b><span>Years serving clients</span><i></i></div>
        <div class="stat reveal" style="--d:80ms"><b>3</b><span>Advisors on your team</span><i></i></div>
        <div class="stat reveal" style="--d:160ms"><b>1</b><span>Focus: your best interests</span><i></i></div>
      </div>
    </section>

    <section class="sec wash">
      <div class="wrap">
        <div class="sec-head center reveal">
          <span class="eyebrow">Who we serve</span>
          <h2>Clients at every stage of life.</h2>
        </div>
        <div class="card-grid">
          <div class="card reveal" style="--d:0ms">
            {ICONS['home']}
            <h3>Family Business Owners</h3>
            <p>Coordinating business and personal wealth, succession, and
            the transition you&rsquo;ve worked a lifetime to earn.</p>
          </div>
          <div class="card reveal" style="--d:100ms">
            {ICONS['handshake']}
            <h3>Retirees</h3>
            <p>Turning savings into dependable income and protecting what
            you&rsquo;ve built for the people you love.</p>
          </div>
          <div class="card reveal" style="--d:200ms">
            {ICONS['chart']}
            <h3>Wealth Builders</h3>
            <p>Disciplined strategies for growing careers and growing
            families &mdash; compounding into tomorrow&rsquo;s freedom.</p>
          </div>
        </div>
      </div>
    </section>

{CTA_BAND}"""

SOLUTIONS_BODY = page_hero(
    "Our Solutions",
    "Comprehensive guidance,<br>tailored to you.",
    "Through disciplined financial planning, investment management, and "
    "insurance consulting, we provide the expertise to help turn your "
    "life&rsquo;s goals into reality.",
) + f"""
    <section class="sec">
      <div class="wrap solution-list">
        <article class="solution reveal">
          {ICONS['compass']}
          <div>
            <h2>Financial Planning</h2>
            <p>
              A strong, sound financial plan encompasses many different
              aspects of your financial future &mdash; cash flow, retirement,
              taxes, education, estate considerations, and the goals that are
              uniquely yours. We build plans that connect those pieces into
              one clear picture, then revisit them with you as your life
              evolves.
            </p>
          </div>
        </article>
        <article class="solution reveal">
          {ICONS['chart']}
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
          {ICONS['shield']}
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
          {ICONS['ledger']}
          <div>
            <h2>Tax Coordination</h2>
            <p>
              Through Triada Tax Services LLC and the CPA credentials on our
              team, we help you keep your tax picture and your financial plan
              working together instead of at cross purposes.
            </p>
          </div>
        </article>
      </div>
    </section>

{CTA_BAND}"""

EXPERIENCE_BODY = page_hero(
    "Your Experience",
    "Living Intently&trade;",
    "Wealth is a means, not an end. Our Living Intently experience is an "
    "interactive way to assess your total well-being &mdash; family, "
    "health, work, purpose, and finances &mdash; and shape meaningful "
    "goals from that fuller picture.",
) + f"""
    <section class="sec">
      <div class="wrap">
        <div class="sec-head center reveal">
          <span class="eyebrow">What to expect</span>
          <h2>A clear, proven process.</h2>
        </div>
        <div class="step-grid">
          <div class="step reveal" style="--d:0ms">
            <span class="step-num">1</span>
            <h3>Discover</h3>
            <p>We listen first &mdash; your story, your values, your goals,
            and your concerns.</p>
          </div>
          <div class="step reveal" style="--d:100ms">
            <span class="step-num">2</span>
            <h3>Assess</h3>
            <p>Together we take stock of your total well-being and your
            complete financial picture.</p>
          </div>
          <div class="step reveal" style="--d:200ms">
            <span class="step-num">3</span>
            <h3>Design</h3>
            <p>We build a disciplined, personalized strategy across
            planning, investments, and protection.</p>
          </div>
          <div class="step reveal" style="--d:300ms">
            <span class="step-num">4</span>
            <h3>Live</h3>
            <p>We meet regularly, adjust as life changes, and keep your plan
            pointed at what matters.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="sec wash quote">
      <div class="wrap reveal">
        {MARK_SVG}
        <blockquote>
          The result is a plan with a &ldquo;why&rdquo; behind every number
          &mdash; and an advisor relationship built around the life you want
          to live, not just the assets you hold.
        </blockquote>
        <p class="quote-attr">Living Intently&trade;</p>
      </div>
    </section>

{CTA_BAND}"""

BLOG_BODY = page_hero(
    "Insights",
    "Perspective you can use.",
    "Commentary on markets, planning, and living intently &mdash; from the "
    "team that knows your plan.",
) + f"""
    <section class="sec">
      <div class="wrap narrow reveal">
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

{CTA_BAND}"""

EVENTS_BODY = page_hero(
    "Events &amp; Webinars",
    "Join us for our next event.",
    "Market update calls, webinars, and client events throughout the year.",
) + f"""
    <section class="sec">
      <div class="wrap narrow reveal">
        <p class="lede">
          Triada Advisors hosts periodic market update calls and client
          events. Upcoming events will be listed here. To be notified about
          the next one, call us at
          <a href="tel:+16182813444">{PHONE_OFFICE}</a>
          or <a href="/contact-us/">send us a message</a>.
        </p>
      </div>
    </section>

{CTA_BAND}"""

CONTACT_BODY = page_hero(
    "Contact Us",
    "We&rsquo;d be glad to talk.",
    "About the markets, your plan, or what&rsquo;s next for your family. "
    "Reach out anytime &mdash; there&rsquo;s no pressure and no obligation.",
) + f"""
    <section class="sec">
      <div class="wrap contact-grid">
        <div class="info-card reveal">
          <h2>Visit or call</h2>
          <p class="info-lines">
            <strong>Triada Advisors</strong><br>
            {ADDRESS_LINES[0]}<br>
            {ADDRESS_LINES[1]}
          </p>
          <p class="info-lines">
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
          <h2>Send us a message</h2>
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
    ("blog", "Insights | Triada Advisors",
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
