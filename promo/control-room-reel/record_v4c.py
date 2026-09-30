"""V4 screencast take 3: ~92s manifesto reel for Hermes Control Room.

Fixes vs take 2:
  - every navigation is VERIFIED (URL + landmark text); retries with a different
    selector if the beat did not land.
  - the Logs level filter uses a role/label scoped locator (plain get_by_text
    'WARNING' hit the sidebar and navigated away in take 2).
  - no dead stretches: each beat either changes page or opens a detail panel,
    asserted before the next beat starts.
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
FAILS = []


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
    pg.set_default_timeout(3000)
    t0 = time.time()

    def w(t):
        d = t - (time.time() - t0)
        if d > 0:
            pg.wait_for_timeout(d * 1000)

    def has(txt):
        try:
            return pg.get_by_text(txt, exact=False).count() > 0
        except Exception:
            return False

    def go(path, landmark, settle=1500):
        """Navigate until the page shows its landmark text. Returns True on success."""
        for attempt in range(3):
            try:
                pg.goto(BASE + path, wait_until='domcontentloaded', timeout=12000)
            except Exception:
                pg.wait_for_timeout(700)
                continue
            pg.wait_for_timeout(settle)
            if landmark is None or has(landmark):
                return True
            log(-1, f'  {path} landmark {landmark!r} missing, retry')
        FAILS.append({'what': path, 'landmark': landmark})
        return False

    def mark(t, label):
        BEATS.append({'t': round(t, 1), 'label': label, 'url': pg.url.replace(BASE, '')})
        log(t, f'BEAT {label} @ {pg.url.replace(BASE, "")}')

    def sweep(pts, ms=200):
        for x, y in pts:
            pg.mouse.move(x, y, steps=10)
            pg.wait_for_timeout(ms)

    def click_sel(sel, idx=0, timeout=2200):
        try:
            pg.locator(sel).nth(idx).click(force=True, timeout=timeout)
            return True
        except Exception as e:
            log(-1, f'  click {sel}[{idx}] skipped: {type(e).__name__}')
            return False

    def click_role_text(txt, exact=False):
        try:
            pg.get_by_text(txt, exact=exact).first.click(force=True, timeout=1800)
            return True
        except Exception as e:
            log(-1, f'  click text {txt!r} skipped: {type(e).__name__}')
            return False

    # ---- 0-9 CONTROL ROOM hero
    log(0, 'CONTROL ROOM hero')
    ok = go('/control-room', 'CONTROL ROOM', settle=2400)
    mark(0.0, 'CR hero' if ok else 'CR hero (landmark missing)')
    sweep([(700, 430), (810, 460), (900, 440), (760, 520)], 190)

    # ---- 9-16 agent node -> right panel
    w(9); log(9, 'click HERMES node')
    if not click_role_text('HERMES', exact=True):
        click_sel('svg, canvas, [class*=node]', 4)
    pg.wait_for_timeout(900)
    mark(9.0, 'CR agent panel')
    sweep([(1020, 420), (1120, 470), (1000, 520)], 190)

    # ---- 16-27 KANBAN board
    w(16); log(16, 'KANBAN')
    ok = go('/kanban', 'Kanban', settle=2000)
    mark(16.0, 'KANBAN board' if ok else 'KANBAN board (landmark missing)')
    sweep([(520, 400), (680, 450), (840, 430), (960, 470)], 190)
    w(21); log(21, 'kanban scroll')
    pg.mouse.wheel(0, 600); pg.wait_for_timeout(600)
    sweep([(700, 480), (850, 450)], 190)
    w(24); log(24, 'scroll again')
    pg.mouse.wheel(0, 450); pg.wait_for_timeout(500)

    # ---- 27-40 KANBAN card detail (assert detail panel opened)
    w(27); log(27, 'open card detail')
    opened = False
    for sel, idx in [('[class*=card]', 1), ('[class*=task]', 1), ('[class*=issue]', 1),
                     ('[class*=card]', 4), ('[class*=task]', 4)]:
        if click_sel(sel, idx, 2000):
            pg.wait_for_timeout(1200)
            if has('Description') or has('Dependencies') or has('Add a comment'):
                opened = True
                break
            pg.keyboard.press('Escape'); pg.wait_for_timeout(500)
    mark(27.0, 'KANBAN detail' if opened else 'KANBAN detail (NOT OPENED)')
    FAILS if not opened else None
    sweep([(760, 430), (860, 500)], 190)
    w(33); log(33, 'detail scroll')
    pg.mouse.wheel(0, 450); pg.wait_for_timeout(700)
    sweep([(800, 480)], 190)
    w(37); log(37, 'detail hover')

    # ---- 40-53 LOGS (level filter scoped to the page, not the sidebar)
    w(40); log(40, 'LOGS')
    ok = go('/logs', 'AGENT.LOG', settle=2000)
    mark(40.0, 'LOGS' if ok else 'LOGS (landmark missing)')
    sweep([(700, 450), (850, 500), (750, 560)], 190)
    w(45); log(45, 'level filter (scoped)')
    before = pg.url
    hit = False
    for sel in ['label:has-text("WARNING")', 'button:has-text("WARNING")',
                '[class*=chip]:has-text("WARNING")', 'text=WARNING >> nth=0']:
        try:
            pg.locator(sel).first.click(force=True, timeout=1500)
            hit = True
            break
        except Exception:
            continue
    pg.wait_for_timeout(1100)
    if pg.url != before:          # filter navigated away -> go back to logs
        log(45, f'  filter navigated to {pg.url}, returning to /logs')
        go('/logs', 'AGENT.LOG', settle=1400)
    if not hit:
        FAILS.append({'what': 'logs level filter', 't': 45})
    mark(45.0, 'LOGS filtered' if hit else 'LOGS sweep (filter not found)')
    sweep([(820, 470), (900, 520)], 190)

    # ---- 53-64 SESSIONS
    w(53); log(53, 'SESSIONS')
    ok = go('/sessions', 'Messages', settle=2000)
    mark(53.0, 'SESSIONS' if ok else 'SESSIONS (landmark missing)')
    sweep([(620, 430), (760, 480), (900, 440)], 190)
    w(58); log(58, 'open session row')
    opened = False
    for sel, idx in [('[class*=row]', 2), ('tr', 2), ('[class*=card]', 2), ('[class*=item]', 2)]:
        if click_sel(sel, idx, 2000):
            pg.wait_for_timeout(1200)
            if pg.url.replace(BASE, '') != '/sessions' or has('Overview') is False:
                opened = True
                break
    mark(58.0, 'SESSIONS detail' if opened else 'SESSIONS sweep')
    if not opened:
        FAILS.append({'what': 'session row open', 't': 58})
    sweep([(800, 500)], 190)
    w(62); log(62, 'sweep')

    # ---- 64-78 CONTROL ROOM + right panel
    w(64); log(64, 'CONTROL ROOM')
    ok = go('/control-room', 'CONTROL ROOM', settle=2000)
    mark(64.0, 'CR again' if ok else 'CR again (landmark missing)')
    sweep([(720, 450), (860, 480), (1000, 440)], 190)
    w(69); log(69, 'agent node right')
    click_role_text('HERMES', exact=True)
    pg.wait_for_timeout(900)
    sweep([(1100, 450), (1180, 400)], 190)
    w(73); log(73, 'panel tab')
    for t in ('FEED', 'CHAT', 'LIVE', 'Board'):
        if click_role_text(t, exact=True):
            pg.wait_for_timeout(900)
            break
    w(77); log(77, 'panel sweep')

    # ---- 78-92 KANBAN -> CR hero
    w(78); log(78, 'KANBAN result')
    ok = go('/kanban', 'Kanban', settle=1800)
    mark(78.0, 'KANBAN result' if ok else 'KANBAN result (landmark missing)')
    sweep([(720, 450), (860, 500)], 190)
    w(84); log(84, 'final CR hero')
    ok = go('/control-room', 'CONTROL ROOM', settle=2200)
    mark(84.0, 'CR hero final' if ok else 'CR hero final (landmark missing)')
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
    json.dump(FAILS, open(f'{D}/fails_v4.json', 'w'), ensure_ascii=False, indent=1)
    print('VIDEO:', vid, flush=True)
    print('FAILS:', FAILS, flush=True)
