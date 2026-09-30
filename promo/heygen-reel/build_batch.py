import os, subprocess
base="/opt/data/projects/dailyqapp/promo/heygen-reel/"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
variants={
 "v1_radar":"Me at 3AM watching the\nusername radar. Two sold\nwhile I slept.",
 "v2_dailyq":"Me at 3AM leveling up\ninstead of sleeping.",
 "v3_botify":"Me at 3AM building a bot\nthat automates my\nwhole business.",
 "v4_agents":"Me at 3AM checking if my\nagents are still running.\nThey are.",
}
src=base+"pixswap_clean.mp4"  # без текста, 5.4с, лицо уже твоё
for name,text in variants.items():
    tf=base+f"overlay_{name}.txt"
    open(tf,"w").write(text)
    lines=text.count("\n")+1
    boxh=170+lines*60
    out=base+f"batch_{name}.mp4"
    vf=(f"drawbox=x=0:y=0:w=iw:h={boxh}:color=black@0.45:t=fill,"
        f"drawtext=textfile={tf}:fontfile={FONT}:fontsize=40:fontcolor=white:"
        f"x=max((w-text_w)/2\\,40):y=70:line_spacing=14")
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-vf",vf,"-r","30",
                    "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",out],check=True)
    print("done",name)
