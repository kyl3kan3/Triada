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
# Brand assets — the "triad" mark drawn in fine line-work.
# ---------------------------------------------------------------------------

MARK_SVG = """<svg class="mark" viewBox="0 0 44 40" aria-hidden="true" focusable="false">
  <path d="M22 3 L41 37 H3 Z" fill="none" stroke="currentColor" stroke-width="1.1"/>
  <path d="M22 13.5 L31.5 30.5 H12.5 Z" fill="none" stroke="currentColor" stroke-width="1.1"/>
  <path d="M22 22.5 L26.2 30.5 H17.8 Z" fill="currentColor"/>
</svg>"""

HERO_LINEART = """<svg class="hero-lines" viewBox="0 0 400 360" aria-hidden="true" focusable="false">
  <g fill="none" stroke="currentColor" stroke-width="1">
    <path d="M200 10 L390 350 H10 Z"/>
    <path d="M200 52 L366 350 H34 Z" opacity=".75"/>
    <path d="M200 94 L342 350 H58 Z" opacity=".55"/>
    <path d="M200 136 L318 350 H82 Z" opacity=".4"/>
    <path d="M200 178 L294 350 H106 Z" opacity=".3"/>
    <path d="M200 220 L270 350 H130 Z" opacity=".22"/>
    <path d="M200 262 L246 350 H154 Z" opacity=".16"/>
  </g>
  <path d="M200 296 L226 350 H174 Z" fill="currentColor" opacity=".5"/>
</svg>"""

DRIFT_TRIANGLE = """<svg viewBox="0 0 44 40"><path d="M22 3 L41 37 H3 Z" fill="none" stroke="currentColor" stroke-width="1"/></svg>"""

_MARQUEE_SEQ = (
    "<span>Plan wisely</span><b>&#10022;</b>"
    "<span>Invest intently</span><b>&#10022;</b>"
    "<span>Live fully</span><b>&#10022;</b>"
) * 3
# Track is two identical halves; the animation translates -50% for a seamless loop.
MARQUEE = f"""    <div class="marquee" aria-hidden="true">
      <div class="marquee-track">{_MARQUEE_SEQ}{_MARQUEE_SEQ}</div>
    </div>
"""
MARQUEE_REVERSE = MARQUEE.replace('class="marquee"', 'class="marquee reverse"')

AURORA = '<div class="aurora" aria-hidden="true"></div>'

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 44 40'%3E"
    "%3Cpath d='M22 3 L41 37 H3 Z' fill='none' stroke='%239a7b3f' stroke-width='2'/%3E"
    "%3Cpath d='M22 13.5 L31.5 30.5 H12.5 Z' fill='none' stroke='%239a7b3f' stroke-width='2'/%3E"
    "%3Cpath d='M22 22.5 L26.2 30.5 H17.8 Z' fill='%239a7b3f'/%3E%3C/svg%3E"
)

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

  <div class="topline">
    <div class="frame topline-inner">
      <span class="topline-item">{ADDRESS_LINES[0]}, {ADDRESS_LINES[1]}</span>
      <span class="topline-item"><a href="tel:+16182813444">Office {PHONE_OFFICE}</a></span>
      <span class="topline-item"><a href="tel:+18448949822">Toll-Free {PHONE_TOLLFREE}</a></span>
    </div>
  </div>

  <header class="masthead" id="site-header">
    <div class="frame masthead-inner">
      <a class="wordmark" href="/" aria-label="Triada Advisors home">
        {MARK_SVG}
        <span>Triada&thinsp;<i>Advisors</i></span>
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

{MARQUEE_REVERSE}
  <footer class="colophon">
    <div class="frame colophon-grid">
      <div class="colophon-brand">
        <a class="wordmark wordmark-light" href="/">
          {MARK_SVG}
          <span>Triada&thinsp;<i>Advisors</i></span>
        </a>
        <p class="colophon-tagline">Plan wisely. Invest intently.<br>Live fully.</p>
      </div>
      <div>
        <h2>Office</h2>
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
    <div class="frame">
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

      /* 3D tilt on plates */
      if (!reduced && window.matchMedia('(hover: hover)').matches) {{
        document.querySelectorAll('.plate').forEach(function (el) {{
          el.addEventListener('pointermove', function (e) {{
            var r = el.getBoundingClientRect();
            var x = (e.clientX - r.left) / r.width - 0.5;
            var y = (e.clientY - r.top) / r.height - 0.5;
            el.style.transform = 'perspective(800px) rotateY(' + (x * 10).toFixed(2) +
              'deg) rotateX(' + (-y * 10).toFixed(2) + 'deg) translateY(-4px)';
          }});
          el.addEventListener('pointerleave', function () {{ el.style.transform = ''; }});
        }});
      }}

      /* Cursor glow + parallax in hero */
      var glow = document.querySelector('.glow');
      if (glow && !reduced) {{
        glow.parentElement.addEventListener('pointermove', function (e) {{
          var r = glow.getBoundingClientRect();
          glow.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
          glow.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
        }}, {{ passive: true }});
      }}
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

      /* 3D wireframe triad — rotating tetrahedra on canvas */
      var cv = document.getElementById('triad3d');
      if (cv && !reduced && cv.getContext) {{
        cv.parentElement.classList.add('has-3d');
        var ctx = cv.getContext('2d');
        var dpr = Math.min(window.devicePixelRatio || 1, 2);
        var size = function () {{
          var r = cv.getBoundingClientRect();
          cv.width = r.width * dpr; cv.height = r.height * dpr;
        }};
        size();
        window.addEventListener('resize', size);

        var V = [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]];
        var E = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]];
        var mx = 0, my = 0;
        window.addEventListener('pointermove', function (e) {{
          mx = e.clientX / window.innerWidth - 0.5;
          my = e.clientY / window.innerHeight - 0.5;
        }}, {{ passive: true }});

        var project = function (v, ax, ay, scale, w, h) {{
          var ca = Math.cos(ax), sa = Math.sin(ax);
          var cb = Math.cos(ay), sb = Math.sin(ay);
          var x1 = v[0] * cb + v[2] * sb, z1 = -v[0] * sb + v[2] * cb;
          var y1 = v[1] * ca - z1 * sa, z2 = v[1] * sa + z1 * ca;
          var f = 3 / (3 + z2);
          return [w / 2 + x1 * f * scale, h / 2 + y1 * f * scale, z2];
        }};

        var t = 0;
        var draw = function () {{
          requestAnimationFrame(draw);
          t += 0.0045;
          var w = cv.width, h = cv.height;
          var s = Math.min(w, h) / 3.1;
          ctx.clearRect(0, 0, w, h);
          [
            {{ scale: 1,    ax: t * 0.7 + my,       ay: t + mx * 1.6,        alpha: 1 }},
            {{ scale: 0.55, ax: -t * 0.9 - my * .6, ay: -t * 1.3 - mx,       alpha: 0.55 }},
            {{ scale: 0.28, ax: t * 1.4 + my * .3,  ay: t * 1.8 + mx * .5,   alpha: 0.35 }}
          ].forEach(function (o) {{
            var P = V.map(function (v) {{ return project(v, o.ax, o.ay, s * o.scale, w, h); }});
            E.forEach(function (e) {{
              var a = P[e[0]], b = P[e[1]];
              var depth = 1 - ((a[2] + b[2]) / 2 + 1.8) / 3.6;
              ctx.beginPath();
              ctx.moveTo(a[0], a[1]);
              ctx.lineTo(b[0], b[1]);
              ctx.strokeStyle = 'rgba(212,175,90,' + (o.alpha * (0.25 + depth * 0.75)).toFixed(3) + ')';
              ctx.lineWidth = dpr * (0.6 + depth * 1.1);
              ctx.stroke();
            }});
            P.forEach(function (p) {{
              var depth = 1 - (p[2] + 1.8) / 3.6;
              ctx.beginPath();
              ctx.arc(p[0], p[1], dpr * (1.2 + depth * 2.2), 0, 6.2832);
              ctx.fillStyle = 'rgba(242,215,141,' + (o.alpha * (0.3 + depth * 0.7)).toFixed(3) + ')';
              ctx.fill();
            }});
          }});
        }};
        draw();
      }}
    }})();
  </script>
</body>
</html>
"""


def chapter_open(index, label, *, dark=False):
    """Magazine-style section: numbered margin label + content column."""
    cls = "chapter dark" if dark else "chapter"
    return f"""    <section class="{cls}">
      <div class="frame chapter-grid">
        <div class="chapter-label reveal">
          <span class="chapter-index">{index}</span>
          <span class="chapter-name">{label}</span>
        </div>
        <div class="chapter-body">
"""

CHAPTER_CLOSE = """        </div>
      </div>
    </section>
"""


def arrow_link(href, label):
    return (f'<a class="arrow-link" href="{href}">{label}'
            f'<span class="arrow" aria-hidden="true">&#8594;</span></a>')


def page_hero(eyebrow, heading, lede=""):
    lede_html = f'\n        <p class="hero-lede reveal">{lede}</p>' if lede else ""
    return f"""    <section class="page-plate">
      {AURORA}
      <div class="drift" style="top:18%; right:10%; width:44px; --t:9s;" aria-hidden="true">{DRIFT_TRIANGLE}</div>
      <div class="frame">
        <p class="eyebrow reveal">{eyebrow}</p>
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
    return ".".join(part[0] for part in m["slug"].split("-")[:2]).upper() + "."


def team_plate(m, idx, delay):
    return f"""            <a class="plate reveal" style="--d:{delay}ms" href="/team/{m['slug']}/">
              <span class="plate-top">
                <span class="plate-index">{idx:02d}</span>
                <span class="plate-mono" aria-hidden="true">{initials(m)}</span>
              </span>
              <span class="plate-name">{m['name']}</span>
              <span class="plate-title">{m['title']}</span>
              <span class="plate-cta">Profile <span class="arrow" aria-hidden="true">&#8594;</span></span>
            </a>"""


def team_index_body():
    out = [page_hero(
        "The people behind the plan",
        "Our<br><em>Team.</em>",
        "A teamwork approach adds broader perspective &mdash; and greater "
        "benefit &mdash; to every client relationship.",
    )]
    n = 0
    for gi, (group, label) in enumerate(TEAM_GROUPS, start=1):
        plates, d = [], 0
        for m in TEAM:
            if m["group"] != group:
                continue
            n += 1
            plates.append(team_plate(m, n, d))
            d += 90
        plates_html = "\n".join(plates)
        out.append(chapter_open(f"{gi:02d}", label) + f"""          <h2 class="chapter-heading reveal">{group}</h2>
          <div class="plate-grid">
{plates_html}
          </div>
""" + CHAPTER_CLOSE)
    return "\n".join(out)


def team_member_body(m):
    first = m["name"].split(",")[0].split()[0]
    return page_hero(m["group"], f"{m['name'].replace(', ', ',<br><em>') + ('</em>' if ',' in m['name'] else '')}", m["title"]) + f"""
    <section class="chapter">
      <div class="frame chapter-grid">
        <div class="chapter-label reveal">
          <span class="plate-mono plate-mono-lg" aria-hidden="true">{initials(m)}</span>
        </div>
        <div class="chapter-body">
          <p class="statement reveal">{m['bio']}</p>
          <p class="reveal">
            To connect with {first} or any member of the Triada Advisors
            team, call our office at
            <a href="tel:+16182813444">{PHONE_OFFICE}</a> or
            <a href="/contact-us/">send us a message</a>.
          </p>
          <div class="link-row reveal">
            {arrow_link('/contact-us/', 'Start a conversation')}
            {arrow_link('/team/', 'Back to the team')}
          </div>
        </div>
      </div>
    </section>
"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

HOME_BODY = f"""    <section class="hero">
      {AURORA}
      <div class="glow" aria-hidden="true"></div>
      <div class="drift" style="top:12%; left:6%; width:52px; --t:8s;" data-plx="0.12" aria-hidden="true">{DRIFT_TRIANGLE}</div>
      <div class="drift" style="top:64%; left:44%; width:30px; --t:11s; opacity:.2;" data-plx="0.2" aria-hidden="true">{DRIFT_TRIANGLE}</div>
      <div class="drift" style="top:20%; right:8%; width:38px; --t:9.5s; opacity:.25;" data-plx="0.16" aria-hidden="true">{DRIFT_TRIANGLE}</div>
      <div class="frame hero-grid">
        <div class="hero-copy">
          <p class="eyebrow reveal is-visible">Columbia, Illinois &middot; Serving clients nationwide</p>
          <h1>
            <span class="w" style="--wd:60ms">Feel</span>
            <span class="w" style="--wd:140ms">confident</span><br>
            <span class="w" style="--wd:220ms">in</span>
            <span class="w" style="--wd:280ms">your</span><br>
            <span class="w" style="--wd:380ms"><em>financial</em></span>
            <span class="w" style="--wd:480ms"><em>future.</em></span>
          </h1>
          <p class="hero-lede reveal is-visible" style="--d:600ms">
            For more than two decades, Triada Advisors has helped family
            business owners, retirees, and wealth builders pursue their
            long-term goals through disciplined financial planning,
            investment management, and insurance consulting.
          </p>
          <div class="link-row reveal is-visible" style="--d:780ms">
            <a class="btn" href="/contact-us/">Start the conversation</a>
            {arrow_link('/your-experience/', 'Discover your experience')}
          </div>
        </div>
        <div class="hero-figure" aria-hidden="true">
          {HERO_LINEART}
          <canvas id="triad3d" class="hero-3d"></canvas>
        </div>
      </div>
      <div class="frame hero-foot" aria-hidden="true">
        <span>Est. two decades of stewardship</span>
        <span>Financial planning &middot; Investments &middot; Insurance</span>
        <span class="hero-scroll">Scroll <i></i></span>
      </div>
    </section>

{MARQUEE}

{chapter_open("01", "Our philosophy")}          <p class="statement reveal">
            Earning your trust and caring about your best interests come
            before everything else. When we work with clients, it is never
            merely transactional &mdash; <em>it is personal.</em>
          </p>
          <div class="prose-cols">
            <p class="reveal">
              We are proud to walk alongside you through life&rsquo;s biggest
              milestones, from building a career and starting a family to
              selling a business and stepping into retirement. Our firm is
              rooted in that simple conviction, and it shapes how we plan,
              how we invest, and how we communicate.
            </p>
            <p class="reveal">
              Based in the heart of Columbia, Illinois, we serve neighbors
              here at home and clients across the country. Through our
              relationship with Cornerstone Wealth Management and our
              alignment with LPL Financial, we combine the personal service
              of a local firm with the resources of a large institution
              &mdash; and the freedom to offer objective, unbiased advice.
            </p>
          </div>
{CHAPTER_CLOSE}
{chapter_open("02", "What we do")}          <h2 class="chapter-heading reveal">Three disciplines.<br><em>One plan.</em></h2>
          <div class="ledger">
            <a class="ledger-row reveal" href="/our-solutions/">
              <span class="ledger-num">01</span>
              <span class="ledger-title">Financial Planning</span>
              <span class="ledger-desc">A sound plan addresses every corner
              of your financial life &mdash; not just your portfolio.</span>
              <span class="arrow" aria-hidden="true">&#8594;</span>
            </a>
            <a class="ledger-row reveal" href="/our-solutions/">
              <span class="ledger-num">02</span>
              <span class="ledger-title">Investment Management</span>
              <span class="ledger-desc">No one-size-fits-all models. Every
              strategy is customized to your needs &mdash; and yours alone.</span>
              <span class="arrow" aria-hidden="true">&#8594;</span>
            </a>
            <a class="ledger-row reveal" href="/our-solutions/">
              <span class="ledger-num">03</span>
              <span class="ledger-title">Insurance Consulting</span>
              <span class="ledger-desc">Experienced guidance to assess your
              coverage and address the risks that matter.</span>
              <span class="arrow" aria-hidden="true">&#8594;</span>
            </a>
          </div>
{CHAPTER_CLOSE}
{chapter_open("03", "Your experience", dark=True)}          <h2 class="chapter-heading reveal">Living <em>Intently.</em>&trade;</h2>
          <p class="statement reveal">
            Wealth is a means, not an end. Our Living Intently experience is
            an interactive way to assess your total well-being and shape
            meaningful personal and financial life goals &mdash; so your
            money serves the life you actually want to live.
          </p>
          <div class="figures reveal">
            <div class="figure">
              <span class="figure-num"><span data-count="20" data-suffix="+">20+</span></span>
              <span class="figure-label">Years serving clients</span>
            </div>
            <div class="figure">
              <span class="figure-num"><span data-count="3">3</span></span>
              <span class="figure-label">Advisors, one team</span>
            </div>
            <div class="figure">
              <span class="figure-num"><span data-count="1">1</span></span>
              <span class="figure-label">Focus: your best interests</span>
            </div>
          </div>
          <div class="link-row reveal">
            {arrow_link('/your-experience/', 'Discover your experience')}
          </div>
{CHAPTER_CLOSE}
{chapter_open("04", "Your advisors")}          <h2 class="chapter-heading reveal">A team<br><em>in your corner.</em></h2>
          <div class="plate-grid">
{team_plate(TEAM[0], 1, 0)}
{team_plate(TEAM[1], 2, 90)}
{team_plate(TEAM[2], 3, 180)}
          </div>
          <div class="link-row reveal">
            {arrow_link('/team/', 'Meet everyone')}
          </div>
{CHAPTER_CLOSE}
    <section class="epigraph">
      <div class="aurora" aria-hidden="true"></div>
      <div class="frame reveal">
        {MARK_SVG}
        <blockquote>
          &ldquo;Establishing trust and caring about our clients&rsquo; best
          interests are of the utmost importance to us.&rdquo;
        </blockquote>
        <p class="epigraph-attr">The Triada Advisors philosophy</p>
      </div>
    </section>

    <section class="coda">
      <div class="aurora" aria-hidden="true"></div>
      <div class="frame coda-grid">
        <h2 class="reveal">Ready to take<br><em>the next step?</em></h2>
        <div class="coda-body reveal">
          <p>Call us at <a href="tel:+16182813444">{PHONE_OFFICE}</a> or send
          a message &mdash; we&rsquo;d be glad to talk.</p>
          <a class="btn" href="/contact-us/">Contact Triada Advisors</a>
        </div>
      </div>
    </section>
"""

ABOUT_BODY = page_hero(
    "More than 20 years of stewardship",
    "About<br><em>Us.</em>",
    "Supporting the financial success and wellness of our clients for more "
    "than two decades.",
) + f"""
{chapter_open("01", "Who we are")}          <p class="statement reveal">
            Rooted in Columbia, Illinois. Reaching nationwide. Built on the
            belief that trust is earned <em>one family at a time.</em>
          </p>
          <div class="prose-cols">
            <p class="reveal">
              Triada Advisors provides comprehensive investment management,
              insurance, and financial planning services. For more than two
              decades we have worked with family business owners, retirees,
              and wealth builders to help maximize their capital for
              long-term prosperity and growth.
            </p>
            <p class="reveal">
              Establishing trust and caring about our clients&rsquo; best
              interests are of the utmost importance to us. That conviction
              shapes how we plan, how we invest, and how we communicate
              &mdash; in plain language, with your goals at the center.
            </p>
          </div>
{CHAPTER_CLOSE}
{chapter_open("02", "How we're built")}          <h2 class="chapter-heading reveal">Independent<br><em>by design.</em></h2>
          <div class="ledger">
            <div class="ledger-row reveal">
              <span class="ledger-num">01</span>
              <span class="ledger-title">A local firm, personally invested</span>
              <span class="ledger-desc">You work directly with advisors who
              know you, your family, and your goals &mdash; neighbors, not a
              call center.</span>
            </div>
            <div class="ledger-row reveal">
              <span class="ledger-num">02</span>
              <span class="ledger-title">Institutional resources</span>
              <span class="ledger-desc">Through our relationship with
              Cornerstone Wealth Management, LLC, clients receive tailored
              service with access to the same caliber of resources as large
              institutions.</span>
            </div>
            <div class="ledger-row reveal">
              <span class="ledger-num">03</span>
              <span class="ledger-title">Objective, unbiased advice</span>
              <span class="ledger-desc">Aligned with LPL Financial &mdash;
              one of the nation&rsquo;s largest independent broker-dealers
              &mdash; we are free to recommend what serves you. No
              proprietary products. No hidden agendas.</span>
            </div>
          </div>
{CHAPTER_CLOSE}
{chapter_open("03", "Who we serve", dark=True)}          <h2 class="chapter-heading reveal">Clients at<br><em>every stage.</em></h2>
          <div class="ledger ledger-dark">
            <div class="ledger-row reveal">
              <span class="ledger-num">01</span>
              <span class="ledger-title">Family Business Owners</span>
              <span class="ledger-desc">Coordinating business and personal
              wealth, succession, and the transition you&rsquo;ve worked a
              lifetime to earn.</span>
            </div>
            <div class="ledger-row reveal">
              <span class="ledger-num">02</span>
              <span class="ledger-title">Retirees</span>
              <span class="ledger-desc">Turning savings into dependable
              income and protecting what you&rsquo;ve built for the people
              you love.</span>
            </div>
            <div class="ledger-row reveal">
              <span class="ledger-num">03</span>
              <span class="ledger-title">Wealth Builders</span>
              <span class="ledger-desc">Disciplined strategies for growing
              careers and growing families &mdash; so today&rsquo;s
              decisions compound into tomorrow&rsquo;s freedom.</span>
            </div>
          </div>
          <div class="link-row reveal">
            {arrow_link('/your-experience/', 'See what working with us looks like')}
          </div>
{CHAPTER_CLOSE}"""

SOLUTIONS_BODY = page_hero(
    "Comprehensive by design",
    "Our<br><em>Solutions.</em>",
    "Expertise and guidance to help turn your life&rsquo;s goals into "
    "reality.",
) + f"""
{chapter_open("01", "Financial Planning")}          <h2 class="chapter-heading reveal">Every corner of your<br><em>financial life.</em></h2>
          <p class="reveal">
            A strong, sound financial plan encompasses many different
            aspects of your financial future &mdash; cash flow, retirement,
            taxes, education, estate considerations, and the goals that are
            uniquely yours. We build plans that connect those pieces into
            one clear picture, then revisit them as your life evolves.
          </p>
{CHAPTER_CLOSE}
{chapter_open("02", "Investment Management")}          <h2 class="chapter-heading reveal">Your needs &mdash;<br><em>and yours alone.</em></h2>
          <p class="reveal">
            Rather than relying on a single solution or a model portfolio,
            we customize each strategy based on your needs. Portfolios are
            managed with discipline and supported by the Cornerstone Wealth
            Portfolios investment team, giving you institutional-caliber
            research with personal accountability.
          </p>
{CHAPTER_CLOSE}
{chapter_open("03", "Insurance Consulting")}          <h2 class="chapter-heading reveal">Protection for<br><em>the unexpected.</em></h2>
          <p class="reveal">
            With deep experience in the insurance marketplace and knowledge
            of the universe of options available, our advisors help you
            address insurance needs and assess appropriate coverage &mdash;
            protecting your income, your family, and your plan.
          </p>
{CHAPTER_CLOSE}
{chapter_open("04", "Tax Coordination")}          <h2 class="chapter-heading reveal">Working together,<br><em>not at cross purposes.</em></h2>
          <p class="reveal">
            Through Triada Tax Services LLC and the CPA credentials on our
            team, we help clients keep their tax picture and financial plan
            aligned.
          </p>
{CHAPTER_CLOSE}
    <section class="coda">
      <div class="aurora" aria-hidden="true"></div>
      <div class="frame coda-grid">
        <h2 class="reveal">Not sure<br><em>where to start?</em></h2>
        <div class="coda-body reveal">
          <p>Every engagement begins with a conversation about you.</p>
          <a class="btn" href="/contact-us/">Talk with an advisor</a>
        </div>
      </div>
    </section>
"""

EXPERIENCE_BODY = page_hero(
    "Living Intently&trade;",
    "Your<br><em>Experience.</em>",
    "An interactive approach to total well-being &mdash; and a plan with a "
    "&ldquo;why&rdquo; behind every number.",
) + f"""
{chapter_open("01", "More than money")}          <p class="statement reveal">
            Financial success and financial wellness are not the same thing.
            Wealth is a means, <em>not an end.</em>
          </p>
          <div class="prose-cols">
            <p class="reveal">
              Our Living Intently experience invites you to step back and
              self-assess your total well-being &mdash; family, health,
              work, purpose, and finances &mdash; and then create meaningful
              personal and financial life goals from that fuller picture.
            </p>
            <p class="reveal">
              The result is a plan with a &ldquo;why&rdquo; behind every
              number, and an advisor relationship built around the life you
              want to live &mdash; not just the assets you hold.
            </p>
          </div>
{CHAPTER_CLOSE}
{chapter_open("02", "What to expect")}          <h2 class="chapter-heading reveal">Four movements,<br><em>one rhythm.</em></h2>
          <div class="ledger">
            <div class="ledger-row reveal">
              <span class="ledger-num">01</span>
              <span class="ledger-title">Discover</span>
              <span class="ledger-desc">We listen first &mdash; your story,
              your values, your goals, and your concerns.</span>
            </div>
            <div class="ledger-row reveal">
              <span class="ledger-num">02</span>
              <span class="ledger-title">Assess</span>
              <span class="ledger-desc">Together we take stock of your total
              well-being and your complete financial picture.</span>
            </div>
            <div class="ledger-row reveal">
              <span class="ledger-num">03</span>
              <span class="ledger-title">Design</span>
              <span class="ledger-desc">We build a disciplined, personalized
              strategy across planning, investments, and protection.</span>
            </div>
            <div class="ledger-row reveal">
              <span class="ledger-num">04</span>
              <span class="ledger-title">Live</span>
              <span class="ledger-desc">We meet regularly, adjust as life
              changes, and keep your plan pointed at what matters.</span>
            </div>
          </div>
{CHAPTER_CLOSE}
    <section class="coda">
      <div class="aurora" aria-hidden="true"></div>
      <div class="frame coda-grid">
        <h2 class="reveal">Begin<br><em>living intently.</em></h2>
        <div class="coda-body reveal">
          <a class="btn" href="/contact-us/">Schedule a conversation</a>
        </div>
      </div>
    </section>
"""

BLOG_BODY = page_hero(
    "Insights &amp; intellect",
    "Our<br><em>Perspective.</em>",
    "Commentary on markets, planning, and living intently.",
) + f"""
{chapter_open("01", "Coming soon")}          <p class="reveal">
            Our team regularly shares market commentary, week-in-review
            notes, and planning insights. New posts will appear here &mdash;
            in the meantime, follow us on
            <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
            or <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>,
            or <a href="/contact-us/">contact us</a> to join our
            distribution list.
          </p>
{CHAPTER_CLOSE}"""

EVENTS_BODY = page_hero(
    "Calls, webinars &amp; gatherings",
    "Events &amp;<br><em>Webinars.</em>",
    "Market update calls, webinars, and client events.",
) + f"""
{chapter_open("01", "Upcoming")}          <p class="reveal">
            Triada Advisors hosts periodic market update calls and client
            events. Upcoming events will be listed here. To be notified
            about the next one, call us at
            <a href="tel:+16182813444">{PHONE_OFFICE}</a>
            or <a href="/contact-us/">send us a message</a>.
          </p>
{CHAPTER_CLOSE}"""

CONTACT_BODY = page_hero(
    "We&rsquo;d be glad to talk",
    "Contact<br><em>Us.</em>",
    "About markets, your plan, or what&rsquo;s next.",
) + f"""
{chapter_open("01", "Visit or call")}          <div class="contact-cols">
            <div class="reveal">
              <p class="contact-big">
                {ADDRESS_LINES[0]}<br>
                {ADDRESS_LINES[1]}
              </p>
              <p class="contact-big">
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
              <div class="field">
                <label for="cf-name">Name</label>
                <input id="cf-name" name="name" type="text" autocomplete="name" required>
              </div>
              <div class="field">
                <label for="cf-email">Email</label>
                <input id="cf-email" name="email" type="email" autocomplete="email" required>
              </div>
              <div class="field">
                <label for="cf-phone">Phone <span class="optional">(optional)</span></label>
                <input id="cf-phone" name="phone" type="tel" autocomplete="tel">
              </div>
              <div class="field">
                <label for="cf-message">How can we help?</label>
                <textarea id="cf-message" name="body" rows="4" required></textarea>
              </div>
              <button class="btn" type="submit">Send message</button>
              <p class="form-note">Please do not include account numbers or
              other sensitive personal information in this form.</p>
            </form>
          </div>
{CHAPTER_CLOSE}"""


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
