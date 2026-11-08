"""Run video generations. Single:  python src/run.py --exp M1 --model omni_12 --prompt prompts/x.yaml [--duration 5 --res 720p --aspect 16:9 --rep 1]
Batch:   python src/run.py --exp O1 --model omni_12 --spec prompts/opening/s1-s3.yaml [--only id1,id2]
Each flow: estimate -> cap check -> call -> save video+meta -> ledger."""
import argparse, json, os, sys, yaml, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget, probe
from clients import omni, xai

def run_one(exp, model_key, spec, dur, res, asp, rep=1):
    cfg = budget.CFG; m = cfg["models"][model_key]
    prov = "omni" if m["provider"] == "gemini" else m["provider"]
    est = budget.estimate(model_key, dur, res)
    spent_before = budget.check_cap(prov, est, exp=exp)
    run_id = f"{exp}/{model_key}-{spec['id']}-r{rep}-{uuid.uuid4().hex[:6]}"
    out_dir = os.path.join(budget.ROOT, "runs", run_id); os.makedirs(out_dir, exist_ok=True)
    video = os.path.join(out_dir, "video.mp4")
    refs = [os.path.join(budget.ROOT, r) for r in spec.get("refs", [])]
    print(f"[{run_id}] est ${est:.3f} (spent {prov} {spent_before:.3f}) -> {m['id']} {dur}s {res} {asp} refs={len(refs)}", flush=True)
    entry = dict(exp=exp, provider=prov, model=m["id"], prompt_id=spec["id"], rep=rep,
                 params={"duration_s": dur, "resolution": res, "aspect": asp, "refs": spec.get("refs", [])}, est_cost=est, run_id=run_id)
    try:
        if m["provider"] == "gemini":
            r = omni.generate(m["id"], spec["text"], dur, res, asp, video, ref_images=refs)
        else:
            r = xai.generate(m["id"], spec["text"], dur, res, asp, video)
        pr = probe.ffprobe(video)
        entry.update(status="ok", error=None, latency_s=r["latency_s"], usage=r.get("usage"), actual_cost=r.get("actual_cost"), ffprobe=pr)
        json.dump({"run_id": run_id, "model": m["id"], "prompt": spec, "params": entry["params"], "est_cost": est,
                   "actual_cost": r.get("actual_cost"), "latency_s": r["latency_s"], "ffprobe": pr, "response": r["raw"]},
                  open(os.path.join(out_dir, "meta.json"), "w"), indent=1, ensure_ascii=False)
        print(f"[{run_id}] OK latency {r['latency_s']}s actual ${r.get('actual_cost')} probe {json.dumps(pr)}", flush=True)
    except Exception as e:
        entry.update(status="failed", error=str(e)[:800])
        json.dump({"run_id": run_id, "error": str(e), "params": entry["params"]}, open(os.path.join(out_dir, "meta.json"), "w"), indent=1)
        print(f"[{run_id}] FAILED {e}", file=sys.stderr, flush=True)
    finally:
        budget.record(**entry)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True); ap.add_argument("--model", required=True)
    ap.add_argument("--prompt"); ap.add_argument("--spec"); ap.add_argument("--only")
    ap.add_argument("--duration", type=int); ap.add_argument("--res"); ap.add_argument("--aspect"); ap.add_argument("--rep", type=int, default=1)
    a = ap.parse_args(); d = budget.CFG["defaults"]
    if a.prompt:
        p = yaml.safe_load(open(a.prompt))
        run_one(a.exp, a.model, p, a.duration or d["duration_s"], a.res or d["resolution"], a.aspect or d["aspect"], a.rep)
    else:
        only = set(a.only.split(",")) if a.only else None
        for s in yaml.safe_load(open(a.spec))["videos"]:
            if only and s["id"] not in only: continue
            run_one(a.exp, a.model, s, a.duration or s.get("duration", d["duration_s"]), a.res or s.get("res", d["resolution"]), a.aspect or s.get("aspect", d["aspect"]), a.rep)
