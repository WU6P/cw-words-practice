#!/usr/bin/env bash
# Push commits and create GitHub release v1.5.
# Run from the repo root.
set -euo pipefail

git push origin main

NOTES=$(mktemp)
cat > "$NOTES" << 'EOF'
## What's new in v1.5

### Listen Mode — stable Morse volume on locked iPhone
- With Voice Reveal on, the 2 s `speechSynthesis` heartbeat that keeps TTS permission alive was firing a silent utterance every tick, even mid-Morse. On a locked or backgrounded iPhone, each `speak()` call shifts system audio focus to TTS for ~100–300 ms and ducks the HTMLAudio Morse element, producing an audible level dip inside a single word.
- Heartbeat now skips its tick while a Morse blob is currently playing (`!_morseAudio.paused && !_morseAudio.ended`). Permission stays alive via the next tick after Morse ends, the actual `speakWord()` call, and the heartbeat ticks during inter-word gaps.
- Symptom only appeared when locked/backgrounded; on screen the page kept audio focus and no ducking happened.

### Help → About
- Version updated to 1.5.

### Service worker
- Cache bumped to v17; existing installs will prompt for an update.
EOF

gh release create v1.5 \
  --title "v1.5 — Stable Morse volume on locked iPhone" \
  --notes-file "$NOTES"

rm -f "$NOTES"
