"""Screen clips with Gemini Decision 1 (Decisions API): calibrated yes/no glitch checks + a script-adherence rubric.
usage: python3 src/check_decision.py EXP:shot_id [EXP:shot_id ...] [--res medium]
Writes review/wedding/decision-check.json. Input-only billing ($0.10 / 1M tokens), zero output tokens.
"""
import argparse, base64, glob, json, os, sys, time, requests, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget
URL = "https://generativelanguage.googleapis.com/v1beta/decisions"
GLITCH = {
  "walk_backwards": "At any moment in this video, does a person walk backwards, moonwalk, or slide along the ground without taking proper steps?",
  "objects_change": "At any moment in this video, do objects (plates, food, cups, keys, props) suddenly appear, disappear, duplicate, or change in number?",
  "layout_jump": "At any moment in this continuous shot, does furniture, the table, or the room layout suddenly jump, move by itself, or change?",
  "hands_glitch": "At any moment in this video, do hands or fingers merge, twist unnaturally, float in mid-air, or pass through objects?",
  "morph": "At any moment in this video, does a character's face or body morph, melt, or change into a different-looking person?",
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("clips", nargs="+"); ap.add_argument("--res", default="medium"); a = ap.parse_args()
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("gemini_key")
    sb = yaml.safe_load(open(os.path.join(budget.ROOT, "prompts/wedding/storyboard.yaml")))
    shots = {sh["id"]: sh for seg in sb["segments"] for sh in seg["shots"]}
    out_path = os.path.join(budget.ROOT, "review", "wedding", "decision-check.json")
    res = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for c in a.clips:
        exp, sid = c.split(":")
        m = [p for p in sorted(glob.glob(os.path.join(budget.ROOT, "runs", exp, f"*-{sid}-r*", "meta.json")), key=os.path.getmtime) if "error" not in json.load(open(p))][-1]
        d = os.path.dirname(m)
        script = " ".join(shots[sid].get("prompt", "").split())
        q = {k: {"type": "noul", "instructions": v} for k, v in GLITCH.items()}
        q["follows_script"] = {"type": "score", "instructions": "Here is the script for this shot: \"" + script + "\" How closely does the video follow this script?",
                               "criteria": ["Does not follow: wrong place, people or action.", "Partly: the place and people match but the main action or camera move is missing or wrong.",
                                            "Mostly: the main action happens with small deviations.", "Fully: place, people, action and camera move all match the script."]}
        body = {"model": "gemini-decision-1", "questions": q,
                "input": [{"type": "video", "mime_type": "video/mp4", "resolution": a.res, "data": base64.b64encode(open(os.path.join(d, "video.mp4"), "rb").read()).decode()}]}
        budget.check_cap("vision", 0.01, exp="WD")
        t0 = time.time(); r = requests.post(URL, headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, timeout=300)
        entry = dict(exp="WD", provider="gemini", model="gemini-decision-1", prompt_id=f"decision:{exp}:{sid}", rep=1, params={"res": a.res}, est_cost=0.001)
        if r.status_code != 200:
            budget.record(**entry, status="failed", error=r.text[:300]); print("ERR", c, r.text[:300]); continue
        j = r.json(); u = j.get("usage", {}); cost = u.get("total_input_tokens", 0) * 0.10 / 1e6
        budget.record(**entry, status="ok", error=None, usage=u, actual_cost=round(cost, 6), latency_s=round(time.time() - t0, 1))
        ans = j["answers"]; res[c] = {"run": os.path.relpath(d, budget.ROOT), "answers": ans}
        json.dump(res, open(out_path, "w"), ensure_ascii=False, indent=1)
        g = " ".join(f"{k}={ans[k]['noul']:.2f}" for k in GLITCH)
        s = ans["follows_script"]
        print(f"{c:26} {g} | script={s['score']:.2f}/3 (conf {s['confidence']:.2f}) | {u.get('total_input_tokens')} tok ${cost:.4f} {time.time()-t0:.1f}s", flush=True)
if __name__ == "__main__":
    main()
