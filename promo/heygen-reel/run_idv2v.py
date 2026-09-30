import os, fal_client, json
key=open("/opt/data/secrets-fal.txt").read().split("=",1)[1].strip()
os.environ["FAL_KEY"]=key
base="/opt/data/projects/dailyqapp/promo/heygen-reel/"
video=fal_client.upload_file(base+"wan_3am_raw.mp4")
face=fal_client.upload_file(base+"facerefs/img_4c952c3ef244.jpg")
r=fal_client.subscribe("fal-ai/id-v2v", arguments={
 "prompt": "Replace the face of the man working on the laptop with the face of the person from the reference image. Preserve his identity faithfully: dark wavy hair, stubble beard, large rectangular glasses. Keep the scene, motion and lighting unchanged.",
 "video_url": video,
 "image_url": face,
})
open(base+"idv2v_res.json","w").write(json.dumps(r))
print(json.dumps(r)[:600])
