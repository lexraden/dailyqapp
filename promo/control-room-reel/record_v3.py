"""V3 screencast: dense 50s timeline, no idle, no login screen (pre-auth via cookies).
Actions every 2-4s: theme flip, agent click, kanban card open, chat typing. Strict w() sync, short timeouts."""
import json, os, time, sys
D='/opt/data/projects/dailyqapp/promo/control-room-reel'
sys.path.insert(0,f'{D}/venv/lib/python3.11/site-packages')
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8080'
PASS=json.load(open(f'{D}/.pw.json'))['p']
STATE=f'{D}/.state.json'

def log(t,msg): print(f"[{t:5.1f}] {msg}",flush=True)

with sync_playwright() as p:
    b=p.chromium.launch()
    # Pre-auth context (no video): login once, save storage_state
    ctx0=b.new_context(viewport={'width':1440,'height':900},device_scale_factor=1.5,
                       http_credentials={'username':'lexraden','password':PASS})
    pg0=ctx0.new_page()
    pg0.goto(f'{BASE}/login'); pg0.fill('input[name=username]','lexraden'); pg0.fill('input[name=password]',PASS)
    pg0.click('form button[type=submit]'); pg0.wait_for_load_state()
    try: pg0.wait_for_url('**/sessions**',timeout=8000)
    except Exception: pass
    ctx0.storage_state(path=STATE); ctx0.close()

    ctx=b.new_context(viewport={'width':1440,'height':900},device_scale_factor=1.5,
                      http_credentials={'username':'lexraden','password':PASS},
                      storage_state=STATE,
                      record_video_dir=f'{D}/raw3', record_video_size={'width':1440,'height':900})
    pg=ctx.new_page()
    t0=time.time()
    def w(t):
        d=t-(time.time()-t0)
        if d>0: pg.wait_for_timeout(d*1000)
    def go(url):
        for _ in range(2):
            try: pg.goto(url,wait_until='domcontentloaded',timeout=15000); return
            except Exception: pg.wait_for_timeout(800)

    # 0s: сразу Control Room — уже залогинены, форма не покажется
    log(0,'control-room direct')
    go(f'{BASE}/control-room')
    try: pg.wait_for_load_state('networkidle',timeout=6000)
    except Exception: pass
    pg.wait_for_timeout(1200)

    w(3); log(3,'theme switcher OPEN')
    try: pg.locator('button[aria-label="Switch theme"]').click(force=True,timeout=2500)
    except Exception: pass
    w(5); log(5,'pick EMBER (hover)')
    try:
        mo=pg.locator('[role=option],li,button').filter(has_text='EMBER').first
        mo.hover(timeout=2000)
    except Exception: pass
    w(7); log(7,'CLICK EMBER -> dark flip')
    try: mo.click(force=True,timeout=2000)
    except Exception: pass
    pg.wait_for_timeout(600)

    w(9); log(9,'agent map sweep FAST')
    for xy in [(760,440),(840,470),(920,500),(1000,470)]:
        pg.mouse.move(xy[0],xy[1],steps=8); pg.wait_for_timeout(320)

    w(12); log(12,'CLICK agent TOM node')
    try: pg.get_by_text('TOM',exact=True).first.click(timeout=2500)
    except Exception as e: log(12,f'tom skip {type(e).__name__}')
    pg.wait_for_timeout(400)

    w(15); log(15,'CLICK HERMES node (center)')
    try: pg.get_by_text('HERMES',exact=True).first.click(timeout=2500)
    except Exception as e: log(15,f'hermes skip {type(e).__name__}')
    pg.wait_for_timeout(400)

    w(18); log(18,'FEED tab')
    try:
        tb=pg.locator('button,a').filter(has_text='FEED').first
        tb.click(force=True,timeout=2000)
    except Exception: pass

    w(21); log(21,'CHAT tab on agent panel')
    try:
        cb=pg.locator('button,a').filter(has_text='CHAT').first
        cb.click(force=True,timeout=2000)
    except Exception: pass

    w(24); log(24,'kanban direct')
    go(f'{BASE}/kanban'); pg.wait_for_timeout(1500)

    w(27); log(27,'cards sweep')
    for xy in [(620,420),(720,470),(560,520),(700,560)]:
        pg.mouse.move(xy[0],xy[1],steps=8); pg.wait_for_timeout(300)

    w(30); log(30,'CLICK first card -> detail')
    try: pg.locator('[class*=card],[class*=task],[class*=item]').first.click(force=True,timeout=2500)
    except Exception as e: log(30,f'card skip {type(e).__name__}')
    pg.wait_for_timeout(900)

    w(34); log(34,'kanban scroll right')
    pg.mouse.wheel(0,600); pg.wait_for_timeout(500)
    for xy in [(850,480),(950,520)]:
        pg.mouse.move(xy[0],xy[1],steps=8); pg.wait_for_timeout(300)

    w(38); log(38,'back to control-room for live chat')
    go(f'{BASE}/control-room'); pg.wait_for_timeout(1500)
    w(40); log(40,'type into @hermes composer')
    try:
        ta=pg.locator('textarea,[contenteditable=true]').last
        ta.click(timeout=2500)
        pg.keyboard.type('status update: all agents online',delay=55)
        pg.wait_for_timeout(800)
        pg.keyboard.press('Enter')
    except Exception: pass

    w(45); log(45,'back to map hero')
    go(f'{BASE}/control-room'); pg.wait_for_timeout(1500)
    pg.mouse.move(760,470,steps=8)

    w(50); log(50,'stop')
    try: vid=pg.video.path()
    except Exception: vid='?'
    ctx.close(); b.close()
    print('VIDEO:',vid,flush=True)
