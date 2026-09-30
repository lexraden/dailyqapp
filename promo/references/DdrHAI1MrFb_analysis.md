# DdrHAI1MrFb — разбор референса

URL: https://www.instagram.com/reel/DdrHAI1MrFb/
Автор: rick.theengineer

### 1) О чём

- Это учебный ролик **«System Design 101»** для начинающих backend-разработчиков и подготовки к system design interview.
- На примере простого social app — лента, лайки, фотографии и сообщения — автор показывает, как система развивается от **одного сервера и одной базы**.
- Каждый компонент появляется только из-за конкретной проблемы: нехватка CPU, перегрузка базы, долгие запросы, большой объём файлов, медленные загрузки, отказы и невозможность диагностики.
- Последовательность: один сервер → масштабирование и load balancer → cache → read replicas → sharding → object storage → CDN → queue и workers → redundancy → observability.
- Главный вывод: **не запоминать инструменты, а спрашивать: “What problem forced us to add this?”** Метод: `Start simple → Find the bottleneck → Smallest fix → Repeat`.

### 2) Визуальный стиль

- **Кадр и композиция:** вертикальный формат 9:16, 720×1280. Светло-серый фон с технической сеткой. Слева почти всегда находится рисованный персонаж с голубыми волосами и чёрным худи; справа или по центру — схемы, карточки и blueprint. Сверху закреплена навигационная шапка, снизу — плашка с текущей фразой речи.
- **Текст и плашки:** практически весь текст на экране английский, в верхнем регистре. Есть вкладки `LB`, `CACHE`, `REPLICAS`, `SHARDS`, `STORAGE`, `CDN`, `QUEUE`, `REDUNDANCY`, `OBSERVABILITY`, счётчик пользователей, версии схемы `V0–V9`, карточки `PROBLEM`, `GOAL`, `FIX`, `RULE`.
- **Цвет:** белые карточки с мягкими тенями; тёмно-серый текст; фиолетовый и синий для активных элементов и потоков; красный/розовый для проблем; зелёный для успешных состояний; жёлтый для выделения слов в субтитрах.
- **Шрифт:** жирный геометрический sans-serif для заголовков, компактный технический шрифт для подписей, интерфейсных меток и чисел. Крупные числа и названия компонентов служат визуальными акцентами.
- **Монтаж:** последовательная смена инфографических слайдов; элементы появляются, подсвечиваются и переключаются. Стрелки, синие точки запросов, цветные потоки и графики показывают движение данных. Реальной съёмки нет — только motion graphics, схемы, макеты телефона и диаграммы.
- **Субтитры:** внизу находится белая скруглённая плашка с коротким фрагментом английской речи. Текущее слово или часть фразы подсвечиваются жёлтым; это работает как karaoke-сабтитры, а не как обычные длинные реплики.

### 3) Хук

- В первом кадре сразу показан уже собранный полный blueprint системы, включая серверы, базу, cache, queue, CDN и observability.
- Затем термины намеренно превращаются в визуальный хаос: `LOAD BALANCER`, `CACHE`, `KAFKA`, `KUBERNETES`, `MICROSERVICES`, `SHARDING` и десятки других названий.
- Этот контраст цепляет новичка: сначала кажется, что system design — это набор сложных buzzwords, а затем ролик обещает свести его к простой последовательности «проблема → минимальное исправление».

### 4) CTA и финал

- Финальный кадр снова показывает полную архитектуру `V9` и крупный заголовок **SYSTEM DESIGN 101**.
- Итоговая плашка: **“That’s system design 101.”**
- Отдельного CTA на последнем кадре нет. В описании ролика есть призывы:
  - **“Save this for your next system design interview”**
  - **“Which of the 9 steps did you learn the hard way? Tell me in the comments”**

### 5) Формат и длительность

- Вертикальный образовательный Reel в формате **9:16**.
- Длительность: **155,5 секунды**, около **2:36**.
- В подборке **52 опорных кадра**, примерно каждые 3 секунды.
- Англоязычная озвучка сопровождается короткими субтитрами и последовательной анимацией схем.

## Кадры 1–52 по порядку

Повторяющиеся сетка, шапка, персонаж слева и нижняя плашка показаны в каждом кадре; ниже указаны основные изменения и текст плашки.

### Вступление

- **1.** Открывающий обзор: blueprint `V9` уже показывает целевую архитектуру social app — users, CDN, load balancer, серверы, storage, cache, queue, workers, шарды, реплики и observability. Ниже крупно: `SYSTEM DESIGN 101`. Плашка: **«System design 101.»**
- **2.** Появляется блок `PEOPLE HEAR...` и четыре парящие карточки: `LOAD BALANCER`, `CACHE`, `QUEUE`, `DATABASE REPLICA`. Плашка: **«queue, database replica,»**
- **3.** Словарь buzzwords уплотняется: `KAFKA`, `KUBERNETES`, `MICROSERVICES`, `DOCKER`, `PROMETHEUS`, `S3`, `NGINX`, `GRAFANA`, `DYNAMODB`, `CONSISTENT HASHING`, `SHARDING`, `MONGODB`, `RABBITMQ`, `LAMBDA`. Плашка: **«a giant collection of»**
- **4.** Появляется mental model: правило `It’s really just three things` и три карточки — product requirement, reliable operation, рост числа пользователей. В третьей карточке виден счётчик `1 USERS`. Плашка: **«really just this.»**
- **5.** Первая карточка mental model подсвечена фиолетовым: `START WITH A PRODUCT REQUIREMENT`. Плашка: **«to make it work»**
- **6.** Слева появляется цель `Build it from scratch`, справа — пустая страница `BLUEPRINT · SOCIAL APP V0` с плашкой `BLANK PAGE`. Плашка: **«Let's build the mental»**

### Один сервер

- **7.** Раздел `01 ONE SERVER`. Слева цель `A simple social app`, в центре макет телефона с пустым экраном `circle`, справа список запросов: `GET /home`, `GET /feed`, `POST /likes`, `POST /photos`, `POST /messages`. Плашка: **«A user opens it,»**
- **8.** На телефоне появляется лента с фотографией моря, профилем `maya.k` и прогрессом `Uploading photo`; четыре запроса подсвечены синим. Плашка: **«photo, sends a message.»**
- **9.** Blueprint `V1`: пользователи связаны с одной машиной, внутри которой находятся `BACKEND — your code` и `DATABASE — your data`. Плашка: **«One backend, one database,»**
- **10.** На схеме появляется `1,000 USERS`; все компоненты по-прежнему имеют метку `×1`. Плашка: **«For a thousand users,»**
- **11.** Счётчик вырастает до `250K users`. Карточка проблемы: `One server can’t keep up`; блок сервера красный, появляется `CPU 100%`. Плашка: **«server can’t handle»**

### Масштабирование и load balancer

- **12.** Раздел `02 SCALE OUT`. Проблема снимается двумя серверами рядом, оба подключены к одной базе `primary · writes`. Плашка: **«Instead of one back-end»**
- **13.** Серверов становится четыре, но перед ними по-прежнему нет единой точки входа; красная плашка спрашивает `WHICH SERVER?`. Плашка: **«system.»**
- **14.** Добавляется `LOAD BALANCER — NGINX · ELB` с меткой `ROUND ROBIN`; запросы распределяются по четырём серверам. Плашка: **«distributes requests»**

### База, cache и реплики

- **15.** Раздел `03 THE DATABASE`, счётчик `1M users`. Красная плашка: `Every server hits one database`; трафик с серверов сходится в одну базу. Плашка: **«hit the same database»**
- **16.** На схеме появляется предупреждение `SAME READS, AGAIN`; повторяющиеся чтения продолжают давить на database. Плашка: **«So you reduce unnecessary»**
- **17.** Активирована вкладка `CACHE`. Пример профиля `maya.k` запрашивается `10,000×`; сравниваются `CACHE — Redis · in memory — 9,999 HITS` и `DATABASE — query on disk — 1 QUERY`. Плашка: **«gets requested 10,000»**
- **18.** Появляется сетка из 100 квадратов, один запрос к базе и множество cache hits; вверху `10,000 REQUESTS`, внизу `9,999 HITS` и `1 QUERY`. Плашка: **«instead of querying the»**
- **19.** При `5M users` появляется проблема `Reads keep growing`; рядом с базой показан cache `Redis · memory` и стрелка `READS ↑`. Плашка: **«you add read replicas.»**
- **20.** Правило `Writes: primary. Reads: replicas.`; в схеме появляются primary database и две реплики, отмеченные для чтения. Плашка: **«writes, replicas handle»**
- **21.** При `20M users` база достигает предела: красная плашка `One cluster can’t hold it all`, метка `DISK 97% · 4 TB`. Плашка: **«enough.»**

### Файлы, шардирование и CDN

- **22.** Раздел `04 FILES`. Показан разрез таблицы `USERS — 20M ROWS` и деление по диапазону: `SHARD 1 — users A–M` с именами Ana, Ben, Chloe, Dev, Maya и `SHARD 2 — users N–Z`. Плашка: **«database, others go»**
- **23.** Красная проблема: `Files bloat the database`. Сверхху маленький `USER ROW — 1 KB`, ниже большая `RELATIONAL DATABASE — 12 GB`. Плашка: **«Now files. You don't»**
- **24.** В схему добавляются `PHOTO — 4 MB` и `VIDEO — 480 MB`; база вырастает до `3.8 TB`, появляется красная плашка `BLOBS DON'T BELONG HERE`. Плашка: **«relational database.»**
- **25.** Добавляется `STORAGE — S3 · R2`; видны метки `AMAZON S3` и `CLOUDFLARE R2`, а также выноска `DB keeps: s3://avatars/maya.jpg`. Плашка: **«R2.»**
- **26.** Активирована вкладка `CDN`. Карта показывает edge-узлы по миру, `ORIGIN — VIRGINIA` и `TOKYO`; сравниваются 180 ms до origin и 12 ms до ближайшего edge. Плашка: **«closer to users around»**

### Медленные jobs, queue и workers

- **27.** Раздел `05 SLOW WORK`, счётчик `50M users`. На экране телефон с загрузкой `trip.mp4 — 480 MB`, а справа — thumbnails, notifications, analytics и transcoding с суммарным ожиданием `14.2 S`. Плашка: **«Should the user wait»**
- **28.** Красная плашка `The user sits and waits`; прогресс на телефоне достигает `13.2 s`, thumbnails и notifications подсвечены как задерживающие операции. Плашка: **«notifications, analytics,»**
- **29.** Добавляется `QUEUE — jobs wait here`: операции отделяются от пользовательского запроса и ожидают фоновой обработки. Плашка: **«a queue,»**
- **30.** Появляется `WORKERS — slow jobs`; queue передаёт им задачи `THUMBNAILS · TRANSCODE`, а пользователь получает быстрый ответ `200 OK · 120 MS`. Плашка: **«workers process the slow»**

### Отказоустойчивость

- **31.** Раздел `06 FAILURE`. Красная плашка спрашивает: `What if something crashes?`; полная архитектура показана без нового компонента. Плашка: **«when one service crashes?»**
- **32.** Карта `FOUR REGIONS, ONE APP` показывает `us-west-2`, `eu-central-1`, `ap-northeast-1` и красный `X` у `us-east-1`. Status card: database `DOWN`, servers `UNREACHABLE`, region `OFFLINE`. Плашка: **«one region disappears.»**
- **33.** Раздел redundancy показывает `MULTIPLE SERVERS`, `REPLICATED DATA`, `HEALTH CHECKS`, `RETRIES` и `FAILOVER`. Плашка: **«Multiple servers,»**
- **34.** Крупный слоган `EXPECT PARTS TO BREAK.` и три карточки серверов; правило `Assume parts will break`. Плашка: **«The system should expect»**
- **35.** Цель сформулирована как локализация отказа: не `NOTHING EVER FAILS`, а `FAILURE STAYS CONTAINED`. Ниже 12 зелёных отсеков приложения, все с меткой `12 / 12 UP`. Плашка: **«ever fails. It’s failure»**

### Observability

- **36.** Раздел `07 OBSERVABILITY`; к уже собранной архитектуре добавляется наблюдаемость. Плашка: **«Now add observability.»**
- **37.** Три панели: `LOGS` с записями запросов и ошибкой `POST /photos 500 · s3 timeout 3000 ms`, `METRICS` с графиком p99 latency и пустая `TRACES`. Плашка: **«Metrics tell you how»**
- **38.** Заполняется traces: показаны пути `load balancer`, `api server`, `cache · Redis`, `database`, `storage · S3`, `queue` с временами 4, 150, 2, 38, 88 и 3 ms; график показывает пик `p99 840 ms`. Плашка: **«one request moved across»**
- **39.** Красная проблема `Blind debugging`; логи, метрики и traces превращаются в три больших знака вопроса. Плашка: **«distributed system is a»**

### Ошибка overengineering и метод

- **40.** Раздел `08 THE MISTAKE`, красная плашка `More isn’t better`; сверху минимальная строка `COMPONENTS` с числом `6` и тремя иконками. Плашка: **«They think system design»**
- **41.** Показаны четыре типовых избыточных решения: `MICROSERVICES`, `KAFKA`, `KUBERNETES`, `10 DATABASES`. Их описания: `a service per verb`, `event streaming`, `container orchestration`, `one for every feature`. Плашка: **«Microservices, Kafka,»**
- **42.** Те же четыре карточки становятся цветными и хорошо заметными. Плашка: **«That’s not good system»**
- **43.** Плашка `Every part adds complexity`; список из observability, redundancy, queue, CDN, storage, shards, replicas, cache и load balancer получает `+1` у каждого элемента, рядом — шкала `COMPLEXITY ×9`. Плашка: **«complexity.»**
- **44.** Три риска: `CACHE CAN GO STALE`, `QUEUE CAN DELIVER TWICE`, `REPLICAS CAN LAG`. Показаны несовпадение cache и database, две копии welcome email и отставание primary на два лайка. Плашка: **«deliver twice, replicas»**
- **45.** Два следующих риска: `SHARDING — QUERIES GET HARDER` и `MICROSERVICES — NETWORK FAILURES`; показаны merge двух шардов и `504 TIMEOUT`. Плашка: **«harder. Microservices»**
- **46.** Раздел `09 THE METHOD`. Крупный тезис: `ONLY ADD COMPLEXITY WHEN IT SOLVES A REAL BOTTLENECK.` Ниже красный отказ `because it’s popular` и зелёный вариант `because something broke`. Плашка: **«complexity when it solves»**
- **47.** Схема `THE CORE OF SYSTEM DESIGN` показывает цикл из четырёх шагов: `START SIMPLE`, `FIND THE BOTTLENECK`, `SMALLEST FIX`, `REPEAT`. Плашка: **«system design.»**
- **48.** Первые три шага подсвечены фиолетовым, `REPEAT` пока приглушён; внизу появляется строка `LAPS IN THIS VIDEO` с номерами 1–9. Плашка: **«smallest component that»**
- **49.** Правило `Start simple. Fix the bottleneck. Repeat.`; список компонентов временно приглушён. Плашка: **«So when you hear»**
- **50.** Список снова становится цветным под заголовком `WHEN YOU HEAR...`: `LOAD BALANCER`, `CACHE`, `QUEUE`, `CDN`, `REPLICA`, `SHARD`. Плашка: **«shard,»**
- **51.** Главный вопрос: `WHAT PROBLEM FORCED US TO ADD THIS?` Слева шесть полей `WHY WAS IT ADDED?`, справа те же шесть компонентов. Плашка: **«Ask one question: what»**
- **52.** Финальный возврат к полной архитектуре `V9` и крупному标题 `SYSTEM DESIGN 101`. Плашка: **«That’s system design 101.»**
