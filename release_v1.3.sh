#!/usr/bin/env bash
# Push commits and create GitHub release v1.3
# Run from the repo root when ready to ship.
set -euo pipefail

git push origin main

NOTES=$(mktemp)
cat > "$NOTES" << 'EOF'
## What's new in v1.3

### Bug fixes
- Sound volume stabilized
- Eliminate screen freeze in corner case

### Listen Mode — Word Repeats fixed
- Setting now means additional plays after the first (0=once, 1=twice, 2=three times). Previously 0 and 1 both produced only 1 play.

### Listen Mode — Word Gap repositioned
- Gap now falls after the first Morse play — before the next repeat (voice off) or before the voice reveal (voice on). Range extended to 1–20×.

### Service worker
- Cache bumped to v13; existing installs will prompt for an update.
EOF

gh release create v1.3 \
  --title "v1.3 — Listen Mode Fix" \
  --notes-file "$NOTES"

rm -f "$NOTES"
