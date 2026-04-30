#!/usr/bin/env python3
"""
Generate M4A TTS audio for every word/phrase that playWordAudio() may receive.
Uses macOS `say` (Samantha, rate 1.1×) + `afconvert` (AAC/M4A).

Output:
  ../audio/words/<slug>.m4a   — one file per entry
  ../audio/manifest.json      — {slug: filename} map used by the JS runtime

Slug rules (must match slugify() in CW_words_practice.html exactly):
  - lowercase
  - strip leading/trailing angle brackets (CW prosigns: <ar> → ar)
  - strip trailing punctuation ? . /
  - replace remaining non-alphanumeric chars with -
  - collapse runs of - ; strip leading/trailing -
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
WORDS_DIR  = SCRIPT_DIR.parent / "words"
AUDIO_DIR  = SCRIPT_DIR.parent / "audio" / "words"
MANIFEST   = SCRIPT_DIR.parent / "audio" / "manifest.json"

SAY_VOICE  = "Samantha"
SAY_RATE   = 176          # "words per minute" for say; ~1.1× of Samantha's default 160 wpm
AAC_BITRATE = "24k"       # ffmpeg bitrate; 24k mono AAC ≈ 2KB/word (vs afconvert's 7KB with 4096-byte fixed overhead)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# ── Fixed phrases always passed to playWordAudio() ──────────────────────────
FIXED_PHRASES = ["Correct", "Incorrect"]

# ── Prosign display → spoken form ────────────────────────────────────────────
PROSIGN_SPOKEN = {
    "<ar>": "ar",
    "<bt>": "bt",
    "<kn>": "kn",
    "<sk>": "sk",
}

# ── Special-char entries → spoken form ───────────────────────────────────────
# Keys are lowercased (matched against raw.lower()).
# Single uppercase letters must map to lowercase so `say` says "eye" not "capital i".
# Multi-letter abbreviations spelled out use spaces so `say` reads each letter.
# All-digit slugs are handled generically in spoken_form().
SPECIAL_SPOKEN = {
    ".":    "period",
    "/":    "slash",
    "?":    "question mark",
    "hw?":  "hw",
    "qrl?": "qrl",
    "qrz?": "qrz",
    "i":    "i",
    "r":    "r",
    "xyl":  "x y l",
}


def slugify(text: str) -> str:
    s = text.lower()
    s = s.strip("<>")           # prosigns
    s = s.rstrip("?./")        # trailing punctuation
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "unknown"


def spoken_form(raw: str) -> str:
    low = raw.lower().strip()
    if low in PROSIGN_SPOKEN:
        return PROSIGN_SPOKEN[low]
    if low in SPECIAL_SPOKEN:
        return SPECIAL_SPOKEN[low]
    # All-digit entries: spell each digit individually (73 → "7 3", 359 → "3 5 9")
    if re.match(r'^\d+$', low):
        return ' '.join(low)
    # Strip angle brackets if present but not in map
    cleaned = re.sub(r"[<>?]", "", raw).strip()
    return cleaned or raw


def collect_entries() -> list[tuple[str, str]]:
    """Return list of (raw_text, spoken_form) for everything to generate."""
    seen_slugs: set[str] = set()
    entries: list[tuple[str, str]] = []

    def add(raw: str, spoken: str) -> None:
        sl = slugify(raw)
        if sl in seen_slugs or not sl:
            return
        seen_slugs.add(sl)
        entries.append((raw, spoken))

    # Fixed phrases first
    for phrase in FIXED_PHRASES:
        add(phrase, phrase)

    # All word list entries
    for txt_file in sorted(WORDS_DIR.glob("*.txt")):
        for line in txt_file.read_text().splitlines():
            raw = line.split("=")[0].strip()
            if not raw:
                continue
            spoken = spoken_form(raw)
            add(raw, spoken)

    return entries


def generate_one(raw: str, spoken: str, force: bool = False) -> str | None:
    """Generate audio/words/<slug>.m4a; return slug on success, None on skip."""
    slug = slugify(raw)
    out_path = AUDIO_DIR / f"{slug}.m4a"

    if out_path.exists() and not force:
        return slug

    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp:
        aiff_path = tmp.name

    try:
        result = subprocess.run(
            ["say", "-v", SAY_VOICE, "-r", str(SAY_RATE), "-o", aiff_path, spoken],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  WARN say failed for {raw!r}: {result.stderr.strip()}", file=sys.stderr)
            return None

        result = subprocess.run(
            ["ffmpeg", "-y", "-i", aiff_path,
             "-c:a", "aac", "-b:a", AAC_BITRATE, "-ac", "1",
             str(out_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  WARN ffmpeg failed for {raw!r}: {result.stderr.strip()}", file=sys.stderr)
            return None

        return slug
    finally:
        try:
            os.unlink(aiff_path)
        except OSError:
            pass


def main() -> None:
    force = "--force" in sys.argv
    entries = collect_entries()
    print(f"Generating {len(entries)} audio files (voice={SAY_VOICE}, rate={SAY_RATE} wpm)…")

    manifest: dict[str, str] = {}
    ok = skipped = failed = 0

    for i, (raw, spoken) in enumerate(entries, 1):
        slug = slugify(raw)
        out_path = AUDIO_DIR / f"{slug}.m4a"
        if out_path.exists() and not force:
            manifest[slug] = f"audio/words/{slug}.m4a"
            skipped += 1
            if i % 200 == 0:
                print(f"  {i}/{len(entries)}  (skipping existing)")
            continue

        result_slug = generate_one(raw, spoken, force=True)
        if result_slug:
            manifest[result_slug] = f"audio/words/{result_slug}.m4a"
            ok += 1
        else:
            failed += 1
        if i % 100 == 0 or i == len(entries):
            print(f"  {i}/{len(entries)}  generated={ok}  skipped={skipped}  failed={failed}")

    MANIFEST.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print(f"\nDone. {ok} generated, {skipped} skipped, {failed} failed.")
    print(f"Manifest → {MANIFEST}")


if __name__ == "__main__":
    main()
