"""Реальный скринкаст Control Room: 60с, таймлайн по сториборду, Playwright video."""
import json, os, time
from playwright.sync_api import sync_playwright

D='/opt/data/projects/dailyqapp/promo/control-room-reel'
PW='/opt/data/projects/dailyqapp/promo/control-room-reel/venv'
import subprocess, sys
# playwright из venv
sys.path.insert(0,f'{PW}/lib/python3.11/site-packages')
from playwright.sync_api import sync_playwright as spw

BASE='http://127.0.0.1:8080'
USER='lexraden'; PASS=json.load(open(f'{D}/.pw.json'))['p']

def log(t,msg): print(f"[{t:5.1f}] {msg}",flush=True)

with spw() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':1440,'height':900},device_scale_factor=1.5,
                      http_credentials={'username':USER,'password':PASS},
                      record_video_dir=f'{D}/raw', record_video_size={'width':1440,'height':900})
    pg=ctx.new_page(); pg.goto(f'{BASE}/login')
    pg.fill('input[name=username]',USER); pg.fill('input[name=password]',PASS)
    pg.click('form button[type=submit]'); pg.wait_for_load_state()
    pg.wait_for_url('**/sessions**',timeout=15000)
    def safe_goto(url):
        for a in range(3):
            try:
                pg.goto(url, wait_until='domcontentloaded', timeout=20000); return
            except Exception as e:
                print(f'  goto retry {a}: {e}',flush=True); pg.wait_for_timeout(1500)
    t0=time.time()
    def w(t):  # ждать абсолютный момент таймлайна
        d=t-(time.time()-t0)
        if d>0: pg.wait_for_timeout(d*1000)
        return time.time()-t0
    def themebtn(): return pg.locator('button[aria-label="Switch theme"]')

    # 0-2s: заходим на Control Room (светлая Nous Blue? текущая = Midnight после прошлой съёмки)
    log(0,'go control-room')
    safe_goto(f'{BASE}/control-room'); pg.wait_for_load_state(); pg.wait_for_timeout(2500)
    # сброс в светлую (Nous Blue) для холодного старта
    log(2,'theme->Nous Blue')
    themebtn().click(); pg.wait_for_timeout(800)
    try: pg.locator('[role=option],li,button').filter(has_text='Nous Blue').first.click(force=True,timeout=3000)
    except Exception as e: log(3,f'theme skip {type(e).__name__}')
    pg.wait_for_timeout(1500)

    t=6
    w(t); log(t,'hover agent nodes: sweep across map')
    for xy in [(700,450),(760,430),(820,480),(900,460),(980,500),(860,540)]:
        pg.mouse.move(xy[0],xy[1],steps=12); pg.wait_for_timeout(450)
    t=10.5
    w(t); log(t,'click agent node TOM')
    try: pg.get_by_text('TOM',exact=True).first.click(timeout=3000)
    except Exception as e: log(t,f'node click skipped {e}')

    t=14; w(t); log(t,'open theme switcher')
    themebtn().click(); pg.wait_for_timeout(1200)
    t=17; w(t); log(t,'hover options: scroll list')
    pg.mouse.move(700,300,steps=10); pg.wait_for_timeout(700)
    pg.mouse.move(700,450,steps=10); pg.wait_for_timeout(700)
    t=20.5; w(t); log(t,'hover Midnight (not click)')
    mo=pg.locator('[role=option],li,button').filter(has_text='Midnight').first
    mo.hover(); pg.wait_for_timeout(1800)
    t=24.5; w(t); log(t,'CLICK Midnight -> dark transition')
    mo.click(force=True); pg.wait_for_timeout(2200)
    t=27.5; w(t); log(t,'settle on dark map, sweep nodes')
    for xy in [(720,470),(800,450),(880,500),(760,530)]:
        pg.mouse.move(xy[0],xy[1],steps=10); pg.wait_for_timeout(600)
    t=33.5; w(t); log(t,'click agent HERMES node')
    try: pg.get_by_text('HERMES',exact=True).first.click(timeout=3000)
    except Exception as e: log(t,f'skip {e}')
    t=36.5; w(t); log(t,'sweep right panel tabs: FEED')
    tabs=pg.locator('button,a').filter(has_text='FEED')
    if tabs.count(): tabs.first.click(force=True)
    pg.wait_for_timeout(1500)
    t=40; w(t); log(t,'tab CHAT')
    ch=pg.locator('button,a').filter(has_text='CHAT')
    if ch.count(): ch.first.click(force=True)
    pg.wait_for_timeout(1200)
    t=43; w(t); log(t,'go kanban (dark)')
    safe_goto(f'{BASE}/kanban'); pg.wait_for_load_state(); pg.wait_for_timeout(2000)
    t=45.5; w(t); log(t,'sweep cards')
    for xy in [(600,420),(700,470),(540,520),(680,560)]:
        pg.mouse.move(xy[0],xy[1],steps=10); pg.wait_for_timeout(600)
    t=49; w(t); log(t,'click first card')
    try: pg.locator('[class*=card],[class*=task],[class*=item]').first.click(timeout=2500)
    except Exception as e: log(t,f'skip {e}')
    pg.wait_for_timeout(1200)
    t=52; w(t); log(t,'sweep board right')
    for xy in [(800,500),(900,540),(760,480)]:
        pg.mouse.move(xy[0],xy[1],steps=8); pg.wait_for_timeout(500)
    t=55; w(t); log(t,'go chat page (dark), type into composer')
    safe_goto(f'{BASE}/chat'); pg.wait_for_load_state(); pg.wait_for_timeout(1500)
    ta=pg.locator('textarea,[contenteditable=true],input[type=text]').last
    try:
        ta.click()
        for c in 'show me the fleet':
            ta.type(c,delay=90)
    except Exception as e: log(56,f'type skip {e}')
    pg.wait_for_timeout(2500)
    t=60; w(t)
    log(60,'stop')
    video=pg.video.path() if hasattr(pg.video,'path') else pg.video.path
    ctx.close(); b.close()
    print('VIDEO:',video,flush=True)