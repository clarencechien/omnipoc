# omnipoc 計劃 v0.2 — Omni 1.2 vs Grok Imagine 1.5，各約 US$1

- 日期：2026-11-07
- 取代 v0.1 的實驗設計（v0.1 的「Veo 路徑選擇」作廢；市場盤點保留在第 5 節）
- 已花：**$0.70**（一次意外的 xAI 探針，見第 2 節；`ledger/spend.jsonl` 第 1 筆）
- 需求（Clarence 2026-11-07）：只測 Omni 1.2 vs xAI；用 env 的 key；各花 US$1 左右；prompt 從「商品」到「電影場景」，拿別人做過的 prompt 或評測。

---

## 0. 結論先講

| 項目 | 決定 |
|---|---|
| 對照組 | `gemini-omni-1.2-flash`（Gemini key，直連 Interactions API）vs `grok-imagine-video-1.5`（`xai_key`，直連 xAI Videos API） |
| 為什麼不走 OpenRouter | `or_key` 可用（剩 $5.05 額度），OpenRouter 有 `google/gemini-omni-1.2-flash`，但**沒有任何 xAI 影片模型**；且走中介拿不到 Google 原生 usage。Omni 直連、xAI 直連最乾淨。 |
| 對齊條件 | 720p、16:9、5 s、文字生影片、同一 prompt 原文 |
| 預算 | Omni ≤ $1.10、xAI ≤ $1.10（不含已花的 $0.70）；超過停 |
| 建議版本（二選一，見第 3 節） | **方案 1**：2 個 prompt（商品 hero + 電影場景）× 720p × 5 s，Omni $0.70、Grok $1.40 |

**關鍵價格發現**：xAI 牌價 `$0.080/s` 是 480p；實測 **720p 是 $0.14/s**（5 s = $0.70，回應的 `usage.cost_in_usd_ticks: 7000000000`，1 tick = 1e-10 USD）。所以同樣 720p 5 s，Grok 1.5 是 Omni 1.2 的 **2 倍價**（$0.70 vs $0.35）。這個數字本身就是結論之一。

---

## 1. 兩邊 API 事實（本輪免費探針 + 文件）

| | Gemini Omni 1.2 Flash | Grok Imagine Video 1.5 |
|---|---|---|
| Model ID | `gemini-omni-1.2-flash`（`GET /models` 有列） | `grok-imagine-video-1.5`（alias `-preview`、`-2026-05-30`；`GET /v1/video-generation-models` 列 input `text,image,audio`） |
| 端點 | `POST /v1beta/interactions`，`response_format: {type: video, duration, resolution, aspect_ratio}` | `POST /v1/videos/generations` → `request_id`；`GET /v1/videos/{id}` 輪詢到 `status: done`，`video.url` |
| 長度 | 3–15 s 整秒（探針證實上限 15） | 1–15 s（探針證實） |
| 解析度 | `360p` `720p`(預設) `1080p`/`4k`(upscale) | `480p` `720p` `1080p`（422 錯誤訊息列出） |
| 比例 | `16:9` `9:16` | `1:1 16:9 9:16 4:3 3:4 3:2 2:3 21:9 5:2` |
| 音訊 | 原生 | 原生（smoke 檔有 AAC 48k 立體聲） |
| 牌價 720p | $0.07/s（5,792 tok/s × $12/1M；thinking 計入輸出） | **$0.14/s 實測**（文件只寫 $0.08/s，未標解析度） |
| 計費回饋 | 預期回 usage tokens（M0 驗證） | `usage.cost_in_usd_ticks`（直接給美元，很好用） |
| 實際輸出（smoke） | 待測 | 1280×720、24 fps、5.04 s、h264+aac、7.0 MB |
| 不支援 | temperature / system prompt / negative prompt | 文件未列 seed |
| 語言 | 官方只評估英文 | 未說明 |
| 地區 | sandbox 出口美國，無 EEA 限制 | 同 |

---

## 2. 已花的 $0.70（意外，記錄在案）

探 xAI 欄位時我送了四個 body：前三個故意無效（duration 999、resolution bogus、aspect bogus），拿到 400/422 並得到允許值；**第四個 body 是合法的**（只多塞一個未知欄位 `bogus_field`，被忽略），端點直接受理並生成。結果：

- `runs/S0/xai-smoke-2f0a5942/`：`meta.json`（已 commit）+ `video.mp4`（gitignore）
- `ledger/spend.jsonl` 第 1 筆：est $0.40、actual **$0.70**
- 收穫：xAI 回應 schema、720p 真實單價、ffprobe 規格。它就是 xAI 的 M0 smoke，**不再另跑**。
- 教訓寫進規則：探 schema 一律用無效值，**永遠不送合法 body**。

---

## 3. 實驗設計（二選一）

### 方案 1（建議）：公平對齊，2 個 prompt

| prompt | 類型 | Omni 1.2 720p 5 s | Grok 1.5 720p 5 s |
|---|---|---|---|
| P1 商品 / 物件 hero | 官方 Veo prompt guide 例句 | $0.35 | $0.70 |
| P2 電影場景 | GLBGPT 六模型同題測試 Prompt 1 | $0.35 | $0.70 |
| 小計 | | **$0.70** | **$1.40** |

- 加上已花 $0.70 → xAI 共 $2.10。超過「各 $1」，但這是唯一不混淆畫質評分的做法。
- 若要壓回 $1：Grok 改 4 s（$0.56 × 2 = $1.12），Omni 同步 4 s（$0.56）。4 s 對電影場景偏短，但可接受。

### 方案 2：3 個 prompt，Grok 降到 480p

| prompt | Omni 1.2 720p 5 s | Grok 1.5 480p 5 s（假設 $0.08/s，**未驗證**） |
|---|---|---|
| P1 商品 hero | $0.35 | $0.40 |
| P2 電影場景 | $0.35 | $0.40 |
| P3 對白 + 原生音訊 | $0.35 | $0.40 |
| 小計 | **$1.05** | **$1.20** |

- 多一個「人物對白 lip-sync」題（Grok 評測常被說強項），但 480p vs 720p **畫質欄不能比**，只能比遵循度、運鏡、音訊。
- 480p 單價是推測（文件 $0.08/s 沒標解析度），第一支跑完若不是 $0.40 就停。

### 兩案共用

- 每題 **1 rep**（$1 買不到 3 reps）。報告會明寫 n=1，只做「觀察」不下「結論」；若兩邊差異明顯到 n=1 也能看出，才寫。
- 順序：Omni M0 smoke（360p 3 s，$0.07，拿 usage 欄位）→ P1 兩邊 → P2 兩邊 →（方案 2 的 P3）。每支跑完先落檔、記 ledger、印累計。
- 預算斷路：Omni 累計 > $1.10 或 xAI 新增 > $1.50（方案 1）/ $1.30（方案 2）就停。

---

## 4. Prompt（都是別人公開用過的，原文照抄，版本化到 `prompts/`）

### P1 `obj-compass-v1` — 物件 hero / 商品型鏡頭
> A slow, dramatic zoom in on a mysterious, ancient compass lying on a dusty map.

來源：Google Cloud 官方 Veo prompt guide「Camera movements」例句。沒有商業商品字眼但就是「單一物件 + 慢推 + 質感」的商品 hero 結構。
**為什麼不用 handoff p01**：Clarence 要「別人做過的」。p01 留作後續正式跑。

### P2 `cine-redcoat-v1` — 電影場景（第三方六模型同題）
> A cinematic tracking shot follows a woman in a long red coat walking through a rain-soaked neon street at night. She turns toward the camera as a tram passes behind her, reflections moving naturally across the wet pavement. Realistic human motion, consistent face and clothing, shallow depth of field, controlled handheld camera, no cuts.

來源：GLBGPT「AI Video Prompt Adherence Comparison」Prompt 1，他們用 5 s / 720p / 16:9 跑過 Wan 3.0、Kling 3.0、Seedance 2.5、**Grok Imagine**、Happy Horse、Veo 3.1。我們用**完全相同設定**，所以可以跟他們對 Grok 的觀察（紅大衣、電車過背景有做到）直接對照。

### P3 `dlg-train-v1` — 對白 + 原生音訊（方案 2 才跑）
> Inside a quiet train compartment, a woman says, "We missed the last stop." A man across from her replies, "Then we ride to the end." Keep the two voices distinct, synchronize each line to the correct speaker, include subtle train ambience and wheel sounds, and do not add music.

來源：同上 Prompt 4（他們跑了 Grok，說兩人同框但音訊未細評）。

### 備用（不跑，列著）
- GLBGPT Prompt 3 複雜運鏡（單車衝下地中海市場，低角→側→俯瞰）：他們說 Grok 運鏡路徑最完整。
- VBench-2.0 物理題：「A clear glass of oil is gently poured into a glass of milk.」「A sturdy steel key is dropped onto a hard marble floor」。
- Omni 官方文件例句：「A single unbroken tracking shot following a paper airplane gliding through a bustling library.」

---

## 5. 評分與產出

- 自動：ffprobe（實際秒數、解析度、fps、音軌）、檔案大小、延遲、實際費用 vs 估價。
- 人評（Clarence，盲測頁隨機、藏模型名）：畫質、prompt 遵循（P2 有 checklist：紅大衣／雨夜霓虹／轉頭／電車過背景／倒影／無剪接）、動作物理、音訊，各 1–5。
- 影片放 `review/media/` 360p 預覽（總量 < 20 MB）進 repo，`review/index.html` 純靜態。
- `REPORT.md`：費用表（實際 vs 牌價，含 Grok 720p = 2× Omni 的發現）、每題兩邊觀察、對照 GLBGPT 的 Grok 描述、「n=1 的限制」。

---

## 6. 執行順序

1. Clarence 選方案 1 或 2（或說「方案 1 改 4 s」）。
2. 建 `config.yaml`、`prompts/*.yaml`、`src/`（omni / xai client、budget、probe、run）。
3. Omni M0 smoke（$0.07）→ 看 usage 欄位 → 回報一行。
4. 跑矩陣，每支記 ledger。
5. 盲測頁 → Clarence 打分 → REPORT.md。

停下來問：任何一支實際費用與估價差 > 30%；xAI 480p 單價不是 $0.40/5 s；任一端回地區／審核錯誤；預算斷路觸發。

---

## 7. 市場盤點（v0.1 原文保留，供背景）

來源等級：**官** = 官方文件/價格頁本輪抓到；**三** = 第三方整理；**驗** = 本輪免費 API 呼叫驗證。

### 7.1 仍在線、可直接用的（排除中國廠商）

| 廠商 / 模型 | 存取方式 | 牌價（720p 含音訊，/s） | 單支長度 | 音訊 | 特色 / 限制 | 等級 |
|---|---|---|---|---|---|---|
| Google Gemini Omni 1.2 Flash | Gemini API Interactions；OpenRouter 也有 | $0.07（360p $0.023；1080p/4K upscale $0.104/$0.209） | 3–15 s | 原生 | 多輪編輯、extend 到 30 s、6 張參考圖、timecode、畫面文字；無 temperature/negative prompt；官方只評估英文；thinking 計入輸出價 | 官 + 驗 |
| Google Gemini Omni 1.1 Flash | 同上 | $0.10 | 3–10 s | 原生 | 2026-12-03 起自動導流到 1.2 | 官 + 驗 |
| Google Veo 3.1 / Fast / Lite | **只剩 Vertex**（us-central1）或 Runway / Replicate / fal 轉售；Gemini API 三個 preview ID 已 2026-10-22 下架 | $0.40 / $0.15 / $0.05（Runway 價格頁；Vertex 頁 JS 擋抓） | 4/6/8 s | 原生 | 首尾幀、extension、reference images（Lite 不支援）、4K（Standard） | 官 |
| xAI Grok Imagine Video 1.5 / 1.5 Lite / 1.0 | xAI API | 文件 $0.08 / $0.02 / $0.05（未標解析度）；**1.5 720p 實測 $0.14** | 1–15 s | 原生 | 480p/720p/1080p、9 種比例、14 張參考圖、3 段聲音參考；評測說 talking head 強；Arena Elo 墊底 | 官 + 驗 |
| Runway Gen-4.5 / Gen-4 Turbo / Aleph 2 / Act-Two | Runway Dev API（$0.01/credit） | $0.12 / $0.05 / $0.28 / $0.05 | 2–10 s | 否（Gen-4.5） | 鏡頭控制、video-to-video、表演驅動；平台也轉售 Veo、Omni、Grok | 官 |
| Luma Ray3.14 / Ray3.2 | Dream Machine / Luma Agents API | 第三方 720p 約 $0.06–0.09 | 5–10 s | 部分 | HDR、專業後製 | 三 |
| Pika 2.x | Pika API | 約 $0.12 | ≤5 s | — | 特效類 | 三 |
| Adobe Firefly Video | Firefly Services API | credits 計 | — | — | 商業安全／版權賠償 | 三 |
| Lightricks LTX-2 | 自家 API 或開放權重 | fal $0.0018/megapixel | — | 有 | 自架最便宜 | 三 |
| Genmo Mochi | 開放權重 | 自架 | — | 無 | 研究用 | 三 |

### 7.2 已下架：OpenAI Sora 2 API（2026-09）、Amazon Nova Reel（2026-09-30 EOL）、Veo 3.1 Preview on Gemini API、`gemini-omni-flash-preview`（2026-10-22）。
### 7.3 排除（中國廠商）：Kling、Seedance、Hailuo/MiniMax、Wan、Vidu、Hunyuan。

### 7.4 場景 → 模型（第三方評測推論，未自測）

| 場景 | 第一選擇 | 備選 |
|---|---|---|
| 商品 hero、單鏡頭電影感 | Veo 3.1 Standard | Omni 1.2、Runway Gen-4.5 |
| 人物對白、lip-sync | Omni 1.2、Grok 1.5 | Veo 3.1 |
| timecode 多鏡頭 | Omni 1.2 | — |
| 對話式編輯 | Omni 1.2（唯一） | Runway Aleph 2 |
| 延伸 / 尾幀 | Veo 3.1 Standard | Omni 1.2 |
| 角色一致性 | Omni 1.2（6 參考圖）、Grok 1.5（14 參考圖） | Veo 3.1 Standard |
| 最便宜草稿 | Grok 1.5 Lite、Omni 360p | Veo Lite、LTX-2 自架 |
| 商業安全 | Adobe Firefly | Google（Vertex indemnity） |

---

## 附錄 A：本輪探針原始輸出

```
# Gemini
GET /v1beta/models → 61 models，含 gemini-omni-1.2-flash / 1.1-flash；無 veo-*
POST /v1beta/interactions duration=99s → 1.1: "maximum allowed 10s"；1.2: "maximum allowed 15s"

# xAI
GET /v1/video-generation-models → grok-imagine-video (text,image,video→video) / -1.5 (text,image,audio→video) / -1.5-lite (text,image→video)
POST /v1/videos/generations duration=999 → 400 "Duration must be between 1 and 15 seconds"
  resolution=bogus → 422 expected one of `480p`, `720p`, `1080p`
  aspect_ratio=bogus → 422 expected one of `1:1`,`16:9`,`9:16`,`4:3`,`3:4`,`3:2`,`2:3`,`21:9`,`5:2`
  (valid body, 5s 720p 16:9) → 200 request_id → ~40 s 後 status done,
  usage.cost_in_usd_ticks=7000000000 (= $0.70), video 1280x720 24fps 5.04s h264+aac 7.0MB

# OpenRouter
GET /api/v1/models → google/gemini-omni-1.2-flash (output text,video)；無 xai 影片模型
GET /api/v1/auth/key → limit 10, remaining 5.05

# egress: US (Ohio)
```

## 附錄 B：`config.yaml` 草稿

```yaml
budget:
  omni_cap_usd: 1.10
  xai_cap_usd_new: 1.50          # 不含已花 0.70
  stop_if_actual_vs_est_over: 0.30
  max_retries: 2
models:
  omni_12: { id: gemini-omni-1.2-flash, provider: gemini, api: interactions, max_s: 15, verified: 2026-11-07 }
  grok_15: { id: grok-imagine-video-1.5, provider: xai, api: videos.generations, max_s: 15, verified: 2026-11-07 }
pricing_usd:
  omni_tokens_per_s: { 360p: 1931, 720p: 5792 }
  omni_12_output_per_m_tok: 12.00
  grok_15_per_s: { 480p: 0.08, 720p: 0.14 }   # 720p 實測；480p 為文件推測
defaults: { resolution: 720p, aspect: "16:9", duration_s: 5 }
```

## 附錄 C：來源

- Gemini 價格 https://aistudio.google.com/docs/pricing ；deprecations https://aistudio.google.com/docs/deprecations ；Omni 指南 https://aistudio.google.com/docs/omni.md.txt
- xAI 影片指南 https://docs.x.ai/docs/guides/video-generation ；模型頁 https://docs.x.ai/docs/models/grok-imagine-video-1.5 ；價格 https://docs.x.ai/developers/pricing
- Google Cloud Veo prompt guide（P1 來源）https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide
- GLBGPT 同題六模型測試（P2、P3 來源）https://www.glbgpt.com/hub/ai-video-prompt-adherence-comparison/
- VBench-2.0 prompt 清單 https://github.com/Vchitect/VBench/tree/master/VBench-2.0/prompts
- Arena 排名引用 https://videogen.io/best-ai-video-models ；Higgsfield 評測 https://higgsfield.ai/blog/5-Best-AI-Video-Models-2026-Tested-Compared
- Runway API 價格（Veo / Omni / Grok 轉售價）https://docs.dev.runwayml.com/guides/pricing/
- Vertex Veo 3.1 模型頁 https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate
