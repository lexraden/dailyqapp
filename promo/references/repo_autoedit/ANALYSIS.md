# 1) ЧТО ЭТО

**Архитектура.** `LochlanMacQueen/auto-edit` — локальный оркестратор контента и физических iPhone: Phone Farm принимает и возобновляет задания, планирует их через PostgreSQL, отображает экран устройства и выполняет версионированные WDA/Appium-действия; Claude не тапает координаты постоянно, а составляет план/recipe, а локальный runner детерминированно выполняет шаги и останавливается на неоднозначных состояниях. UGC-конвейер состоит из трёх этапов: Palmier Pro/ffmpeg нормализует talking-head素材 и запекает звук, Instagram Edits на iPhone добавляет captions/headers и экспортирует ролик, затем Instagram Composer публикует его. Jev используется только как классификатор состояния экрана в контрольных точках, когда обычных accessibility-признаков недостаточно.

**Ключевые компоненты:**

- **Phone Farm iOS** — Node.js dashboard/API, worker, Appium и сервис подписанного WebDriverAgent; PostgreSQL-очередь, per-device ownership, история, Stop, durable task contract `pluginId/taskType/taskVersion/payload`.
- **Palmier Pro** — desktop-редактор с локальным MCP на `127.0.0.1:19789`; Claude управляет монтажом через raw JSON-RPC, а ffmpeg и Whisper выполняют подготовку и проверку.
- **Instagram Edits** — нативное iOS-приложение для captions, текстовых дорожек, стилей и экспорта; автоматизируется через WDA.
- **Jev** — модель TypeSafe, получающая компактное accessibility-наблюдение, а не изображение или видео; проверяет состояние вроде `timeline`, `text_editor`, `export`, `share`. Дефолтный порог — confidence и selected probability не ниже `0.85`.
- **UGC-пайплайн** — агентный контракт, Palmier/ffmpeg runbook, scripts для captions/headers, resume-флаги, визуальные checkpoints, trial/publication gate и журнал времени публикаций.

# 2) ЧТО ЦЕННО ДЛЯ НАС

- **Агентный контракт — взять почти напрямую.** Из `ugc/AGENT_PROMPT.md` стоит перенести правила: сначала делать работу, а не перечислять варианты; на первом запуске нового формата проводить целевой бриф; derives all on-screen text from the actual transcript; требовать approval перед следующим этапом и перед публикацией; выдавать короткий фактический отчёт с результатами и проверками. Для DailyQ это хороший системный prompt для цепочки `IDEA→SCRIPT/RENDER→QA→PUBLISH`.

- **FFmpeg-рецепт — наиболее прямой适配 для Linux.** Из `ugc/docs/palmier-pipeline.md`, `ugc/examples/palmier_build_example.py` и `ugc/examples/bake_music_example.sh` берутся:
  - `silencedetect` как начальная метрика речи;
  - padding начала/конца speech span;
  - повторная транскрипция отдельных фрагментов для поиска false starts;
  - frame-accurate trimming по `round(duration × fps)`;
  - проверка отсутствия однокадровых gaps;
  - запекание разрешённой музыки с fade;
  - финальный `ffprobe` и повторное чтение готового файла через Whisper.
  
  Параметры из примера (`-28 dB`, `0.25 s`, padding `0.07/0.13 s`) — стартовый профиль для benchmark, а не универсальная константа для любого DailyQ-контента.

- **Транскрипт как единственный источник текста.** Правило «не угадывать сказанное» особенно важно для автоматических headers, captions и CTA. Полезный формат входа — адаптация `ugc/examples/headers.example.json`: transcript-derived секции, тайминги, стили, CTA и platform caption в одном manifest-файле.

- **Recipe/checkpoint model — перенести в Playwright.** Из `docs/claude-edits.md` и `examples/edits/check-editor.json` берутся:
  - именованные семантические selectors вместо произвольных координат;
  - `expect`/postcondition после каждого действия;
  - polling конкретного состояния вместо длинных sleeps;
  - модель только на неоднозначных переходах;
  - обязательный screenshot/review checkpoint;
  - batch по одному смысловому макро;
  - выполнение только оставшейся части recipe после ошибки;
  - запрет blind retry после неоднозначного mutation.
  
  В Playwright это ложится на `getByRole`/label/locator, `expect`, screenshots и Playwright trace. Jev как отдельный платный сервис не обязателен: сначала следует использовать DOM/ARIA и детерминированные assertions.

- **Динамическое обнаружение timeline вместо фиксированной геометрии.** Из `ugc/edits_timeline.py` полезен принцип `rows()/tracks()/caption_y()` — повторно читать структуру перед каждым действием, потому что строки прокручиваются и toolbar меняет координаты. Само значение `PLAYHEAD_X = 195` и другие константы не переносить: они привязаны к iPhone 13 Pro. Для DailyQ нужен эквивалент discovery по semantic timeline markers или metadata из собственного renderer.

- **Визуальная QA-логика.** `ugc/edits_text.py` показывает полезный паттерн: снимать кадр, измерять фактическое положение и размер текста через пиксельный анализ и повторять действие до допуска. Это стоит адаптировать на выходные кадры ffmpeg: проверять safe zones, переполнения, размер, контраст, длительность и отсутствие чёрного хвоста. Хардкод `1170`, `PREVIEW_Y0` и drag gain не переносить.

- **Stage state machine и resume.** `ugc/edits_pipeline.py` полезен как образец декомпозиции `import → project → captions → headers → export → compose` и флагов `--resume-headers/--resume-sections/--no-import`. В DailyQ это стоит превратить в явные состояния задания и operation IDs, чтобы повторный запуск не дублировал экспорт или публикацию. Сам WDA-код не исполнять.

- **Dry-run и publication gate.** Из `ugc/ig_share_trial.py` полезны идеи trial-режима, обязательного подтверждения аккаунта и журнала времени постинга. В DailyQ это должно стать publish manifest, manual approval и audit log, а не автоматическим нажатием Share.

- **Версионированный job contract.** Из `src/plugin.ts`, `docs/plugins.md` и `PLUGIN_DEVELOPMENT.md` стоит взять неизменяемую версию payload, явный contract stage, plugin/task type, durable status и запрет silently running старого расписания с новой семантикой. PostgreSQL для этого не нужен — достаточно текущего durable queue DailyQ.

- **Preflight и безопасность.** Из `ugc/check_setup.sh`, `SECURITY.md` и `docs/architecture.md` берутся идеи проверки окружения до запуска, loopback-only binding, secrets вне репозитория и запрет подключения production devices/credentials в CI. Preflight DailyQ должен проверять ffmpeg/ffprobe, fonts, whisper/model, browser, storage, proxies и credentials.

# 3) ЧТО НЕ ПОДХОДИТ

**Железо и ОС:**

- Репозиторию нужны macOS, полный Xcode, Apple signing, физический iPhone с Developer Mode, USB/trust, подписанный real-device WebDriverAgent и Appium XCUITest driver.
- Нужны Node.js 22+, PostgreSQL и четыре долгоживущих процесса: dashboard/web, worker, Appium и WDA service.
- Нужны logged-in Instagram и Instagram Edits, Palmier Pro с MCP, а также Apple-ориентированный `mlx-whisper`.
- Linux-сервер не может заменить Xcode/signing и надёжно эмулировать native iOS UI. Playwright не является drop-in replacement для WDA в Instagram Edits.
- Поэтому роль «Claude оперирует iPhone» у нас невозможна без физических устройств. Теоретически можно держать отдельную Mac+iPhone farm и управлять ею удалённо, но это уже отдельный дорогой и сложный контур, а не часть текущего Linux DailyQ.
- Код `ugc/phone.py`, `ugc/edits_pipeline.py`, `ugc/edits_headers2.py` и `ugc/ig_share_trial.py` не следует запускать на DailyQ: он зависит от WDA, bundle IDs, авторизованного Instagram и geometry конкретного iPhone.

**Надёжность и сопровождение:**

- Runbook и geometry измерены на iPhone 13 Pro; другие размеры экрана, версии iOS и изменения Instagram Edits ломают coordinates.
- В коде много фиксированных координат, `sleep`, ручной проверки и screen-specific констант. Это runbook, а не универсальный production automation SDK.
- Jev не умеет оценивать изображение, звук, типографику, монтаж или качество видео; это только state classifier.
- Документация прямо признаёт отсутствие live benchmark и требует supervised representative run. Заявленный выигрыш нельзя принимать без собственного измерения времени, recoveries и manual interventions.
- Старые scripts в `~/ugc-ops` содержат stale fixed-coordinate и clear-and-retry логику; их нельзя переносить wholesale.

**Лицензия и права:**

- **Apache-2.0 для кода — в принципе подходит** для внутреннего и коммерческого использования, модификации и распространения. При публичном redistribution нужно сохранить `LICENSE`/`NOTICE`, notices и отметить изменения.
- Apache-2.0 репозитория не покрывает автоматически лицензии/права Palmier Pro, TypeSafe/Jev, Instagram/Meta, Apple, шрифтов, музыки, моделей Whisper и содержимого из `ugc/examples/`. Их надо проверять отдельно; особенно не переносить example music/reel без прав.
- Palmier Pro и другие внешние компоненты могут иметь собственные EULA/коммерческие ограничения даже при Apache-лицензии форка.

**Instagram-риск:**

- UI-автоматизация Instagram/Edits может нарушать применимые Terms of Use и внутренние anti-automation правила. Возможны challenge, temporary block, ограничение аккаунта, потеря draft/session и прекращение поддержки selectors без предупреждения.
- Бан-риск нельзя считать устранённым локальным WDA или медленным темпом. Для основного аккаунта безопаснее официальный API там, где он доступен, либо ручная загрузка после approval.
- Если автоматизация всё-таки тестируется: отдельный тестовый аккаунт, минимальные rate limits, dry-run, ручное подтверждение аккаунта/caption, сохранение screenshots и audit log, никаких credentials в prompts/logs.

# 4) ВЕРДИКТ ДЛЯ НАС

## **Вердикт: ADAPT.**

- **ADOPT:** агентные правила, transcript-derived text, approval gates, manifest-driven render, named selectors, expected postconditions, checkpoints, resume по оставшимся операциям, verification через ffprobe/Whisper/визуальные кадры.
- **ADAPT:** Palmier pipeline — в нативный Linux/ffmpeg renderer; Edits recipes — в Hermes/Playwright; Jev — в локальный rule-based state machine с моделью только при неоднозначности.
- **SKIP:** Phone Farm целиком, PostgreSQL scheduler, Xcode/Appium/WDA, Palmier MCP, iPhone-specific geometry, `ig_share_trial.py` и автоматический Instagram Share.

**Минимальный шаг сегодня:** не разворачивать репозиторий как сервис, а сохранить его как versioned reference subset:

```bash
export AUTO_EDIT=/путь/к/auto-edit
DEST=/opt/data/projects/dailyqapp/third_party/auto-edit-reference

mkdir -p "$DEST"
cd "$AUTO_EDIT"

cp --parents \
  LICENSE \
  ugc/AGENT_PROMPT.md \
  ugc/docs/palmier-pipeline.md \
  ugc/examples/palmier_build_example.py \
  ugc/examples/bake_music_example.sh \
  ugc/examples/headers.example.json \
  ugc/edits_timeline.py \
  ugc/edits_text.py \
  ugc/edits_pipeline.py \
  ugc/ig_share_trial.py \
  docs/claude-edits.md \
  examples/edits/check-editor.json \
  docs/plugins.md \
  src/plugin.ts \
  "$DEST"/

# Скопировать NOTICE отдельно, если он есть в корне.
printf '%s\n' \
  'Reference only. Do not execute iPhone/WDA/Palmier/Instagram code.' \
  'Adapt prompts, ffmpeg verification, recipe checkpoints and task contracts into DailyQ.' \
  > "$DEST/REFERENCE_ONLY.md"
```

После копирования взять **один существующий DailyQ-ролик** и добавить только пилотный профиль: transcript-derived `content_spec.json`, dead-space cut, запекание разрешённого аудио, `ffprobe`, повторную транскрипцию и `qa.json`. Не подключать пока ни Xcode/Appium/PostgreSQL, ни автоматизацию Instagram.