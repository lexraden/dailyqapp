#!/bin/bash
# v3: композит (bg+fg) -> 2x канва -> мягкий зум 1.0-1.05 -> 9:16 без обрезки
set -e
D=/opt/data/projects/dailyqapp/promo/control-room-reel
OUT=$D/control_room_reel.mp4
cd $D

shot() { # $1=input $2=dur $3=out $4=zf $5=zt
  local d=$2
  local zoom="(1+$4+($5-$4)*on/$d)"
  ffmpeg -v error -y -loop 1 -i "$1" -filter_complex "
    [0:v]scale=2160:1350,split=2[bg][fg];
    [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.18[bgb];
    [fg]scale=1080:-1[fgs];
    [bgb][fgs]overlay=(W-w)/2:(H-h)/2,format=yuv420p,scale=2160:3840[zp];
    [zp]zoompan=z='$zoom':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$((25*d)):s=1080x1920:fps=25[v]" \
    -map "[v]" -t "$d" -r 25 "$3"
}

shot s1_cr_light.png        6  seg01.mp4 0 0.03
shot s1_cr_light.png        4  seg02.mp4 0.03 0.06
shot s3_theme_menu_light.png 5 seg03.mp4 0 0.04
shot s3_theme_menu_light.png 5 seg04.mp4 0.03 0.06
shot s4_cr_dark.png         6  seg05.mp4 0 0.04
shot s4_cr_dark.png        11  seg06.mp4 0.03 0.06
shot s5_kanban_dark.png    11  seg07.mp4 0 0.05
shot s6_chat_dark.png       6  seg08.mp4 0 0.03
shot s6_chat_dark.png       6  seg09.mp4 0.03 0.06

printf "file '%s/seg0%s.mp4'\n" "$D" 1 > list.txt
for i in 2 3 4 5 6 7 8 9; do printf "file '%s/seg0%s.mp4'\n" "$D" $i >> list.txt; done
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy nosound.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 nosound.mp4)
ffmpeg -v error -y -i nosound.mp4 -i voice.aac -filter_complex "[1:a]apad=whole_dur=${DUR}[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k -shortest "$OUT"
echo "DONE"; ffprobe -v error -show_entries format=duration -of csv=p=0 control_room_reel.mp4