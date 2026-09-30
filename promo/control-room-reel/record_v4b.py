"""V4 screencast take 2: ~92s manifesto reel for Hermes Control Room.

Every beat verifies the live URL after navigation and logs it, so build_v4 can
sync cuts to real content instead of guessed timings. Shorter settles, one
action per beat, no dead stretches.

Beat map (target seconds):
  0-9    Control Room hero (agent map)
  9-16   Control Room, agent node click -> right panel
  16-27  Kanban board sweep + scroll
  27-40  Kanban card detail
  40-53  Logs page + level filter
  53-64  Sessions page
  64-78  Control Room + right panel
  78-92  Kanban -> Control Room hero (result)
"""
import json, os, sys, time
D = '/opt/data/projects/dailyqapp/promo/control-room-reel'
sys.path.insert(0, f'{D}/venv/lib/python3.13/site-packages')
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8080'
PASS = json.load(open(f'{D}/.pw.json'))['p']
STATE = f'{D}/.state_v4.json'
OUT = f'{D}/raw4'
os.makedirs(OUT, exist_ok=True)
TOTAL = 92.0
BEATS = []


def log(t, msg):
    print(f"[{t:5.1f}] {msg}", flush=True)


with sync_playwright() as p:
    b = p.chromium.launch(args=['--force-device-scale-factor=1.5'])
    ctx0 = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1.5,
                         http_credentials={'username': 'lexraden', 'password': PASS})
    pg0 = ctx0.new_page()
    pg0.goto(f'{BASE}/login'); pg0.fill('input[name=username]', 'lexraden')
    pg0.fill('input[name=password]', PASS)
    pg0.click('form button[type=submit]'); pg0.wait_for_load_state()
    try:
        pg0.wait_for_url('**/sessions**', timeout=8000)
    except Exception:
        pass
    ctx0.storage_state(path=STATE); ctx0.close()
    log(0, 'auth ok')

    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1.5,
                        http_credentials={'username': 'lexraden', 'password': PASS},
                        storage_state=STATE,
                        record_video_dir=OUT, record_video_size={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    pg.set_default_timeout(3500)
    t0 = time.time()

    def w(t):
        d = t - (time.time() - t0)
        if d > 0:
            pg.wait_for_timeout(d * 1000)

    def go(path, settle=1500):
        for _ in range(3):
            try:
                pg.goto(BASE + path, wait_until='domcontentloaded', timeout=12000)
                break
            except Exception:
                pg.wait_for_timeout(700)
        pg.wait_for_timeout(settle)

    def mark(t, label):
        BEATS.append({'t': round(t, 1), 'label': label, 'url': pg.url.replace(BASE, '')})
        log(t, f'BEAT {label} @ {pg.url.replace(BASE, "")}')

    def sweep(pts, ms=240):
        for x, y in pts:
            pg.mouse.move(x, y, steps=10)
            pg.wait_for_timeout(ms)

    def click_text(txt, idx=0):
        try:
            pg.get_by_text(txt, exact=True).nth(idx).click(force=True, timeout=2200)
            return True
        except Exception as e:
            log(-1, f'  click {txt!r} skipped: {type(e).__name__}')
            return False

    def click_any(sel, idx=0):
        try:
            pg.locator(sel).nth(idx).click(force=True, timeout=2200)
            return True
        except Exception as e:
            log(-1, f'  click {sel} skipped: {type(e).__name__}')
            return False

    # 0-9 CONTROL ROOM hero
    log(0, 'CONTROL ROOM hero')
    go('/control-room', settle=2400)
    mark(0.0, 'CR hero')
    sweep([(700, 430), (810, 460), (900, 440), (760, 520)], 200)

    # 9-16 agent node -> right panel
    w(9); log(9, 'click HERMES node')
    click_text('HERMES')
    pg.wait_for_timeout(800)
    mark(9.0, 'CR agent panel')
    sweep([(1020, 420), (1120, 470), (1000, 520)], 200)

    # 16-27 KANBAN
    w(16); log(16, 'KANBAN')
    go('/kanban', settle=2000)
    mark(16.0, 'KANBAN board')
    sweep([(520, 400), (680, 450), (840, 430), (960, 470)], 200)
    w(21); log(21, 'kanban scroll')
    pg.mouse.wheel(0, 600); pg.wait_for_timeout(600)
    sweep([(700, 480), (850, 450)], 200)
    w(24); log(24, 'scroll again')
    pg.mouse.wheel(0, 450); pg.wait_for_timeout(500)

    # 27-40 KANBAN card detail
    w(27); log(27, 'CLICK card -> detail')
    click_any('[class*=card], [class*=task], [class*=issue]', 1)
    pg.wait_for_timeout(1400)
    mark(27.0, 'KANBAN detail')
    sweep([(760, 430), (860, 500)], 200)
    w(32); log(32, 'open another card')
    click_any('[class*=card], [class*=task], [class*=issue]', 3)
    pg.wait_for_timeout(1300)
    sweep([(780, 480), (900, 440)], 200)
    w(36); log(36, 'detail scroll')
    pg.mouse.wheel(0, 500); pg.wait_for_timeout(700)
    sweep([(800, 500)], 200)

    # 40-53 LOGS
    w(40); log(40, 'LOGS')
    go('/logs', settle=2000)
    mark(40.0, 'LOGS')
    sweep([(700, 450), (850, 500), (750, 560)], 200)
    w(45); log(45, 'level filter')
    if click_text('WARNING'):
        pg.wait_for_timeout(1200)
    mark(45.0, 'LOGS filtered')
    sweep([(820, 470), (900, 520)], 200)
    w(49); log(49, 'back to ALL level')
    if click_text('ALL'):
        pg.wait_for_timeout(1000)
    sweep([(760, 490)], 200)

    # 53-64 SESSIONS
    w(53); log(53, 'SESSIONS')
    go('/sessions', settle=2000)
    mark(53.0, 'SESSIONS')
    sweep([(620, 430), (760, 480), (900, 440)], 200)
    w(58); log(58, 'open session row')
    click_any('[class*=row], [class*=item], tr', 2)
    pg.wait_for_timeout(1400)
    mark(58.0, 'SESSIONS detail')
    sweep([(800, 500)], 200)
    w(62); log(62, 'sweep')

    # 64-78 CONTROL ROOM + panel
    w(64); log(64, 'CONTROL ROOM')
    go('/control-room', settle=2000)
    mark(64.0, 'CR again')
    sweep([(720, 450), (860, 480), (1000, 440)], 200)
    w(69); log(69, 'agent node right')
    click_text('HERMES')
    pg.wait_for_timeout(900)
    sweep([(1100, 450), (1180, 400)], 200)
    w(73); log(73, 'panel tabs')
    for t in ('FEED', 'CHAT', 'LIVE'):
        if click_text(t):
            pg.wait_for_timeout(900)
            break
    w(77); log(77, 'panel sweep')

    # 78-92 KANBAN -> CR hero
    w(78); log(78, 'KANBAN result')
    go('/kanban', settle=1800)
    mark(78.0, 'KANBAN result')
    sweep([(720, 450), (860, 500)], 200)
    w(84); log(84, 'final CR hero')
    go('/control-room', settle=2200)
    mark(84.0, 'CR hero final')
    pg.mouse.move(780, 470, steps=10)
    w(90); log(90, 'hold')
    pg.wait_for_timeout(2200)

    w(TOTAL)
    try:
        vid = pg.video.path()
    except Exception:
        vid = '?'
    ctx.close(); b.close()
    json.dump(BEATS, open(f'{D}/beats_v4.json', 'w'), ensure_ascii=False, indent=1)
    print('VIDEO:', vid, flush=True)
