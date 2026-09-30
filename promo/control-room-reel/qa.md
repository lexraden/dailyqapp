# QA — control_room_reel_v2.mp4

Source: `raw/page@310642add65247df0e8f0c43bea3e17e.webm` (VP8 1440x900, 25fps, **91.8s**) — the real Playwright screencast, no static screenshots.
Build: `./build_v2.sh` (ffmpeg only, ~45s).

## Trim / sync
- Uses source **1.75s → 61.75s** (60.0s). 0–1.75s is the login screen and page load, so it's cut. After ~62s the page is idle (a blank chat page), so that's cut too.
- voice.aac decodes to **60.04s**. The container header says 55.17s, but that estimate is wrong. The voice starts at t=0 and is trimmed to 60.0s. The beats line up: "change the theme" (14–24s) plays while the theme menu is open, "dark theme / there we go" plays on the dark map, "my projects" (44–53s) on the kanban, "where's the chat" (55s) on the chat page.
- Audio: loudnorm (I=-14, TP=-1.5), measured **I = -15.0 LUFS, LRA 7.0 LU** (fade included), fade-out 58.5–60s, AAC 128k 48kHz. No music.

## Composition
- 1080x1920 at 30fps. Foreground = an 810x900 focus window from the live recording (1.33x → 1080x1200). The window follows the active area with smooth 1s pans:
  map (0–12.8) → theme menu on the left (13.8–24.3) → dark map (25.3–31.8) → right agent panel/dropdown (32.8–40.3) → kanban (41.3–53.8) → sidebar CHAT (54.6–60).
- Background: the same frame, cover-scaled, gblur 32, darkened. Ken Burns 1.00→1.06 over the whole 60s.
- Captions bottom-center, fade 0.3s: Control Room / Agent map / Theme switcher / Theme: Midnight / Agent panel / Kanban / Chat.

## ffprobe
```
video: h264 (High), 1080x1920, yuv420p, 30/1 fps, duration 60.000000, ~986 kb/s
audio: aac, 48000 Hz, 2 ch, ~128 kb/s, duration 60.000000
format: mp4 (isom), duration 60.000000, size 8428440 B (~8.0 MB), moov at start (faststart)
```

## Frames (qa_frames/)
| file | t | shows |
|---|---|---|
| t02.jpg | 2s | Control Room, dark, agent map |
| t10.jpg | 10s | light theme (Nous Blue), agent map |
| t18.jpg | 18s | theme switcher menu open (live) |
| t28.jpg | 28s | Midnight applied, dark map |
| t36.jpg | 36s | agent panel + style dropdown |
| t48.jpg | 48s | Kanban board |
| t57.jpg | 57s | Chat page (sidebar) |

## Known limitations (honest)
- **No cursor in the recording.** Headless Chromium doesn't draw the pointer into the Playwright video. Mouse activity shows only through hover/click reactions, so a cursor ring was not added (it would have been faked).
- **The chat page never loaded** during recording (it shows "Loading chat…" and then stays empty). The last ~5.5s (54.5–60) shows the sidebar with CHAT, not typing in the composer. If you need the chat typing, re-record just the /chat segment.
- 0–4s: the dashboard opens in Midnight and switches to Nous Blue at ~4s (a leftover from the previous take). That's real behaviour, left as is.
