"""xAI Grok Imagine Video via /v1/videos/generations + polling."""
import os, time, json, requests
BASE = "https://api.x.ai/v1"
TICK = 1e-10  # usage.cost_in_usd_ticks -> USD
def key():
    k = os.environ.get("XAI_API_KEY") or os.environ.get("xai_key")
    if not k: raise SystemExit("no XAI_API_KEY / xai_key in env")
    return k

def generate(model_id, prompt, duration_s, resolution, aspect, out_path, timeout_s=900):
    H = {"Authorization": f"Bearer {key()}", "Content-Type": "application/json"}
    body = {"model": model_id, "prompt": prompt, "duration": duration_s, "resolution": resolution, "aspect_ratio": aspect}
    t0 = time.time()
    r = requests.post(f"{BASE}/videos/generations", headers=H, json=body, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
    rid = r.json()["request_id"]
    while True:
        s = requests.get(f"{BASE}/videos/{rid}", headers=H, timeout=60).json()
        st = s.get("status")
        if st in ("done", "failed", "expired"):
            break
        if time.time() - t0 > timeout_s:
            raise RuntimeError(f"timeout polling {rid}")
        time.sleep(5)
    latency = round(time.time() - t0, 1)
    if st != "done":
        raise RuntimeError(f"status {st}: {json.dumps(s)[:500]}")
    dl = requests.get(s["video"]["url"], timeout=600)
    dl.raise_for_status()
    open(out_path, "wb").write(dl.content)
    ticks = (s.get("usage") or {}).get("cost_in_usd_ticks")
    return {"latency_s": latency, "raw": {"request_id": rid, **s}, "usage": s.get("usage"),
            "actual_cost": round(ticks * TICK, 4) if ticks is not None else None}
