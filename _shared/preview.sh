#!/usr/bin/env bash
# preview.sh · serve all five repos as one site, the way visitors see it
#
# The nav uses root-relative links ("/photos/"), which only resolve when
# everything is served from a single web root. Opening a file directly in the
# browser will NOT work: the links will all 404. Use this instead.
#
#   ./_shared/preview.sh          # serve on http://localhost:8000
#   ./_shared/preview.sh 9000     # or pick your own port
#
# It builds a throwaway web root of symlinks, so it never copies or touches
# your working files.

set -euo pipefail

PORT="${1:-8000}"
HUB="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the root repo
PARENT="$(dirname "$HUB")"                                # where all repos live
WEBROOT="$(mktemp -d)"

trap 'rm -rf "$WEBROOT"' EXIT

# The hub's own files sit at the web root.
for f in "$HUB"/*; do
  [ "$(basename "$f")" = "_shared" ] && continue
  ln -s "$f" "$WEBROOT/"
done

# Each sibling repo becomes a top-level directory.
for repo in about books photos auroras lv gm; do
  if [ -d "$PARENT/$repo" ]; then
    ln -s "$PARENT/$repo" "$WEBROOT/$repo"
  else
    echo "note: $repo not cloned beside the root repo, its nav link will 404 locally"
  fi
done

echo
echo "serving all repos as one site at http://localhost:$PORT"
echo "walk the nav across every page, then Ctrl-C"
echo
cd "$WEBROOT"
python3 -m http.server "$PORT"
