"""Face-only consistency check: detect each character's face, crop it large, compare with the face sheet.

usage: python3 src/check_faces.py --manifest prompts/wedding/look-check.yaml [--only id1,id2] [--exp WF]
Step 1 (gemini-3.8-flash): find faces -> box_2d + who (man with glasses / woman).
Step 2 (gemini-3.8-flash): compare each 512 px crop with that character's face sheet, ignoring expression,
        angle and lighting; score 1-5 on facial structure. Score < 4 = drift.
Writes review/wedding/face-check.json; every call is logged to the ledger.
"""
import argparse, base64, io, json, os, sys, time, requests, yaml
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget

MODEL = os.environ.get("FACE_MODEL", "gemini-3.8-flash")
PRICE_IN, PRICE_OUT = {"gemini-3.8-flash": (0.75, 3.75), "gemini-3.5-flash-lite": (0.30, 2.50)}.get(MODEL, (1.0, 6.0))
FACE = {"he": "refs/wedding/he-face.jpg", "she": "refs/wedding/she-face.jpg"}
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

def img_part(im):
    buf = io.BytesIO(); im.convert("RGB").save(buf, "JPEG", quality=92)
    return {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}

def call(parts, schema, key, exp, tag):
    budget.check_cap("vision", 0.02, exp=exp)
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": schema, "temperature": 0}}
    t0 = time.time()
    r = requests.post(URL, headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, timeout=180)
    entry = dict(exp=exp, provider="gemini", model=MODEL, prompt_id=tag, rep=1, params={}, est_cost=0.01)
    if r.status_code != 200:
        budget.record(**entry, status="failed", error=r.text[:300]); raise RuntimeError(r.text[:300])
    j = r.json(); u = j.get("usageMetadata", {})
    cost = u.get("promptTokenCount", 0) * PRICE_IN / 1e6 + (u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)) * PRICE_OUT / 1e6
    budget.record(**entry, status="ok", error=None, usage=u, actual_cost=round(cost, 5), latency_s=round(time.time() - t0, 1))
    return json.loads(j["candidates"][0]["content"]["parts"][0]["text"])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--only"); ap.add_argument("--exp", default="WF")
    a = ap.parse_args(); key = os.environ.get("GEMINI_API_KEY") or os.environ.get("gemini_key")
    items = yaml.safe_load(open(a.manifest))["items"]; only = set(a.only.split(",")) if a.only else None
    out_path = os.path.join(budget.ROOT, "review", "wedding", "face-check.json")
    results = json.load(open(out_path)) if os.path.exists(out_path) else {}
    crop_dir = os.path.join(budget.ROOT, "review", "wedding", "face-crops"); os.makedirs(crop_dir, exist_ok=True)
    sheets = {w: Image.open(os.path.join(budget.ROOT, p)) for w, p in FACE.items()}
    for it in items:
        if only and it["id"] not in only: continue
        wants = set()
        for w in it["who"]:
            wants |= {"wed": {"she", "he"}, "she": {"she"}, "he": {"he"}, "he-face": {"he"}}[w]
        im = Image.open(os.path.join(budget.ROOT, it["path"])); W, H = im.size
        det = call([{"text": "Find the face of each main clay character in this image. who = 'he' for the man with black rectangular glasses, "
                             "'she' for the woman with long dark-brown hair. box_2d = [ymin, xmin, ymax, xmax] normalized to 0-1000, covering the "
                             "whole head including hair. visible = false if the face is turned away (back view) or hidden."}, img_part(im)],
                   {"type": "OBJECT", "properties": {"faces": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                       "who": {"type": "STRING"}, "box_2d": {"type": "ARRAY", "items": {"type": "INTEGER"}}, "visible": {"type": "BOOLEAN"}},
                       "required": ["who", "box_2d", "visible"]}}}, "required": ["faces"]}, key, a.exp, "face-detect:" + it["id"])
        res = {"path": it["path"], "faces": {}}
        for f in det["faces"]:
            w = f["who"]
            if w not in wants or w in res["faces"]: continue
            if not f.get("visible", True) or len(f["box_2d"]) != 4:
                res["faces"][w] = {"score": None, "note": "face not visible"}; continue
            y0, x0, y1, x1 = f["box_2d"]; pad = 0.15
            bw, bh = (x1 - x0) * W / 1000, (y1 - y0) * H / 1000
            box = (max(0, x0 * W / 1000 - pad * bw), max(0, y0 * H / 1000 - pad * bh), min(W, x1 * W / 1000 + pad * bw), min(H, y1 * H / 1000 + pad * bh))
            crop = im.crop(tuple(int(v) for v in box)); px = crop.width
            crop = crop.resize((512, int(512 * crop.height / max(crop.width, 1))))
            cpath = os.path.join(crop_dir, f"{it['id']}-{w}.jpg"); crop.convert("RGB").save(cpath, quality=90)
            cmp = call([{"text": "Image 1 is the approved face reference sheet of a clay character (front, three-quarter and profile views). "
                                 "Image 2 is a crop of the same character's face from a scene. IGNORE expression (smiling, closed or squinting eyes, "
                                 "laughing), head angle, lighting, blur and clothing. Compare ONLY facial structure: eye size relative to the face, "
                                 "eye spacing, iris size and catchlights when the eyes are open, eyebrow shape, nose size and shape, mouth size, "
                                 "cheek fullness and blush, head and jaw shape, hairline" + (", glasses frame shape and thickness" if w == "he" else "") +
                                 ". The reference has LARGE round dark-brown eyes with clear white catchlight highlights, a small button nose and a round full face. "
                                 "Known ways this character drifts (each one means score 3 or lower): open eyes shrunk to small black dots or beads, "
                                 "open eyes without white catchlights, a longer or bigger nose, a narrower or longer face, thick dark eyebrows"
                                 + (", thin or round glasses frames instead of thick rectangular ones" if w == "he" else "") +
                                 ". Closed smiling eyes are fine and should be judged on the other features. Score 1-5: 5 = clearly the same character, "
                                 "4 = same character with minor differences, 3 = noticeably different features, 2 = looks like a different character, 1 = completely different. "
                                 "In differences, name the drift pattern if one is present."}, img_part(sheets[w]), img_part(crop)],
                       {"type": "OBJECT", "properties": {"score": {"type": "INTEGER"}, "differences": {"type": "STRING"}}, "required": ["score", "differences"]},
                       key, a.exp, "face-compare:" + it["id"] + ":" + w)
            res["faces"][w] = {"score": cmp["score"], "note": cmp["differences"], "crop": os.path.relpath(cpath, budget.ROOT), "face_px": int(px)}
        scores = [v["score"] for v in res["faces"].values() if v.get("score") is not None]
        res["verdict"] = "pass" if all(s >= 4 for s in scores) else "drift"
        results[it["id"]] = res
        print(f"{res['verdict'].upper():5} {it['id']:22} " + "  ".join(
            f"{w}={v['score']}({v.get('face_px','-')}px) {('' if (v['score'] or 5) >= 4 else v['note'][:70])}" for w, v in res["faces"].items()), flush=True)
        json.dump(results, open(out_path, "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
