# omnipoc 計劃 v0.1 — 影片生成 API 盤點 + US$5 Veo vs Omni 小比較

- 日期：2026-11-07
- 狀態：**計劃，尚未花任何錢**（本文件所有探針都是免費呼叫：`GET /models`、故意送無效參數拿 400）
- 原始需求：handoff v0.1（`docs/handoff-v0.1.md`）+ Clarence 口頭追加：
  1. 先整理目前能產影片的 API 服務有哪些、什麼類型用什麼比較好（Google、xAI 要含，中國廠商排除）
  2. 用 Gemini key、預算 US$5 以內，做一次 Veo vs Omni 比較
  3. 先寫計劃

---

## 0. 先講結論（開工前要 Clarence 決定一件事）

**Veo 3.1 已經不在 Gemini API 上了。** 官方 deprecations 頁：`veo-3.1-generate-preview`、`veo-3.1-fast-generate-preview`、`veo-3.1-lite-generate-preview` 三個 ID 全部於 **2026-10-22 shut down**，replacement 都寫 `gemini-omni-1.2-flash`。我用這把 key 打 `GET /v1beta/models` 列了 61 個模型，沒有任何 `veo-*`；直接 GET 九個候選 Veo ID 全部 404（見附錄 A）。

所以「用 Gemini key 比 Veo vs Omni」在字面上做不到。Veo 3.1 現在只剩三條路，三條都不是 Gemini key：

| 路徑 | 需要什麼 | Veo 牌價（720p 含音訊，/s） | 優點 | 缺點 |
|---|---|---|---|---|
| **A. Vertex AI（現名 Gemini Enterprise Agent Platform）** | GCP 專案 + 開 billing + `gcloud auth`（sandbox 已預裝 gcloud，目前無帳號） | Standard $0.40 / Fast $0.15 / Lite $0.05（第三方轉述，官方價格頁是 JS 渲染抓不到 → **待驗證**） | 官方、完整參數（seed、首尾幀、extension、reference images）、有 usage metadata | 要 GCP 專案；Lite 仍是 Preview、English only、不支援 reference images |
| **B. Runway Dev API** | Runway 開發者帳號，credits $0.01/顆 | veo3.1 $0.40 / veo3.1_fast $0.15（官方 pricing 頁，有抓到） | 一把 key 同時有 Veo 3.1、Omni 1.1/1.2、Grok Imagine、Gen-4.5；價格與 Google 牌價相同 | 看不到 Google 端 usage/thought token 欄位（E1 做不了）；多一層中介的延遲 |
| **C. fal.ai / Replicate** | 各自帳號 | Veo 3.1 約 $0.40（第三方，數字互相矛盾） | 彈性 | 同 B，且價格更不透明 |

**我的建議**：
- 若 Clarence 有現成 GCP 專案 → 走 **A**（最貼近 handoff 原意，也最便宜能跑 Lite）。
- 若沒有、不想開 → 走 **B**（Runway 一把 key 最省事，而且順便能接 Grok Imagine 當第三個對照）。
- **不管選哪條，先用 Gemini key 把「Omni 1.1 vs 1.2」跑掉**（第 4 節 M1）。這部分只要 Gemini key、有 12/03 期限（1.1 之後被自動導到 1.2），而且是 handoff E7 的縮小版。

---

## 1. 市場盤點：能產影片的 API（2026-11 現況，排除中國廠商）

來源等級：**官** = 官方文件/價格頁本輪抓到；**三** = 第三方整理，數字可能過時或互相矛盾；**驗** = 本輪用免費 API 呼叫驗證。

### 1.1 仍在線、可直接用的

| 廠商 / 模型 | 存取方式 | 牌價（720p 含音訊，/s） | 單支長度 | 音訊 | 特色 / 限制 | 等級 |
|---|---|---|---|---|---|---|
| **Google Gemini Omni 1.2 Flash** `gemini-omni-1.2-flash` | Gemini API，`POST /v1beta/interactions`（Interactions API） | $0.07（360p $0.023；1080p/4K 為 upscale $0.104/$0.209）；輸出 $12/1M tok，720p = 5,792 tok/s | 3–15 s 整秒，預設 10 s | 原生 | 多輪對話式編輯、extend 到 30 s、最多 6 張參考圖、timecode prompt、畫面文字；無 temperature/system prompt/negative prompt；官方只評估英文；無 free tier；**thinking tokens 計入輸出價**（價格頁原文 "including thinking tokens"） | 官 + 驗（key 能打到 1.2，最長 15 s） |
| **Google Gemini Omni 1.1 Flash** `gemini-omni-1.1-flash` | 同上 | $0.10（輸出 $17.50/1M tok） | 3–10 s | 原生 | **2026-12-03 起自動導流到 1.2、以 1.2 計價**（官方 deprecations 頁，已證實 handoff 第 1 節的「待驗證」） | 官 + 驗（key 能打到 1.1，最長 10 s） |
| **Google Veo 3.1 / Fast / Lite** `veo-3.1-generate-001` / `veo-3.1-fast-generate-001` / `veo-3.1-lite-generate-001` | **只剩 Vertex**（`us-central1`），或經 Runway / Replicate / fal 轉售 | $0.40 / $0.15 / $0.05（Vertex 數字為第三方；Runway 頁官方：veo3.1 40 credits/s、fast 15、無音訊減半） | 4 / 6 / 8 s | 原生 | Standard 到 4K、首尾幀、extension、reference images（Lite 不支援）、C2PA；Standard/Fast GA，Lite Preview；Vertex 頁寫「不支援 pay-as-you-go」只列 Provisioned Throughput / Fixed quota → **待驗證實際能否按量計費** | 官（Vertex 模型頁、Runway 價格頁）|
| **xAI Grok Imagine Video 1.5 / 1.5 Lite / (舊版)** `grok-imagine-video-1.5` / `grok-imagine-video-1.5-lite` / `grok-imagine-video` | xAI API（docs.x.ai） | $0.08 / $0.02 / $0.05（官方 models 頁）；Runway 轉售 1.5 720p $0.16、Lite 720p $0.03 | 官方頁未列 | 1.5 有 | 第三方評測常把它列為 talking head / 對白最佳；Lite 是目前最便宜的 720p 選項之一 | 官（價格）+ 三（能力） |
| **Runway Gen-4.5 / Gen-4 Turbo / Aleph 2 / Act-Two** | Runway Dev API | Gen-4.5 $0.12、Gen-4 Turbo $0.05、Aleph 2（影片編輯）$0.28、Act-Two（表演驅動）$0.05 | 2–10 s（Gen-4.5） | 否（Gen-4.5） | 鏡頭控制、影片轉影片編輯、表演捕捉；Runway 平台也轉售 Veo / Omni / Grok | 官 |
| **Luma Ray3.14 / Ray3.2** | Dream Machine API / Luma Agents API | 官方價未抓到；第三方 720p 約 $0.06–0.09 | 5–10 s | 部分 | HDR、專業後製管線；HDR/企業層要 sales 報價 | 三 |
| **Pika 2.x** | Pika API | 約 $0.12（單一來源） | ≤5 s | — | 特效類，業務用途少 | 三 |
| **Adobe Firefly Video（Firefly Services API）** | Adobe 企業 API | 以 credits 計，USD 換算未公開 | — | — | 賣點是訓練資料商業安全 / 版權賠償，不是畫質或價格 | 三 |
| **Lightricks LTX-2** `ltx-2-fast` / `ltx-2-pro` | 自家 API，或開放權重自架 | fal 以 $0.0018/megapixel 計，不能直接換算 | — | 有 | 開放權重，自架最便宜；畫質在第三方評比中屬中段 | 三 |
| **Genmo Mochi** | 開放權重 | 自架 | — | 無 | 研究用，無音訊 | 三 |

### 1.2 已下架 / 不要排進計劃的

| 項目 | 狀態 | 來源 |
|---|---|---|
| OpenAI Sora 2 / Sora 2 Pro API | 2026-03-24 宣布停止；App 4 月關、API 9 月關（9/24 日期為第三方） | 多家媒體引述 OpenAI 聲明；官方 help 頁未抓到 |
| Amazon Nova Reel v1:0 / v1:1 | AWS lifecycle 頁：2026-03-30 Legacy、**2026-09-30 EOL**；無 Nova 2 影片替代 | AWS 官方 lifecycle 頁（搜尋摘要） |
| Veo 3.1 Preview（Gemini API 三個 ID）、`gemini-omni-flash-preview` | 2026-10-22 shut down | 官方 deprecations 頁 |
| 中國廠商（依 Clarence 指示排除）：Kling（快手）、Seedance（字節）、Hailuo/MiniMax、Wan（阿里）、Vidu、Hunyuan（騰訊） | 不納入 | — |

### 1.3 聚合平台（一把 key 打很多模型）

- **Runway Dev API**：模型最齊（Veo 3.1、Omni 1.1/1.2、Grok 1.5、自家 Gen-4.5），價格頁公開且等於各家牌價。缺點：拿不到各家原生 usage 欄位。
- **fal.ai / Replicate**：模型多但價格矛盾多、文件品質參差；適合臨時試一支，不適合做計費解剖。

### 1.4 「什麼類型用什麼」初步對照（**全部是第三方評測與官方 feature 表推論，沒有自測，當假設用**）

| 場景 | 第一選擇 | 備選 | 依據 |
|---|---|---|---|
| 商品 hero、單鏡頭電影感 | Veo 3.1 Standard | Omni 1.2（便宜 6 倍）、Runway Gen-4.5（鏡頭控制） | 第三方評測多說 Veo Standard 單鏡頭質感較好；但 Arena 盲測 Omni 領先，**互相矛盾**，正是本 PoC 要自己驗的 |
| 人物對白、lip-sync | Omni 1.2（官方稱 7 語 lip-sync）、Grok Imagine 1.5（評測說 talking head 最佳） | Veo 3.1（原生音訊） | 第三方；中文對白沒人測過 → handoff E3 |
| 多鏡頭敘事、timecode 分段 | Omni 1.2（官方文件直接教 `[0-3s]` 語法） | Veo 3.1（8 s 內切鏡要靠 prompt） | 官方文件 |
| 對話式編輯（換色、換背景、保留其他） | Omni 1.2（唯一有 multi-turn edit 的） | Runway Aleph 2（video-to-video） | 官方 |
| 延伸到 30 s+、尾幀控制 | Veo 3.1 Standard（官方原本建議） | Omni 1.2（文件現在也說能 extend 到 30 s，首尾幀用自然語言描述） | 官方文件自相矛盾 → handoff E5 |
| 角色 / 商品一致性（參考圖） | Omni 1.2（6 張參考圖、每角色 3 張）| Veo 3.1 Standard（reference images；Lite 不支援）| 官方 |
| 大量草稿、最便宜 | Grok 1.5 Lite $0.02、Omni 360p $0.023、Veo Lite $0.05 | LTX-2 自架 | 官方價格 |
| 版權 / 商業安全優先 | Adobe Firefly | Google（Vertex 有 indemnity，Gemini API 端**待確認**） | 三 |
| 表演驅動 / 數位人 | Runway Act-Two | 專門 lip-sync 工具（多為中國廠商，排除） | 三 |

---

## 2. 這把 Gemini key 目前能做什麼（免費探針結果，附錄 A 有原始輸出）

- 連線：`generativelanguage.googleapis.com` 通；sandbox 出口 **美國（Ohio，Google LLC AS396982）**，沒有 EEA/UK/CH 限制問題。
- `GET /v1beta/models` 200，61 個模型；含 `gemini-omni-1.2-flash`、`gemini-omni-1.1-flash`、`gemini-omni-flash-preview`（後者文件說已 10/22 下架，list 還在）；**無任何 Veo**。
- Interactions 端點對 1.1 / 1.2 都能解析模型（故意送 `duration: 99s`，分別回「最大 10 s」與「最大 15 s」的 `invalid_request`，未產生影片、未計費）。
- 注意：`GET /models/gemini-omni-1.2-flash` 的 `supportedGenerationMethods` 列 `generateContent`，但官方 Omni 文件只教 Interactions API；**不要走 generateContent**，避免行為與計價不明。
- gcloud 已安裝但 `No credentialed accounts`、無 project → Vertex 路徑目前打不通。
- 工具：Python 3.13、ffmpeg/ffprobe 有；`google-genai` 最新 3.0.0（要裝，確認有 `client.interactions`）。

---

## 3. 花錢規則（沿用 handoff 第 3 節，預算改成 US$5）

1. 全專案上限 **US$5.00**；單一實驗 cap 見第 4 節；**用到 $3.50（70%）停下回報**。
2. 先估價 → 寫 `ledger/spend.jsonl` → 呼叫 → 影片 + usage 落檔 → 才發下一筆。
3. 重試上限 2；同 spec 連續失敗標 `failed`，不重排。
4. 預設 720p、16:9、8 s（Veo 上限、兩邊對齊）；不跑 1080p/4K、不跑 Veo Standard（一支 8 s 就 $3.20，直接吃掉 64% 預算）。
5. `config.yaml` 是單一事實來源（草稿見附錄 B）；model ID 只填本輪 `GET /models` 或 Vertex 模型頁驗過的。
6. Secret 只從環境變數讀（目前 sandbox 變數名是 `gemini_key`），不進 log、不進 ledger。

### 估價公式（Omni，官方 token 計量）

```
cost = seconds × tokens_per_second[res] × output_price_per_token
720p: 5,792 tok/s   360p: 1,931 tok/s   1080p(up): 8,688 tok/s   4K(up): 17,376 tok/s
Omni 1.2 output $12.00 / 1M tok   → 720p 8 s = 46,336 tok = $0.556
Omni 1.1 output $17.50 / 1M tok   → 720p 8 s = 46,336 tok = $0.811
Omni 1.2 360p 3 s = 5,793 tok = $0.070（最便宜的 smoke）
輸入 $1.50 / 1M tok（prompt 很短，忽略；參考圖另計）
```

Veo（Vertex 或 Runway）按秒：Lite $0.05、Fast $0.15、Standard $0.40 → 8 s = $0.40 / $1.20 / $3.20。

---

## 4. US$5 實驗設計

原則：$5 買不到 handoff 要求的「每設定 3 reps × 6 prompts」。這是 **pilot**，目的是（a）把管線、ledger、ffprobe、盲測頁跑通，（b）拿到第一批可看的對照片，（c）量出實際帳單 vs 牌價。**不是**定論；報告會明寫 n。

### M0 Smoke（cap $0.30）— 只要 Gemini key

| # | 模型 | 設定 | 估價 |
|---|---|---|---|
| s1 | Omni 1.2 | 360p、3 s、p01 | $0.07 |
| s2 | Omni 1.1 | 360p、3 s、p01 | $0.10 |

出口：usage 欄位長什麼樣（有沒有 thought tokens、分不分開計）、延遲、`delivery: uri` 流程、ffprobe 實際秒數/解析度/音軌。**M0 做完先回報一次**（對應 handoff E1 的固定回報點）。

### M1 Omni 1.1 vs 1.2 回歸（cap $2.10）— 只要 Gemini key，**12/03 前要做**

3 個 prompt × 2 模型 × 1 rep，720p、8 s、16:9：

| prompt | 測什麼 | Omni 1.2 | Omni 1.1 |
|---|---|---|---|
| p04 timecode 多鏡頭 | `[0-3s]` 語法有沒有照切 | $0.56 | $0.81 |
| p01 商品單鏡頭 | 連續鏡頭、不亂切 | $0.56 | $0.81 |
| p-text（新，畫面文字：招牌「台北夜市」）| 繁中字卡正確率 | $0.56 | $0.81 |
| 小計 | | $1.67 | $2.43 |

合計 **$4.10**。這已經超過 M1 cap，所以 **M1 預設只跑 p04 + p-text（$2.74）**，p01 留給 M2 當 Omni 那邊的樣本。

### M2 Veo vs Omni（cap $2.20）— **需要 Clarence 先選路徑 A 或 B**

| prompt | Omni 1.2（Gemini key） | Veo 3.1 Lite（Vertex 或 Runway） |
|---|---|---|
| p01 商品單鏡頭 | $0.56 | $0.40 |
| p02 人物對白 lip-sync | $0.56 | $0.40 |
| 小計 | $1.12 | $0.80 |

合計 **$1.92**。Veo Fast / Standard 一支就 $1.20 / $3.20，$5 內放不下；若 Clarence 願意把 M1 砍到只剩 p04（省 $1.37），可以換一支 **Veo 3.1 Fast × p01（$1.20）** 當 Veo 真正實力的錨點。

### 總表

| 區塊 | 估價 | 累計 | 備註 |
|---|---|---|---|
| M0 smoke | $0.17 | $0.17 | |
| M1 Omni 1.1 vs 1.2（p04 + p-text） | $2.74 | $2.91 | |
| M2 Veo Lite vs Omni 1.2（p01 + p02） | $1.92 | $4.83 | |
| 緩衝（1 次重試） | — | → $5.00 | 超過就停 |

70% 回報點 $3.50 會落在 M2 中間；屆時回報一次再跑完。

### 若 Clarence 不開 Vertex 也不開 Runway

M2 改成 **Omni 1.2 × p01、p02 各 2 reps（$2.24）**，純量 Omni 的自然變異，Veo 那欄留白、報告明寫「Veo 不可達，原因：Gemini API 已下架」。

---

## 5. 指標與產出（pilot 版）

- 每支：`run_id, exp, model, prompt_id, rep, params, est_cost, usage{...原樣}, latency_s, ffprobe{duration, w×h, fps, audio}`。
- 人評（Clarence）：畫質、prompt 遵循、物理、音訊各 1–5；盲測頁隨機排序、隱藏模型名。
- 影片存放：pilot 只有 ~6–8 支，轉 360p 低碼率預覽放 `review/media/`（總量 < 30 MB）進 repo，Chromebook/手機直接開 `review/index.html`；R2 等正式跑再說。
- `REPORT.md`：M0 計費解剖（thought 有沒有另計、實際 vs 牌價誤差）、M1 回歸觀察、M2 對照 + 盲測結果、以及「第 1.4 節哪些假設被推翻」。

---

## 6. 執行順序與停下來問的點

1. **現在**：Clarence 決定 M2 路徑（A Vertex / B Runway / 不做）；確認 $5 與 70% 回報點。
2. 建 `config.yaml`、`src/`（omni client、budget、probe、run）、`prompts/*.yaml`（p01、p02、p04、p-text 版本化）。
3. M0 → 回報（usage 欄位、thought 計費、實際成本）。
4. M1（12/03 前）。
5. M2（拿到 A 或 B 的憑證後）。
6. 盲測頁 → Clarence 打分 → REPORT.md。

停下來問：M0 完成時；花到 $3.50；任何「User location is not supported」或 404 model；需要 Vertex/Runway 憑證；估價與實際帳單差 >30%。

---

## 附錄 A：本輪免費探針原始輸出（2026-11-07）

```
GET /v1beta/models?pageSize=200 → 200, 61 models, 影片相關：
  models/gemini-omni-flash-preview | generateContent, countTokens
  models/gemini-omni-1.1-flash     | generateContent, countTokens
  models/gemini-omni-1.2-flash     | generateContent, countTokens   (thinking: true)
  (無 veo-*)

GET /v1beta/models/veo-3.1-generate-preview … veo-2.0-generate-001（9 個候選）→ 全部 404

POST /v1beta/interactions {"model":"gemini-omni-1.1-flash","input":"test",
  "response_format":{"type":"video","duration":"99s","resolution":"360p"},"store":false,"background":false}
  → {"error":{"message":"Requested video duration 99s 0ns exceeds the maximum allowed 10s 0ns","code":"invalid_request"}}
同請求換 gemini-omni-1.2-flash
  → {"error":{"message":"Requested video duration 99s 0ns exceeds the maximum allowed 15s 0ns","code":"invalid_request"}}

gcloud auth list → No credentialed accounts; project (unset)
egress: US / Columbus, Ohio / AS396982 Google LLC
```

## 附錄 B：`config.yaml` 草稿（開工時落檔）

```yaml
budget:
  project_cap_usd: 5.00
  report_at_fraction: 0.70
  caps_usd: { M0: 0.30, M1: 2.10, M2: 2.20 }
  max_retries: 2
models:
  omni_12: { id: gemini-omni-1.2-flash, api: interactions, max_s: 15, verified: 2026-11-07 }
  omni_11: { id: gemini-omni-1.1-flash, api: interactions, max_s: 10, verified: 2026-11-07,
             note: "auto-routes to 1.2 from 2026-12-03" }
  veo_31_lite: { id: veo-3.1-lite-generate-001, api: vertex|runway, max_s: 8, verified: null }
  veo_31_fast: { id: veo-3.1-fast-generate-001, api: vertex|runway, max_s: 8, verified: null }
pricing_usd:
  omni_tokens_per_s: { 360p: 1931, 720p: 5792, 1080p: 8688, 4k: 17376 }
  omni_12_output_per_m_tok: 12.00
  omni_11_output_per_m_tok: 17.50
  omni_input_per_m_tok: 1.50
  veo_per_s_720p_audio: { lite: 0.05, fast: 0.15, standard: 0.40 }   # 第三方/Runway，待 Vertex 驗證
defaults: { resolution: 720p, aspect: "16:9", duration_s: 8 }
```

## 附錄 C：來源

官方（本輪抓到）
- Gemini API 價格頁 https://aistudio.google.com/docs/pricing（Omni 1.1/1.2 token 價與 tok/s；無 Veo）
- Gemini API deprecations https://aistudio.google.com/docs/deprecations（Veo 3.1 三 ID 10/22 下架；Omni 1.1 12/03 導流）
- Gemini API video 頁 https://aistudio.google.com/docs/video.md.txt（Veo Preview shutdown 聲明）
- Omni 指南 https://aistudio.google.com/docs/omni.md.txt
- Vertex Veo 3.1 模型頁 https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate
- Vertex express mode https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview（不含 Veo）
- xAI models https://docs.x.ai/docs/models
- Runway API pricing https://docs.dev.runwayml.com/guides/pricing/

第三方（數字僅供參考）
- Sora 停止：https://the-decoder.com/openai-sets-two-stage-sora-shutdown-with-app-closing-april-2026-and-api-following-in-september/
- Nova Reel EOL：https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html（AWS 官方，經搜尋摘要）
- 市場價格綜整：https://www.atlascloud.ai/blog/tips/cheapest-ai-video-generation-api-2026 、https://morphed.app/blog/ai-video-generation-cost
- Luma：https://wavespeed.ai/blog/cost-and-billing/luma-ai-pricing/
- 場景評測：https://videogen.io/best-ai-video-models 、https://pixverse.ai/en/blog/best-ai-lip-sync-video-generators-2026
