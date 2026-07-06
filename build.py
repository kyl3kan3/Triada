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


def nav_html(active_path):
    items = []
    for label, href in NAV:
        cls = ' class="active"' if href == active_path else ""
        items.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    return "\n            ".join(items)


def page_shell(*, title, description, active_path, body):
    address = "<br>".join(ADDRESS_LINES)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="stylesheet" href="/assets/css/styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>

  <div class="topbar">
    <div class="container topbar-inner">
      <span>{ADDRESS_LINES[0]}, {ADDRESS_LINES[1]}</span>
      <span>
        <a href="tel:+16182813444">Office: {PHONE_OFFICE}</a>
        <span aria-hidden="true">&middot;</span>
        <a href="tel:+18448949822">Toll-Free: {PHONE_TOLLFREE}</a>
      </span>
    </div>
  </div>

  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/">
        <span class="brand-mark" aria-hidden="true">&#9651;</span>
        <span class="brand-text">Triada <em>Advisors</em></span>
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">
        <span class="sr-only">Menu</span>&#9776;
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
    <div class="container footer-grid">
      <div>
        <h2 class="footer-brand">Triada <em>Advisors</em></h2>
        <p>{address}</p>
        <p>
          Office: <a href="tel:+16182813444">{PHONE_OFFICE}</a><br>
          Toll-Free: <a href="tel:+18448949822">{PHONE_TOLLFREE}</a><br>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </p>
        <p class="social-links">
          <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
          <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>
        </p>
      </div>
      <div>
        <h2>Quick Links</h2>
        <ul class="footer-links">
          <li><a href="/about-us/">About Us</a></li>
          <li><a href="/our-solutions/">Our Solutions</a></li>
          <li><a href="/your-experience/">Your Experience</a></li>
          <li><a href="/team/">Our Team</a></li>
          <li><a href="/blog/">Insights</a></li>
          <li><a href="/events/">Events</a></li>
          <li><a href="/contact-us/">Contact</a></li>
        </ul>
      </div>
      <div>
        <h2>Resources</h2>
        <ul class="footer-links">
          <li><a href="{LINKS['brokercheck']}" rel="noopener" target="_blank">FINRA BrokerCheck</a></li>
          <li><a href="{LINKS['lpl_crs']}" rel="noopener" target="_blank">LPL Relationship Summary (Form CRS)</a></li>
          <li><a href="{LINKS['lpl']}" rel="noopener" target="_blank">LPL Financial</a></li>
          <li><a href="{LINKS['cornerstone']}" rel="noopener" target="_blank">Cornerstone Wealth Management</a></li>
          <li><a href="{LINKS['finra']}" rel="noopener" target="_blank">FINRA</a></li>
          <li><a href="{LINKS['sipc']}" rel="noopener" target="_blank">SIPC</a></li>
        </ul>
      </div>
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
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      }});
    }})();
  </script>
</body>
</html>
"""


def hero(kicker, heading, lede, cta=None):
    cta_html = ""
    if cta:
        cta_html = f'\n        <p><a class="btn" href="{cta[1]}">{cta[0]}</a></p>'
    return f"""    <section class="hero">
      <div class="container">
        <p class="kicker">{kicker}</p>
        <h1>{heading}</h1>
        <p class="lede">{lede}</p>{cta_html}
      </div>
    </section>
"""


def page_hero(heading, lede=""):
    lede_html = f'\n        <p class="lede">{lede}</p>' if lede else ""
    return f"""    <section class="page-hero">
      <div class="container">
        <h1>{heading}</h1>{lede_html}
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

TEAM_GROUPS = ["Advisors", "Tax Services", "Client Services", "Cornerstone Wealth Management"]


def team_index_body():
    sections = []
    for group in TEAM_GROUPS:
        cards = []
        for m in TEAM:
            if m["group"] != group:
                continue
            initials = "".join(
                part[0] for part in m["slug"].split("-")[:2]
            ).upper()
            cards.append(f"""          <a class="team-card" href="/team/{m['slug']}/">
            <span class="team-avatar" aria-hidden="true">{initials}</span>
            <span class="team-name">{m['name']}</span>
            <span class="team-title">{m['title']}</span>
          </a>""")
        cards_html = "\n".join(cards)
        sections.append(f"""      <section class="container section">
        <h2>{group}</h2>
        <div class="team-grid">
{cards_html}
        </div>
      </section>""")
    sections_html = "\n".join(sections)
    return page_hero(
        "Our Team",
        "A teamwork approach adds broader perspective &mdash; and greater "
        "benefit &mdash; to every client relationship.",
    ) + f"""
{sections_html}
"""


def team_member_body(m):
    initials = "".join(part[0] for part in m["slug"].split("-")[:2]).upper()
    return page_hero(m["name"], m["title"]) + f"""
    <section class="container section member">
      <div class="member-grid">
        <div class="member-photo" aria-hidden="true">{initials}</div>
        <div>
          <p>{m['bio']}</p>
          <p>
            To connect with {m['name'].split(',')[0].split()[0]} or any member
            of the Triada Advisors team, call our office at
            <a href="tel:+16182813444">{PHONE_OFFICE}</a> or
            <a href="/contact-us/">send us a message</a>.
          </p>
          <p><a class="btn" href="/team/">&larr; Back to the team</a></p>
        </div>
      </div>
    </section>
"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

HOME_BODY = hero(
    "Columbia, Illinois &middot; Serving clients nationwide",
    "Feel confident in your financial future.",
    "For more than two decades, Triada Advisors has helped family business "
    "owners, retirees, and wealth builders pursue their long-term goals "
    "through disciplined financial planning, investment management, and "
    "insurance consulting.",
    cta=("Start the conversation", "/contact-us/"),
) + f"""
    <section class="container section">
      <h2>Built on trust. Focused on you.</h2>
      <div class="cols-2">
        <p>
          Our firm is rooted in a simple belief: earning your trust and
          caring about your best interests come before everything else.
          When we work with clients, it is never merely transactional &mdash;
          it is personal. We are proud to walk alongside you through
          life&rsquo;s biggest milestones, from building a career and
          starting a family to selling a business and stepping into
          retirement.
        </p>
        <p>
          Based in the heart of Columbia, Illinois, we serve neighbors here
          at home and clients across the country. Through our relationship
          with Cornerstone Wealth Management and our alignment with LPL
          Financial, we combine the personal service of a local firm with
          the resources of a large institution &mdash; and the freedom to
          offer objective, unbiased advice.
        </p>
      </div>
    </section>

    <section class="band">
      <div class="container feature-grid">
        <a class="feature" href="/our-solutions/">
          <h3>Financial Planning</h3>
          <p>A sound plan addresses every corner of your financial life &mdash;
          not just your portfolio.</p>
          <span class="feature-link">Explore our solutions &rarr;</span>
        </a>
        <a class="feature" href="/our-solutions/">
          <h3>Investment Management</h3>
          <p>No one-size-fits-all models. Every strategy is customized to
          your needs &mdash; and yours alone.</p>
          <span class="feature-link">Explore our solutions &rarr;</span>
        </a>
        <a class="feature" href="/our-solutions/">
          <h3>Insurance Consulting</h3>
          <p>Experienced guidance to assess your coverage and address the
          risks that matter.</p>
          <span class="feature-link">Explore our solutions &rarr;</span>
        </a>
      </div>
    </section>

    <section class="container section">
      <div class="cols-2 align-center">
        <div>
          <h2>Living Intently&trade;</h2>
          <p>
            Wealth is a means, not an end. Our Living Intently experience is
            an interactive way to assess your total well-being and shape
            meaningful personal and financial life goals &mdash; so your
            money serves the life you actually want to live.
          </p>
          <p><a class="btn btn-outline" href="/your-experience/">Discover your experience</a></p>
        </div>
        <div>
          <h2>A team in your corner</h2>
          <p>
            Three advisors. One coordinated team. Our teamwork approach adds
            broader perspective to every recommendation, backed by tax,
            client service, and investment professionals.
          </p>
          <p><a class="btn btn-outline" href="/team/">Meet the team</a></p>
        </div>
      </div>
    </section>

    <section class="cta-band">
      <div class="container">
        <h2>Ready to take the next step?</h2>
        <p>Call us at <a href="tel:+16182813444">{PHONE_OFFICE}</a> or send a
        message &mdash; we&rsquo;d be glad to talk.</p>
        <p><a class="btn" href="/contact-us/">Contact Triada Advisors</a></p>
      </div>
    </section>
"""

ABOUT_BODY = page_hero(
    "About Us",
    "Supporting the financial success and wellness of our clients for more "
    "than 20 years.",
) + """
    <section class="container section">
      <div class="cols-2">
        <div>
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
            shapes how we plan, how we invest, and how we communicate &mdash;
            in plain language, with your goals at the center.
          </p>
        </div>
        <div>
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
            free to provide truly objective, unbiased advice and investment
            recommendations. No proprietary products. No hidden agendas.
          </p>
        </div>
      </div>
    </section>

    <section class="band">
      <div class="container stats-grid">
        <div class="stat"><span class="stat-num">20+</span><span class="stat-label">Years serving clients</span></div>
        <div class="stat"><span class="stat-num">3</span><span class="stat-label">Advisors, one team</span></div>
        <div class="stat"><span class="stat-num">1</span><span class="stat-label">Focus: your best interests</span></div>
      </div>
    </section>

    <section class="container section">
      <h2>Who we serve</h2>
      <div class="feature-grid">
        <div class="feature">
          <h3>Family Business Owners</h3>
          <p>Coordinating business and personal wealth, succession, and the
          transition you&rsquo;ve worked a lifetime to earn.</p>
        </div>
        <div class="feature">
          <h3>Retirees</h3>
          <p>Turning savings into dependable income and protecting what
          you&rsquo;ve built for the people you love.</p>
        </div>
        <div class="feature">
          <h3>Wealth Builders</h3>
          <p>Disciplined strategies for growing careers and growing
          families &mdash; so today&rsquo;s decisions compound into
          tomorrow&rsquo;s freedom.</p>
        </div>
      </div>
      <p><a class="btn" href="/your-experience/">See what working with us looks like</a></p>
    </section>
"""

SOLUTIONS_BODY = page_hero(
    "Our Solutions",
    "Expertise and guidance to help turn your life&rsquo;s goals into "
    "reality.",
) + """
    <section class="container section">
      <article class="solution">
        <h2>Financial Planning</h2>
        <p>
          A strong, sound financial plan encompasses many different aspects
          of your financial future &mdash; cash flow, retirement, taxes,
          education, estate considerations, and the goals that are uniquely
          yours. We build plans that connect those pieces into one clear
          picture, then revisit them as your life evolves.
        </p>
      </article>
      <article class="solution">
        <h2>Investment Management</h2>
        <p>
          Rather than relying on a single solution or a model portfolio, we
          customize each strategy based on your needs &mdash; and your needs
          alone. Portfolios are managed with discipline and supported by the
          Cornerstone Wealth Portfolios investment team, giving you
          institutional-caliber research with personal accountability.
        </p>
      </article>
      <article class="solution">
        <h2>Insurance Consulting</h2>
        <p>
          With deep experience in the insurance marketplace and knowledge of
          the universe of options available, our advisors help you address
          insurance needs and assess appropriate coverage &mdash; protecting
          your income, your family, and your plan against the unexpected.
        </p>
      </article>
      <article class="solution">
        <h2>Tax Coordination</h2>
        <p>
          Through Triada Tax Services LLC and the CPA credentials on our
          team, we help clients keep their tax picture and financial plan
          working together instead of at cross purposes.
        </p>
      </article>
    </section>

    <section class="cta-band">
      <div class="container">
        <h2>Not sure where to start?</h2>
        <p>Every engagement begins with a conversation about you.</p>
        <p><a class="btn" href="/contact-us/">Talk with an advisor</a></p>
      </div>
    </section>
"""

EXPERIENCE_BODY = page_hero(
    "Your Experience",
    "Living Intently&trade; &mdash; an interactive approach to total "
    "well-being.",
) + """
    <section class="container section">
      <div class="cols-2">
        <div>
          <h2>More than money</h2>
          <p>
            Financial success and financial wellness are not the same thing.
            Our Living Intently experience invites you to step back and
            self-assess your total well-being &mdash; family, health, work,
            purpose, and finances &mdash; and then create meaningful personal
            and financial life goals from that fuller picture.
          </p>
          <p>
            The result is a plan with a &ldquo;why&rdquo; behind every number,
            and an advisor relationship built around the life you want to
            live &mdash; not just the assets you hold.
          </p>
        </div>
        <div>
          <h2>What to expect</h2>
          <ol class="steps">
            <li><strong>Discover.</strong> We listen first &mdash; your story,
            your values, your goals, and your concerns.</li>
            <li><strong>Assess.</strong> Together we take stock of your total
            well-being and your complete financial picture.</li>
            <li><strong>Design.</strong> We build a disciplined, personalized
            strategy across planning, investments, and protection.</li>
            <li><strong>Live.</strong> We meet regularly, adjust as life
            changes, and keep your plan pointed at what matters.</li>
          </ol>
        </div>
      </div>
    </section>

    <section class="cta-band">
      <div class="container">
        <h2>Begin living intently.</h2>
        <p><a class="btn" href="/contact-us/">Schedule a conversation</a></p>
      </div>
    </section>
"""

BLOG_BODY = page_hero(
    "Insights &amp; Intellect",
    "Perspective on markets, planning, and living intently.",
) + f"""
    <section class="container section">
      <p>
        Our team regularly shares market commentary, week-in-review notes,
        and planning insights. New posts will appear here &mdash; in the
        meantime, follow us on
        <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
        or <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>,
        or <a href="/contact-us/">contact us</a> to join our distribution
        list.
      </p>
    </section>
"""

EVENTS_BODY = page_hero(
    "Events &amp; Webinars",
    "Market update calls, webinars, and client events.",
) + f"""
    <section class="container section">
      <p>
        Triada Advisors hosts periodic market update calls and client
        events. Upcoming events will be listed here. To be notified about
        the next one, call us at <a href="tel:+16182813444">{PHONE_OFFICE}</a>
        or <a href="/contact-us/">send us a message</a>.
      </p>
    </section>
"""

CONTACT_BODY = page_hero(
    "Contact Us",
    "We&rsquo;d be glad to talk &mdash; about markets, your plan, or "
    "what&rsquo;s next.",
) + f"""
    <section class="container section">
      <div class="cols-2">
        <div>
          <h2>Visit or call</h2>
          <p>
            <strong>Triada Advisors</strong><br>
            {ADDRESS_LINES[0]}<br>
            {ADDRESS_LINES[1]}
          </p>
          <p>
            Office: <a href="tel:+16182813444">{PHONE_OFFICE}</a><br>
            Toll-Free: <a href="tel:+18448949822">{PHONE_TOLLFREE}</a><br>
            Email: <a href="mailto:{EMAIL}">{EMAIL}</a>
          </p>
          <p class="social-links">
            <a href="{LINKS['linkedin']}" rel="noopener" target="_blank">LinkedIn</a>
            <a href="{LINKS['facebook']}" rel="noopener" target="_blank">Facebook</a>
          </p>
        </div>
        <div>
          <h2>Send a message</h2>
          <form class="contact-form" action="mailto:{EMAIL}" method="get">
            <label for="cf-name">Name</label>
            <input id="cf-name" name="name" type="text" autocomplete="name" required>
            <label for="cf-email">Email</label>
            <input id="cf-email" name="email" type="email" autocomplete="email" required>
            <label for="cf-phone">Phone (optional)</label>
            <input id="cf-phone" name="phone" type="tel" autocomplete="tel">
            <label for="cf-message">How can we help?</label>
            <textarea id="cf-message" name="body" rows="5" required></textarea>
            <button class="btn" type="submit">Send message</button>
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
    ("", "Triada Advisors | Financial Planning &amp; Investment Management, Columbia IL",
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
    ("blog", "Insights &amp; Intellect | Triada Advisors",
     "Market commentary and planning insights from the Triada Advisors team.",
     "/blog/", BLOG_BODY),
    ("events", "Events &amp; Webinars | Triada Advisors",
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
        write(out, page_shell(title=title, description=desc, active_path=active, body=body))

    for m in TEAM:
        plain_name = m["name"].replace("&reg;", "®").replace("&trade;", "™")
        write(
            os.path.join(root, "team", m["slug"], "index.html"),
            page_shell(
                title=f"{plain_name} | Triada Advisors",
                description=f"{plain_name} — {m['title']} at Triada Advisors in Columbia, Illinois.",
                active_path="/team/",
                body=team_member_body(m),
            ),
        )

    for slug, target in REDIRECTS:
        write(os.path.join(root, slug, "index.html"), redirect_page(target))


if __name__ == "__main__":
    main()
