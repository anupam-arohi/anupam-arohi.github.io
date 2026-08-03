#!/usr/bin/env bash
# commit.sh · commits the cohesive-navigation change across all five repos.
# Does NOT push. Review with `git -C <repo> show` before you do.
#
#   ./_shared/commit.sh
set -euo pipefail

HUB="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PARENT="$(dirname "$HUB")"

HUB_MSG="Serve about at the root and hold the shared shell

/ was a noindex redirect stub, so the site had no home and About was
pretending to be the trunk. About now lives here instead.

- about's page, meditation page, stylesheet and images move in from the
  about repo; /about/ keeps redirect stubs for existing inbound links
- _shared/ becomes the source of truth for the nav and site.css
- 404 page joins the shell and stops pointing at the old URLs"

SITE_MSG="Adopt the shared site shell

The sites were developed independently and drifted apart: six nav items on
About, four different ones on Photographs, none at all on the aurora guide,
and Books pointed Meditation at the sign-up redirect instead of the page.

- load site.css, the shared shell (tokens, base type, hero, nav, footer)
- drop the rules site.css now provides, keep only what is page-specific
- replace the hand-written nav with the canonical one, generated between
  site-nav markers by _shared/sync.py in the root repo
- point at the new root: about is now / and meditation is /meditation.html
- use root-relative links so the repos serve as one web root"

commit_one() {
  local repo="$1" msg="$2" name="$3"
  [ -d "$repo/.git" ] || { echo "skip $name: not a git repo"; return; }
  # Cowork's sandbox can leave these behind; harmless to clear.
  rm -f "$repo/.git/index.lock"
  git -C "$repo" add -A
  if git -C "$repo" diff --cached --quiet; then
    echo "$name: nothing to commit"
  else
    git -C "$repo" commit -q -m "$msg"
    echo "$name: $(git -C "$repo" log --oneline -1)"
  fi
}

commit_one "$HUB" "$HUB_MSG" "anupam-arohi.github.io"
for d in about books photos auroras; do
  commit_one "$PARENT/$d" "$SITE_MSG" "$d"
done

echo
echo "Nothing pushed. Preview first:  ./_shared/preview.sh"
