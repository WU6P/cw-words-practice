# CW Words Practice

Morse code multiple-choice trainer for desktop and mobile.

## Canonical app

**[CW_words_practice.html](CW_words_practice.html)** — open directly in any browser.  
No build step, no server required.

## Quick start

```bash
open CW_words_practice.html          # macOS
# or just double-click the file
```

For full PWA/offline support (service worker), serve from a local web server:

```bash
python3 -m http.server 8080
# then open http://localhost:8080/CW_words_practice.html
```

## Files

| Path | Purpose |
|---|---|
| `CW_words_practice.html` | **The app** — single-file, inline CSS + JS |
| `words/*.txt` | Word list source files |
| `manifest.json` | PWA manifest (app name, icons, theme) |
| `sw.js` | Service worker (offline cache) |
| `icons/` | App icons (192 × 192 and 512 × 512 SVG) |
| `design_handoff_cw_practice/` | Design spec / reference (not the live app) |
| `docs/` | Archived design-direction prototypes |

## Credit

Nian WU6P
