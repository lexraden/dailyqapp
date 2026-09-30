# QA — control_room_reel_v4.mp4 (Control Room манифест, 90s)

Style reference: Lorens Ghiraldo `DduKmiODkeV` (~93s, hype-manifest about AI agents).
Full breakdown: `/opt/data/projects/dailyqapp/promo/references/reels/DduKmiODkeV/analysis.md`.

Build: `bash build_v4.sh` (ffmpeg only). VO: `bash vo_v4_piper.sh 1.16` (local piper).
Screencast: `venv/bin/python record_v4c.py` → `raw4/page@6e828b7ecaa1b35ccc604db2d83168a3.webm`.

## Source

- Real Playwright screencast of the live Hermes dashboard at `127.0.0.1:8080` — no static
  screenshots, no mockups. VP8 1440x900 @ 1.5 DPR, **93.12s**.
- Every navigation in the recording is verified: the script waits for a landmark string
  (`CONTROL ROOM`, `Kanban`, `AGENT.LOG`, `Messages`) and retries up to 3x, then records the
  failure to `fails_v4.json`. Beat log: `beats_v4.json`.
- Recorded content is real: live agent map with actual model names, the real 139-task kanban
  board, real task detail panels, the real gateway log tail, real session list.

## Timeline (8 segments, explicit trims)

The raw take has a **black page-transition frame at ~84.0s**, so the reel is assembled from
explicit trimmed segments instead of one linear pass — that is why PASS A exists.

| seg | source in | source out | len | content |
|---|---|---|---|---|
| cr_hero | 0.6 | 16.0 | 15.4s | Control Room agent map, node hover |
| kanban | 16.2 | 27.0 | 10.8s | Kanban board, columns, scroll |
| kanban_detail | 27.2 | 40.0 | 12.8s | Task card detail (description, dependencies, final result) |
| logs | 40.2 | 53.0 | 12.8s | Logs page, gateway log tail |
| sessions | 53.2 | 64.0 | 10.8s | Sessions list |
| cr_panel | 64.2 | 78.0 | 13.8s | Control Room + right agent panel |
| kanban_result | 78.2 | 83.8 | 5.6s | Kanban board (result beat) |
| cr_final | 84.8 | 92.0 | 7.2s | Control Room hero, held for the CTA |

Working copy `seg4/work.mp4` = **89.20s**. No duplicate-page stretches: each segment either
changes page or opens a detail panel (verified in `beats_v4.json`).

## Composition

- 1080x1920, 30fps, h264 High yuv420p, faststart.
- Background: same frame cover-scaled, `gblur sigma=34`, brightness −0.22 — dark ember backdrop.
- Foreground: sharp 1080x1440 focus window inside the 2304x1440 working copy, X driven by a
  piecewise expression so the active area stays centred and legible on every beat
  (CR 470 → kanban 640 → card detail 760 → logs 500 → sessions 620 → CR panel 700 → kanban 640 → CR 470).
- Ken Burns 1.00 → 1.05 across the reel.
- Captions: DejaVuSans-Bold 48px, white 0.97 on a black 0.55 box, bottom-centre at y=h−236,
  0.3s fade in/out. Nine captions: ОДИН ЭКРАН. ЦЕЛАЯ КОМАНДА / CONTROL ROOM / ЗАДАЧА /
  АГЕНТЫ ЗА РАБОТОЙ / ЛОГИ / КОНТРОЛЬ / ПАРАЛЛЕЛЬНО / РЕЗУЛЬТАТ / Ссылка на демо — в профиле.

## Voice

- Russian, 18 lines, 249 words, `vo_text_v4.txt`.
- TTS: **local piper** `ru_RU-dmitri-medium`, `--length_scale 1.16` → 90.12s
  (edge-tts currently returns empty audio from this host — `text_to_speech` fails with
  "No audio was received", and the `piper` provider needs a `piper-tts` pip package that is
  not installed; the vendored binary at `/opt/data/piper/piper/piper` works and is what
  `vo_v4_piper.sh` calls directly).
- Mix: VO + `music_bed.m4a` looped at 0.14, `loudnorm I=-14 TP=-2 LRA=11`, fade 88.8→90.0s,
  `alimiter` after loudnorm (AAC re-encode overshoots otherwise — measured +1.1 dBFS before
  the limiter was added).

## Measured facts (ffprobe / ffmpeg ebur128, not estimates)

```
video: h264 High, 1080x1920, yuv420p, 30/1 fps
audio: aac, 48000 Hz, 2 ch
format: mp4, duration 90.000000, size 11617073 B (~11.1 MB), faststart
loudness: I = -14.8 LUFS, True peak = -2.8 dBFS
```

## Frame QA

`qa4/grid_final.jpg` = 15 frames (t = 3, 10, 18, 25, 31, 37, 45, 50, 57, 62, 69, 74, 80, 84, 88).
Full-size individual frames in `qa4/`. Verified: all 15 show readable live interface, all carry
their caption, **no blank/teal frames**. The CTA lands over the running Control Room hero
(t=84), not over an empty screen.

## Known limitations (honest)

- **No cursor in the recording.** Headless Chromium's Playwright video does not draw the
  pointer. Mouse activity shows only through hover/click reactions, so no cursor ring was
  faked.
- **The Logs level filter did not survive.** The `WARNING` chip selector matched the left
  sidebar and navigated to `/sessions`; the script detected the URL change and returned to
  `/logs`, so the beat plays as a plain log-tail sweep rather than a filtered view. Logged
  in `fails_v4.json`.
- **The Sessions row detail did not open** (row/table selectors timed out). That beat plays
  as a sessions-list sweep. Also in `fails_v4.json`.
- The card-detail and logs segments are the same page for ~12s each. They carry live scroll
  and hover, but the visual variety inside a segment is lower than the reference's ~1–3s
  cut rhythm. Fixing this needs a denser recording pass (more distinct views per segment),
  not a re-cut.
- **The video is a screen recording of the internal dashboard**, so it shows real task text,
  agent names and model names from this workspace. No credentials or keys are visible, but
  the task titles are real internal titles — check before publishing publicly.
- The audio is a synthesised voice (piper medium), noticeably flatter than the reference's
  human VO. If a human voiceover of the same script becomes available, drop it in as
  `voiceover_v4.wav` and re-run PASS C/D only.
