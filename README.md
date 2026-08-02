# anupam-arohi.github.io

The user site. GitHub serves whatever is in a repo named exactly
`<username>.github.io` at the bare domain, so this repo owns
<https://anupam-arohi.github.io/> and nothing else does.

It holds two files and no content of its own.

## index.html

Bounces the root to [/about/](https://anupam-arohi.github.io/about/).

GitHub Pages cannot issue a server-side 301, so this is a meta refresh with a
`location.replace()` fallback and a real link underneath for anyone running
neither. `rel=canonical` points at the About page and the page is `noindex,
follow`, so search engines credit About rather than this stub.

`replace()` rather than `assign()` on purpose: the back button should return
visitors where they came from, not bounce them through here again.

## 404.html

GitHub Pages serves this for any unmatched path **at the root of this domain**,
for example a typo like `/abuot/`. It does not cover 404s inside the project
sites; `/books/nonsense` is served by the `books` repo, which would need its own
`404.html`.

It borrows `/about/about.css` rather than carrying a copy of the tokens. That
keeps it in step with the rest of the family for free, at the cost of one
cross-repo dependency: rename or move `about.css` and this page loses its
styling. It stays perfectly readable, just unstyled.

## Deploying

Settings → Pages → Deploy from a branch → `main` → `/ (root)`.
