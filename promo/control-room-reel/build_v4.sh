#!/bin/bash
# v4 build — 90s manifesto reel, 1080x1920, RU VO + RU captions.
#
# Source: raw4/*.webm (Playwright screencast 1440x900 @1.5 DPR, 93.1s).
# The raw take has a black page-transition frame at ~84.0s, so the timeline is
# assembled from explicit segments instead of one linear -ss/-t pass.
#
# Pass A: concat trimmed segments -> 2304x1440 working copy
# Pass B: vertical compose (blurred cover bg + sharp focus window) + captions
# Pass C: audio mix (VO + music bed, loudnorm)
# Pass D: mux
set -euo pipefail
D=/opt/data/projects/dailyqapp/promo/control-room-reel
cd "$D"
SRC=$(ls -t raw4/*.webm | head -1)
VO=voiceover_v4.wav
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VO" | cut -d. -f1)
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
[ -f "$FONT" ] || FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
mkdir -p seg4

# name:start:end  (seconds in source)
SEGS="
cr_hero:0.6:16
kanban:16.2:27
kanban_detail:27.2:40
logs:40.2:53
sessions:53.2:64
cr_panel:64.2:78
kanban_result:78.2:83.8
cr_final:84.8:92
"

# ---- PASS A: segments -> identical-format files, then concat
FILES=""
for s in $SEGS; do
  name=${s%%:*}; rest=${s#*:}; st=${rest%%:*}; en=${rest#*:}
  dur=$(awk -v a="$st" -v b="$en" 'BEGIN{printf "%.2f", b-a}')
  ffmpeg -v error -y -ss "$st" -t "$dur" -i "$SRC" \
    -vf "setpts=PTS-STARTPTS,fps=30,scale=2304:1440:flags=lanczos,format=yuv420p" \
    -c:v libx264 -preset veryfast -crf 16 "seg4/$name.mp4"
  FILES="$FILES $name.mp4"
  echo "seg $name ${st}-${en} (${dur}s)"
done
printf "file '%s'\n" $FILES > seg4/list.txt
ffmpeg -v error -y -f concat -safe 0 -i seg4/list.txt -c copy seg4/work.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 seg4/work.mp4

# ---- PASS B: vertical compose
# focus X per segment (window is 1080 wide inside the 2304x1440 working copy)
XF="if(lt(t,15.4),470,if(lt(t,26.2),640,if(lt(t,39.2),760,if(lt(t,51.8),500,if(lt(t,62.8),620,if(lt(t,76.6),700,if(lt(t,82.0),640,470)))))))"
XF=${XF//,/\\,}

cap() { echo "drawtext=fontfile=$FONT:text='$3':fontsize=48:fontcolor=white@0.97:x=(w-tw)/2:y=h-236:box=1:boxcolor=black@0.55:boxborderw=18:enable='between(t,$1,$2)':alpha='min(1,min((t-$1)/0.3,($2-t)/0.3))'"; }
C1=$(cap 0 6   'ОДИН ЭКРАН. ЦЕЛАЯ КОМАНДА')
C2=$(cap 6 15  'CONTROL ROOM')
C3=$(cap 15 26 'ЗАДАЧА')
C4=$(cap 26 39 'АГЕНТЫ ЗА РАБОТОЙ')
C5=$(cap 39 52 'ЛОГИ')
C6=$(cap 52 63 'КОНТРОЛЬ')
C7=$(cap 63 77 'ПАРАЛЛЕЛЬНО')
C8=$(cap 77 82 'РЕЗУЛЬТАТ')
C9=$(cap 82 90 'Ссылка на демо — в профиле')
CAPS="$C1,$C2,$C3,$C4,$C5,$C6,$C7,$C8,$C9"

ffmpeg -v error -stats -y -i seg4/work.mp4 -filter_complex "
[0:v]split=2[a][b];
[a]scale=3072:1920,crop=1080:1920,gblur=sigma=34,eq=brightness=-0.22:saturation=1.12[bg];
[b]crop=1080:1440:x='$XF':y=0[fg];
[bg][fg]overlay=0:60,drawbox=x=0:y=58:w=1080:h=2:color=white@0.20:t=fill,drawbox=x=0:y=1498:w=1080:h=2:color=white@0.20:t=fill[comp];
[comp]scale=w='trunc(1080*(1+0.05*t/$DUR)/2)*2':h='trunc(1920*(1+0.05*t/$DUR)/2)*2':eval=frame:flags=bicubic,crop=1080:1920,setsar=1,$CAPS,format=yuv420p[v]" \
-map "[v]" -r 30 -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p v4_nosound.mp4

# ---- PASS C: audio
# aformat=stereo on every leg: the music bed is mono, and amix otherwise
# collapses the whole mix to mono. alimiter AFTER loudnorm is required —
# loudnorm's -2 dBTP target is not honoured post-encode and AAC overshoots.
FADEST=$(awk -v d="$DUR" 'BEGIN{printf "%.2f", d-1.2}')
ffmpeg -v error -y -i "$VO" -stream_loop -1 -i music_bed.m4a -filter_complex "
[1:a]aformat=channel_layouts=stereo,volume=0.14,aresample=48000[bed];
[0:a]aformat=channel_layouts=stereo,aresample=48000[vo];
[vo][bed]amix=inputs=2:duration=first:dropout_transition=0,loudnorm=I=-14:TP=-2:LRA=11,afade=t=out:st=$FADEST:d=1.2,alimiter=limit=0.7:attack=5:release=50:level=false,aformat=channel_layouts=stereo[au]" \
-map "[au]" -t "$DUR" -c:a aac -b:a 128k -ar 48000 -ac 2 v4_audio.m4a

# ---- PASS D: mux
ffmpeg -v error -y -i v4_nosound.mp4 -i v4_audio.m4a -map 0:v -map 1:a -c copy -movflags +faststart control_room_reel_v4.mp4

rm -rf qa4; mkdir -p qa4
for t in 3 10 18 25 31 37 45 50 57 62 69 74 80 84 88; do ffmpeg -v error -y -ss $t -i control_room_reel_v4.mp4 -frames:v 1 -q:v 3 "qa4/v4_t$t.jpg"; done
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate -of default=nw=1 control_room_reel_v4.mp4
echo "DONE_V4 dur=$DUR src=$SRC"
