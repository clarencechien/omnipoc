"""Estimate, ledger, caps. Ledger = ledger/spend.jsonl (committed)."""
import json, os, datetime, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = yaml.safe_load(open(os.path.join(ROOT, "config.yaml")))
LEDGER = os.path.join(ROOT, "ledger", "spend.jsonl")

def estimate(model_key, duration_s, resolution):
    p = CFG["pricing_usd"]
    if model_key == "omni_12":
        tok = p["omni_tokens_per_s"][resolution] * duration_s
        return round(tok * p["omni_12_output_per_m_tok"] / 1e6, 4)
    if model_key == "grok_15":
        per_s = p["grok_15_per_s"][resolution]
        if per_s is None:
            raise ValueError(f"no price for grok {resolution}")
        return round(per_s * duration_s, 4)
    raise ValueError(model_key)

def entries():
    if not os.path.exists(LEDGER):
        return []
    return [json.loads(l) for l in open(LEDGER) if l.strip()]

def spent(provider, exclude_exp=("S0",)):
    tot = 0.0
    for e in entries():
        if e.get("provider") == provider and e.get("exp") not in exclude_exp:
            if e.get("actual_cost") is not None:
                tot += e["actual_cost"]
            elif e.get("status") == "ok":
                tot += e.get("est_cost", 0)   # failed (4xx) calls are not billed
    return round(tot, 4)

def check_cap(provider, est):
    cap = CFG["budget"]["caps_usd"][provider]
    s = spent(provider)
    if s + est > cap:
        raise SystemExit(f"BUDGET STOP: {provider} spent {s:.3f} + est {est:.3f} > cap {cap:.2f}")
    return s

def record(**e):
    e.setdefault("ts", datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return e

def summary():
    rows = {}
    for e in entries():
        k = (e.get("exp"), e.get("provider"), e.get("model"))
        r = rows.setdefault(k, {"n": 0, "est": 0.0, "actual": 0.0, "ok": 0})
        r["n"] += 1; r["est"] += e.get("est_cost") or 0; r["actual"] += e.get("actual_cost") or 0
        r["ok"] += 1 if e.get("status") == "ok" else 0
    return rows
