# iOS / Browser Audio Lessons — CW Words Practice

Session date: 2026-04-25

---

## Problem

In Listen mode, when the iPhone screen locked or the app was minimised, the
Morse code tone went silent while the natural voice (speech synthesis) kept
playing.

---

## Root Cause Chain

### 1. WebAudio is suspended on iOS background / lock screen

`AudioContext` + `AudioBufferSourceNode` is a page-level resource. iOS
hard-suspends it the moment the page is hidden (lock or home button). There is
**no API that prevents this**. `MediaSession`, Wake Lock, and silent audio
loops do not save WebAudio.

`speechSynthesis`, by contrast, calls the iOS *system* TTS service — it runs
outside the page's audio session and survives background/lock without any tricks.
That is why voice kept working but Morse did not.

**Fix:** In listen mode, pre-render Morse PCM into a WAV blob and play it
through an `HTMLAudioElement`. With a silent loop + MediaSession registered,
iOS keeps HTMLAudio elements playing on the lock screen.

### 2. All-zero PCM silent loop does not keep the iOS audio session alive

The original silent-audio keepalive was a 0.1 s WAV of all-zero samples. iOS
detects zero-fill as "no media" and tears down the audio session on lock,
defeating the keepalive purpose.

**Fix:** Fill the loop WAV with ±1 LSB alternating samples (8 kHz, 2 s). The
content is inaudible at any system volume but is recognised as active media.

### 3. The non-zero silent loop + MediaSession ducked macOS Safari speech

When the long ±1 LSB loop and MediaSession `playbackState='playing'` are
active, macOS Safari treats the page as a media-playing app and ducks
`speechSynthesis` to inaudible. One Mac showed the symptom; another did not —
suggesting a per-machine Safari ducking policy or audio routing difference.

**Fix:** Gate all iOS-specific behaviours (long non-zero loop, MediaSession)
behind a `_isIOS` UA check. Non-iOS platforms keep the original 0.1 s
zero-fill and skip MediaSession entirely, restoring speech on macOS.

```js
const _isIOS = (() => {
  const ua = navigator.userAgent || '';
  if (/iPad|iPhone|iPod/.test(ua)) return true;
  // iPadOS 13+ reports MacIntel — disambiguate by touch points
  return navigator.platform === 'MacIntel' && (navigator.maxTouchPoints || 0) > 1;
})();
```

### 4. HTMLAudioElement pool exhaustion (morse dies after a few words)

First attempt created a **new** `Audio()` element + blob URL per Morse
playback. iOS Safari caps the number of concurrent HTMLMediaElements per tab
(roughly 6). After 2–3 words the pool was exhausted; symptoms were:
- Word 1: correct
- Word 2: repeats cut short
- Word 3+: no Morse at all, voice unaffected (speech is a system call, no element needed)

**Fix:** Pool a **single** reused `Audio` element (`_morseAudio`). Swap `src`
and call `load()` per playback. Revoke the previous blob URL 100 ms *after*
assigning the new `src` so iOS does not tear down the element during the swap.

```js
let _morseAudio = null;
let _lastMorseUrl = null;
function _ensureMorseAudio() {
  if (_morseAudio) return _morseAudio;
  const a = new Audio();
  a.preload = 'auto'; a.playsInline = true;
  a.setAttribute('playsinline', '');
  _morseAudio = a;
  return a;
}
```

### 5. Double Morse playback race (canplaythrough + 800 ms fallback)

To handle the case where `canplaythrough` never fires, an 800 ms fallback
`setTimeout` also called `start()` (which calls `a.play()`). For short words
at fast WPM, the audio could finish in under 800 ms. Sequence:

1. `canplaythrough` → `start()` → audio plays → `ended` → `finish()` resolves
2. 800 ms fallback fires *after* `finish()` → calls `start()` again → iOS
   restarts the ended audio → user hears Morse **twice** before voice

**Fix:** Guard `start()` with a `started` boolean and `done` flag. Clear both
timers (`startTimer`, `watchdogTimer`) inside `finish()`.

```js
let done = false, started = false;
let startTimer = null, watchdogTimer = null;
const finish = () => {
  if (done) return;
  done = true;
  clearTimeout(startTimer); clearTimeout(watchdogTimer);
  /* remove listeners */ resolve();
};
const start = () => {
  if (started || done) return;   // ← key guard
  started = true;
  a.removeEventListener('canplaythrough', start);
  const p = a.play();
  if (p && p.catch) p.catch(() => finish());
};
startTimer  = setTimeout(start,  800);
watchdogTimer = setTimeout(finish, (totalSec + 3.0) * 1000);
```

### 6. Speech heartbeat ducks Morse on lock screen (volume wobble within a word)

The 2 s `speechSynthesis` heartbeat that keeps TTS permission alive (see
`startSpeechHeartbeat`) was firing a silent utterance every tick — even while a
Morse blob was mid-playback. On a *locked or backgrounded* iPhone, calling
`speechSynthesis.speak()` shifts the system audio focus to TTS for ~100–300 ms
and ducks the HTMLAudio Morse element. On screen the page keeps focus and no
ducking happens, which is why the symptom only appears when locked.

A typical word at 20 WPM takes 1.5–3 s, so each word easily catches one
heartbeat tick → audible mid-word level dip. Diagnostic that nailed it:
turning **Voice Reveal off** (which gates the heartbeat) made the wobble
disappear with the phone locked.

**Fix:** Skip the heartbeat tick when `_morseAudio` is currently playing.
Permission stays alive via the next tick (after Morse ends), the actual
`speakWord()` call, and the heartbeat ticks during inter-word gaps.

```js
_speechHeartbeat = setInterval(() => {
  if (!window.speechSynthesis) return;
  if (window.speechSynthesis.speaking || window.speechSynthesis.pending) return;
  // Skip while Morse is mid-playback; speak() ducks HTMLAudio on lock screen.
  if (_morseAudio && !_morseAudio.paused && !_morseAudio.ended) return;
  /* … speak silent utterance … */
}, 2000);
```

---

## Additional iOS Audio Patterns

| Goal | Technique |
|---|---|
| Keep WebAudio alive on lock | Not possible; switch to HTMLAudio |
| Keep HTMLAudio alive on lock | Silent loop (non-zero PCM) + MediaSession |
| Unlock AudioContext on first gesture | Call `ctx.resume()` synchronously inside click handler |
| Unlock speech synthesis on iOS | Call `speechSynthesis.speak()` synchronously inside click handler, *before* any `await` |
| Keep speech synthesis permission | Silent utterance heartbeat every 2 s while session is active |
| Resume AudioContext after unlock | `visibilitychange` + `pageshow` handlers calling `ctx.resume()` |
| Resume silent loop after lock | `pageshow` handler: re-play `_silentAudio` if paused and session active |
| Detect iPadOS (reports MacIntel) | `navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1` |

---

## MediaSession Setup (iOS only)

```js
function setupMediaSession(playing) {
  if (!_isIOS || !('mediaSession' in navigator)) return;
  try {
    if (playing) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: 'CW Practice — Listen Mode',
        artist: 'CW Words Practice',
      });
      navigator.mediaSession.setActionHandler('play',  () => {});
      navigator.mediaSession.setActionHandler('pause', () => {
        if (state?.listenState?.active) stopListen();
      });
      navigator.mediaSession.playbackState = 'playing';
    } else {
      navigator.mediaSession.playbackState = 'paused';
    }
  } catch (e) {}
}
```

Call `setupMediaSession(true)` inside `unlockAudio()` (which is already inside
the gesture handler). Call `setupMediaSession(false)` in `stopListen()` and
`goSettings()`.

---

## Service Worker Note

Every cache-name bump (`cw-practice-vN`) triggers the update banner in the
browser. This is correct — Chrome and Safari check `sw.js` byte-content on
every navigation. During active development, bump the cache only when
deploying a stable checkpoint to avoid showing users repeated update banners.

---

### 7. Cold `_morseAudio` ramp + `_silentAudio` loop-boundary ducking (volume unstable on words 1–2 and intra-word)

**Symptom:** In Listen mode with Voice Reveal ON, the volume sounds low or
unstable on the 1st and 2nd word, and occasional mid-word level dips occur
throughout the session. Disappears when Voice Reveal is OFF. Does not happen
on macOS or Android.

**Root cause chain (three independent sources):**

1. **`_morseAudio` cold-session ramp.** `unlockAudio()` warms the AudioContext
   and `_silentAudio`, but `_morseAudio` — the HTMLAudioElement that plays every
   beep and Morse blob — is never played until the listen loop starts. iOS
   performs a full audio-session ramp (~100–300 ms) on the first `play()` of a
   cold HTMLAudioElement. The 0.20 s of leading silence baked into each blob is
   often shorter than this ramp, so word 1's beep and first Morse play at reduced
   volume. This happens with or without Voice; Voice just makes the gap more
   audible.

2. **Post-`speakWord()` TTS-focus lingering.** The existing 2.0 s lead on the
   first Morse repeat after voice correctly absorbs TTS-focus release for that
   repeat. But word 2's **announcement beep** and **first Morse** (before voice)
   had only 0.20 s lead — too short when the preceding word's TTS focus hasn't
   fully released. When `listenRepeat == 0`, the word-2 beep arrives immediately
   after the word-1 TTS-focus window, getting partially ducked.

3. **`_silentAudio` 2 s loop boundary.** The iOS keepalive loop was 2 s of
   ±1 LSB PCM. Every time the loop re-entered, iOS briefly re-arbitrated audio
   focus among active HTMLAudio elements. A typical Morse word at 18–25 WPM
   takes 1.5–3 s, so long words reliably caught a loop boundary mid-playback,
   producing an audible intra-word level dip.

**Diagnostic:** Turning Voice Reveal OFF makes all three symptoms disappear
because no TTS events fire (eliminating Cause 2) and the smaller overall audio
activity makes Cause 1 and Cause 3 sub-threshold.

**Fixes (all `_isIOS`-gated):**

- **Fix A** — `unlockAudio()`: play a 1.5 s silent blob through `_morseAudio`
  immediately after `primeAudio(0.2)`. This performs the iOS audio-session
  ramp on the actual element, so the first real beep starts into a hot session.

- **Fix B** — `playListenBeepBlob`: bump `leadSec` from 0.20 to 0.50 s.
  Also bump the first-Morse-before-voice `leadSec` from 0.20 to 0.50 in the
  listen loop. Provides enough silence before any audible content to absorb
  post-TTS focus-release residue and loop-boundary jitter.

- **Fix C** — `ensureSilentAudio`: extend the iOS loop track from 2 s to 30 s
  of ±1 LSB PCM. At typical per-word durations (max ~10 s), the loop boundary
  falls in an inter-word gap or is skipped entirely, eliminating the mid-word
  focus arbitration trigger.

---

## macOS Chrome Speech Was a System Issue

On one macOS machine, `speechSynthesis.speak()` produced no audio even in the
browser console — unrelated to our code. Fix was a **system reboot**. When
diagnosing "no voice" on macOS, verify first:

1. Raw `speechSynthesis.speak(new SpeechSynthesisUtterance('test'))` in
   console — audible?
2. Test in Safari on the same machine.
3. Check System Settings → Sound → Output device.
4. Check System Settings → Accessibility → Spoken Content → System Voice.
5. Reboot if above are all configured correctly.
