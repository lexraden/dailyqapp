import cairosvg, math, os, subprocess, shutil

BASE = "/opt/data/projects/dailyqapp/promo/emoji"
OUT = f"{BASE}/anim"
os.makedirs(OUT, exist_ok=True)
TMP = f"{OUT}/frames"
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)

BG = '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1f2937"/><stop offset="1" stop-color="#111827"/></linearGradient></defs><rect width="100" height="100" rx="24" fill="url(#bg)"/>'
FIRE = '<defs><linearGradient id="fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbbf24"/><stop offset="1" stop-color="#f97316"/></linearGradient></defs>'

def render(name, svg_fn, n=30):
    for i in range(n):
        t = i/n
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{svg_fn(t)}</svg>'
        p = f"{TMP}/{name}_{i:02d}.png"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=p, output_width=100, output_height=100)

# fire flicker: scale + inner flame wiggle
def fire(t):
    s = 1 + 0.05*math.sin(2*math.pi*t*2)
    wob = 4*math.sin(2*math.pi*t)
    return f'{FIRE}{BG}<g transform="translate(50 50) scale({s:.3f}) translate(-50 -50)"><path d="M50 16c8 12 22 18 22 36a22 22 0 0 1-44 0c0-12 6-18 12-26 2 6 4 9 10 12 2-8 {wob:.1f}-14 0-22z" fill="url(#fl)"/><path d="M50 60a10 10 0 0 0 10 10 12 12 0 0 1-20-2c0-5 4-7 10-8z" fill="#111827" opacity=".85"/></g>'

# level up bounce arrow
def level(t):
    dy = -8*abs(math.sin(2*math.pi*t))
    spark = 0.5+0.5*math.sin(2*math.pi*t)
    return f'{BG}<g transform="translate(0 {dy:.2f})"><path d="M50 78V34" stroke="#fbbf24" stroke-width="9" stroke-linecap="round"/><path d="M30 52l20-24 20 24" fill="none" stroke="#fbbf24" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></g><path d="M24 24h8M68 20h8" stroke="#fde68a" stroke-width="4" stroke-linecap="round" opacity="{spark:.2f}"/><path d="M50 12v6" stroke="#fde68a" stroke-width="4" stroke-linecap="round" opacity="{1-spark:.2f}"/>'

# lightning flash
def bolt(t):
    op = 0.55+0.45*abs(math.sin(math.pi*t*3))**3
    return f'{BG}<path d="M56 14L30 54h16l-6 32 30-44H52l6-28z" fill="#fbbf24" opacity="{op:.2f}" stroke="#fde68a" stroke-width="2" stroke-linejoin="round"/>'

# star twinkle rotate
def star(t):
    rot = 10*math.sin(2*math.pi*t)
    s = 1+0.06*math.sin(4*math.pi*t)
    return f'{BG}<g transform="translate(50 50) rotate({rot:.2f}) scale({s:.3f}) translate(-50 -50)"><path d="M50 16l9 20 22 2-17 15 5 22-19-11-19 11 5-22-17-15 22-2z" fill="url(#st)"/></g>' if 'st' in BG else f'{BG}<g transform="translate(50 50) rotate({rot:.2f}) scale({s:.3f}) translate(-50 -50)"><path d="M50 16l9 20 22 2-17 15 5 22-19-11-19 11 5-22-17-15 22-2z" fill="#fbbf24"/></g>'

# logo pulse check
def logo(t):
    s = 1+0.07*math.sin(2*math.pi*t)
    return f'{BG}<g transform="translate(50 50) scale({s:.3f}) translate(-50 -50)"><path d="M27 52l15 15 32-34" fill="none" stroke="#fbbf24" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></g>'

ST='{"st":[{"offset":"0","stop-color":"#fde68a"},{"offset":"1","stop-color":"#f59e0b"}]}'
for name, fn in [("fire",fire),("level_up",level),("lightning",bolt),("star",star),("logo",logo)]:
    render(name, fn)
    # encode webm vp9 yuva420p, 1.2s loop
    subprocess.run(f"ffmpeg -y -framerate 25 -i {TMP}/{name}_%02d.png -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 100k -loop 0 -an {OUT}/anim_{name}_100x100.webm 2>/dev/null", shell=True, check=True)
    print(name, os.path.getsize(f"{OUT}/anim_{name}_100x100.webp" if False else f"{OUT}/anim_{name}_100x100.webm"), "bytes")
