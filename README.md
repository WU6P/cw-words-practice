# CW Words Practice

A Morse code trainer for amateur radio operators, focused on CW word copy practice. It has two modes:

**Listen Mode** mimics MorseCode Ninja audio sessions — continuous Morse stream with user-controlled tone, repeat count, word gap, and optional voice reveal (woman or man voice).

**Practice Mode** is interactive — hear a word in Morse, pick the correct answer from four choices. Missed words are collected for targeted follow-up training.

Works on desktop and mobile. Installs as a PWA for offline use.

---

## Use It

Point your browser to:

**https://wu6p.github.io/cw-words-practice/CW_words_practice.html**

No login, no install required. To use offline, see the Offline Use section below.

---

## Listen Mode

Runs a continuous stream of Morse words — like a beacon or on-the-air practice session. No multiple choice; just listen and copy.

- **Session Duration** — 5 minutes to 12 hours. Timer counts up in the header. Ends automatically or stop early.
- **Announcement Dit** — A soft dit (letter E) at reduced volume signals a new word is coming, followed by a brief pause.
- **Word Repeats** — Each word is repeated 0–10 times. Higher counts give more chances to copy before the next word arrives.
- **Word Gap** — Silence between words is a multiple (1×–10×) of standard inter-word space. Pick what fits your current level.
- **Voice Reveal** — When enabled, the spoken English word plays after the first Morse transmission. Subsequent repeats are Morse only.

---

## Practice Mode

Plays a word in Morse and presents four multiple-choice answers. Select the correct word before time runs out.

- **Word Pool** — Top 100 up to Top 2000 common English words, QSO Elements (ham-radio phrases), or your Missed Words list.
- **Character Speed** — 10–75 WPM. Sets the true character rate.
- **Session Size** — 10, 20, 50, or 100 questions. Results shown at the end.
- **Progress** — Accuracy tracked across the session, shown in the header and on the summary screen.
- **Replay** — Tap the waveform card to replay the current word at any time before answering.

---

## Settings

**Tone**
- *Frequency* — Sidetone pitch 300–1000 Hz. Default 550 Hz.
- *Tone Variation* — Each word sent on a slightly different pitch (±200 Hz random). Simulates real on-air conditions.

**Farnsworth Timing**
Sends characters at full speed but widens the gaps between characters and words. Lets you hear correct character rhythm without needing high overall copy speed.
- *Spacing Speed* — 5 WPM minimum, up to character speed. Lower = wider gaps.

**Voice Reveal**
- *Gender* — Woman or Man. Picks the best available voice from your device's speech engine.
- *Voice Speed* — 0.5× to 2×. Default 1×.
- *Allow Cloud Voices* — iOS/macOS only. Enables higher-quality cloud voices (requires internet). Off = local voices only, works offline.

**Session (Practice)**
- *Questions per Session* — 10, 20, 50, or 100.

**Theme**
- *Shack* — Dark amber, easy on the eyes in a dimly lit room.
- *Clean* — Light, high contrast. Good for daylight.
- *Terminal* — Dark green-on-black.

---

## Missed Words

When *Save Missed Words* is enabled (default on), every incorrectly answered word is recorded with a miss counter. The counter resets to 2 each time you miss the same word again, and decrements by one each time you get it right. When a word's count reaches zero it is removed from the list.

The Missed Words pool lets you do targeted training on your weakest words. Use *Clear Saved Words* in Settings to start fresh.

---

## Offline Use

CW Words Practice is a Progressive Web App (PWA). Once installed it runs fully offline — no internet needed for Morse playback, practice sessions, or your missed-words list.

**iPhone / iPad** — Open in Safari, tap the Share button, tap "Add to Home Screen". The app icon appears on your home screen and opens full-screen.

**Android** — Open in Chrome, tap the three-dot menu, tap "Add to Home Screen" or "Install App".

**Desktop (Chrome / Edge)** — Look for the install icon (⊕) in the address bar, or open the browser menu and choose "Install CW Words Practice".

**Notes:**
- Cloud Voices require internet. Turn off *Allow Cloud Voices* in Settings to use local voices only.
- All word lists are bundled in the app — no internet needed after install.
- Your missed-words list is stored locally on your device.

---

## Files

| Path | Purpose |
|---|---|
| `CW_words_practice.html` | The app — single file, all CSS and JS inline |
| `manifest.json` | PWA manifest |
| `sw.js` | Service worker (offline cache) |
| `icons/icon.svg` | App icon |

---

## Credit

Nian WU6P — nian.wu6p@gmail.com
