# HeyGen avatar reel — план (реф: AIS Live DdpDsUyAHzY)

## Формат рефа (разобран)
9:16 композит: светлая инфографика сверху (логотип, крупная цифра-хук «~$420K/mo», карточка «<10 employees»), снизу окно с говорящим аватаром (talking head, скруглённые углы), субтитр-строка речи между блоками, дисклеймер внизу.
Скрипт рефа: хук-цифра → «how a team that small can operate at that scale» → AI OS → «every person has their own AI OS» → перечисление domains → blueprint → CTA «click below».

## Ограничения HeyGen (проверено 27.09)
- Регистрация с сервера: «suspicious activity» (датацентровый IP), Google-SSO скрыт → юзер регистрируется с телефона.
- Free: 3 видео/мес, 720p, вотермарка. API pay-as-you-go от $5: Avatar III ~$1/мин, Avatar IV Photo ~$2.3/мин.
- Токен API в чат не присылать — хранится в vault/на устройстве юзера.

## Скрипт для аватара (EN, ~40-45с, под бизнес Александра)
"My AI company runs about [$X] per month — with fewer than five employees.
People always ask how such a small team moves that fast.
The answer is the AI operating system I built on Hermes.
Every agent I have — coder, backend, QA, content, traffic — is live on one control map.
I click an agent, and I see exactly what it's doing right now.
Tasks move through the pipeline on their own: idea, build, QA, deploy.
I talk to my agents like a team — and they answer in real time.
No managers. No calls. No overhead.
If you want the blueprint — comment HERMES below."

## Композит (делает Jarvis после получения аватар-видео)
1. Верх: брендинг «ALEX RED · AI OS» + хук-цифра (реальные цифры юзера или DEMO-маркировка).
2. Низ: talking head от HeyGen (скруглённая рамка).
3. Субтитры речи (whisper-таймкоды), музыка bed, CTA-строка.
4. QA через vision, отправка.

## Статус
- [x] Реф скачан/разобран (/opt/data/tmp-work/heygen-ref/)
- [ ] Юзер: регистрация с телефона → генерация видео в Studio → скинуть файл в TG
- [ ] Композит
