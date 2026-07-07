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
    ("About", "/about-us/"),
    ("Solutions", "/our-solutions/"),
    ("Experience", "/your-experience/"),
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
# Brand assets
# ---------------------------------------------------------------------------

MARK_SVG = """<svg class="mark" viewBox="0 0 44 40" aria-hidden="true" focusable="false">
  <path d="M22 3 L41 37 H3 Z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/>
  <path d="M22 20 L28 31 H16 Z" fill="currentColor"/>
</svg>"""

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 44 40'%3E"
    "%3Cpath d='M22 3 L41 37 H3 Z' fill='none' stroke='%23f2e8d8' stroke-width='3'/%3E"
    "%3Cpath d='M22 20 L28 31 H16 Z' fill='%23ff5c1f'/%3E%3C/svg%3E"
)

# Design-annotation overlay: dotted circle with orange selection handles.
def anno(size, top="", left="", right="", bottom="", extra=""):
    pos = ""
    if top: pos += f"top:{top};"
    if left: pos += f"left:{left};"
    if right: pos += f"right:{right};"
    if bottom: pos += f"bottom:{bottom};"
    return f"""<svg class="anno {extra}" style="width:{size};{pos}" viewBox="0 0 120 120" aria-hidden="true">
  <circle cx="60" cy="60" r="52" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="3 5"/>
  <circle cx="60" cy="60" r="34" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="2 4"/>
  <rect x="56" y="4" width="8" height="8" class="handle"/>
  <rect x="56" y="108" width="8" height="8" class="handle"/>
  <rect x="4" y="56" width="8" height="8" class="handle"/>
  <rect x="108" y="56" width="8" height="8" class="handle"/>
  <rect x="18" y="18" width="8" height="8" class="handle"/>
  <rect x="94" y="18" width="8" height="8" class="handle"/>
  <rect x="18" y="94" width="8" height="8" class="handle"/>
  <rect x="94" y="94" width="8" height="8" class="handle"/>
</svg>"""


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
  <div class="progress" aria-hidden="true"><i></i></div>

  <div class="strip" aria-hidden="true">
    <span>Made for families. Built for the long term.</span>
  </div>

  <header class="masthead" id="site-header">
    <div class="wide masthead-inner">
      <a class="wordmark" href="/" aria-label="Triada Advisors home">
        {MARK_SVG}
        <span>TRIADA</span>
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

  <aside class="side-tab" aria-hidden="true"><span>&#9679; Triada &mdash; Columbia, IL &mdash; est. 20+ yrs</span></aside>

  <main id="main">
{body}
  </main>

  <footer class="colophon">
    <div class="wide colophon-head">
      <span class="micro">Triada Advisors</span>
      <span class="micro">Columbia, Illinois</span>
      <span class="micro">Since the last millennium&rsquo;s final chapter</span>
    </div>
    <div class="wide colophon-grid">
      <div>
        <a class="wordmark wordmark-foot" href="/">
          {MARK_SVG}
          <span>TRIADA</span>
        </a>
        <p class="colophon-tag">Plan wisely. Invest intently.<br>Live fully.</p>
      </div>
      <div>
        <h2 class="micro">Office</h2>
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
        <h2 class="micro">Explore</h2>
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
        <h2 class="micro">Resources</h2>
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
    <div class="wide">
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

      /* ghost wordmark drifts slower than the page */
      if (!reduced) {{
        var plx = document.querySelectorAll('[data-plx]');
        if (plx.length) {{
          window.addEventListener('scroll', function () {{
            var y = window.scrollY;
            plx.forEach(function (el) {{
              el.style.transform = 'translate3d(0,' + (y * parseFloat(el.getAttribute('data-plx'))).toFixed(1) + 'px,0)';
            }});
          }}, {{ passive: true }});
        }}
      }}
    }})();
  </script>
</body>
</html>
"""


SCROLL_CUE = """      <div class="scroll-cue" aria-hidden="true"><span class="cue-dot"></span> Scroll to continue</div>"""


def micro_row(*labels):
    spans = "".join(f"<span>{l}</span>" for l in labels)
    return f'<div class="micro-row" aria-hidden="true">{spans}</div>'


def page_hero(index, label, heading, lede=""):
    lede_html = f'\n        <p class="plate-lede reveal">{lede}</p>' if lede else ""
    return f"""    <section class="plate">
      <div class="plate-glow" aria-hidden="true"></div>
      {anno("200px", top="14%", right="6%")}
      <div class="wide">
        <p class="micro accent reveal">{index} &mdash; {label}</p>
        <h1 class="reveal">{heading}</h1>{lede_html}
      </div>
      {micro_row("Triada Advisors", "Columbia, IL", index)}
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


def unit_card(m, idx, delay):
    return f"""            <a class="unit reveal" style="--d:{delay}ms" href="/team/{m['slug']}/">
              <span class="unit-head">
                <span class="micro">Unit {idx:02d}</span>
                <span class="micro accent">&#9679;</span>
              </span>
              <span class="unit-mono" aria-hidden="true">{initials(m)}</span>
              <span class="unit-name">{m['name']}</span>
              <span class="micro dim">{m['title']}</span>
              <span class="unit-go micro accent">View profile &#8594;</span>
            </a>"""


def team_index_body():
    out = [page_hero(
        "05", "Personnel file",
        "REAL PEOPLE.<br><span class='accent'>ONE TEAM.</span>",
        "A teamwork approach adds broader perspective &mdash; and greater "
        "benefit &mdash; to every client relationship.",
    )]
    n = 0
    for gi, (group, label) in enumerate(TEAM_GROUPS, start=1):
        cards, d = [], 0
        for m in TEAM:
            if m["group"] != group:
                continue
            n += 1
            cards.append(unit_card(m, n, d))
            d += 70
        cards_html = "\n".join(cards)
        out.append(f"""    <section class="sec">
      <div class="wide">
        <div class="sec-head reveal">
          <p class="micro accent">{gi:02d} &mdash; {label}</p>
          <h2>{group.upper()}</h2>
        </div>
        <div class="unit-grid">
{cards_html}
        </div>
      </div>
    </section>
""")
    return "\n".join(out)


def team_member_body(m, i):
    first = m["name"].split(",")[0].split()[0]
    return page_hero(
        f"Unit {i+1:02d}", m["group"],
        m["name"].upper().replace(", ", ",<br>"),
        m["title"],
    ) + f"""
    <section class="sec">
      <div class="wide member-grid">
        <div class="member-visual reveal">
          {anno("150%", top="-25%", left="-25%", extra="anno-slow")}
          <span class="unit-mono unit-mono-lg">{initials(m)}</span>
        </div>
        <div class="reveal">
          <p class="bigp">{m['bio']}</p>
          <p>
            To connect with {first} or any member of the Triada Advisors
            team, call our office at
            <a href="tel:+16182813444">{PHONE_OFFICE}</a> or
            <a href="/contact-us/">send us a message</a>.
          </p>
          <div class="btn-row">
            <a class="btn" href="/contact-us/">Start a conversation</a>
            <a class="btn btn-ghost" href="/team/">&larr; All personnel</a>
          </div>
        </div>
      </div>
    </section>
"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

HOME_BODY = f"""    <section class="hero">
      <div class="plate-glow" aria-hidden="true"></div>
      <div class="ghost" data-plx="0.18" aria-hidden="true">TRIADA</div>
      {anno("240px", top="16%", left="7%")}
      {anno("340px", top="30%", right="4%", extra="anno-slow")}
      <div class="wide hero-inner">
        <div class="hero-product reveal is-visible" aria-hidden="true">
          <span class="product-disc"><i class="mark-big">{MARK_SVG}</i></span>
        </div>
        <div class="hero-copy">
          <h1 class="reveal is-visible">THIS ISN&rsquo;T<br>JUST A PLAN.</h1>
          <p class="hero-side reveal is-visible" style="--d:150ms">
            It&rsquo;s two decades of helping family business owners,
            retirees, and wealth builders point their money at the lives
            they actually want.
          </p>
          <div class="btn-row reveal is-visible" style="--d:280ms">
            <a class="btn" href="/contact-us/">Start the conversation</a>
            <a class="btn btn-ghost" href="/your-experience/">Your experience</a>
          </div>
        </div>
      </div>
{SCROLL_CUE}
      {micro_row("Financial planning", "Investment management", "Insurance consulting", "Est. 20+ yrs")}
    </section>

    <section class="sec mat">
      <div class="mat-ruler" aria-hidden="true"></div>
      <div class="wide">
        <div class="sec-head reveal">
          <p class="micro accent">01 &mdash; The workbench</p>
          <h2>DISCIPLINED BY DESIGN.<br><span class="accent">MEASURED TWICE.</span></h2>
        </div>
        <div class="spec-grid">
          <a class="spec reveal" style="--d:0ms" href="/our-solutions/">
            <span class="micro accent">Spec 01</span>
            <h3>Financial Planning</h3>
            <p>Cash flow, retirement, taxes, education, estate &mdash; one
            plan that connects every corner of your financial life.</p>
            <span class="dotted-rule" aria-hidden="true"></span>
            <span class="micro">Revisited as life evolves &#8594;</span>
          </a>
          <a class="spec reveal" style="--d:110ms" href="/our-solutions/">
            <span class="micro accent">Spec 02</span>
            <h3>Investment Management</h3>
            <p>Customized to your needs &mdash; and yours alone &mdash; with
            institutional-caliber research behind every decision.</p>
            <span class="dotted-rule" aria-hidden="true"></span>
            <span class="micro">Model portfolios: none &#8594;</span>
          </a>
          <a class="spec reveal" style="--d:220ms" href="/our-solutions/">
            <span class="micro accent">Spec 03</span>
            <h3>Insurance Consulting</h3>
            <p>Deep marketplace experience to assess your coverage and
            address the risks that actually matter.</p>
            <span class="dotted-rule" aria-hidden="true"></span>
            <span class="micro">Protection, assessed &#8594;</span>
          </a>
          <a class="spec reveal" style="--d:330ms" href="/our-solutions/">
            <span class="micro accent">Spec 04</span>
            <h3>Tax Coordination</h3>
            <p>Through Triada Tax Services LLC, your tax picture and your
            plan work together &mdash; not at cross purposes.</p>
            <span class="dotted-rule" aria-hidden="true"></span>
            <span class="micro">CPAs on the bench &#8594;</span>
          </a>
        </div>
      </div>
    </section>

    <section class="sweep">
      <div class="sweep-scene" aria-hidden="true"></div>
      <div class="sweep-text" aria-hidden="true">LIVE&nbsp;FULLY.</div>
      <div class="wide sweep-caption reveal">
        <p class="micro">Living Intently&trade; &mdash; total well-being. No spreadsheet required.</p>
        <p class="sweep-sub">Family. Health. Work. Purpose. Finances. Our
        Living Intently experience shapes goals from the whole picture
        &mdash; then builds the plan to match.</p>
        <a class="btn btn-light" href="/your-experience/">Discover your experience</a>
      </div>
    </section>

    <section class="sec">
      <div class="wide">
        <div class="sec-head reveal">
          <p class="micro accent">02 &mdash; Choose your discipline</p>
          <h2>ALL INCLUDED.<br><span class="accent">NO UPSELL.</span></h2>
        </div>
        <div class="tiers reveal">
          <div class="tier">
            <p class="micro accent">Discipline</p>
            <h3>PLANNING</h3>
            <p class="micro dim">One plan. Every corner. Done thoughtfully.</p>
            <dl>
              <div><dt>Scope</dt><dd>Whole life</dd></div>
              <div><dt>Customization</dt><dd>Total</dd></div>
              <div><dt>Model portfolios</dt><dd>None</dd></div>
              <div><dt>Reviews</dt><dd>Ongoing</dd></div>
              <div><dt>Best for</dt><dd>Connecting all the pieces</dd></div>
            </dl>
          </div>
          <div class="tier tier-hi">
            <p class="micro accent">Discipline</p>
            <h3>INVESTMENTS</h3>
            <p class="micro dim">Your needs. Your strategy. Nothing off the rack.</p>
            <dl>
              <div><dt>Scope</dt><dd>Portfolio</dd></div>
              <div><dt>Customization</dt><dd>Total</dd></div>
              <div><dt>Model portfolios</dt><dd>None</dd></div>
              <div><dt>Reviews</dt><dd>Ongoing</dd></div>
              <div><dt>Best for</dt><dd>Long-term growth with discipline</dd></div>
            </dl>
          </div>
          <div class="tier">
            <p class="micro accent">Discipline</p>
            <h3>INSURANCE</h3>
            <p class="micro dim">Coverage that fits. Risks addressed.</p>
            <dl>
              <div><dt>Scope</dt><dd>Protection</dd></div>
              <div><dt>Customization</dt><dd>Total</dd></div>
              <div><dt>Model portfolios</dt><dd>N/A</dd></div>
              <div><dt>Reviews</dt><dd>Ongoing</dd></div>
              <div><dt>Best for</dt><dd>Guarding the plan against surprises</dd></div>
            </dl>
          </div>
        </div>
      </div>
    </section>

    <section class="numbers">
      <div class="ghost ghost-num" data-plx="0.12" aria-hidden="true">TRIADA-20</div>
      <div class="wide numbers-inner reveal">
        <div class="num"><span class="num-big"><span data-count="20" data-suffix="+">20+</span></span><span class="micro">Years serving clients</span></div>
        <div class="num"><span class="num-big"><span data-count="3">3</span></span><span class="micro">Advisors, one team</span></div>
        <div class="num"><span class="num-big"><span data-count="1">1</span></span><span class="micro">Focus: your best interests</span></div>
        <div class="num"><span class="num-big"><span data-count="0">0</span></span><span class="micro">Proprietary products pushed</span></div>
      </div>
    </section>

    <section class="sec">
      <div class="wide">
        <div class="sec-head reveal">
          <p class="micro accent">03 &mdash; Personnel</p>
          <h2>REAL PEOPLE.<br><span class="accent">NO CHATBOTS.</span></h2>
        </div>
        <div class="unit-grid unit-grid-3">
{unit_card(TEAM[0], 1, 0)}
{unit_card(TEAM[1], 2, 110)}
{unit_card(TEAM[2], 3, 220)}
        </div>
        <div class="btn-row reveal">
          <a class="btn btn-ghost" href="/team/">All personnel &#8594;</a>
        </div>
      </div>
    </section>

    <section class="coda">
      <div class="plate-glow" aria-hidden="true"></div>
      {anno("220px", bottom="10%", right="8%")}
      <div class="wide reveal">
        <p class="micro accent">04 &mdash; Transmission</p>
        <h2 class="coda-h">READY WHEN<br>YOU ARE.</h2>
        <p>Call <a href="tel:+16182813444">{PHONE_OFFICE}</a> or send a
        message &mdash; we&rsquo;d be glad to talk.</p>
        <a class="btn" href="/contact-us/">Contact Triada Advisors</a>
      </div>
      {micro_row("Triada Advisors", "Columbia, IL", "End of page 01")}
    </section>
"""

ABOUT_BODY = page_hero(
    "02", "The firm",
    "BUILT ON TRUST.<br><span class='accent'>FOCUSED ON YOU.</span>",
    "Supporting the financial success and wellness of our clients for more "
    "than two decades.",
) + f"""
    <section class="sec">
      <div class="wide two-col">
        <div class="reveal">
          <p class="micro accent">Who we are</p>
          <p class="bigp">
            Based in Columbia, Illinois, Triada Advisors provides
            comprehensive investment management, insurance, and financial
            planning services &mdash; for more than two decades, to family
            business owners, retirees, and wealth builders.
          </p>
          <p>
            Establishing trust and caring about our clients&rsquo; best
            interests are of the utmost importance to us. That conviction
            shapes how we plan, how we invest, and how we communicate
            &mdash; in plain language, with your goals at the center.
          </p>
        </div>
        <div class="reveal">
          <p class="micro accent">How we&rsquo;re built</p>
          <p class="bigp">
            Local service. Institutional resources. Independent advice.
          </p>
          <p>
            Through our relationship with Cornerstone Wealth Management,
            LLC, clients receive tailored service with access to the same
            caliber of resources as large institutions. And because we are
            aligned with LPL Financial &mdash; one of the nation&rsquo;s
            largest independent broker-dealers &mdash; we are free to
            recommend what serves you. No proprietary products. No hidden
            agendas.
          </p>
        </div>
      </div>
    </section>

    <section class="sec mat">
      <div class="mat-ruler" aria-hidden="true"></div>
      <div class="wide">
        <div class="sec-head reveal">
          <p class="micro accent">Who we serve</p>
          <h2>CLIENTS AT<br><span class="accent">EVERY STAGE.</span></h2>
        </div>
        <div class="spec-grid">
          <div class="spec reveal" style="--d:0ms">
            <span class="micro accent">File A</span>
            <h3>Family Business Owners</h3>
            <p>Business and personal wealth, succession, and the transition
            you&rsquo;ve worked a lifetime to earn.</p>
          </div>
          <div class="spec reveal" style="--d:110ms">
            <span class="micro accent">File B</span>
            <h3>Retirees</h3>
            <p>Savings turned into dependable income; what you&rsquo;ve
            built, protected for the people you love.</p>
          </div>
          <div class="spec reveal" style="--d:220ms">
            <span class="micro accent">File C</span>
            <h3>Wealth Builders</h3>
            <p>Disciplined strategies for growing careers and growing
            families &mdash; compounding into freedom.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="coda">
      <div class="plate-glow" aria-hidden="true"></div>
      <div class="wide reveal">
        <h2 class="coda-h">SEE HOW<br>WE WORK.</h2>
        <a class="btn" href="/your-experience/">Your experience</a>
      </div>
    </section>
"""

SOLUTIONS_BODY = page_hero(
    "03", "Capabilities",
    "FOUR DISCIPLINES.<br><span class='accent'>ONE PLAN.</span>",
    "Expertise and guidance to help turn your life&rsquo;s goals into "
    "reality.",
) + f"""
    <section class="sec mat">
      <div class="mat-ruler" aria-hidden="true"></div>
      <div class="wide spec-stack">
        <article class="spec spec-wide reveal">
          <span class="micro accent">Spec 01</span>
          <h2>FINANCIAL PLANNING</h2>
          <p>
            A strong, sound financial plan encompasses many different
            aspects of your financial future &mdash; cash flow, retirement,
            taxes, education, estate considerations, and the goals that are
            uniquely yours. We build plans that connect those pieces into
            one clear picture, then revisit them as your life evolves.
          </p>
          <span class="dotted-rule" aria-hidden="true"></span>
          <span class="micro">Status: living document</span>
        </article>
        <article class="spec spec-wide reveal">
          <span class="micro accent">Spec 02</span>
          <h2>INVESTMENT MANAGEMENT</h2>
          <p>
            Rather than relying on a single solution or a model portfolio,
            we customize each strategy based on your needs &mdash; and your
            needs alone. Portfolios are managed with discipline and
            supported by the Cornerstone Wealth Portfolios investment team,
            giving you institutional-caliber research with personal
            accountability.
          </p>
          <span class="dotted-rule" aria-hidden="true"></span>
          <span class="micro">Model portfolios: none</span>
        </article>
        <article class="spec spec-wide reveal">
          <span class="micro accent">Spec 03</span>
          <h2>INSURANCE CONSULTING</h2>
          <p>
            With deep experience in the insurance marketplace and knowledge
            of the universe of options available, our advisors help you
            address insurance needs and assess appropriate coverage &mdash;
            protecting your income, your family, and your plan against the
            unexpected.
          </p>
          <span class="dotted-rule" aria-hidden="true"></span>
          <span class="micro">Coverage: assessed, not assumed</span>
        </article>
        <article class="spec spec-wide reveal">
          <span class="micro accent">Spec 04</span>
          <h2>TAX COORDINATION</h2>
          <p>
            Through Triada Tax Services LLC and the CPA credentials on our
            team, we help clients keep their tax picture and financial plan
            working together instead of at cross purposes.
          </p>
          <span class="dotted-rule" aria-hidden="true"></span>
          <span class="micro">April: less dramatic</span>
        </article>
      </div>
    </section>

    <section class="coda">
      <div class="plate-glow" aria-hidden="true"></div>
      <div class="wide reveal">
        <h2 class="coda-h">NOT SURE WHERE<br>TO START?</h2>
        <p>Every engagement begins with a conversation about you.</p>
        <a class="btn" href="/contact-us/">Talk with an advisor</a>
      </div>
    </section>
"""

EXPERIENCE_BODY = page_hero(
    "04", "Living Intently&trade;",
    "WEALTH IS A MEANS.<br><span class='accent'>NOT AN END.</span>",
    "An interactive approach to total well-being &mdash; and a plan with a "
    "&ldquo;why&rdquo; behind every number.",
) + f"""
    <section class="sweep">
      <div class="sweep-scene" aria-hidden="true"></div>
      <div class="sweep-text" aria-hidden="true">LIVE&nbsp;FULLY.</div>
      <div class="wide sweep-caption reveal">
        <p class="micro">Family. Health. Work. Purpose. Finances.</p>
        <p class="sweep-sub">Our Living Intently experience invites you to
        self-assess your total well-being &mdash; then shape meaningful
        personal and financial goals from that fuller picture.</p>
      </div>
    </section>

    <section class="sec mat">
      <div class="mat-ruler" aria-hidden="true"></div>
      <div class="wide">
        <div class="sec-head reveal">
          <p class="micro accent">Operating procedure</p>
          <h2>FOUR MOVEMENTS.<br><span class="accent">ONE RHYTHM.</span></h2>
        </div>
        <div class="spec-grid">
          <div class="spec reveal" style="--d:0ms">
            <span class="micro accent">Step 01</span>
            <h3>Discover</h3>
            <p>We listen first &mdash; your story, your values, your goals,
            and your concerns.</p>
          </div>
          <div class="spec reveal" style="--d:110ms">
            <span class="micro accent">Step 02</span>
            <h3>Assess</h3>
            <p>Together we take stock of your total well-being and your
            complete financial picture.</p>
          </div>
          <div class="spec reveal" style="--d:220ms">
            <span class="micro accent">Step 03</span>
            <h3>Design</h3>
            <p>We build a disciplined, personalized strategy across
            planning, investments, and protection.</p>
          </div>
          <div class="spec reveal" style="--d:330ms">
            <span class="micro accent">Step 04</span>
            <h3>Live</h3>
            <p>We meet regularly, adjust as life changes, and keep your plan
            pointed at what matters.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="coda">
      <div class="plate-glow" aria-hidden="true"></div>
      <div class="wide reveal">
        <h2 class="coda-h">BEGIN LIVING<br>INTENTLY.</h2>
        <a class="btn" href="/contact-us/">Schedule a conversation</a>
      </div>
    </section>
"""

BLOG_BODY = page_hero(
    "06", "Insights &amp; intellect",
    "OUR<br><span class='accent'>PERSPECTIVE.</span>",
    "Commentary on markets, planning, and living intently.",
) + f"""
    <section class="sec">
      <div class="wide narrow reveal">
        <p class="bigp">
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
    "07", "Transmissions",
    "EVENTS &amp;<br><span class='accent'>WEBINARS.</span>",
    "Market update calls, webinars, and client events.",
) + f"""
    <section class="sec">
      <div class="wide narrow reveal">
        <p class="bigp">
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
    "08", "Transmission",
    "SAY<br><span class='accent'>HELLO.</span>",
    "About markets, your plan, or what&rsquo;s next.",
) + f"""
    <section class="sec">
      <div class="wide contact-grid">
        <div class="reveal">
          <p class="micro accent">Coordinates</p>
          <p class="bigp">
            {ADDRESS_LINES[0]}<br>
            {ADDRESS_LINES[1]}
          </p>
          <p class="bigp">
            <a href="tel:+16182813444">{PHONE_OFFICE}</a><br>
            <a href="tel:+18448949822">{PHONE_TOLLFREE}</a><br>
            <a href="mailto:{EMAIL}">{EMAIL}</a>
          </p>
          <p class="social-links">
            <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
            <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>
          </p>
        </div>
        <form class="contact-form reveal" action="mailto:{EMAIL}" method="get">
          <p class="micro accent">Form TR-01 &mdash; Inquiry</p>
          <div class="field-row">
            <div class="field">
              <label class="micro" for="cf-name">Name</label>
              <input id="cf-name" name="name" type="text" autocomplete="name" required>
            </div>
            <div class="field">
              <label class="micro" for="cf-phone">Phone (optional)</label>
              <input id="cf-phone" name="phone" type="tel" autocomplete="tel">
            </div>
          </div>
          <div class="field">
            <label class="micro" for="cf-email">Email</label>
            <input id="cf-email" name="email" type="email" autocomplete="email" required>
          </div>
          <div class="field">
            <label class="micro" for="cf-message">How can we help?</label>
            <textarea id="cf-message" name="body" rows="5" required></textarea>
          </div>
          <button class="btn" type="submit">Send message</button>
          <p class="micro dim">Please do not include account numbers or
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
