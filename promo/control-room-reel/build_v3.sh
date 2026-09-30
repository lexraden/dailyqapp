#!/bin/bash
# v3 final: видео-пасс (фокус-кроп+CAPS) -> аудио-микс (voice 1.0 + bed loop 0.16) -> mux. 50s.
set -euo pipefail
D=/opt/data/projects/dailyqapp/promo/control-room-reel
cd "$D"
SRC=$(ls raw3/*.webm | head -1)
DUR=50
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
X2="if(lt(t,23),204,if(lt(t,25),204+(t-23)*322,if(lt(t,37),849,if(lt(t,39),849+(t-39)*-255,if(lt(t,44),339,if(lt(t,46),339+(t-44)*-67,204))))))"
X2=${X2//,/\\,}
cap() { echo "drawtext=fontfile=$FONT:text='$3':fontsize=42:fontcolor=white@0.95:x=(w-tw)/2:y=h-210:box=1:boxcolor=black@0.5:boxborderw=16:enable='between(t,$1,$2)':alpha='min(1,min((t-$1)/0.25,($2-t)/0.25))'"; }
CAPS="$(cap 0 5 'AI command center'),$(cap 5 11 'Theme\: EMBER flip'),$(cap 11 17 'Live agent map'),$(cap 17 24 'Inside\: logs + chat'),$(cap 24 31 'Kanban\: 125 tasks'),$(cap 31 38 'Agent at work'),$(cap 38 45 'Talk to your agent'),$(cap 45 50 'Comment HERMES')"

# PASS 1: видео
ffmpeg -v error -stats -y -ss 0.8 -t $DUR -i "$SRC" -filter_complex "
[0:v]setpts=PTS-STARTPTS,fps=30,split=2[a][b];
[a]scale=3072:1920,crop=1080:1920,gblur=sigma=32,eq=brightness=-0.22:saturation=1.15[bg];
[b]scale=2304:1440:flags=lanczos,crop=1080:1440:x='$X2':y=0[fg];
[bg][fg]overlay=0:60,drawbox=x=0:y=58:w=1080:h=2:color=white@0.22:t=fill,drawbox=x=0:y=1498:w=1080:h=2:color=white@0.22:t=fill[comp];
[comp]scale=w='trunc(1080*(1+0.05*t/50)/2)*2':h='trunc(1920*(1+0.05*t/50)/2)*2':eval=frame:flags=bicubic,crop=1080:1920,setsar=1,$CAPS,format=yuv420p[v]" \
-map "[v]" -r 30 -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p v3_nosound.mp4

# PASS 2: аудио (voice + bed loop)
ffmpeg -v error -y -i voiceover_v3_50s.wav -stream_loop -1 -i music_bed.m4a -filter_complex "
[1:a]volume=0.16,aresample=48000[bed];
[0:a]aresample=48000[vo];
[vo][bed]amix=inputs=2:duration=first:dropout_transition=0,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=48.8:d=1.2[au]" \
-map "[au]" -t $DUR -c:a aac -b:a 128k -ar 48000 v3_audio.m4a

# PASS 3: mux
ffmpeg -v error -y -i v3_nosound.mp4 -i v3_audio.m4a -map 0:v -map 1:a -c:v copy -c:a copy -movflags +faststart control_room_reel_v3.mp4

mkdir -p qa3
for t in 2 9 15 27 40 48; do ffmpeg -v error -y -ss $t -i control_room_reel_v3.mp4 -frames:v 1 -q:v 3 "qa3/v3_t$t.jpg"; done
ffprobe -v error -show_entries format=duration,size:stream=codec_type,width,height,r_frame_rate -of default=nw=1 control_room_reel_v3.mp4
echo DONE_V3
