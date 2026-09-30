"""Probe: what pages/labels exist in the Hermes dashboard for the v4 reel."""
import json, sys
D='/opt/data/projects/dailyqapp/promo/control-room-reel'
sys.path.insert(0,f'{D}/venv/lib/python3.11/site-packages')
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8080'
PASS=json.load(open(f'{D}/.pw.json'))['p']
STATE=f'{D}/.state.json'

with sync_playwright() as p:
    b=p.chromium.launch()
    ctx0=b.new_context(viewport={'width':1440,'height':900},device_scale_factor=1.5,
                       http_credentials={'username':'lexraden','password':PASS})
    pg0=ctx0.new_page()
    pg0.goto(f'{BASE}/login'); pg0.fill('input[name=username]','lexraden')
    pg0.fill('input[name=password]',PASS)
    pg0.click('form button[type=submit]'); pg0.wait_for_load_state()
    try: pg0.wait_for_url('**/sessions**',timeout=8000)
    except Exception: pass
    print('AFTER LOGIN URL:',pg0.url)
    ctx0.storage_state(path=STATE); ctx0.close()

    ctx=b.new_context(viewport={'width':1440,'height':900},device_scale_factor=1.5,
                      http_credentials={'username':'lexraden','password':PASS},
                      storage_state=STATE)
    pg=ctx.new_page()
    for path in ['/control-room','/kanban','/agents','/chat','/sessions','/logs','/cron','/projects','/']:
        try:
            pg.goto(BASE+path,wait_until='domcontentloaded',timeout=15000)
            pg.wait_for_timeout(2500)
            txt=pg.inner_text('body')[:900].replace('\n',' | ')
            print(f'--- {path} -> {pg.url}')
            print('   ',txt[:700])
            pg.screenshot(path=f'{D}/qa3/probe{path.replace("/","_") or "_root"}.png')
        except Exception as e:
            print(f'--- {path} ERR {type(e).__name__} {e}')
    ctx.close(); b.close()
