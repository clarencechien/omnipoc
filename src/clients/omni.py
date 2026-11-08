"""Gemini Omni via Interactions API (REST). Sync unary call, delivery=uri."""
import os, time, json, requests
BASE = "https://generativelanguage.googleapis.com/v1beta"
def key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("gemini_key")
    if not k: raise SystemExit("no GEMINI_API_KEY / gemini_key in env")
    return k

def generate(model_id, prompt, duration_s, resolution, aspect, out_path, timeout_s=900, ref_images=()):
    H = {"x-goog-api-key": key(), "Content-Type": "application/json"}
    import base64
    inp = prompt
    if ref_images:
        inp = [{"type": "image", "mime_type": "image/png" if p.endswith(".png") else "image/jpeg",
                "data": base64.b64encode(open(p, "rb").read()).decode()} for p in ref_images]
        inp.append({"type": "text", "text": prompt})
    body = {"model": model_id, "input": inp,
            "response_format": {"type": "video", "duration": f"{duration_s}s", "resolution": resolution,
                                "aspect_ratio": aspect, "delivery": "uri"},
            "store": True, "background": False, "stream": False}  # store=true is required for delivery=uri (API 400 otherwise)
    t0 = time.time()
    r = requests.post(f"{BASE}/interactions", headers=H, json=body, timeout=timeout_s)
    latency = round(time.time() - t0, 1)
    try:
        j = r.json()
    except Exception:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {json.dumps(j)[:800]}")
    # locate video content + strip inline base64 for the meta record
    uri, inline = None, None
    for step in j.get("steps", []):
        for c in step.get("content", []) or []:
            if c.get("type") == "video":
                uri = c.get("uri") or uri
                if c.get("data"):
                    inline = c["data"]; c["data"] = f"<base64 {len(inline)} chars stripped>"
    for c in j.get("outputs", []) or []:
        if isinstance(c, dict) and c.get("type") == "video":
            uri = c.get("uri") or uri
            if c.get("data"):
                inline = c["data"]; c["data"] = f"<base64 {len(inline)} chars stripped>"
    if uri:
        fid = uri.split("/files/")[1].split(":")[0]
        for _ in range(120):
            s = requests.get(f"{BASE}/files/{fid}", headers=H, timeout=60).json()
            if s.get("state") in ("ACTIVE", "FAILED") or s.get("error"):
                break
            time.sleep(3)
        if s.get("state") == "FAILED" or s.get("error"):
            raise RuntimeError(f"file failed: {json.dumps(s)[:500]}")
        dl = requests.get(f"{BASE}/files/{fid}:download?alt=media", headers=H, timeout=600, allow_redirects=True)
        dl.raise_for_status()
        open(out_path, "wb").write(dl.content)
    elif inline:
        import base64
        open(out_path, "wb").write(base64.b64decode(inline))
    else:
        raise RuntimeError(f"no video in response: {json.dumps(j)[:1200]}")
    u = j.get("usage") or {}
    vid = sum(x["tokens"] for x in u.get("output_tokens_by_modality", []) if x.get("modality") == "video")
    # price page: video output $12/1M "including thinking tokens"; we book thought at the text-output rate $9/1M
    # as an upper-bound assumption until Cloud Billing confirms. Input $1.50/1M.
    cost = vid * 12.0 / 1e6 + (u.get("total_thought_tokens") or 0) * 9.0 / 1e6 + (u.get("total_input_tokens") or 0) * 1.5 / 1e6
    return {"latency_s": latency, "raw": j, "usage": u, "actual_cost": round(cost, 4) if u else None}
