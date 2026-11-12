"""Render a storyboard YAML into a readable doc + pipeline prompt files, with validation and a cost estimate.

usage: python3 src/storyboard.py prompts/wedding/storyboard.yaml
outputs (next to the YAML unless noted):
  docs/storyboard-<name>.md   human-readable shot list
  videos.yaml                 for src/run.py --spec   (Omni shots, full prompts, ref paths)
  refs.yaml                   for src/run_image.py    (references to generate)
  refs-fallback.yaml          for src/run_image.py    (locations that should be real photos; generate only if none)
  stills.yaml                 for src/run_image.py    (still shots)
Reference images are expected at refs/<name>/<ref-id>.jpg.
"""
import json, os, sys, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "ledger", "spend.jsonl")

# --- unit prices: measured from our own ledger where possible -----------------------------------------
def measured_per_s(res, fallback):
    tot_cost = tot_s = 0.0
    if os.path.exists(LEDGER):
        for l in open(LEDGER):
            e = json.loads(l)
            p = e.get("params") or {}
            if e.get("model") == "gemini-omni-1.2-flash" and e.get("status") == "ok" and p.get("resolution") == res \
               and e.get("actual_cost") is not None:
                tot_cost += e["actual_cost"]; tot_s += p["duration_s"]
    return (round(tot_cost / tot_s, 4), "measured") if tot_s else (fallback, "list price")

P360, P360_SRC = measured_per_s("360p", 0.0232)
P720, P720_SRC = measured_per_s("720p", 0.0695)
P1080 = round(0.1043 * P720 / 0.0695, 4)          # list $0.104/s scaled by our measured 720p overhead
IMG_1K = 0.0673                                   # measured on O0 (Nano Banana 2, 1K)
IMG_TRIES = 2
TTS_PER_S = 25 * 9.0 / 1e6                         # gemini-3.8-flash-tts: 25 audio tok/s, $9/1M (through 2026)
TTS_CHARS_PER_S = 4.5                              # rough speaking rate for Mandarin
TTS_TRIES = 3
LYRIA = {"lyria-3.5": 0.08, "lyria-3-clip-preview": 0.04}
LYRIA_TRIES = 2

def fail(msg):
    raise SystemExit(f"storyboard error: {msg}")

def main(path):
    sb = yaml.safe_load(open(path))
    name = os.path.basename(os.path.dirname(os.path.abspath(path)))
    out_dir = os.path.dirname(os.path.abspath(path))
    meta, chars = sb["meta"], sb["characters"]
    refs = {r["id"]: r for r in sb["refs"]}
    stills = {s["id"]: s for s in sb["stills"]}
    ref_path = lambda rid: refs[rid]["path"]

    # ---------- validation ----------
    t = 0
    for seg in sb["segments"]:
        a, b = seg["tc"]
        if a != t: fail(f"segment {seg['id']} starts at {a}, expected {t}")
        t = b
        for sh in seg["shots"]:
            if sh["kind"] == "omni":
                if not (3 <= sh["duration"] <= 15): fail(f"{sh['id']} duration {sh['duration']} outside 3–15 s")
                if len(sh["refs"]) > 6: fail(f"{sh['id']} has {len(sh['refs'])} refs (max 6)")
                for who in chars:
                    n = sum(1 for r in sh["refs"] if refs.get(r, {}).get("who") == who)
                    if n > 3: fail(f"{sh['id']} has {n} refs for {who} (max 3 per character)")
                for r in sh["refs"]:
                    if r not in refs: fail(f"{sh['id']} references unknown ref {r}")
            if sh["kind"] == "still" and sh["id"] not in stills: fail(f"still {sh['id']} not defined in stills")
    if t != meta["duration_s"]: fail(f"timeline ends at {t}, expected {meta['duration_s']}")

    # ---------- prompt assembly ----------
    def describe(ref):
        k = ref["kind"]
        if k == "character":
            return f"{chars[ref['who']]['label']}'s character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit"
        if k == "couple":
            return "the couple in the outfits for this scene: keep exactly these faces, hairstyles and outfits"
        if k == "style":
            return "the approved art style: sculpted matte clay figurines placed in a painted storybook set"
        return "the location, lighting and art direction for this scene: match this place"

    def full_prompt(sh):
        lines, present = [], []
        parts = [f"image {i} shows {describe(refs[r])}" for i, r in enumerate(sh["refs"], 1)]
        if parts:
            lines.append("Reference images, in order: " + "; ".join(parts) + ".")
        for r in sh["refs"]:
            ref = refs[r]
            whos = [ref["who"]] if ref["kind"] == "character" else (list(chars) if ref["kind"] == "couple" else [])
            for w_ in whos:
                if w_ not in present: present.append(w_)
        for who in present:
            lines.append(f"{chars[who]['label'].capitalize()} is {chars[who]['en']}.")
        lines.append(" ".join(sb["style"].split()))
        lines.append(" ".join(sh["prompt"].split()))
        lines.append(f"Audio: only ambient sound — {sh['ambient']}. {sb['audio_rule']}")
        return " ".join(lines)

    videos, n_omni, omni_s = [], 0, 0
    for seg in sb["segments"]:
        for sh in seg["shots"]:
            if sh["kind"] == "omni":
                n_omni += 1; omni_s += sh["duration"]
                videos.append({"id": sh["id"], "duration": sh["duration"], "text": full_prompt(sh),
                               "refs": [ref_path(r) for r in sh["refs"]]})

    def img_spec(x, size="1K"):
        d = {"id": x["id"], "aspect": x.get("aspect", "16:9"), "size": size, "text": " ".join(x["prompt"].split())}
        paths = list(x.get("from_paths", [])) + [ref_path(r) for r in x.get("from", [])]
        if paths: d["refs"] = paths
        if x.get("path"): d["out"] = x["path"]
        return d
    gen_refs = [img_spec(r) for r in sb["refs"] if r.get("status") == "todo"]
    still_specs = [img_spec(s) for s in sb["stills"]]
    for r in sb["refs"]:
        if r.get("status") == "done" and not os.path.exists(os.path.join(ROOT, r["path"])):
            fail(f"ref {r['id']} marked done but {r['path']} is missing")

    hdr = f"# GENERATED by src/storyboard.py from {os.path.relpath(path, ROOT)} — do not edit by hand\n"
    def dump(fname, key, items, extra=""):
        with open(os.path.join(out_dir, fname), "w") as f:
            f.write(hdr + extra)
            yaml.safe_dump({"version": meta["version"], key: items}, f, allow_unicode=True, sort_keys=False, width=1000)
    dump("videos.yaml", "videos", videos)
    dump("refs.yaml", "images", gen_refs)
    dump("stills.yaml", "images", still_specs)

    # ---------- cost ----------
    d, f = meta["drafts_per_shot"], meta["finals_per_shot"]
    c_draft = omni_s * d * P360
    c_720 = omni_s * f * P720
    c_1080 = omni_s * f * P1080
    n_imgs = len(gen_refs) + len(still_specs)
    c_img = n_imgs * IMG_1K * IMG_TRIES
    vo_lines = [v for seg in sb["segments"] for v in seg.get("vo", [])]
    vo_chars = sum(len(v["text"]) for v in vo_lines)
    c_tts = vo_chars / TTS_CHARS_PER_S * TTS_PER_S * TTS_TRIES
    c_music = sum(LYRIA[m["model"]] for m in sb["music"]) * LYRIA_TRIES
    base = c_draft + c_img + c_tts + c_music
    total_720, total_1080 = base + c_720, base + c_1080

    # ---------- markdown ----------
    L = []
    w = L.append
    w(f"# 分鏡完整描述 — {meta['title']}（{meta['version']}）\n")
    w(f"> 由 `src/storyboard.py` 從 `{os.path.relpath(path, ROOT)}` 產生，改內容請改 YAML 後重跑。")
    w(f"> 原始分鏡由 Clarence 提供；本文件補上每個鏡頭的製作方式、Omni prompt、參考圖、聲音與字幕時間。\n")
    w("## 0. 總覽\n")
    w("| 項目 | 數值 |\n|---|---|")
    w(f"| 片長 | {meta['duration_s']} 秒，{len(sb['segments'])} 段 |")
    w(f"| Omni 影片鏡頭 | {n_omni} 支，共 {omni_s} 秒（單支 3–15 秒） |")
    w(f"| 圖片鏡頭 | {len(still_specs)} 張（Ken Burns／合成底圖） |")
    w(f"| 參考圖 | {len(sb['refs'])} 張（已完成 {sum(1 for r in sb['refs'] if r.get('status')=='done')}、待生成 {len(gen_refs)}） |")
    w(f"| 旁白／口白 | {len(vo_lines)} 句，TTS（{sb['tts_model']}） |")
    w(f"| 配樂 | {len(sb['music'])} 段 Lyria |")
    w(f"| 輸出 | {meta['aspect']}，草稿 {meta['draft_res']}，定稿 {meta['final_res']} |\n")
    w("**估價（美金）**\n")
    w("| 項目 | 算法 | 費用 |\n|---|---|---|")
    w(f"| Omni 草稿 | {omni_s} 秒 × {d} 支 × ${P360}/s（360p，{P360_SRC}） | ${c_draft:.2f} |")
    w(f"| Omni 定稿 720p | {omni_s} 秒 × {f} 支 × ${P720}/s（{P720_SRC}） | ${c_720:.2f} |")
    w(f"| 參考圖＋圖片鏡頭 | {n_imgs} 張 × {IMG_TRIES} 次 × ${IMG_1K} | ${c_img:.2f} |")
    w(f"| TTS | 約 {vo_chars} 字 ÷ {TTS_CHARS_PER_S} 字/秒 × {TTS_TRIES} 次 | ${c_tts:.2f} |")
    w(f"| 配樂 | Lyria × {LYRIA_TRIES} 次 | ${c_music:.2f} |")
    w(f"| **合計（720p 定稿＋本機放大到 1080p）** | | **${total_720:.2f}** |")
    w(f"| 合計（改用 Google 1080p 定稿，${P1080}/s） | | ${total_1080:.2f} |")
    w("")
    w("估價假設每支影片 2 支 360p 草稿、平均 1.2 支定稿；草稿和定稿是分開生成的兩支，不是把草稿放大。單價取自 `ledger/spend.jsonl` 的實測。\n")

    w("## 1. 製作流程\n")
    w("1. **參考圖**：角色取自 theplaybillv2 定案人物，用 Nano Banana 2 出便服三視圖；地點用維基共享資源的 CC 照片轉繪成同一風格；缺照片的地點直接生成（`prompts/" + name + "/refs.yaml`）。")
    w("2. **草稿**：每支 Omni 鏡頭用 360p 跑 2 支（`python3 src/run.py --exp W1 --model omni_12 --spec prompts/" + name + "/videos.yaml --res 360p`），挑方向。")
    w("3. **定稿**：選定的鏡頭用同一組 prompt 和參考圖跑 720p；每支過 `cropdetect` 檢查 letterbox。")
    w("4. **圖片鏡頭與圖形**：`stills.yaml` 出圖；聊天泡泡、字幕、拍立得、心型、Married! 都在後製做，不讓 Omni 寫字。")
    w("5. **聲音**：Omni 只留環境音（每支 prompt 已禁止對白與音樂）；旁白用 TTS，配樂用 Lyria，ffmpeg 混音並在旁白下 ducking。")
    w("6. **組裝**：ffmpeg 依本文件的時間軸剪接、疊字、混音，最後放大到 1080p。\n")

    w("## 2. 全片設定\n")
    w("**風格（自動附加到每支 Omni prompt）**\n")
    w("```text\n" + " ".join(sb["style"].split()) + "\n```\n")
    w("**角色**\n")
    for k, c in chars.items():
        w(f"- **{k}**：{c['zh']}")
    w("\n**聲音角色（TTS）**\n")
    for k, v in sb["voices"].items():
        w(f"- **{k}**：{v}")
    w("\n**字型**\n")
    for ft in sb["fonts"]:
        w(f"- {ft['use']}：{ft['name']}（{ft['license']}）")
    w("\n**參考圖清單**\n")
    w("| id | 類型 | 內容 | 檔案 | 狀態 |\n|---|---|---|---|---|")
    kz = {"character": "角色", "couple": "雙人", "style": "風格", "location": "地點"}
    for r in sb["refs"]:
        w(f"| `{r['id']}` | {kz[r['kind']]} | {r.get('zh','')} | `{r['path']}` | {'已完成' if r.get('status')=='done' else '待生成'} |")
    w("\n地點照片來源與授權見 `refs/" + name + "/ATTRIBUTION.md`。\n")

    w("## 3. 逐段分鏡\n")
    for seg in sb["segments"]:
        a, b = seg["tc"]
        w(f"### {seg['id']} · {a}–{b} 秒 · {seg['title']}\n")
        bd = seg["board"]
        w(f"- **原分鏡畫面**：{bd['picture']}")
        w(f"- **劇情／字幕／旁白**：{bd['story']}")
        w(f"- **鏡頭運動與轉場**：{bd['camera']}")
        w(f"- **音樂／環境音**：{bd['sound']}\n")
        w("| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |\n|---|---|---|---|---|---|")
        for sh in seg["shots"]:
            kind = {"omni": "Omni 影片", "still": "圖片（Ken Burns）", "freeze": "定格（ffmpeg）"}[sh["kind"]]
            cost = f"${sh['duration']*(d*P360 + f*P720):.2f}" if sh["kind"] == "omni" else ("$0.13" if sh["kind"] == "still" else "$0")
            rr = ", ".join(f"`{r}`" for r in sh.get("refs", [])) or "—"
            w(f"| `{sh['id']}` | {kind} | {sh['duration']} | {sh['use']} | {rr} | {cost} |")
        w("")
        for sh in seg["shots"]:
            w(f"**`{sh['id']}`**：{sh['zh']}\n")
            if sh["kind"] == "omni":
                w("<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>\n")
                w("```text\n" + full_prompt(sh) + "\n```\n</details>\n")
            elif sh["kind"] == "still":
                w("<details><summary>Nano Banana prompt</summary>\n")
                w("```text\n" + " ".join(stills[sh["id"]]["prompt"].split()) + "\n```\n</details>\n")
        layer = []
        for v in seg.get("vo", []):
            layer.append(f"| {v['tc']} | 旁白／口白（{v['speaker']}） | {v['text']} | TTS 語氣：{v['style']} |")
        for c in seg.get("captions", []):
            layer.append(f"| {c['tc']} | 字幕 | {c['text']} | {c['where']} |")
        for g in seg.get("gfx", []):
            layer.append(f"| {g['tc']} | 圖形 | {g['text']} | {g['where']} |")
        for o in seg.get("overlays", []):
            layer.append(f"| | 疊加動畫 | {o} | |")
        for s in seg.get("sfx", []):
            layer.append(f"| | 音效 | {s} | |")
        if seg.get("music"):
            layer.append(f"| | 配樂 | {seg['music']} | |")
        if layer:
            w("| 時碼 | 層 | 內容 | 說明 |\n|---|---|---|---|")
            for x in layer: w(x)
            w("")
        if seg.get("edit"):
            w(f"**剪接**：{seg['edit']}\n")
        for n in seg.get("notes", []):
            w(f"> ⚠️ {n}\n")

    w("## 4. 聲音總表\n")
    w("**旁白／口白（TTS）**\n")
    w("| 時碼 | 聲音 | 台詞 | 語氣 |\n|---|---|---|---|")
    for seg in sb["segments"]:
        for v in seg.get("vo", []):
            w(f"| {v['tc']} | {v['speaker']} | {v['text']} | {v['style']} |")
    w("\n**配樂（Lyria）**\n")
    w("| cue | 時碼 | 模型 | prompt |\n|---|---|---|---|")
    for m in sb["music"]:
        w(f"| {m['id']} | {m['tc']} | `{m['model']}` | {m['prompt']} |")
    w("\n**字幕與圖形**\n")
    w("| 時碼 | 內容 | 位置／樣式 |\n|---|---|---|")
    for seg in sb["segments"]:
        for c in seg.get("captions", []) + seg.get("gfx", []):
            w(f"| {c['tc']} | {c['text']} | {c['where']} |")
    w("")

    w("## 5. 風險\n")
    w("- **兩個角色 × " + str(n_omni) + " 支的一致性還沒驗證。** 靜態參考圖已經一致；影片端只證明過 1 個角色加 1 個道具。建議先用 360p 跑 3–4 支雙人鏡頭確認。")
    w("- **風格漂移。** 只拿空景當風格參考時，人物會變成平面插畫；每支都要附 `style-clay`（陶土人物在場景裡的畫面）。")
    w("- **畫面中文字。** Omni 會把招牌、證書、校名寫錯；prompt 已要求無字，所有中文字一律後製。")
    w("- **正面說話的戲。** 全片人物不開口（沿用 playbill 的閉嘴微笑）；台詞全由 TTS 旁白承接。")
    w("- **Letterbox 黑邊。** prompt 禁止無效，定稿每支都要 `cropdetect`，有黑邊就裁切或全片統一加黑邊。")
    w("- **分割畫面裁切。** 第 2 段兩支要裁成窄條，動作必須留在中間三分之一。\n")

    w("## 6. 待決問題\n")
    for q in sb["open_questions"]:
        w(f"- {q}")
    w("")

    doc = os.path.join(ROOT, "docs", f"storyboard-{name}.md")
    open(doc, "w").write("\n".join(L))
    print(f"ok: {n_omni} omni shots / {omni_s}s; images to make {n_imgs}")
    print(f"cost 720p total ${total_720:.2f} | google 1080p total ${total_1080:.2f} | P360 {P360} ({P360_SRC}) P720 {P720} ({P720_SRC})")
    print(f"wrote {os.path.relpath(doc, ROOT)} and {os.path.relpath(out_dir, ROOT)}/{{videos,refs,stills}}.yaml")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "prompts", "wedding", "storyboard.yaml"))
