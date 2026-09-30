#!/bin/bash
# VO v4: local piper (ru_RU-dmitri-medium). Edge TTS currently returns empty audio.
# Usage: bash vo_v4_piper.sh [length_scale]  (1.0 = normal, >1 = slower)
set -euo pipefail
D=/opt/data/projects/dailyqapp/promo/control-room-reel
cd "$D"
PIPER=/opt/data/piper/piper/piper
MODEL=/opt/data/piper/voices/ru_RU-dmitri-medium.onnx
LS=${1:-1.0}
tr '\n' ' ' < vo_text_v4.txt > vo_chunk.txt
$PIPER --model "$MODEL" --length_scale "$LS" --output_file vo_v4_raw.wav < vo_chunk.txt 2>&1 | tail -2
ffmpeg -v error -y -i vo_v4_raw.wav -af "highpass=f=90,dynaudnorm=f=200:g=5" -ar 48000 -ac 2 voiceover_v4.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 voiceover_v4.wav
