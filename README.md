# omnipoc

Google 影片生成 API 實測：Gemini Omni Flash vs Veo 3.1。

- 計劃 v0.3（Omni 尋寶開場）：`docs/PLAN-opening.md`（先讀這份）
- 計劃 v0.2（Omni vs Grok pilot，已執行）：`docs/PLAN.md` → 結果 `REPORT.md`
- 原始 handoff：`docs/handoff-v0.1.md`
- 花費帳本：`ledger/spend.jsonl`（開跑後才會有）

Secret 只從環境變數讀（`gemini_key` / `GEMINI_API_KEY`），不 commit、不印進 log。
