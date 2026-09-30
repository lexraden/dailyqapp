# Спец-док SKILL auto-reel-montage (stealth, черновик к t_f19cced1)

## Готовый SKILL.md

Сохранить как `skills/auto-reel-montage/SKILL.md`.

~~~markdown
---
name: auto-reel-montage
description: >-
  Автоматически собирает вертикальные Reels из raw footage или HTML-dashboards:
  анализирует сцены, выбирает hook, обновляет hooks.cfg/scenes.cfg,
  рендерит через Playwright/ffmpeg и выполняет QA-ffprobe/volumedetect.
---

# Auto Reel Montage

## Mission

Собрать готовый к публикации silent Reel из:

- HTML-dashboards с CSS-анимацией;
- на