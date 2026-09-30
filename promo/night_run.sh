#!/bin/bash
# Ночная продакшн-сборка контент-фермы через Claude Code
set -u
PROMO=/opt/data/projects/dailyqapp/promo
REFS=$PROMO/references
export PATH="/opt/data/npm-global/bin:$PATH"
cd $PROMO

run() {
  name="$1"; promptfile="$2"
  echo "=== [$name] start $(date +%H:%M:%S)"
  claude -p --dangerously-skip-permissions --output-format text --max-turns 60 < "$promptfile"
  echo "=== [$name] done rc=$? $(date +%H:%M:%S)"
}

# TASK 1: яхта-рилс продакшн-пакет
cat > /tmp/prompt_yacht.md <<'EOF'
Ты — продакшн-агент контент-фермы. Работай в /opt/data/projects/dailyqapp/promo/yacht-campaign/ (создай если нет).

Задача: подготовить ПОЛНЫЙ продакшн-пакет рилса для Meta Ads (проект: продажа яхт в UAE, у владельца 2 тёплых контакта).

Сначала ПРОЧИТАЙ референсы:
- references/yachts_DdmoqJtANBC/README.md (чеклист пересъёмки, 7 ракурсов)
- references/yachts_DdmoqJtANBC/vision.json (покадровый разбор)
- references/nh_partners_ad_screenshot.jpg нельзя читать, но разбор оффера есть в README яхт-папки (раздел про NH Partners).

Создай в yacht-campaign/:
1. shot-list.md — 7 ракурсов на 15с, адаптирован под съёмку ТЕЛЕФОНОМ с джетски/воды: каждый шот = длительность, ракурс, движение камеры, что в кадре, совет по стабилизации/экспозиции.
2. script.md — сценарий с тайм-кодами, вариант A (без титров, трендовый трэп-трек) и вариант B (2-3 текстовых плашки-оффера).
3. caption.md — 3 варианта caption (RU+EN) + хэштеги + CTA.
4. meta-ads-setup.md — структура кампании: objective (Traffic vs Leads vs Engagement для теста), 3 креатива для ABO-теста с бюджетами, таргетинг UAE (interests: yachting, luxury, real estate; age 28-55; размещение Reels/Facebook), события пикселя/лид-форма, метрики успеха (CPL, thumbstop >30%, CTR).
5. offer-copy.md — 3 варианта оффера по шаблону NH Partners (обещание → гео → ценовой якорь → снятие рисков → CTA), RU+EN. ВАЖНО: цены НЕ выдумывать — оставить плейсхолдеры [ЦЕНА] с комментарием «согласовать с владельцем», т.к. у него 2 контакта и модель продажи не зафиксирована.
6. checklist-launch.md — чеклист запуска с нуля: что снять, чем смонтировать (CapCut), как собрать кампанию, что замерить через 72ч.

Пиши по-русски, конкретно, без воды. Не ходи в интернет. Не отправляй ничего наружу.
EOF
run yacht /tmp/prompt_yacht.md

# TASK 2: FlipRadar-формат под TG-names
cat > /tmp/prompt_flip.md <<'EOF'
Ты — продакшн-агент контент-фермы. Работай в /opt/data/projects/dailyqapp/promo/tg-names-flip/ (создай если нет).

Задача: воспроизвести формат вирального рилса FlipRadar AI (8 секунд, БЕЗ звука, 977 shares/2619 saves) под продукт: ИИ-агент скупает и перепродаёт Telegram-юзернеймы на autopilot.

Сначала ПРОЧИТАЙ референс:
- references/flipradar_DcXan02Nepm/README.md (разбор формата и инсайт «беззвучный формат»)
- references/flipradar_DcXan02Nepm/vision.json (покадровый разбор вёрстки)

Создай в tg-names-flip/:
1. dashboard.html — ОДИН файл: тёмный дашборд 9:16-фрейма (charcoal/navy фон, неоново-зелёные метрики, наклон/перспектива как у референса). Содержимое: шапка с названием (например "NameRadar AI"), строка-хук сверху, таблица 6-8 строк: username | bought | est. resale | profit | статус-бейдж (Undervalued/Scanning/Sold). Реалистичные цифры TG-юзернеймов (короткие @name, цены $50-$3000). CSS-анимация: строки появляются, статусы мигают, счётчик scans растёт. Кнопка/тултип NOT включать.
2. render.py — скрипт: Playwright или selenium открывает dashboard.html и снимает N фреймов (анимация по шагам) в 1080x1920 PNG + сборка в mp4 через ffmpeg (8с, 30fps, без звука, лёгкий zoom-in 1.0→1.08). Если Playwright не установлен — pip install playwright && playwright install chromium (в venv ./venv).
3. hooks.md — 3 варианта hook-строки (EN): базовый + 2 альтернативы.
4. caption.md — caption с CTA «Comment "NAME"» + дисклеймер.
5. ethics.md — короткая заметка: таблица в макете — демонстрационная (simulated data); перед публикацией заменить на реальные данные работающего бота или пометить «Demo».
6. README.md — как собрать финальное видео за 5 минут (команды).

Пиши по-русски (кроме UI-текстов — они EN). Проверь что dashboard.html открывается и render.py запускается (если окружение позволяет). Не ходи в интернет кроме pip/playwright. Не отправляй ничего наружу.
EOF
run flip /tmp/prompt_flip.md

echo "ALL NIGHT JOBS DONE $(date +%H:%M:%S)"
