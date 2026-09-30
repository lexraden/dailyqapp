# Пайплайн публикации рилсов: Instagram (основная) + другие соцсети

_Исследование от 2026-09-28. Все лимиты взяты из официальной документации (ссылки рядом). Где источник сторонний — помечено «(вторичный источник)»._

---

## TL;DR

1. **Официальный путь работает и бесплатный:** Instagram API with Instagram Login (бывший «Business Login for Instagram»). Нужен **профессиональный аккаунт (Business или Creator)**, Facebook Page **не обязательна**. Для своего аккаунта хватает приложения в Development mode, App Review не нужен.
2. **Лимит: 100 опубликованных через API постов за скользящие 24 часа** (не 25 — эта цифра устарела). Reels поддерживаются (`media_type=REELS`).
3. **Кликабельных ссылок в подписи нет** (кроме теста для части Meta Verified). Рабочая схема: CTA в подписи → **ссылка в bio (до 5 ссылок)** → свой лендинг с UTM. Плюс сторис со стикером-ссылкой — вручную (у API нет link sticker).
4. **instagrapi / private API — не для основного аккаунта бренда.** Нарушает правила, в 2026 часто ловит `challenge_required` и баны. Мобильная автоматизация (эмулятор/телефон) — тот же риск.
5. **Для combo-posting строим:** Python-сервис на сервере → очередь mp4 → ffmpeg-нормализация → публичный URL (или resumable upload) → Graph API → лог/ретраи. Playwright для IG **не нужен**.

---

## 1. Instagram Content Publishing API (Meta) — факты 2026

Источники:
- Content Publishing: https://developers.facebook.com/docs/instagram-platform/content-publishing/
- То же для Instagram Login: https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing
- Обзор двух конфигураций API: https://developers.facebook.com/docs/instagram-platform/overview/
- Справочник `/media` (спеки видео): https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media
- Refresh токена: https://developers.facebook.com/docs/instagram-platform/reference/refresh_access_token

### 1.1 Два варианта API

| | **Instagram API with Instagram Login** | **Instagram API with Facebook Login for Business** |
|---|---|---|
| Facebook Page | **не нужна** («presence on Instagram only») | **обязательна**, IG привязан к Page |
| Типы аккаунтов | Business и Creator | Business и Creator (привязанные к Page) |
| Публикация (в т.ч. Reels) | ✅ | ✅ |
| Комменты / DM / Insights | ✅ / ✅ / ✅ | ✅ / ✅ (через Messenger Platform) / ✅ |
| Hashtag search, product tagging | ❌ | ✅ |
| Хост API | `graph.instagram.com` | `graph.facebook.com` |
| Права | `instagram_business_basic`, `instagram_business_content_publish` | `instagram_basic`, `instagram_content_publish`, `pages_read_engagement` (+ `ads_management`, `ads_read` если роль на Page через Business Manager) |

Личные (personal) аккаунты не поддерживаются ни в одном варианте.

**Доступ:** «Standard Access» — по умолчанию, достаточно, если приложение работает только с аккаунтами, которыми вы владеете/управляете. «Advanced Access» (с App Review) нужен только для чужих аккаунтов. Т.е. для аккаунтов Александра — App Review не нужен.

**Нюанс с Page (только для варианта с Facebook Login):** если Page требует Page Publishing Authorization (PPA), публикация падает, пока PPA не пройдена; Meta советует пройти PPA заранее.

> Замечание: некоторые сторонние гайды 2026 года (напр. getphyllo) пишут, что для Reels «обязательна Facebook Page» — это противоречит официальному обзору Meta выше. Опираемся на официальную доку. Если при первой публикации без Page будет ошибка — fallback: привязать Page и перейти на Facebook Login.

### 1.2 Лимиты

- **100 API-публикаций на аккаунт за скользящие 24 часа**; карусель считается за 1 пост. Проверка использования: `GET /<IG_ID>/content_publishing_limit`.
- Токен: long-lived действует **60 дней**; обновляется через `GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=...` — токен должен быть **не моложе 24 часов и не истёкший**. Истёк → заново логиниться. ⇒ в сервисе нужен cron на refresh (например, раз в неделю).

Практически: для органического роста 100/сутки не ограничение — разумная частота 1–2 рилса в день на аккаунт.

### 1.3 Что можно

- Reels (`media_type=REELS`), видео, фото (только JPEG), карусели (до 10 элементов), Stories (`media_type=STORIES`).
- Параметры Reels: `caption`, `share_to_feed` (показывать и в ленте), `cover_url` / `thumb_offset` (обложка), `audio_name`, `collaborators` (до 3 username), `location_id`, `user_tags`, `trial_params` (Trial Reels — показ сначала не-подписчикам; `MANUAL` или `SS_PERFORMANCE`).
- Подпись: до **2200 символов**, до **30 хэштегов**, до **20 @упоминаний**.

### 1.4 Чего нельзя через API

- Фильтры, shopping tags (в Instagram Login варианте), `alt_text` для Reels/Stories, не-JPEG картинки.
- Link sticker в Stories (в API его нет — только из приложения).
- Выбор трека из музыкальной библиотеки Instagram (можно только своё аудио в файле; `audio_name` лишь переименовывает).
- Кликабельные ссылки в подписи (их вообще нет, см. раздел 3).

### 1.5 Спеки видео для Reels (официальные)

| Параметр | Требование |
|---|---|
| Контейнер | MP4/MOV, **без edit lists, moov atom в начале файла** |
| Видео | H.264 или HEVC, progressive, closed GOP, 4:2:0 |
| Аудио | AAC, **≤ 48 kHz**, моно/стерео, 128 kbps |
| FPS | 23–60 |
| Разрешение | макс. 1920 px по горизонтали; рекомендуется 9:16 |
| Битрейт видео | VBR, ≤ 25 Mbps |
| Длительность | **3 сек – 15 мин** |
| Размер | ≤ 300 MB |
| Обложка | JPEG, ≤ 8 MB, sRGB, 9:16 |

**Проверка наших готовых файлов (ffprobe, 2026-09-28):**

| Файл | Размер/кадр | Длит. | Аудио | moov в начале | Вердикт |
|---|---|---|---|---|---|
| `control-room-reel/control_room_reel_v3.mp4` | 1080×1920, 30fps, h264 | 50 с | AAC 48k | ✅ | готов |
| `tg-names-flip/nameradar_reel_sfx.mp4` | 1080×1920, 30fps | 8 с | AAC 44.1k | ❌ (moov в конце) | нужен `-movflags +faststart` |
| `heygen-reel/batch_v{1..4}_*.mp4` | 720×1280, 30fps | 5.4 с | **нет аудио** | ❌ | faststart + добавить звук (рилс без звука хуже ранжируется) |

Нормализация одной командой (перекодирует под спеку, ставит faststart):
```bash
ffmpeg -i in.mp4 -c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -g 60 -keyint_min 60 -sc_threshold 0 -b:v 8M -maxrate 10M -bufsize 16M \
  -c:a aac -ar 48000 -ac 2 -b:a 128k -movflags +faststart out.mp4
# для файлов без звука добавить тишину или music bed:
#   -f lavfi -i anullsrc=r=48000:cl=stereo -shortest
```

### 1.6 Flow публикации рилса

1. `POST https://graph.instagram.com/v<ver>/<IG_ID>/media` с `media_type=REELS`, `video_url=<публичный https URL>`, `caption=...`, `share_to_feed=true` → получаем `container_id`.
   - Видео **должно лежать на публично доступном сервере** в момент запроса. Альтернатива — `upload_type=resumable`, затем `POST https://rupload.facebook.com/ig-api-upload/<container_id>` с бинарём (не нужен публичный хостинг).
2. Поллинг `GET /<container_id>?fields=status_code` до `FINISHED` (варианты: `IN_PROGRESS`, `FINISHED`, `ERROR`, `EXPIRED`, `PUBLISHED`). Разумно: раз в 10–30 с, таймаут ~10 мин.
3. `POST /<IG_ID>/media_publish` с `creation_id=<container_id>` → `media_id`.
4. (опц.) `POST /<media_id>/comments` — первый коммент с доп. хэштегами/CTA.
5. `GET /<IG_ID>/content_publishing_limit` — лог квоты.

Официальный пример кода: GitHub `fbsamples/reels_publishing_apis` (insta_reels_publishing_api_sample) — упомянут в доке Content Publishing.

---

## 2. Альтернативы: Graph API vs private API vs мобильная автоматизация

| Путь | Легальность | Стабильность | Риск бана | Когда использовать |
|---|---|---|---|---|
| **Graph API (официальный)** | ✅ разрешено Meta | высокая, версии API документированы | ~нулевой (если контент не нарушает правила) | **основной путь** |
| **instagrapi / private API** (эмулирует мобильное приложение, логин паролем) | ❌ неофициальная автоматизация, против Terms of Use | низкая: ломается при изменениях приложения | высокий: `challenge_required`, чекпоинты, суспенды | только на «одноразовых» тестовых аккаунтах, не на бренде |
| **Мобильная автоматизация** (Appium/ADB на эмуляторе или реальном телефоне, «ферма») | ❌ тоже автоматизация без разрешения | средняя, хрупкие селекторы | средний–высокий (эмуляторы детектируются; с сервера в ЕС/США при аккаунте из Дубая — гео-аномалии) | не рекомендую |
| **Playwright/Chrome на instagram.com** | ❌ то же самое | низкая | средний–высокий | не нужно — всё, что нужно, есть в API |
| **SaaS-планировщики** (Buffer, Later, Metricool, Meta Business Suite) | ✅ используют официальный API | высокая | нет | ручной запасной вариант; **Meta Business Suite — бесплатно**, умеет планировать Reels |

Факты по private API (2026):
- instagrapi логинится паролем и притворяется мобильным приложением; Instagram считает это неавторизованной автоматизацией; в 2025–2026 правоприменение ужесточилось — https://www.postzen.dev/blog/instagrapi-vs-instagram-graph-api (вторичный источник)
- `challenge_required` — серверная риск-модель; issue #2718 (июль 2026) — challenge на логине на актуальной версии — https://instagrapi.com/guides/errors/challenge-required
- Даже официальные best practices библиотеки: переиспользовать сессии, резидентные прокси, не начинать с write-heavy действий на новых аккаунтах — https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html
- Общий разбор рисков: https://postengage.ai/blog/instagram-automation-ban-risk-truth (вторичный источник)

**Вывод:** у нас готовые mp4 и нужна только публикация + подпись → всё покрывается официальным API. Private API даёт лишь то, что нам не критично (музыка из библиотеки, link sticker), ценой риска потерять аккаунт бренда.

---

## 3. Пайплайн: mp4 → IG Reel → caption с CTA → ссылка на продукт

### 3.1 Ссылки в Instagram — что реально работает

- **Ссылки в подписях не кликабельны** (by design). С марта 2026 идёт тест кликабельных ссылок в подписях только для части **Meta Verified** (до 10 ссылок/мес) — не рассчитываем. https://petapixel.com/2026/03/16/instagram-begins-testing-clickable-links-in-post-captions/
- **Bio: до 5 внешних ссылок** (Edit profile → Links → Add external link). В профиле видна первая + «и ещё N». https://www.planoly.com/blog/links-for-instagram-bio
- **Stories: link sticker доступен всем аккаунтам** — https://help.instagram.com/192168966243613/ и https://about.instagram.com/blog/announcements/expanding-sharing-links-in-stories-to-everyone (через API не ставится → ручная сторис-репост рилса со стикером).
- **Comment-to-DM** («напиши DAILY в комментах — пришлём ссылку»): через официальный Instagram API (webhooks комментов + Messaging) — законно, и в DM ссылка кликабельна. Готовые решения (ManyChat и т.п.) платные — только с OK Александра; можно сделать своё на том же API позже.

### 3.2 Схема ссылок (рекомендация)

```
Рилс (CTA в подписи + в последних 2 сек видео: «ссылка в профиле»)
   └─> Bio link #1: свой лендинг  links.<домен>/ig  (одна страница со всеми продуктами)
          ├─ DailyQ      → https://cr-web-production.up.railway.app/?utm_source=instagram&utm_medium=bio&utm_campaign=<reel_id>
          ├─ Botify      → t.me/<bot>?start=ig_<reel_id>   (TG deep-link = трекинг)
          └─ GitHub/code → github.com/lexraden/botify
   └─> Bio links #2–5: прямые на топ-продукты (DailyQ, Botify)
```

**Linktree/Beacons vs свой лендинг:**
- Linktree/Beacons: 5 минут на старт, бесплатные тарифы есть, но брендинг сервиса и ограниченная аналитика на free.
- **Свой лендинг (рекомендую):** одна статическая страница на том же Railway или GitHub Pages, свой домен/поддомен, полные UTM, можно менять «ссылку недели» под свежий рилс без правки профиля. Мы можем сгенерировать её сами — бесплатно.
- Компромисс на сегодня: поставить прямую ссылку на DailyQ + Botify в bio (2 из 5 слотов), свой лендинг — следующим шагом.

### 3.3 Шаблон подписи

```
<хук 1 строка — то же, что на первом кадре>
<1–2 строки ценности>

👉 Попробовать: ссылка в профиле (@<handle>)
💬 Напиши «DAILY» — пришлём ссылку в директ   ← когда будет comment-to-DM

#dailyq #productivity #<3–5 нишевых хэштегов>
```
Ограничения: ≤2200 символов, ≤30 хэштегов, ≤20 упоминаний. Практически 3–5 релевантных хэштегов.

### 3.4 Про музыку

Бизнес-аккаунтам доступна только Meta Sound Collection (коммерчески очищенные треки); Creator-аккаунтам — широкий каталог. Через API в любом случае публикуем **своё аудио из файла**, поэтому треки в наших mp4 должны быть royalty-free/собственные (как `music_bed.m4a`, voiceover). https://tripepismith.com/insights/music-in-reels-business-accounts/

---

## 4. Что нужно от Александра

### 4.1 Тип аккаунта

- **Professional → Creator** (рекомендую для личного бренда-фаундера): работает с API через Instagram Login, шире музыкальная библиотека для ручных постов.
- **Professional → Business** — если аккаунт позиционируется как продукт/компания (DailyQ как бренд), нужны кнопки контактов/адрес. Для API разницы нет.
- Переключение: Settings → Account type and tools → Switch to professional account. Бесплатно и обратимо.

### 4.2 Facebook Page

- **Не требуется** для нашего пути (Instagram Login).
- Нужна, только если потом захотим: hashtag search, product tagging, кросспост Reels на Facebook, реклама через Ads Manager. Тогда: создать Page → привязать IG в Accounts Center → пройти PPA.

### 4.3 Доступы (что Александр делает сам, пароли нам не передаёт)

1. Создаёт (или переключает) IG-аккаунт в Professional.
2. Регистрируется на https://developers.facebook.com (тем же Facebook/Meta-аккаунтом, что в Accounts Center, или отдельным) → создаёт App типа Business → добавляет продукт «Instagram» → «API setup with Instagram login».
3. App roles → Roles → добавить IG-аккаунт как **Instagram Tester**, принять приглашение в приложении Instagram.
4. Нажать «Generate access token» у своего аккаунта → отдать нам **только токен + IG user ID** (через Vault), не пароль.
5. Приложение остаётся в Development mode — App Review не нужен для своего аккаунта.

---

## 5. Связка с Gmail

- **Отдельный Gmail под бренд — да, рекомендую** (например `dailyq.brand@gmail.com`): на него регистрируются IG, Meta Developer, YouTube, TikTok, Threads, домен/лендинг. Причины: разделение с личной почтой, можно дать доступ ассистенту/подрядчику, восстановление аккаунтов не завязано на личный ящик. Один Gmail на все бренды — ок на старте; при появлении отдельной команды у продукта — отдельный.
- **2FA везде через приложение-аутентификатор (TOTP) или passkey, не SMS** (в UAE номер могут сменить/роуминг). Резервные коды — в менеджер паролей/Vault.
- Instagram: Accounts Center → Password and security → Two-factor authentication → Authentication app.
- Gmail: https://myaccount.google.com/security → 2-Step Verification + Passkeys.
- Телефон: один UAE-номер как recovery; не логиниться в IG с множества IP/устройств (VPN из разных стран — частый триггер проверок). API-токен таких проблем не создаёт — поэтому автоматизация через API не мешает безопасности аккаунта.

---

## 6. Другие соцсети (для combo-posting)

| Платформа | Официальный API для видео | Ключевые ограничения (проверено) | Источник |
|---|---|---|---|
| **Threads** | Threads API (Meta), видео-посты | 250 API-постов / 24ч, 1000 ответов / 24ч; тот же Meta App | https://developers.facebook.com/documentation/threads/overview |
| **YouTube Shorts** | YouTube Data API `videos.insert` | С 04.12.2025 upload стоит ~100 units (было ~1600) при дефолтной квоте 10 000/сутки. **Видео из непроверенных проектов (созданных после 28.07.2020) — только private**, пока проект не пройдёт аудит | https://developers.google.com/youtube/v3/revision_history, https://developers.google.com/youtube/v3/docs/videos/insert |
| **TikTok** | Content Posting API (Direct Post / Upload в черновики) | Неаудированные клиенты: только `SELF_ONLY` (приватно), аккаунт должен быть приватным, до 5 пользователей/24ч. Нужен аудит для публичных постов. Режим **Upload (в инбокс-черновик)** — практичный обход: Александр жмёт «опубликовать» в приложении | https://developers.tiktok.com/docs/en/content-sharing-guidelines, https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post |
| **Facebook Reels** | Pages API, Reels publishing | нужна Facebook Page | https://developers.facebook.com/docs/video-api/guides/reels-publishing |

> YouTube: вторичные источники (Postproxy и др.) пишут, что с 01.06.2026 загрузки вынесены в отдельный лимит (~100 вызовов в сутки); в официальной revision history это не подтвердил — проверить в Quotas консоли GCP при настройке.

Порядок подключения: **Instagram → Threads (тот же Meta App, почти бесплатно по усилиям) → YouTube Shorts (подать на аудит сразу, пока идёт — постить private/вручную) → TikTok (Upload-в-черновики, параллельно подать на аудит).**

---

## 7. Рекомендуемый стек combo-posting на нашем сервере

Сервер: Linux, Python, ffmpeg есть. Playwright/Chrome **не нужны** для публикации (официальные API). Playwright полезен только для QA (скриншоты лендинга) и одноразовой помощи в получении OAuth-токенов (и то — лучше руками Александра).

### 7.1 Архитектура

```
/opt/data/projects/combo-posting/
  combo_posting/
    queue.py          # SQLite: posts(id, file, caption, platforms, scheduled_at, status, ig_media_id, error)
    normalize.py      # ffprobe-проверка по спеке + ffmpeg faststart/перекодирование, авто-тишина если нет аудио
    hosting.py        # публичный URL: временная раздача (Caddy/nginx на сервере, подписанный URL c TTL)
                      #   или resumable upload в rupload.facebook.com — тогда хостинг не нужен
    captions.py       # шаблоны CTA + UTM/deeplink на продукт (dailyq/botify)
    platforms/
      instagram.py    # create container → poll status → media_publish → first comment
      threads.py
      youtube.py      # google-api-python-client, OAuth refresh token
      tiktok.py       # Upload-to-inbox
    tokens.py         # хранение токенов в Vault/.env, cron refresh IG-токена (<60 дней)
    cli.py            # `combo add file.mp4 --caption ... --at "2026-09-29 18:00" --to ig,threads`
                      # `combo run` (крон раз в 5 мин), `combo status`
  tests/              # мок-ответы Graph API
```

- Зависимости: `requests` (или `httpx`), `pydantic`, `python-dotenv`, SQLite из stdlib; `google-api-python-client` для YouTube. Никаких платных сервисов.
- Планировщик: systemd timer или cron `*/5 * * * * combo run`.
- Время постинга — по Дубаю (UTC+4); базово 1 рилс/день, 18:00–21:00 GST, дальше смотреть Insights (`/<media_id>/insights`).
- Идемпотентность: статус в SQLite до/после каждого шага (контейнер создан → опубликован), чтобы при падении не опубликовать дубль.
- Логи + уведомление в Telegram о результате (бот у нас уже есть в экосистеме).
- Guardrails: проверять `content_publishing_limit` перед публикацией; ретраи с backoff только для 5xx/`IN_PROGRESS`; на `ERROR` контейнера — не повторять вслепую, а писать ошибку.

### 7.2 MVP (1 вечер)

1. `normalize.py` + `instagram.py` + CLI `publish-now file.mp4 "caption"`.
2. Тест на `control_room_reel_v3.mp4` (уже соответствует спеке).
3. Затем очередь + cron + refresh токена.

---

## 8. Что сделать СЕГОДНЯ

**Александр (≈30–40 мин, с телефона/ноутбука):**
1. [ ] Создать бренд-Gmail, включить 2FA (аутентификатор/passkey), сохранить резервные коды.
2. [ ] Создать IG-аккаунт на этот Gmail (или решить, что используем существующий) → переключить в **Professional (Creator или Business)**.
3. [ ] Включить 2FA в Instagram через приложение-аутентификатор.
4. [ ] Заполнить профиль: аватар, имя, bio с CTA, **2 ссылки в bio**: DailyQ (`https://cr-web-production.up.railway.app/?utm_source=instagram&utm_medium=bio`) и Botify (TG-бот).
5. [ ] developers.facebook.com → создать App → продукт Instagram → «API setup with Instagram login» → добавить свой IG как Instagram Tester → принять приглашение в IG → Generate token.
6. [ ] Положить **токен + IG user ID + App ID/Secret** в Vault (не в чат, не пароль от IG).
7. [ ] Первый рилс опубликовать **вручную** из приложения (`control_room_reel_v3.mp4`) — «прогрев» свежего аккаунта и проверка, что всё отображается.

**Мы (агент, на сервере, без доступа к аккаунтам):**
1. [ ] Прогнать нормализацию: faststart для `nameradar_reel_sfx.mp4`, faststart + music bed для `batch_v*_*.mp4`, сложить в `promo/ready/`.
2. [ ] Написать для каждого рилса подпись с CTA + UTM (файл `promo/ready/<name>.caption.txt`).
3. [ ] Реализовать MVP `combo-posting` (раздел 7.2) с моками Graph API и тестами.
4. [ ] Сделать простой лендинг «все продукты» с UTM (статическая страница) — показать Александру перед деплоем.
5. [ ] Как только токен появится в Vault — тестовая публикация одного рилса через API, затем расписание 1/день.

**Не делаем без явного OK:** платные сервисы (Linktree Pro, ManyChat, Buffer платный, резидентные прокси), instagrapi на бренд-аккаунте, логин в аккаунты Александра.
