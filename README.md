# omnipoc

Google 影片生成 API 實測與婚禮微 MV。總花費 **$31.61**（Gemini $29.21、xAI $2.10、Modal 約 $0.30，截至 2026-11-13）。

**先讀 `REPORT.md` 第 0 節**：場景 → 做法結論表與花費總表。

## 文件
- `docs/wedding-mv-lessons.md` — 婚禮微 MV 的完整製作過程與 lessons learned（先讀這份）
- `docs/storyboard-wedding.md` — 5 分鐘愛情故事短片的完整分鏡（由 `prompts/wedding/storyboard.yaml` 經 `src/storyboard.py` 產生）
- `REPORT.md` — 總結、第一部分（Omni 1.2 vs Grok 1.5 盲測）、第二部分（Omni 尋寶開場 S0–S4）
- `docs/decisions.md` — 決策紀錄與踩坑規則
- `docs/PLAN-opening.md` — 計劃 v0.3（開場；S0–S4 已執行，S5–S6 未做）
- `docs/PLAN.md` — 計劃 v0.2（盲測；已執行）+ 市場盤點（第 7 節）
- `docs/handoff-v0.1.md` — 原始 handoff（其中 Veo 相關實驗已因 Veo 下架作廢）
- `ledger/spend.jsonl` — 每一筆付費呼叫

## 審片頁（純靜態，repo 內或 Artifact 連結）
- `review/index.html` — 盲測頁（Omni vs Grok）
- `review/opening/s0/` 定裝圖 · `review/opening/s1s3/` 草稿 · `review/opening/s4/` 定稿

## 程式
```
config.yaml                  # model IDs、價表、預算 cap（單一事實來源）
prompts/                     # 版本化 prompt；opening/ 尋寶片頭、wedding/ 婚禮短片
prompts/wedding/storyboard.yaml   # 婚禮分鏡單一事實來源 → src/storyboard.py 產生文件與 prompt 檔
prompts/wedding/trial-edl.yaml    # 試片剪接表；mv-edl.yaml = MV 剪接表（對歌詞時間）
src/run.py / run_image.py    # 影片／圖片生成：估價→cap→呼叫→落檔→ledger
src/storyboard.py            # 分鏡 YAML → docs/storyboard-wedding.md、videos/refs/stills.yaml、預算
src/check_look.py            # 參考圖服裝檢查（3.5 flash-lite）
src/check_faces.py           # 框臉放大的臉部檢查（3.8 flash）
src/check_motion.py          # 看整支影片找穿幫（3.8 flash；建議預設設定跑兩次）
src/check_video_frames.py    # 影片抽格做臉部／服裝檢查
src/check_decision.py        # Gemini Decision 1 粗篩（實驗，未採用）
src/cut_trial.py             # 依剪接表剪試片
src/cut_mv.py                # 依歌詞時間剪 MV、字幕、歌；--pieces-only / --pieces-dir 供 1080p 流程
src/modal_upscale.py         # Real-ESRGAN 放大（Modal T4，取自 theplaybillv2）
src/wedding_gallery.py       # 參考圖審片頁
src/spend.py / budget.py     # 花費統計、預算 cap
assets/fonts/LyricSerif.ttf  # 歌詞字型（Noto Serif TC/JP 子集，OFL）
runs/<exp>/<run_id>/         # 每次生成的 meta.json 與原檔
```

環境變數：`gemini_key`（Gemini）、`xai_key`（Grok，已不用）、`modal`／`modal_secret`（Modal，執行前設成 `MODAL_TOKEN_ID`／`MODAL_TOKEN_SECRET`）。Secret 不 commit、不印 log。

婚禮 MV 從頭重出（720p → 1080p）：

```bash
python3 src/cut_mv.py prompts/wedding/mv-edl.yaml review/wedding/mv/mv-720p.mp4
```

```bash
python3 src/cut_mv.py prompts/wedding/mv-edl.yaml review/wedding/mv/unused.mp4 --pieces-only
```

```bash
MODAL_TOKEN_ID="$modal" MODAL_TOKEN_SECRET="$modal_secret" modal run src/modal_upscale.py::batch --src-dir runs/mv-pieces --dst-dir runs/mv-pieces-1080
```

```bash
python3 src/cut_mv.py prompts/wedding/mv-edl.yaml review/wedding/mv/mv-1080p.mp4 --height 1080 --pieces-dir runs/mv-pieces-1080
```

```bash
python3 src/spend.py
```

## 接續點
- **婚禮完整 5 分鐘版**：剩 11 支、100 秒，約 $14（見 `docs/wedding-mv-lessons.md` 第 6 節）。流程見 `docs/storyboard-wedding.md` 第 1 節。
- **分享**：MV 1080p 上 YouTube（不公開）或放到 playbill 網站的 R2。
- 尋寶片頭的 S5／S6 仍未做（REPORT.md 第二部分第 4 節）。
