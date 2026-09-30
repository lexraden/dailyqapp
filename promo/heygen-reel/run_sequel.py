import os, fal_client, json
key=open("/opt/data/secrets-fal.txt").read().split("=",1)[1].strip()
os.environ["FAL_KEY"]=key
base="/opt/data/projects/dailyqapp/promo/heygen-reel/"
refs=[fal_client.upload_file(base+"facerefs/img_4c952c3ef244.jpg"),
      fal_client.upload_file(base+"facerefs/img_f184613e69c8.jpg"),
      fal_client.upload_file(base+"facerefs/img_596c6d121c58.jpg")]
r=fal_client.subscribe("alibaba/wan-3.0-prime/reference-to-video", arguments={
 "prompt": "Cinematic handheld phone footage at night, vertical. The man from the reference photos (dark wavy hair, stubble beard, large rectangular glasses) sits on a beige fabric couch on a tropical villa terrace at night. He slowly closes the laptop on his lap, the screen dimming to black. A smartphone lying on the couch cushion beside him lights up with a notification glow; he glances at it with a faint amused smile. Warm string lights bokeh, wooden furniture, plants, dark garden background. Subtle handheld camera drift, shallow depth of field, photorealistic, natural motion.",
 "reference_images": refs,
 "aspect_ratio": "9:16",
 "resolution": "720p",
 "duration": "5",
})
open(base+"wan_sequel_res.json","w").write(json.dumps(r))
print(json.dumps(r)[:400])
