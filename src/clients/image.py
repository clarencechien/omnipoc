"""Nano Banana 2 (gemini-3.1-flash-image) via Interactions API."""
import os, time, json, base64, requests
BASE = "https://generativelanguage.googleapis.com/v1beta"
def key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("gemini_key")
    if not k: raise SystemExit("no GEMINI_API_KEY / gemini_key in env")
    return k

def generate(model_id, prompt, aspect, image_size, out_path, ref_images=(), mime="image/jpeg"):
    H = {"x-goog-api-key": key(), "Content-Type": "application/json", "Api-Revision": "2026-05-20"}
    inp = []
    for p in ref_images:
        inp.append({"type": "image", "mime_type": "image/png" if p.endswith(".png") else "image/jpeg",
                    "data": base64.b64encode(open(p, "rb").read()).decode()})
    inp.append({"type": "text", "text": prompt})
    body = {"model": model_id, "input": inp,
            "response_format": {"type": "image", "mime_type": mime, "aspect_ratio": aspect, "image_size": image_size},
            "store": False, "background": False, "stream": False}
    t0 = time.time()
    r = requests.post(f"{BASE}/interactions", headers=H, json=body, timeout=300)
    latency = round(time.time() - t0, 1)
    try: j = r.json()
    except Exception: raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
    if r.status_code != 200: raise RuntimeError(f"HTTP {r.status_code}: {json.dumps(j)[:800]}")
    data = None
    for step in j.get("steps", []):
        for c in step.get("content", []) or []:
            if c.get("type") == "image" and c.get("data"):
                data = c["data"]; c["data"] = f"<base64 {len(data)} chars stripped>"
    if not data and j.get("output_image", {}).get("data"):
        data = j["output_image"]["data"]; j["output_image"]["data"] = "<stripped>"
    if not data: raise RuntimeError(f"no image in response: {json.dumps(j)[:1000]}")
    open(out_path, "wb").write(base64.b64decode(data))
    u = j.get("usage") or {}
    img = sum(x["tokens"] for x in u.get("output_tokens_by_modality", []) if x.get("modality") == "image")
    txt_out = sum(x["tokens"] for x in u.get("output_tokens_by_modality", []) if x.get("modality") == "text")
    cost = img * 60.0 / 1e6 + (txt_out + (u.get("total_thought_tokens") or 0)) * 0.50 / 1e6 * 0 + (u.get("total_input_tokens") or 0) * 0.50 / 1e6
    return {"latency_s": latency, "raw": j, "usage": u, "actual_cost": round(cost, 4) if u else None}
