# REPORT — Omni 1.2 Flash vs Grok Imagine Video 1.5（M1 pilot）

- 日期：2026-11-07 · 計劃：`docs/PLAN.md` v0.2 方案 1 · 帳本：`ledger/spend.jsonl`
- 設定：文字生影片、720p、16:9、5 s、同一 prompt 原文、每題 **1 rep**
- 盲測頁：`review/index.html`（Clarence 尚未打分；下面的目視觀察是 Claude 看 6 格 contact sheet 寫的，**不是**盲測結果）

## 1. 花費（全部實際入帳或由 usage 推得）

| run_id | 模型 | prompt | 估價 | 實際 | 延遲 | 來源 |
|---|---|---|---|---|---|---|
| S0/xai-smoke-2f0a5942 | grok-imagine-video-1.5 | "test"（意外探針） | $0.400 | **$0.700** | ~40 s | `usage.cost_in_usd_ticks` |
| M0/omni_12-obj-compass-v1-r1-b427c6 | gemini-omni-1.2-flash（360p 3 s） | obj-compass-v1 | $0.070 | $0.075 | 16.4 s | usage tokens × 牌價 |
| M1/omni_12-obj-compass-v1-r1-1f8fa1 | gemini-omni-1.2-flash | obj-compass-v1 | $0.347 | $0.353 | 27.6 s | usage tokens × 牌價 |
| M1/omni_12-cine-redcoat-v1-r1-9ab089 | gemini-omni-1.2-flash | cine-redcoat-v1 | $0.347 | $0.356 | 30.4 s | usage tokens × 牌價 |
| M1/grok_15-obj-compass-v1-r1-77db01 | grok-imagine-video-1.5 | obj-compass-v1 | $0.700 | $0.700 | 46.9 s | `usage.cost_in_usd_ticks` |
| M1/grok_15-cine-redcoat-v1-r1-000135 | grok-imagine-video-1.5 | cine-redcoat-v1 | $0.700 | $0.700 | 46.9 s | `usage.cost_in_usd_ticks` |
| **合計** | | | | **$2.88**（Omni $0.78、xAI $2.10 含意外 $0.70） | | |

另有一筆 M0 失敗（HTTP 400，`store=false` 不能配 `delivery=uri`），未計費。

### 計費結論

- **Omni 1.2 的 usage 欄位完整**：`total_output_tokens`（全部是 `modality: video`）、`total_thought_tokens` 獨立列出、`total_input_tokens`。720p 5 s = 28,960 video tokens = 5,792 tok/s，**與價格頁完全一致**；360p 3 s = 5,793 = 1,931 tok/s，也一致。
- **thought tokens**：3 支分別 569 / 581 / 919。價格頁寫輸出價「including thinking tokens」，我先用文字輸出價 $9/1M 入帳（每支 < $0.01）。**待 Clarence 隔天對 AI Studio / Cloud Billing**，確認是 $9、$12 還是不另計；三種情況對 5 s 720p 的差異都在 1–2%。
- **Omni 實際 ≈ 牌價**：$0.353 vs 估 $0.347（+1.7%，就是 thought + input）。
- **Grok 1.5 的 720p 是 $0.14/s，不是文件的 $0.08/s**。三支 5 s 720p 都回 7,000,000,000 ticks = $0.70。文件的 $0.08/s 應是 480p。**同設定 Grok 是 Omni 的 2.0 倍價**。
- Grok 回應直接給 `usage.cost_in_usd_ticks`（1 tick = 1e-10 USD），對帳最省事；Omni 要自己乘。

## 2. 實際輸出規格（ffprobe）

| | Omni 1.2 | Grok 1.5 |
|---|---|---|
| 解析度 / fps | 1280×720 / 24 | 1280×720 / 24 |
| 實際長度 | 5.035 s | 5.042 s |
| 編碼 | h264 + aac 48 kHz 立體聲 | h264 + aac 48 kHz 立體聲（另附 mjpeg 封面軌） |
| 檔案大小 | 3.5–3.6 MB | 4.4–6.1 MB |
| 延遲（送出到拿到檔） | 27–30 s（同步 unary） | 47 s（送出 + 輪詢） |
| 音訊電平（volumedetect mean / max） | compass −33.8 / −2.2 dB；redcoat −29.9 / −7.8 dB | compass −38.3 / −26.0 dB；redcoat −25.4 / −11.9 dB |

兩邊都有真實音軌、不是靜音。Grok 的 compass 音軌很小聲（max −26 dB），Omni 的 compass 有一個 −2 dB 的峰值（可能是音效或音樂重音）。音訊內容要 Clarence 聽。

## 3. 目視觀察（Claude 看 contact sheet，n=1，非盲測）

### P1 obj-compass-v1（物件 hero，慢推）

| | Omni 1.2（盲測碼 D） | Grok 1.5（盲測碼 C） |
|---|---|---|
| 鏡頭 | 慢推 + 輕微 dolly，6 格內指南針從中景到占滿畫面 | 乾淨的慢推，進程均勻 |
| 風格 | 暖金色側光、有光束、地圖有海怪插畫與手寫地名、指南針刻花精細、紅色指針 | 低飽和冷灰褐、暗角重、地圖線條較素、整體「神秘」感較強 |
| 遵循 | 單鏡頭、慢推、指南針主體、塵土地圖、古老感：全中 | 同樣全中 |
| 備註 | 更「寶藏地圖」商品片味 | 更「懸疑片」味；畫面偏暗，細節在陰影裡 |

兩邊都完全遵循；差的是美術方向。這題分不出高下，要看 Clarence 偏好哪種 look。

### P2 cine-redcoat-v1（電影場景，GLBGPT 同題）

| | Omni 1.2（盲測碼 A） | Grok 1.5（盲測碼 B） |
|---|---|---|
| 場景解讀 | 現代都市夜街、霓虹招牌（含清楚的粉紅霓虹）、濕地面倒影明顯、現代低地板電車 | 歐洲老城石板街、復古紅色電車、「KAFFEE」霓虹字、路燈暖光、雨絲可見 |
| 動作 | 前 2 格側身走、第 3 格起轉向鏡頭、電車從背後橫過（第 3–6 格）；**「轉頭 + 電車過背景」兩個事件順序正確** | 全程大致面向鏡頭往前走，電車在身側／背後持續存在；「轉向鏡頭」的動作不明顯（本來就面向） |
| 一致性 | 臉、濕髮、紅大衣 6 格一致 | 臉、長捲髮、紅大衣一致；表情每格略變 |
| 運鏡 | 偏固定機位 + 小幅跟隨 | 後退跟拍（她朝鏡頭走），較符合「tracking shot follows」 |
| 景深 | 淺景深明顯，背景霓虹散景 | 淺景深明顯 |
| Checklist（8 項） | 8/8（「tracking shot」偏弱） | 7/8（「she turns toward the camera」存疑） |

**對照 GLBGPT 的描述**：他們說 Grok「kept the red coat, rain, neon street, and tram, with the tram clearly crossing behind the subject」，跟我們這支一致；他們說 Veo 3.1 的鏡頭「more static」，而我們 Omni 這支也是偏靜態機位。

## 4. 這次 $2.9 能說和不能說的

能說：
1. 同設定 **Grok 1.5 720p 單價是 Omni 1.2 的 2 倍**（$0.14 vs $0.07 /s），而且 Grok 文件上的單價會讓人低估。
2. Omni 的計費可完全從 usage 欄位重建，誤差 < 2%；thought tokens 有獨立欄位。
3. 兩邊對這兩個公開 prompt 的**遵循度都高**，沒有明顯翻車；差異主要在美術方向（Omni 偏明亮現代、Grok 偏暗調復古）。
4. 延遲 Omni 約 30 s、Grok 約 47 s（各 n=2）。

不能說：
- 哪個「畫質較好」——要等 Clarence 盲測，而且 n=1 連同模型自身變異都量不到。
- 對白 / lip-sync（P3 沒跑）、中文、參考圖一致性、編輯、延伸：都還沒測。

## 5. 建議的下一步（都要再花錢，先問）

- 若要下「預設用哪個」的結論：同兩題各加 2 reps（Omni +$1.40、Grok +$2.80）。
- 若要測 Grok 的強項：跑 P3 對白題一次（Omni $0.35、Grok $0.70）。
- 若要壓 Grok 成本：試 480p 一支確認是否真的 $0.40/5 s，再決定 480p 對照是否可接受。
