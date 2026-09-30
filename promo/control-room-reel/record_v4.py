"""V4 screencast: ~92s manifesto reel for Hermes Control Room.

Beat map (t = target seconds from record start):
  0-8    Control Room hero, agent map, node hover
  8-16   click agent nodes -> right panel opens
  16-26  Kanban board, column sweep + scroll
  26-40  Kanban card detail, filters, back
  40-54  Logs page, auto-refresh, level filter
  54-66  Sessions / agents page
  66-80  Control Room again, right panel tabs
  80-92  Kanban -> Control Room hero (result)

Strict w() sync so ffmpeg beat cuts line up. Pre-auth via storage_state.
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
    pg.set_default_timeout(4000)
    t0 = time.time()

    def w(t):
        d = t - (time.time() - t0)
        if d > 0:
            pg.wait_for_timeout(d * 1000)

    def go(url, settle=1600):
        for _ in range(3):
            try:
                pg.goto(url, wait_until='domcontentloaded', timeout=15000)
                break
            except Exception:
                pg.wait_for_timeout(900)
        pg.wait_for_timeout(settle)

    def sweep(pts, step_ms=260):
        for x, y in pts:
            pg.mouse.move(x, y, steps=10)
            pg.wait_for_timeout(step_ms)

    def click_text(txt, idx=0):
        try:
            loc = pg.get_by_text(txt, exact=True)
            loc.nth(idx).click(force=True, timeout=2500)
            return True
        except Exception as e:
            log(-1, f'  click {txt!r} skipped: {type(e).__name__}')
            return False

    def click_any(sel, idx=0):
        try:
            pg.locator(sel).nth(idx).click(force=True, timeout=2500)
            return True
        except Exception as e:
            log(-1, f'  click {sel} skipped: {type(e).__name__}')
            return False

    # --- 0-8: Control Room hero
    log(0, 'CONTROL ROOM hero')
    go(f'{BASE}/control-room', settle=2600)
    sweep([(700, 430), (800, 460), (900, 440), (760, 520)], 240)

    # --- 8-16: agent nodes
    w(8); log(8, 'click HERMES node')
    click_text('HERMES')
    pg.wait_for_timeout(700)
    w(11); log(11, 'click other node / right panel')
    click_text('NODE')
    pg.wait_for_timeout(600)
    sweep([(1050, 420), (1150, 470), (1000, 520)], 240)
    w(14); log(14, 'panel tabs sweep')
    sweep([(1100, 380), (1200, 380), (1100, 340)], 220)

    # --- 16-26: Kanban
    w(16); log(16, 'KANBAN board')
    go(f'{BASE}/kanban', settle=2800)
    sweep([(500, 400), (650, 450), (800, 430), (950, 470)], 240)
    w(21); log(21, 'kanban scroll')
    pg.mouse.wheel(0, 700); pg.wait_for_timeout(700)
    sweep([(700, 500), (850, 460)], 240)
    pg.mouse.wheel(0, 500); pg.wait_for_timeout(600)

    # --- 26-40: card detail + filters
    w(26); log(26, 'CLICK card -> detail')
    click_any('[class*=card], [class*=task], [class*=issue]', 1)
    pg.wait_for_timeout(1600)
    sweep([(700, 450), (800, 520)], 240)
    w(31); log(31, 'open second card')
    click_any('[class*=card], [class*=task], [class*=issue]', 3)
    pg.wait_for_timeout(1500)
    sweep([(750, 500), (900, 460)], 240)
    w(35); log(35, 'search / filter field')
    try:
        pg.locator('input[type=search], input[placeholder*=earch]').first.fill('reel')
        pg.wait_for_timeout(1400)
    except Exception:
        log(35, '  no search field')
    w(38); log(38, 'back to board wide')

    # --- 40-54: Logs
    w(40); log(40, 'LOGS page')
    go(f'{BASE}/logs', settle=2800)
    sweep([(700, 450), (850, 500), (750, 560)], 240)
    w(45); log(45, 'click WARNING level')
    click_text('WARNING')
    pg.wait_for_timeout(1500)
    sweep([(800, 470), (900, 520)], 240)
    w(49); log(49, 'LINES -> 200')
    click_text('200')
    pg.wait_for_timeout(1600)
    sweep([(700, 500), (850, 460)], 240)

    # --- 54-66: Sessions / agents
    w(54); log(54, 'SESSIONS page')
    go(f'{BASE}/sessions', settle=2800)
    sweep([(600, 430), (750, 480), (900, 440)], 240)
    w(58); log(58, 'open a session row')
    click_any('[class*=row], [class*=item], tr', 2)
    pg.wait_for_timeout(1600)
    sweep([(800, 500), (700, 560)], 240)
    w(62); log(62, 'back')

    # --- 66-80: Control Room + panel
    w(66); log(66, 'CONTROL ROOM again')
    go(f'{BASE}/control-room', settle=2600)
    sweep([(720, 450), (860, 480), (1000, 440)], 240)
    w(70); log(70, 'click agent node right')
    click_text('HERMES')
    pg.wait_for_timeout(900)
    sweep([(1100, 450), (1180, 400)], 240)
    w(74); log(74, 'FEED / CHAT tab')
    for t in ('FEED', 'CHAT'):
        if click_text(t):
            pg.wait_for_timeout(1100)
            break
    w(78); log(78, 'panel sweep')

    # --- 80-92: kanban -> CR hero
    w(80); log(80, 'KANBAN result')
    go(f'{BASE}/kanban', settle=2400)
    sweep([(700, 450), (850, 500)], 240)
    w(85); log(85, 'final CONTROL ROOM hero')
    go(f'{BASE}/control-room', settle=2600)
    pg.mouse.move(780, 470, steps=10)
    w(90); log(90, 'hold hero')
    pg.wait_for_timeout(2200)

    w(TOTAL)
    try:
        vid = pg.video.path()
    except Exception:
        vid = '?'
    ctx.close(); b.close()
    print('VIDEO:', vid, flush=True)
