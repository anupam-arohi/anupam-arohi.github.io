#!/usr/bin/env python3
"""
sync.py  ·  keeps the shared shell identical across every site

The five sites live in separate repos with no build step, so the nav bar has to
physically exist in each HTML file. This script is what stops those copies from
drifting apart, which is exactly what happened before: six nav items on About,
four different ones on Photographs, none at all on the aurora guide.

WHAT IT DOES
  1. Copies _shared/site.css into every sibling repo.
  2. Rewrites the nav in every HTML file, between these markers:

         <!-- site-nav:start current="photos" -->
         ...anything here is replaced...
         <!-- site-nav:end -->

     The current="..." key is the ONE thing each page decides for itself. It
     controls which item gets aria-current="page". Everything else is generated.

     An optional class="..." attribute picks the CSS class on the <ul>, so the
     same nav can appear twice on a page in two different weights:

         <!-- site-nav:start current="about" class="footer-nav" -->

     It defaults to "nav", which is the header bar.

  3. Rewrites section nav (photos only) between site-subnav markers.

USAGE
    python3 _shared/sync.py            # write the changes
    python3 _shared/sync.py --check    # report drift, change nothing, exit 1 if any

TO CHANGE THE NAV
    Edit NAV below. Run the script. Commit each repo. That is the whole
    procedure. Never hand-edit a nav block in an HTML file: the next run
    overwrites it.

A NOTE ON THE URLS
    They are root-relative ("/about/") rather than absolute. This keeps them
    working if the sites ever move to a custom domain, and lets you serve all
    the repos from one local root to test cross-site links.
"""

import argparse
import pathlib
import re
import shutil
import sys

# ---------------------------------------------------------------------------
# The canonical nav. This list is the single source of truth for the whole site.
# Order matters and is deliberate: Home first, then who I am, then the work.
# ---------------------------------------------------------------------------
NAV = [
    # About IS the landing page, so it sits at "/" and there is no separate
    # Home item. A nav with both would give visitors two words for one place.
    # Labels stay short. A nav item is a signpost, not a description: the page
    # itself still says "The books that inspired me" in its h1.
    ("about",      "About",        "/"),
    ("photos",     "Photographs",  "/photos/"),
    ("auroras",    "Aurora guide", "/auroras/"),
    ("meditation", "Meditation",   "/meditation.html"),
    ("books",      "Books",        "/books/"),
    ("lv",         "Live Version", "/lv/"),
]

# Section navs: within-site navigation, rendered as a second, lighter row.
# Keyed by the set= attribute in the marker.
SUBNAV = {
    "photos": [
        ("all",    "All",    "/photos/"),
        ("series", "Series", "/photos/series/"),
    ],
}

# Repos that receive the shared shell, as directory names sitting beside the
# root repo. Add a new site here and it joins the constellation.
#
# "about" is deliberately absent. Its content became the root page, so the repo
# now serves only redirect stubs, which have no nav to keep in sync.
REPOS = ["books", "photos", "auroras"]

NAV_RE = re.compile(
    r'(?P<open><!--\s*site-nav:start(?P<attrs>[^>]*?)-->)'
    r'.*?'
    r'(?P<close><!--\s*site-nav:end\s*-->)',
    re.DOTALL,
)
SUBNAV_RE = re.compile(
    r'(?P<open><!--\s*site-subnav:start(?P<attrs>[^>]*?)-->)'
    r'.*?'
    r'(?P<close><!--\s*site-subnav:end\s*-->)',
    re.DOTALL,
)
ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


def attrs_of(marker_attrs):
    return dict(ATTR_RE.findall(marker_attrs or ""))


def render(items, current, css_class, indent="  "):
    """Build the <ul>. aria-current is set on at most one item."""
    lines = [f'{indent}<ul class="{css_class}">']
    for key, label, href in items:
        flag = ' aria-current="page"' if key == current else ""
        lines.append(f'{indent}  <li><a href="{href}"{flag}>{label}</a></li>')
    lines.append(f"{indent}</ul>")
    return "\n".join(lines)


def stamp(html, path, problems):
    """Replace every nav and subnav block. Returns the new HTML."""

    def nav_sub(m):
        a = attrs_of(m.group("attrs"))
        current = a.get("current", "")
        if current and current not in {k for k, _, _ in NAV}:
            problems.append(f'{path}: unknown nav key "{current}"')
        # class="" lets a page render the same nav in a lighter footer weight.
        css_class = a.get("class", "nav")
        if css_class not in ("nav", "footer-nav"):
            problems.append(f'{path}: unknown nav class "{css_class}"')
        body = render(NAV, current, css_class)
        return f'{m.group("open")}\n{body}\n  {m.group("close")}'

    def subnav_sub(m):
        a = attrs_of(m.group("attrs"))
        which, current = a.get("set", ""), a.get("current", "")
        if which not in SUBNAV:
            problems.append(f'{path}: unknown subnav set "{which}"')
            return m.group(0)
        body = render(SUBNAV[which], current, "subnav")
        return f'{m.group("open")}\n{body}\n  {m.group("close")}'

    html, n = NAV_RE.subn(nav_sub, html)
    if n == 0:
        problems.append(f"{path}: no site-nav markers, page has no nav")
    html = SUBNAV_RE.sub(subnav_sub, html)
    return html


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report drift without writing; exit 1 if anything differs")
    args = ap.parse_args()

    shared = pathlib.Path(__file__).resolve().parent
    hub = shared.parent                    # the root repo, which holds _shared/
    parent = hub.parent                    # the directory holding all the repos
    css_src = shared / "site.css"

    changed, problems = [], []

    # The hub is a site too: it gets the same stylesheet and the same nav.
    for root in [hub] + [parent / r for r in REPOS]:
        if not root.is_dir():
            problems.append(f"{root.name}: repo not found at {root}")
            continue

        # 1. the stylesheet
        css_dst = root / "site.css"
        if not css_dst.exists() or css_dst.read_text() != css_src.read_text():
            changed.append(str(css_dst.relative_to(parent)))
            if not args.check:
                shutil.copyfile(css_src, css_dst)

        # 2. the nav in every page
        for page in sorted(root.rglob("*.html")):
            if ".git" in page.parts:
                continue
            before = page.read_text()
            after = stamp(before, str(page.relative_to(parent)), problems)
            if after != before:
                changed.append(str(page.relative_to(parent)))
                if not args.check:
                    page.write_text(after)

    verb = "would change" if args.check else "updated"
    if changed:
        print(f"{verb} {len(changed)} file(s):")
        for c in changed:
            print(f"  {c}")
    else:
        print("everything already in sync")

    if problems:
        print("\nproblems:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)

    # --check is meant for CI: fail loudly if a repo drifted.
    if problems or (args.check and changed):
        sys.exit(1)


if __name__ == "__main__":
    main()
