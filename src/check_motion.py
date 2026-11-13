"""Watch whole clips with a video-capable model and report continuity/motion glitches with timestamps,
plus the longest clean segment. usage: python3 src/check_motion.py --exp W12 [--only id1,id2]
Writes review/wedding/motion-check.json. Every call is logged to the ledger.
"""
import argparse, base64, glob, json, os, sys, time, requests, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget

MODEL = os.environ.get("MOTION_MODEL", "gemini-3.8-flash")
PRICE_IN, PRICE_OUT = {"gemini-3.8-flash": (0.75, 3.75)}.get(MODEL, (1.0, 6.0))
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
ASK = ("You are a film continuity checker. Watch this short animated clip (clay figurines) carefully, frame by frame. "
       "Shot description: {desc}\n"
       "List every glitch with start and end time in seconds: people walking or sliding backwards, moonwalking feet, "
       "objects (plates, food, cups, furniture) appearing, disappearing, multiplying or changing count, furniture or the "
       "table jumping position, hands floating in mid-air or passing through objects, sudden scene or layout changes "
       "inside one continuous shot, faces or bodies morphing, extra or missing limbs or fingers. Ignore deliberate cuts "
       "that are part of the described shot. Then give the longest continuous segment with no glitches (clean_start, "
       "clean_end) and a short overall verdict.")
SCHEMA = {"type": "OBJECT", "properties": {
    "glitches": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
        "start": {"type": "NUMBER"}, "end": {"type": "NUMBER"}, "kind": {"type": "STRING"}, "what": {"type": "STRING"}},
        "required": ["start", "end", "kind", "what"]}},
    "clean_start": {"type": "NUMBER"}, "clean_end": {"type": "NUMBER"}, "verdict": {"type": "STRING"}},
    "required": ["glitches", "clean_start", "clean_end", "verdict"]}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", required=True); ap.add_argument("--only"); ap.add_argument("--spec", default="prompts/wedding/videos.yaml")
    a = ap.parse_args(); key = os.environ.get("GEMINI_API_KEY") or os.environ.get("gemini_key")
    sb = yaml.safe_load(open(os.path.join(budget.ROOT, "prompts/wedding/storyboard.yaml")))
    zh = {sh["id"]: sh for seg in sb["segments"] for sh in seg["shots"]}
    only = a.only.split(",")
    out_path = os.path.join(budget.ROOT, "review", "wedding", "motion-check.json")
    res = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for vid in only:
        metas = sorted(glob.glob(os.path.join(budget.ROOT, "runs", a.exp, f"*-{vid}-r*", "meta.json")), key=os.path.getmtime)
        metas = [m for m in metas if "error" not in json.load(open(m))]
        if not metas: print("no run for", vid); continue
        d = os.path.dirname(metas[-1]); data = base64.b64encode(open(os.path.join(d, "video.mp4"), "rb").read()).decode()
        desc = " ".join(zh[vid].get("prompt", "").split())[:900]
        budget.check_cap("vision", 0.03, exp=a.exp)
        body = {"contents": [{"role": "user", "parts": [{"inline_data": {"mime_type": "video/mp4", "data": data}}, {"text": ASK.format(desc=desc)}]}],
                "generationConfig": {"responseMimeType": "application/json", "responseSchema": SCHEMA, "temperature": 0}}
        t0 = time.time()
        r = requests.post(URL, headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, timeout=300)
        entry = dict(exp="WM", provider="gemini", model=MODEL, prompt_id="motion:" + vid, rep=1, params={"run": os.path.relpath(d, budget.ROOT)}, est_cost=0.02)
        if r.status_code != 200:
            budget.record(**entry, status="failed", error=r.text[:300]); print("ERR", vid, r.text[:200]); continue
        j = r.json(); u = j.get("usageMetadata", {})
        cost = u.get("promptTokenCount", 0) * PRICE_IN / 1e6 + (u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)) * PRICE_OUT / 1e6
        budget.record(**entry, status="ok", error=None, usage=u, actual_cost=round(cost, 5), latency_s=round(time.time() - t0, 1))
        out = json.loads(j["candidates"][0]["content"]["parts"][0]["text"]); out["run"] = os.path.relpath(d, budget.ROOT)
        res[vid] = out; json.dump(res, open(out_path, "w"), ensure_ascii=False, indent=1)
        g = "; ".join(f"{x['start']:.1f}-{x['end']:.1f}s {x['kind']}: {x['what'][:60]}" for x in out["glitches"]) or "none"
        print(f"{vid:18} clean {out['clean_start']:.1f}-{out['clean_end']:.1f}s | ${cost:.3f} | {g}", flush=True)

if __name__ == "__main__":
    main()
