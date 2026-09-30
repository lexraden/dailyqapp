#!/bin/bash
# v2: реальный скринкаст (raw/*.webm) -> 9:16 1080x1920 30fps, фокус-кроп следует за активной зоной,
# blur-фон из того же кадра, Ken Burns 1.0->1.06, подписи секций, voice.aac (loudnorm + fade out).
set -euo pipefail
D=/opt/data/projects/dailyqapp/promo/control-room-reel
cd "$D"
SRC=$(ls raw/*.webm | head -1)
OUT=$D/control_room_reel_v2.mp4
SS=1.75      # 0-1.75s исходника = логин/загрузка, Control Room появляется на 1.75s
DUR=60       # voice.aac = 60.04s -> ролик 60s (исходник 1.75..61.75)
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf

SRCDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
if awk "BEGIN{exit !($SRCDUR < 55)}"; then echo "recording incomplete ($SRCDUR s)"; exit 1; fi

# Фокус-окно 810x900 (полная высота 1440x900) -> x по времени ролика, плавные переходы 1s.
# 0-12.8 карта агентов (x=170) | 13.8-24.3 меню темы слева (x=0) | 25.3-31.8 тёмная карта (x=170)
# 32.8-40.3 правая панель агента (x=630) | 41.3-53.8 канбан (x=300) | 54.6-60 чат: сайдбар CHAT (x=0)
ramp() { # $1=t0 $2=t1 $3=from $4=to $5=else
  echo "if(lt(t,$1),$3,if(lt(t,$2),$3+($4-$3)*(t-$1)/($2-$1),$5))"; }
X=$(ramp 53.8 54.6 300 0 0)
X=$(ramp 40.3 41.3 630 300 "$X")
X=$(ramp 31.8 32.8 170 630 "$X")
X=$(ramp 24.3 25.3 0 170 "$X")
X=$(ramp 12.8 13.8 170 0 "$X")
X=${X//,/\\,}

cap() { # $1=from $2=to $3=text
  echo "drawtext=fontfile=$FONT:text='$3':fontsize=40:fontcolor=white@0.92:x=(w-tw)/2:y=h-230:box=1:boxcolor=black@0.45:boxborderw=18:enable='between(t,$1,$2)':alpha='min(1,min((t-$1)/0.3,($2-t)/0.3))'"; }
CAPS="$(cap 0 4 'Control Room'),$(cap 4 12.8 'Agent map'),$(cap 12.8 24.3 'Theme switcher'),$(cap 24.3 31.8 'Theme\: Midnight'),$(cap 31.8 40.3 'Agent panel'),$(cap 40.3 54.3 'Kanban'),$(cap 54.3 60 'Chat')"

ffmpeg -v error -stats -y -ss $SS -t $DUR -i "$SRC" -i voice.aac -filter_complex "
 [0:v]setpts=PTS-STARTPTS,fps=30,split=2[a][b];
 [a]scale=3072:1920,crop=1080:1920,gblur=sigma=32,eq=brightness=-0.22:saturation=1.2[bg];
 [b]crop=810:900:x='$X':y=0,scale=1080:1200:flags=lanczos[fg];
 [bg][fg]overlay=0:360,drawbox=x=0:y=358:w=1080:h=2:color=white@0.25:t=fill,drawbox=x=0:y=1560:w=1080:h=2:color=white@0.25:t=fill[comp];
 [comp]scale=w='trunc(1080*(1+0.06*t/$DUR)/2)*2':h='trunc(1920*(1+0.06*t/$DUR)/2)*2':eval=frame:flags=bicubic,crop=1080:1920,setsar=1,$CAPS,format=yuv420p[v];
 [1:a]atrim=0:$DUR,apad=whole_dur=$DUR,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,afade=t=out:st=$(awk "BEGIN{print $DUR-1.5}"):d=1.5[au]" \
 -map "[v]" -map "[au]" -t $DUR -r 30 -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p \
 -c:a aac -b:a 128k -ar 48000 -movflags +faststart "$OUT"

# QA кадры
mkdir -p qa_frames
for t in 2 10 18 28 36 48 57; do
  ffmpeg -v error -y -ss $t -i "$OUT" -frames:v 1 -q:v 3 "qa_frames/t$(printf %02d $t).jpg"
done
ffprobe -v error -show_entries format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate,sample_rate,channels,bit_rate,duration -of default=nw=1 "$OUT"
