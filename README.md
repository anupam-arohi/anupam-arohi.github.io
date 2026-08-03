# anupam-arohi.github.io

The root of the site. The about page lives here, at `/`, and so does the
shared shell every other site wears (`_shared/`).

## The sites

| Path | Repo | What it is |
|---|---|---|
| `/` | this repo | about me, the landing page |
| `/meditation.html` | this repo | the weekly Helsinki group |
| `/photos/` | [photos](https://github.com/anupam-arohi/photos) | gallery and six series |
| `/auroras/` | [auroras](https://github.com/anupam-arohi/auroras) | field guide to northern lights |
| `/books/` | [books](https://github.com/anupam-arohi/books) | the shelf, built from Goodreads |
| `/lv/` | lv | Live Version |
| `/gm/` | gm | meditation sign-up redirect |
| `/about/` | [about](https://github.com/anupam-arohi/about) | **redirect stubs only**, see below |

They stay separate repos on purpose: books rebuilds itself from Goodreads,
photos has its own resize pipeline. Merging them would cost those workflows and
buy very little, because they already share one design language.

## The about repo is now stubs

The about page became the landing page, so `/about/` and
`/about/meditation.html` are two small redirect pages. They exist because those
URLs are linked from LinkedIn, from the 2022 blogspot post, from the photos and
auroras sites, and, in the meditation case, from messages sent by hand to people
coming to the group.

GitHub Pages cannot issue a real 301, so the stubs use a meta refresh plus
`rel=canonical`. That is the strongest signal available on this host. They are
deliberately **not** `noindex`: that would stop search engines following the
canonical, and the old URLs would drop out of the index instead of handing their
history to the new ones. Leave the stubs in place indefinitely; they cost
nothing.

`about.css`, `site.css` and `images/` are still sitting in that repo, unused.
Harmless, and worth deleting next time you are in there.

## Changing the nav

The nav physically exists in every HTML file, because there is no build step.
`_shared/sync.py` is what keeps those copies identical.

```bash
# 1. edit the NAV list in _shared/sync.py
# 2. stamp it everywhere
python3 _shared/sync.py
# 3. commit each repo
```

Each page decides only one thing for itself, the highlighted item:

```html
<!-- site-nav:start current="photos" -->
   ...generated, do not hand-edit...
<!-- site-nav:end -->
```

Hand-edits inside those markers are overwritten on the next run. That is the
point: drift is what made the sites feel like five unrelated places.

`python3 _shared/sync.py --check` changes nothing and exits non-zero if any repo
has drifted, so it can run in CI.

There is no "Home" item. About *is* home, so a nav carrying both would give
visitors two words for the same place.

## Changing the look

`_shared/site.css` holds the colour tokens, base type, skip link, hero, nav and
footer. `sync.py` copies it into every repo as `site.css`. Each site loads it
first, then its own stylesheet, which may override anything.

Edit `_shared/site.css`, never a repo's copy. The copies are generated.

Deliberately *not* shared: `h2` spacing, and `--maxw`. The prose sites want
840px and room above a heading, the gallery wants 1140px and tight headings.

## Committing

`./_shared/commit.sh` stages and commits all five repos with sensible messages.
It never pushes.

## Previewing

Root-relative links only resolve from a single web root, so opening a file
directly will 404 on every nav click.

```bash
./_shared/preview.sh        # http://localhost:8000
```

It symlinks all the sibling repos into one throwaway web root. Clone the repos
side by side in the same parent directory for this to find them.
