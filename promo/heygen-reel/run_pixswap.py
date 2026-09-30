import os, fal_client, json
key=open("/opt/data/secrets-fal.txt").read().split("=",1)[1].strip()
os.environ["FAL_KEY"]=key
base="/opt/data/projects/dailyqapp/promo/heygen-reel/"
ref="/opt/data/projects/dailyqapp/promo/references/reels/Ddu8AkHBZzV/ref.mp4"
video=fal_client.upload_file(base+"ref_720.mp4")
face=fal_client.upload_file(base+"facerefs/img_4c952c3ef244.jpg")
r=fal_client.subscribe("fal-ai/pixverse/swap", arguments={
 "video_url": video,
 "image_url": face,
})
open(base+"pixverse_swap_res.json","w").write(json.dumps(r))
print(json.dumps(r)[:600])
