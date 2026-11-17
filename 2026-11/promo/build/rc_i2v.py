"""Pornește clipuri image-to-video pe RunComfy (Kling 3.0 Pro) și le descarcă.

Rulare:  python3 rc_i2v.py <fișier_joburi.json> <dir_ieșire>
Fișierul de joburi: [{"name": "...", "image": "<url public>", "prompt": "...", "duration": 5}, ...]
Credențialele RunComfy sunt injectate de proxy; header-ul Authorization e doar un substituent.
"""
import json, os, sys, time, urllib.request

API = "https://model-api.runcomfy.net/v1"
MODEL = "kling/kling-3.0/pro/image-to-video"
NEG = ("morphing, warping walls, melting, new furniture, extra windows, people, text, watermark, "
       "flicker, fast motion, zoom blur, distorted architecture, camera shake")
H = {"Content-Type": "application/json", "Authorization": "Bearer dummy"}


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers=H,
                                 method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


jobs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
ids = {}
for j in jobs:
    r = call(f"{API}/models/{MODEL}", {"prompt": j["prompt"], "start_image_url": j["image"],
                                        "duration": j.get("duration", 5), "generate_audio": False,
                                        "negative_prompt": j.get("negative", NEG), "cfg_scale": 0.6})
    ids[j["name"]] = r["request_id"]; print("pornit", j["name"], flush=True)
pending = dict(ids)
while pending:
    time.sleep(15)
    for name, rid in list(pending.items()):
        st = call(f"{API}/requests/{rid}/status")["status"]
        if st in ("completed", "failed", "cancelled"):
            del pending[name]
            if st != "completed":
                print("EȘUAT", name, st, flush=True); continue
            res = call(f"{API}/requests/{rid}/result")["output"]
            url = res.get("video") or res.get("video_url") or next(v for v in res.values() if isinstance(v, str) and v.startswith("http"))
            urllib.request.urlretrieve(url, os.path.join(out, f"{name}.mp4")); print("gata", name, flush=True)
