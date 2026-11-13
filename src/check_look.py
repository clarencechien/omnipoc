"""Check that characters in generated images still match the model sheets.

usage: python3 src/check_look.py --exp WC --manifest prompts/wedding/look-check.yaml [--only id1,id2]
manifest: {items: [{id, path, who: [she|he|wed|he-face]}]}
Uses gemini-3.5-flash-lite (vision) with the model sheets as references; every call is logged to the ledger.
Writes review/<name>/look-check.json and prints a table. An item fails if any visible attribute mismatches.
"""
import argparse, base64, json, os, sys, time, requests, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget

MODEL = os.environ.get("LOOK_MODEL", "gemini-3.5-flash-lite")
PRICES = {"gemini-3.5-flash-lite": (0.30, 2.50), "gemini-3.8-flash": (0.75, 3.75), "gemini-3.1-pro-preview": (2.00, 12.00)}   # USD per 1M tokens in / out (out includes thinking)
PRICE_IN, PRICE_OUT = PRICES.get(MODEL, (1.0, 6.0))  # unknown models are booked at a conservative guess
R = "refs/wedding/"
SHEETS = {"she": [R + "she-face.jpg", R + "she-sheet.jpg"], "he": [R + "he-face.jpg", R + "he-sheet.jpg"],
          "wed": [R + "she-face.jpg", R + "he-face.jpg", R + "source/playbill-couple-4heads.png"], "he-face": [R + "he-face.jpg"]}
CHECKS = {
    "she": ["half-up princess-style wavy dark-brown hair (twisted strands gathered at the back)", "oatmeal / beige knit sweater",
            "sage-green pleated midi skirt", "white low sneakers", "small tan leather crossbody bag", "rounded face with blushing cheeks, small closed-mouth smile"],
    "he": ["black rectangular glasses", "short swept black hair", "navy overshirt worn open", "white crewneck T-shirt under it",
           "khaki chinos", "white canvas sneakers", "black backpack (only if shown on the sheet's back view or mentioned)"],
    "wed": ["man: black rectangular glasses", "man: black relaxed suit over a white crewneck", "man: black shoes",
            "woman: half-up wavy brown hair", "woman: blush pink cardigan", "woman: ivory calf-length dress", "woman: ivory Mary Jane shoes",
            "woman: small blush and cream bouquet"],
    "he-face": ["black rectangular glasses", "short swept black hair", "same face as the sheet (allowed to look younger)"],
}

def b64(path):
    return base64.b64encode(open(os.path.join(budget.ROOT, path), "rb").read()).decode()

def mime(path):
    return "image/png" if path.endswith(".png") else "image/jpeg"

def check(item, key):
    refs = []
    for w in item["who"]:
        for r in SHEETS[w]:
            if r not in refs and os.path.exists(os.path.join(budget.ROOT, r)): refs.append(r)
    parts = [{"text": "You are checking character consistency for an animated film. The first "
              f"{len(refs)} image(s) are the approved character references (model sheets). The LAST image is the candidate frame."}]
    for r in refs:
        parts.append({"inline_data": {"mime_type": mime(r), "data": b64(r)}})
    parts.append({"inline_data": {"mime_type": mime(item["path"]), "data": b64(item["path"])}})
    lines = []
    for w in item["who"]:
        lines.append(f"[{w}] " + "; ".join(CHECKS[w]))
    parts.append({"text": "For each attribute below, compare the candidate with the references and answer match, mismatch or not_visible "
                  "(use not_visible when the attribute is hidden by pose, crop or a back view). Be strict about colors and garment types. "
                  "Also say whether the characters are rendered as 3D matte clay figurines (not flat 2D drawings), and list any readable text "
                  "or logos in the image.\n" + "\n".join(lines) + "\n"
                  "Finally, for EACH character whose face is visible, compare ONLY the face with the face reference: eye size, shape and spacing, "
                  "eye highlights, eyebrows, nose size, mouth, cheek shape and blush, overall head shape. Give face_score 1-5 "
                  "(5 = clearly the same character, 4 = same with tiny differences, 3 = noticeably different features, 1-2 = a different person). "
                  "Use who = she or he. Skip characters whose face is not visible."})
    schema = {"type": "OBJECT", "properties": {
        "attributes": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "who": {"type": "STRING"}, "attribute": {"type": "STRING"},
            "status": {"type": "STRING", "enum": ["match", "mismatch", "not_visible"]}, "note": {"type": "STRING"}},
            "required": ["who", "attribute", "status"]}},
        "faces": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "who": {"type": "STRING"}, "face_score": {"type": "INTEGER"}, "difference": {"type": "STRING"}}, "required": ["who", "face_score"]}},
        "clay_3d": {"type": "BOOLEAN"}, "readable_text": {"type": "STRING"}, "summary": {"type": "STRING"}},
        "required": ["attributes", "clay_3d", "summary"]}
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": schema, "temperature": 0}}
    t0 = time.time()
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                      headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:400]}")
    j = r.json()
    u = j.get("usageMetadata", {})
    cost = u.get("promptTokenCount", 0) * PRICE_IN / 1e6 + (u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)) * PRICE_OUT / 1e6
    out = json.loads(j["candidates"][0]["content"]["parts"][0]["text"])
    return out, u, round(cost, 5), round(time.time() - t0, 1)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", default="WC"); ap.add_argument("--manifest", required=True); ap.add_argument("--only")
    a = ap.parse_args()
    global key
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("gemini_key")
    items = yaml.safe_load(open(a.manifest))["items"]
    only = set(a.only.split(",")) if a.only else None
    res_path = os.path.join(budget.ROOT, "review", "wedding", "look-check.json")
    results = json.load(open(res_path)) if os.path.exists(res_path) else {}
    for it in items:
        if only and it["id"] not in only: continue
        budget.check_cap("vision", 0.005, exp=a.exp)
        entry = dict(exp=a.exp, provider="gemini", model=MODEL, prompt_id="look-check:" + it["id"], rep=1,
                     params={"image": it["path"], "who": it["who"]}, est_cost=0.004)
        try:
            out, u, cost, lat = check(it, key)
            bad = [x for x in out["attributes"] if x["status"] == "mismatch"]
            faces = out.get("faces", [])
            bad_faces = [f for f in faces if f.get("face_score", 5) < 4]
            verdict = "pass" if not bad and not bad_faces and out.get("clay_3d", True) else "fail"
            results[it["id"]] = {"path": it["path"], "verdict": verdict, "mismatches": bad, "faces": faces, "clay_3d": out.get("clay_3d"),
                                 "readable_text": out.get("readable_text", ""), "summary": out.get("summary", ""),
                                 "not_visible": [x["attribute"] for x in out["attributes"] if x["status"] == "not_visible"]}
            entry.update(status="ok", error=None, usage=u, actual_cost=cost, latency_s=lat)
            flag = "PASS" if verdict == "pass" else "FAIL"
            fs = " ".join(f"{f['who']}={f['face_score']}" for f in faces)
            print(f"{flag}  {it['id']:22} faces[{fs}] " + ("; ".join(f"{m['who']}:{m['attribute'][:28]} ({m.get('note','')[:50]})" for m in bad)
                  or "; ".join(f"{f['who']}: {f.get('difference','')[:60]}" for f in bad_faces) or out.get("summary", "")[:70]), flush=True)
        except Exception as e:
            entry.update(status="failed", error=str(e)[:400]); print(f"ERR   {it['id']}: {e}", flush=True)
        finally:
            budget.record(**entry)
    os.makedirs(os.path.dirname(res_path), exist_ok=True)
    json.dump(results, open(res_path, "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
