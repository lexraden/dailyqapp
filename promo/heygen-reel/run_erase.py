import os, fal_client, json
key=open("/opt/data/secrets-fal.txt").read().split("=",1)[1].strip()
os.environ["FAL_KEY"]=key
base="/opt/data/projects/dailyqapp/promo/heygen-reel/"
video=fal_client.upload_file(base+"pixswap_out.mp4")
mask=fal_client.upload_file(base+"text_mask.mp4")
r=fal_client.subscribe("bria/bria_video_eraser/erase/mask", arguments={
 "video_url": video,
 "mask_video_url": mask,
})
open(base+"bria_erase_res.json","w").write(json.dumps(r))
print(json.dumps(r)[:600])
