"""Build review/wedding/w1/index.html: every segment's reference images, shot list, voice-over,
look-check verdicts and the 360p test plan. Regenerate after changing the storyboard or refs.

usage: python3 src/wedding_gallery.py
"""
import json, os, subprocess, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "review", "wedding", "w1")

def main():
    os.chdir(ROOT); os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".jpg"): os.remove(os.path.join(OUT, f))
    d = yaml.safe_load(open("prompts/wedding/storyboard.yaml"))
    refs = {r["id"]: r for r in d["refs"]}; stills = {s["id"]: s for s in d["stills"]}
    checks = json.load(open("review/wedding/look-check.json")) if os.path.exists("review/wedding/look-check.json") else {}
    by_path = {v["path"]: v for v in checks.values()}
    spent = {}
    for l in open("ledger/spend.jsonl"):
        e = json.loads(l)
        if str(e.get("exp", "")).startswith("W") and e.get("status") == "ok":
            spent[e["exp"]] = spent.get(e["exp"], 0) + (e.get("actual_cost") or 0)
    files = {}
    def thumb(path, name):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vf", "scale='min(1280,iw)':-2", "-q:v", "4", f"{OUT}/{name}.jpg"], check=True)
        files[f"{name}.jpg"] = f"review/wedding/w1/{name}.jpg"
        return f"{name}.jpg"
    def badge(path):
        c = by_path.get(path)
        if not c: return ""
        if c["verdict"] == "pass": return '<span class="ok">造型檢查 ✓</span>'
        return '<span class="bad">造型檢查 ✗ ' + "；".join(m["attribute"] for m in c["mismatches"]) + "</span>"
    cards = []
    chars = [("refs/wedding/he-sheet.jpg", "he-sheet", "男主便服三視圖"), ("refs/wedding/she-sheet.jpg", "she-sheet", "女主便服三視圖"),
             ("refs/wedding/couple-casual.jpg", "couple-casual", "雙人便服"), ("refs/wedding/source/playbill-couple-4heads.png", "couple-wedding", "登記日服裝（playbill 定案）")]
    cards.append('<div class="card"><h2>角色設定（所有畫面都以這四張為準）</h2><div class="grid">' +
                 "".join(f'<figure><img src="{thumb(p, n)}" alt="{z}" loading="lazy"><figcaption>{z}</figcaption></figure>' for p, n, z in chars) + "</div></div>")
    test = d.get("test_shots", {}); test_ids = set(test.get("ids", []))
    for seg in d["segments"]:
        imgs, seen = [], []
        for sh in seg["shots"]:
            if sh["kind"] == "omni":
                for rid in sh["refs"]:
                    if refs[rid]["kind"] == "location" and rid not in seen:
                        seen.append(rid); imgs.append((refs[rid]["path"], rid, refs[rid]["zh"]))
            elif sh["kind"] == "still" and sh["id"] in stills and sh["id"] not in seen:
                seen.append(sh["id"]); imgs.append((stills[sh["id"]]["path"], sh["id"], stills[sh["id"]]["zh"]))
        figs = "".join(f'<figure><img src="{thumb(p, n)}" alt="{z}" loading="lazy"><figcaption>{z} {badge(p)}</figcaption></figure>' for p, n, z in imgs)
        shots = "".join(f'<li><code>{sh["id"]}</code> {sh["duration"]}s・{sh["zh"]}' + (' <b class="tag">360p 測試</b>' if sh["id"] in test_ids else "") + "</li>" for sh in seg["shots"])
        vo = "".join(f'<p class="vo">🎙 {v["speaker"]}（{v["tc"]}）：{v["text"]}</p>' for v in seg.get("vo", []))
        a, b = seg["tc"]
        cards.append(f'<div class="card"><h2>{seg["id"]} · {a}–{b} 秒 · {seg["title"]}</h2><p class="mut">{seg["board"]["picture"]}</p>{figs}<ul>{shots}</ul>{vo}</div>')
    P360 = 0.0243
    test_s = sum(sh["duration"] for seg in d["segments"] for sh in seg["shots"] if sh["id"] in test_ids)
    rows = "".join(f"<tr><td><code>{i}</code></td><td>{test['why'].get(i, '')}</td></tr>" for i in test.get("ids", []))
    n_pass = sum(1 for v in checks.values() if v["verdict"] == "pass"); total = sum(spent.values())
    html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>愛情短片 每幕參考圖</title>
<style>
:root {{ --bg:#fff; --fg:#111; --mut:#666; --card:#f6f6f6; --line:#ddd; --acc:#0b57d0; --tag:#e8f0fe; --ok:#137333; --bad:#c5221f; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#111; --fg:#eee; --mut:#aaa; --card:#1c1c1c; --line:#333; --acc:#8ab4f8; --tag:#1f2a44; --ok:#81c995; --bad:#f28b82; }} }}
:root[data-theme="dark"] {{ --bg:#111; --fg:#eee; --mut:#aaa; --card:#1c1c1c; --line:#333; --acc:#8ab4f8; --tag:#1f2a44; --ok:#81c995; --bad:#f28b82; }}
html, body {{ overflow-x:hidden; }}
body {{ margin:0; padding:16px; background:var(--bg); color:var(--fg); font:16px/1.6 system-ui,-apple-system,"Noto Sans TC",sans-serif; max-width:960px; margin-inline:auto; }}
h1 {{ font-size:1.3rem; margin:0 0 4px; }} h2 {{ font-size:1.05rem; margin:0 0 6px; }}
.mut {{ color:var(--mut); font-size:.88rem; margin:0 0 8px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px; margin:16px 0; }}
img {{ width:100%; border-radius:8px; display:block; }} figure {{ margin:0 0 10px; }} figcaption {{ font-size:.85rem; color:var(--mut); margin-top:4px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:8px; }}
ul {{ padding-left:18px; margin:6px 0; font-size:.92rem; }} code {{ font-size:.82rem; }}
.tag {{ background:var(--tag); color:var(--acc); border-radius:6px; padding:1px 6px; font-size:.78rem; font-weight:600; }}
.ok {{ color:var(--ok); font-weight:600; }} .bad {{ color:var(--bad); font-weight:600; }}
.vo {{ border-left:3px solid var(--acc); padding-left:10px; margin:8px 0 0; }}
table {{ width:100%; border-collapse:collapse; font-size:.92rem; }} td {{ border-top:1px solid var(--line); padding:6px 4px; vertical-align:top; }}
</style></head><body>
<h1>愛情短片・每一幕參考圖（{d["meta"]["version"]}）</h1>
<p class="mut">風格沿用 theplaybillv2。造型檢查：每張都用 gemini-3.5-flash-lite 和設定圖逐項比對（眼鏡、髮型、衣服、包、鞋、陶土質感），{n_pass}/{len(checks)} 張通過，另外人工看過一遍。參考圖累計花費 ${total:.2f}。地點來源見 refs/wedding/ATTRIBUTION.md。</p>
<div class="card"><h2>360p 測試：4 支，共 {test_s} 秒，估 ${test_s*P360:.2f}（等你說 go）</h2><table>{rows}</table>
<p class="mut">四支都以該幕參考圖當影片第一格，再附角色設定圖與風格錨點。生成後每支抽 3 格再做一次造型檢查。跑完約 ${total + test_s*P360 + 0.03:.2f}，婚禮預算上限 $5。</p></div>
{"".join(cards)}
</body></html>'''
    open(f"{OUT}/index.html", "w").write(html)
    json.dump(files, open(f"{OUT}/files.json", "w"), ensure_ascii=False)
    print(f"gallery ok: {len(files)} images, checks {n_pass}/{len(checks)}, spent ${total:.2f}")

if __name__ == "__main__":
    main()
