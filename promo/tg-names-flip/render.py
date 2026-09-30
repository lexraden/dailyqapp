#!/usr/bin/env python3
"""Рендер dashboard.html -> PNG-кадры 1080x1920 -> mp4 (без звука).

Кадры детерминированные: для каждого кадра вызывается window.__setTime(t),
который ставит все CSS-анимации на паузу в момент t и обновляет счётчики/zoom.

Примеры:
    ./venv/bin/python render.py                  # 8 с, 30 fps, с плашкой DEMO
    ./venv/bin/python render.py --no-demo        # без плашки (только с реальными данными!)
    ./venv/bin/python render.py --fps 10 --out preview.mp4   # быстрый черновик
    ./venv/bin/python render.py --frames-only    # только PNG, без ffmpeg
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920


def ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        sys.exit(
            "Playwright не найден. Установи в venv:\n"
            "  python3 -m venv venv && ./venv/bin/pip install playwright "
            "&& ./venv/bin/playwright install chromium\n"
            "и запускай через ./venv/bin/python render.py"
        )


def render_frames(html: Path, frames_dir: Path, duration: float, fps: int, demo: bool) -> int:
    from playwright.sync_api import sync_playwright

    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("frame_*.png"):
        old.unlink()

    total = int(round(duration * fps))
    url = f"{html.as_uri()}?dur={duration}&demo={'1' if demo else '0'}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page.goto(url)
        page.wait_for_load_state("load")
        page.evaluate("document.fonts.ready")
        for i in range(total):
            t = i / fps
            page.evaluate(f"window.__setTime({t})")
            page.screenshot(path=str(frames_dir / f"frame_{i:04d}.png"))
            if i % fps == 0:
                print(f"  кадр {i + 1}/{total} (t={t:.1f}s)", flush=True)
        browser.close()
    return total


def encode(frames_dir: Path, out: Path, fps: int):
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg не найден — кадры лежат в " + str(frames_dir))
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(fps), "-i", str(frames_dir / "frame_%04d.png"),
        "-an",                                  # без аудиодорожки — как в референсе
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(fps),
        "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--html", default=str(HERE / "dashboard.html"))
    ap.add_argument("--duration", type=float, default=8.0)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--frames-dir", default=str(HERE / "frames"))
    ap.add_argument("--out", default=str(HERE / "nameradar_reel.mp4"))
    ap.add_argument("--no-demo", action="store_true", help="скрыть плашку DEMO · SIMULATED DATA")
    ap.add_argument("--frames-only", action="store_true")
    args = ap.parse_args()

    ensure_playwright()
    html, frames_dir, out = Path(args.html).resolve(), Path(args.frames_dir), Path(args.out)

    print(f"Рендер {args.duration}s @ {args.fps}fps, {W}x{H} -> {frames_dir}")
    n = render_frames(html, frames_dir, args.duration, args.fps, demo=not args.no_demo)
    print(f"Готово кадров: {n}")
    if args.frames_only:
        return
    encode(frames_dir, out, args.fps)
    print(f"Видео: {out}")


if __name__ == "__main__":
    main()
