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
config.yaml              # model IDs、價表、預算 cap（單一事實來源）
prompts/                 # 版本化 prompt；opening/ 下是開場用
src/run.py               # 影片：--prompt 單支 或 --spec 批次；估價→cap→呼叫→落檔→ledger
src/run_image.py         # 圖：Nano Banana 2 批次
src/spend.py             # 累計花費（按實驗 × 模型）
src/storyboard.py        # 分鏡 YAML → 文件 + videos/refs/stills prompt 檔 + 估價
src/budget.py            # 估價、ledger、cap
src/probe.py             # ffprobe
src/clients/omni.py      # Omni Interactions API（含參考圖、delivery=uri）
src/clients/image.py     # gemini-3.1-flash-image（Interactions API）
src/clients/xai.py       # Grok Imagine（保留，不再使用）
runs/<exp>/<run_id>/     # meta.json 進 repo，影片 gitignore
```

執行需要環境變數 `gemini_key`（或 `GEMINI_API_KEY`）。Secret 不 commit、不印 log。

```bash
python3 src/run.py --exp O4 --model omni_12 --spec prompts/opening/s4.yaml --res 720p --only s4-hunter
```

```bash
python3 src/spend.py
```

## 接續點
- S5：1080p 對照（Google 重生成 vs 本機 lanczos／Real-ESRGAN），約 $0.62。
- S6：組裝（Lyria 3.5 配樂 $0.08、ffmpeg 字卡、地圖 Ken Burns、混音、letterbox 統一）。定稿素材清單在 REPORT.md 第二部分第 4 節。
