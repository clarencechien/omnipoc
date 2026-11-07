"""Run one generation: estimate -> cap check -> ledger(pending) -> call -> save -> ledger(final).
usage: python src/run.py --exp M1 --model omni_12|grok_15 --prompt prompts/p1-obj-compass.yaml [--duration 5] [--res 720p] [--aspect 16:9] [--rep 1]
"""
import argparse, json, os, sys, time, yaml, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget, probe
from clients import omni, xai

ap = argparse.ArgumentParser()
ap.add_argument("--exp", required=True); ap.add_argument("--model", required=True); ap.add_argument("--prompt", required=True)
ap.add_argument("--duration", type=int); ap.add_argument("--res"); ap.add_argument("--aspect"); ap.add_argument("--rep", type=int, default=1)
a = ap.parse_args()
cfg = budget.CFG; m = cfg["models"][a.model]; d = cfg["defaults"]
dur = a.duration or d["duration_s"]; res = a.res or d["resolution"]; asp = a.aspect or d["aspect"]
p = yaml.safe_load(open(a.prompt))
est = budget.estimate(a.model, dur, res)
spent_before = budget.check_cap(m["provider"] if m["provider"] != "gemini" else "omni", est)
prov = "omni" if m["provider"] == "gemini" else m["provider"]
run_id = f"{a.exp}/{a.model}-{p['id']}-r{a.rep}-{uuid.uuid4().hex[:6]}"
out_dir = os.path.join(budget.ROOT, "runs", run_id); os.makedirs(out_dir, exist_ok=True)
video = os.path.join(out_dir, "video.mp4")
print(f"[{run_id}] est ${est:.3f} (spent {prov} {spent_before:.3f}) -> {m['id']} {dur}s {res} {asp}", flush=True)
entry = dict(exp=a.exp, provider=prov, model=m["id"], prompt_id=p["id"], rep=a.rep,
             params={"duration_s": dur, "resolution": res, "aspect": asp}, est_cost=est, run_id=run_id)
try:
    fn = omni.generate if m["provider"] == "gemini" else xai.generate
    r = fn(m["id"], p["text"], dur, res, asp, video)
    pr = probe.ffprobe(video)
    entry.update(status="ok", error=None, latency_s=r["latency_s"], usage=r.get("usage"),
                 actual_cost=r.get("actual_cost"), ffprobe=pr)
    json.dump({"run_id": run_id, "model": m["id"], "prompt": p, "params": entry["params"], "est_cost": est,
               "actual_cost": r.get("actual_cost"), "latency_s": r["latency_s"], "ffprobe": pr, "response": r["raw"]},
              open(os.path.join(out_dir, "meta.json"), "w"), indent=1, ensure_ascii=False)
    print(f"[{run_id}] OK latency {r['latency_s']}s actual ${r.get('actual_cost')} usage {json.dumps(r.get('usage'))} probe {json.dumps(pr)}")
except Exception as e:
    entry.update(status="failed", error=str(e)[:800])
    json.dump({"run_id": run_id, "error": str(e), "params": entry["params"]}, open(os.path.join(out_dir, "meta.json"), "w"), indent=1)
    print(f"[{run_id}] FAILED {e}", file=sys.stderr)
finally:
    budget.record(**entry)
