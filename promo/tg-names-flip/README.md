# tg-names-flip — рилс «NameRadar AI» (формат FlipRadar AI)

8 секунд, 9:16 (1080x1920), 30 fps, **без звука**. Тёмный наклонённый дашборд, хук сверху,
таблица сделок с Telegram-юзернеймами, бейджи Undervalued/Scanning/Sold, растущий счётчик сканов,
плавный zoom-in 1.0→1.08. Референс: `../references/flipradar_DcXan02Nepm/`.

| Файл | Что |
|---|---|
| `dashboard.html` | один файл, весь кадр + CSS-анимация. Можно открыть в браузере — крутится в цикле |
| `render.py` | Playwright → PNG-кадры → ffmpeg → mp4 |
| `hooks.md` | 3 варианта хука |
| `caption.md` | caption с CTA «Comment "NAME"» + дисклеймер |
| `ethics.md` | данные — simulated; что сделать перед публикацией |

## Сборка за 5 минут

```bash
cd /opt/data/projects/dailyqapp/promo/tg-names-flip

# 1. Один раз: окружение (≈1–2 мин)
python3 -m venv venv
./venv/bin/pip install playwright
./venv/bin/playwright install chromium
#   На этом сервере шаг можно пропустить: PLAYWRIGHT_BROWSERS_PATH=/opt/hermes/.playwright,
#   там уже есть chromium_headless_shell (каталог read-only, install падает с EACCES — это нормально).

# 2. (опц.) поменять хук/данные в dashboard.html — блок #hook и <tbody>

# 3. Быстрый черновик (10 fps, ~20 с)
./venv/bin/python render.py --fps 10 --out preview.mp4

# 4. Финал: 8 с, 30 fps, без звука (~1–2 мин)
./venv/bin/python render.py                 # с плашкой DEMO · SIMULATED DATA
./venv/bin/python render.py --no-demo       # ТОЛЬКО если в таблице реальные данные (ethics.md)

# 5. Проверка
ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate -show_entries format=duration nameradar_reel.mp4
```

Результат: `nameradar_reel.mp4` (H.264, yuv420p, faststart, аудиодорожки нет).
Кадры остаются в `frames/` — их можно удалить: `rm -rf frames`.

## Таймлайн анимации

| t | событие |
|---|---|
| 0.0 | хук уже на экране, радар крутится, тикер едет, счётчик сканов растёт |
| 0.0 | 2 строки таблицы и 2 строки лога уже на экране |
| 0.3–2.5 | ещё 6 строк въезжают по одной с зелёной вспышкой |
| 4.2 | @vpnx: SCANNING → UNDERVALUED, строка в логе «flagged» |
| 5.6 | @tonbox: UNDERVALUED → SOLD, вспышка строки, PROFIT THIS WEEK +$550 |
| 0–8 | zoom-in 1.0 → 1.08 (ease-in-out) |

Тайминги — в CSS (`animation-delay`) и в функции `paint()` внизу `dashboard.html`.

## Публикация

Caption — из `caption.md`, хук-альтернативы — `hooks.md`. Музыку НЕ добавлять: беззвучность — часть формата.
