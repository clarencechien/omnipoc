# 決策紀錄

| 日期 | 決策 | 原因 | 影響 |
|---|---|---|---|
| 2026-11-07 | 不走 Veo，改比 Omni 1.2 vs Grok 1.5 | Veo 3.1 已從 Gemini API 下架；Clarence 指示 | handoff E0–E8 的 Veo 相關實驗全部作廢 |
| 2026-11-07 | xAI 直連、不走 OpenRouter | OpenRouter 無 xAI 影片模型；直連才有原生 usage | `or_key` 未使用 |
| 2026-11-07 | 盲測對照用 720p / 5 s / 16:9、每題 1 rep | $1 預算只買得起；畫質欄需同解析度 | 結論只算觀察 |
| 2026-11-07 | 停止比 xAI，轉做 Omni-only 尋寶開場 | Clarence 看過盲測後指示 | Grok client 保留不用 |
| 2026-11-07 | 開場做遊戲 title sequence、風格 1 實拍、cap $8 | Clarence 選 | 2D／3D 定裝圖保留在 S0 |
| 2026-11-07 | 指南針一律「先 Nano Banana 出參考圖再餵 Omni」 | S2 三種做法中 2 張參考最穩，純文字會錯字 | S3、S4 全部採用 |
| 2026-11-07 | 海面＋船艙用一支 15 s timecode 而非兩支 | 切點準、調色一致、價格相同 | S4 採用 |
| 2026-11-07 | 標題、字幕、地圖段不用影片 | 按秒計費且畫面文字不可靠 | S6 走 ffmpeg + Nano Banana |
| 2026-11-07 | 1080p 走本機放大而非 Google 重生成（暫定） | Google 的 1080p 本身是 upsampling，API 無升級既有影片操作 | S5 未實測，暫定 |
| 2026-11-07 | 做到 S4 告一段落 | Clarence 指示；opening 用了 $4.64 / $8 | S5、S6 待續 |

## 規則（踩坑後新增）
- 探 API schema 只送無效值，永遠不送合法 body（2026-11-07 xAI 意外 $0.70）。
- Omni `delivery=uri` 必須 `store=true`。
- 每支影片過 `cropdetect`，ffprobe 看不出 letterbox。
- 估價 → ledger → 呼叫 → 落檔 → 下一筆；失敗 4xx 不計費但要記。
