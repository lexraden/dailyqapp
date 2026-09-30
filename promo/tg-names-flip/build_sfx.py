#!/usr/bin/env python3
"""Сборка аудио-дорожки NameRadar reel поверх nameradar_reel.mp4.

Только SFX-микс (тики счётчика, whoosh на склейках, pop на появлении строк,
ding на финале). Без drawtext-оверлея: он налезал на таблицу сделок.
"""
import subprocess
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
SFX = D / "sfx"
SRC = D / "nameradar_reel.mp4"
MIX = SFX / "mix.wav"

# (секунда, звук) — таймлайн под 8-секундный ролик
A = [(0.5 + i * 0.5, "tick") for i in range(15)]
A += [(0.1, "whoosh"), (2.0, "whoosh"), (4.0, "whoosh"), (6.0, "whoosh"),
      (7.4, "ding"), (1.2, "pop"), (3.2, "pop"), (5.2, "pop")]


def synth_sfx():
    SFX.mkdir(exist_ok=True)
    run = lambda out, args: subprocess.run(
        ["ffmpeg", "-v", "error", "-y"] + args + [str(SFX / out)], check=True)
    run("tick.wav", ["-f", "lavfi", "-i", "sine=frequency=2200:duration=0.03",
                     "-af", "afade=t=out:st=0.01:d=0.02,volume=0.5"])
    run("whoosh.wav", ["-f", "lavfi", "-i", "anoisesrc=color=pink:duration=0.45",
                       "-af", "lowpass=f=900,afade=t=in:st=0:d=0.15,"
                             "afade=t=out:st=0.2:d=0.25,volume=0.9"])
    run("ding.wav", ["-f", "lavfi", "-i", "sine=frequency=1568:duration=0.5",
                     "-f", "lavfi", "-i", "sine=frequency=2093:duration=0.5",
                     "-filter_complex",
                     "amix,afade=t=out:st=0.05:d=0.45,volume=0.6"])
    run("pop.wav", ["-f", "lavfi", "-i", "sine=frequency=440:duration=0.09",
                    "-af", "asetrate=44100*1.9,aresample=44100,"
                          "afade=t=out:st=0.03:d=0.06,volume=0.45"])


def build_mix(dur=8.2):
    inputs, fc = [], []
    for i, (t, k) in enumerate(A):
        inputs += ["-i", str(SFX / f"{k}.wav")]
        ms = int(t * 1000)
        fc.append(f"[{i}:a]adelay={ms}|{ms},volume=0.8[a{i}]")
    labels = "".join(f"[a{i}]" for i in range(len(A)))
    fc.append(f"{labels}amix=inputs={len(A)}:normalize=0,apad=whole_dur={dur}[aout]")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
         "-i", f"anullsrc=r=44100:cl=stereo:d={dur}"] + inputs +
        ["-filter_complex", ";".join(fc), "-map", "[aout]", "-c:a", "pcm_s16le", str(MIX)],
        check=True)


def mux(out: Path):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-i", str(MIX),
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
         "-b:a", "160k", "-shortest", str(out)], check=True)
    d = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(out)],
        capture_output=True, text=True, check=True).stdout.strip()
    print(f"{out.name}: {d}s -> {out}")


def main():
    if not SRC.exists():
        sys.exit(f"Нет {SRC} — сначала ./venv/bin/python render.py")
    synth_sfx()
    build_mix()
    mux(D / "nameradar_reel_sfx.mp4")
    mux(D / "nameradar_reel_hisaudio.mp4")


if __name__ == "__main__":
    main()