#!/usr/bin/env python3
"""Generate the Heiden intro shots with the Higgsfield API.

  python3 generate.py estimate          # price every request, generate nothing
  python3 generate.py reference         # make the hero reference image of the bike
  python3 generate.py shots             # generate all missing shots into clips/
  python3 generate.py shots 03 07       # only these shots (re-roll)
  python3 generate.py all               # reference, then shots

Credentials: set HF_API_KEY_ID and HF_API_KEY_SECRET, or run inside an environment whose
proxy injects the Authorization header (then any placeholder value works).
Spending is capped by BUDGET_USD (default 20); the script refuses to exceed it.
"""
import json, os, sys, time, uuid, random, urllib.request, urllib.error, shutil

API = "https://api.higgsfield.ai"
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = json.load(open(os.path.join(HERE, "shots-gen.json")))
GEN = os.path.join(HERE, "generated"); os.makedirs(GEN, exist_ok=True)
CLIPS = os.path.join(HERE, "clips")
MANIFEST = os.path.join(GEN, "manifest.json")
BUDGET = float(os.environ.get("BUDGET_USD", "20"))
KEY = f"{os.environ.get('HF_API_KEY_ID','proxy')}:{os.environ.get('HF_API_KEY_SECRET','injected')}"

def manifest():
    return json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {"spent_usd": 0.0, "requests": {}}
def save(m): json.dump(m, open(MANIFEST, "w"), indent=2)

def call(method, url, body=None, idem=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Key {KEY}")
    if data is not None: req.add_header("Content-Type", "application/json")
    if idem: req.add_header("Idempotency-Key", idem)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} {method} {url}\n{e.read().decode(errors='replace')[:800]}")

def fill(p):
    return (p.replace("{BIKE}", PLAN["bike"]).replace("{STUDIO}", PLAN["style_studio"])
             .replace("{RIDE}", PLAN["style_ride"]).replace("{RIDER}", PLAN["rider"]))

def estimate(endpoint, body):
    return float(call("POST", f"{API}/estimate/{endpoint}", body)["usd"])

def submit_and_wait(endpoint, body, label):
    r = call("POST", f"{API}/{endpoint}", body, idem=str(uuid.uuid4()))
    rid, status_url = r["request_id"], r["status_url"]
    print(f"  {label}: submitted {rid}")
    delay = 3.0
    while True:
        time.sleep(delay + random.uniform(0, 0.5)); delay = min(delay * 1.4, 10)
        s = call("GET", status_url)
        if s["status"] in ("completed", "failed", "nsfw", "canceled"):
            return rid, s
        print(f"  {label}: {s['status']}", end="\r")

def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "heiden-video/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    return dest

def video_body(shot):
    body = dict(PLAN["video_defaults"]); body["prompt"] = fill(shot["prompt"])
    m = manifest()
    ref = m.get("reference_image_url")
    if ref: body["image_urls"] = [ref]
    return body

def do_estimate(shot_ids):
    ref = PLAN["reference_image"]; total = estimate(ref["endpoint"], fill_body(ref["body"]))
    print(f"  reference image ({ref['endpoint']}): ${total:.3f}")
    for s in PLAN["shots"]:
        if shot_ids and s["stem"][:2] not in shot_ids: continue
        body = video_body(s); body.setdefault("image_urls", ["https://example.com/ref.jpg"])
        usd = estimate(PLAN["video_endpoint"], body); total += usd
        print(f"  {s['stem']} ({body['duration']}s {body['resolution']}): ${usd:.3f}")
    print(f"  TOTAL ${total:.2f}  (budget ${BUDGET:.2f})")
    return total

def fill_body(b): b = dict(b); b["prompt"] = fill(b["prompt"]); return b

def charge(m, usd, rid, note):
    m["spent_usd"] = round(m["spent_usd"] + usd, 4); m["requests"][rid] = note; save(m)

def do_reference():
    m = manifest()
    if m.get("reference_image_url") and os.path.exists(os.path.join(GEN, "reference.jpg")):
        print("  reference image already exists, skipping"); return
    ref = PLAN["reference_image"]; body = fill_body(ref["body"])
    usd = estimate(ref["endpoint"], body)
    if m["spent_usd"] + usd > BUDGET: raise SystemExit(f"budget: ${usd:.2f} would exceed ${BUDGET}")
    rid, s = submit_and_wait(ref["endpoint"], body, "reference")
    if s["status"] != "completed": raise SystemExit(f"reference image {s['status']}: {s.get('error')}")
    url = s["images"][0]["url"]
    download(url, os.path.join(GEN, "reference.jpg"))
    m["reference_image_url"] = url; charge(m, usd, rid, {"kind": "reference", "usd": usd, "url": url})
    print(f"  reference image -> generated/reference.jpg  (${usd:.3f})")

def do_shots(shot_ids):
    m = manifest()
    if not m.get("reference_image_url"): print("  (no reference image yet; shots will be text-only)")
    for s in PLAN["shots"]:
        if shot_ids and s["stem"][:2] not in shot_ids: continue
        dest = os.path.join(CLIPS, s["stem"] + ".mp4")
        if os.path.exists(dest) and not shot_ids:
            print(f"  {s['stem']}: exists, skipping"); continue
        body = video_body(s)
        if "image_urls" not in body:
            ep = PLAN["video_endpoint"].replace("reference-to-video", "text-to-video")
        else:
            ep = PLAN["video_endpoint"]
        usd = estimate(ep, body)
        if m["spent_usd"] + usd > BUDGET:
            raise SystemExit(f"budget: {s['stem']} ${usd:.2f} would exceed ${BUDGET} (spent ${m['spent_usd']:.2f})")
        rid, st = submit_and_wait(ep, body, s["stem"])
        if st["status"] != "completed":
            print(f"  {s['stem']}: {st['status']} {st.get('error','')} (not charged)"); continue
        url = st["video"]["url"]
        if os.path.exists(dest): shutil.move(dest, dest.replace(".mp4", f".old-{int(time.time())}.mp4"))
        download(url, dest)
        charge(m, usd, rid, {"kind": "shot", "stem": s["stem"], "usd": usd, "url": url, "prompt": body["prompt"]})
        print(f"  {s['stem']} -> clips/{os.path.basename(dest)}  (${usd:.3f}, total ${m['spent_usd']:.2f})")

if __name__ == "__main__":
    cmd, ids = (sys.argv[1] if len(sys.argv) > 1 else "estimate"), sys.argv[2:]
    if cmd == "estimate": do_estimate(ids)
    elif cmd == "reference": do_reference()
    elif cmd == "shots": do_shots(ids)
    elif cmd == "all": do_reference(); do_shots(ids)
    else: raise SystemExit(__doc__)
