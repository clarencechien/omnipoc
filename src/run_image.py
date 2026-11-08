"""Run a batch of image specs: python src/run_image.py --exp O0 --spec prompts/opening/s0.yaml [--only id1,id2]"""
import argparse, json, os, sys, yaml, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget
from clients import image
ap = argparse.ArgumentParser(); ap.add_argument("--exp", required=True); ap.add_argument("--spec", required=True); ap.add_argument("--only")
a = ap.parse_args(); cfg = budget.CFG; m = cfg["models"]["nb2"]; spec = yaml.safe_load(open(a.spec))
only = set(a.only.split(",")) if a.only else None
for s in spec["images"]:
    if only and s["id"] not in only: continue
    size = s.get("size", "1K"); est = round(cfg["pricing_usd"]["nb2_tokens_per_image"][size] * cfg["pricing_usd"]["nb2_output_per_m_tok"] / 1e6, 4)
    budget.check_cap("opening", est, exp=a.exp)
    run_id = f"{a.exp}/nb2-{s['id']}-{uuid.uuid4().hex[:6]}"; out_dir = os.path.join(budget.ROOT, "runs", run_id); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "image.jpg")
    entry = dict(exp=a.exp, provider="nanobanana", model=m["id"], prompt_id=s["id"], rep=1, params={"aspect": s.get("aspect", "16:9"), "size": size, "refs": s.get("refs", [])}, est_cost=est, run_id=run_id)
    print(f"[{run_id}] est ${est:.3f} -> {size} {s.get('aspect','16:9')}", flush=True)
    try:
        refs = [os.path.join(budget.ROOT, r) for r in s.get("refs", [])]
        r = image.generate(m["id"], s["text"], s.get("aspect", "16:9"), size, out, ref_images=refs)
        entry.update(status="ok", error=None, latency_s=r["latency_s"], usage=r["usage"], actual_cost=r["actual_cost"])
        json.dump({"run_id": run_id, "spec": s, "latency_s": r["latency_s"], "actual_cost": r["actual_cost"], "response": r["raw"]}, open(os.path.join(out_dir, "meta.json"), "w"), indent=1, ensure_ascii=False)
        print(f"[{run_id}] OK {r['latency_s']}s ${r['actual_cost']} usage={json.dumps(r['usage'])[:300]}")
    except Exception as e:
        entry.update(status="failed", error=str(e)[:800]); print(f"[{run_id}] FAILED {e}", file=sys.stderr)
    finally:
        budget.record(**entry)
