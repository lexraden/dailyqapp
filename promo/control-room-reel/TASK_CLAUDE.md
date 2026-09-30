# Task: Cinematic Control Room reel (60s, 1080x1920)

Workdir: /opt/data/projects/dailyqapp/promo/control-room-reel

## Inputs
- raw/*.webm — JUST-RECORDED real Playwright screencast (1440x900, ~60s): dashboard at 127.0.0.1:8080, live cursor, theme switch light->dark, agent map hover, kanban card click, chat typing. Convert with `venv/bin/ffmpeg` or system ffmpeg (webm vp8 -> mp4).
- voice.aac — user's 60s Russian voiceover (mux as audio bed, pad to duration).
- storyboard.md — section plan.
- control_room_reel.mp4 — OLD rejected version (static screenshots, do NOT reuse).

## Requirement (user, verbatim intent)
"нам нужно прямо именно скринрекординг... чтобы все в процессе видеть... и по центру всегда должно быть что-то интересное, типа фокуса" — the reel must show the REAL recording, never static screenshots.

## Target quality (user reference: POV "building my own JARVIS" reel)
- 1080x1920 vertical, 30fps, crisp text (source is 1.5x DPR — good).
- The screencast itself is the hero: crop/compose so the ACTIVE area (theme menu, agent node, card, chat composer) stays CENTERED and large. 9:16 composition: blurred/zoomed background of same frame + foreground screen, gentle Ken Burns zoom 1.0-1.06, but the foreground must be the real moving recording, not a still.
- Highlight the cursor: subtle ring/glow overlay following recorded cursor is a bonus (can approximate with ffmpeg filters only if simple).
- Section labels as small captions bottom-center (like user approved on previous reels): e.g. "Control Room", "Theme: Midnight", "Agent map", "Kanban", "Chat". Keep them small, out of the way, MAX ~3-4 words.
- Audio: voice.aac, loudnorm, fade out last 1.5s. No music unless trivially quiet bed (-28 LUFS under voice) — optional, skip if unsure.
- Duration exactly ~60s, synced to voice end.

## Deliverables
- control_room_reel_v2.mp4 in workdir (final, h264, yuv420p, aac 128k, faststart)
- build_v2.sh — reproducible build script
- qa.md — short QA: ffprobe output (duration, resolution, streams) + 6 extracted frames saved as qa_frames/*.jpg

## Constraints
- ffmpeg only (system or venv). No new pip installs except nothing needed.
- Do not touch anything outside this workdir except reading raw/.
- If raw/*.webm missing or duration <55s, STOP and write qa.md saying "recording incomplete" instead of faking.
