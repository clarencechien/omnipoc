# 計劃 v0.3 — 用 Omni 1.2 做「尋寶」電影／遊戲開頭（只寫計劃，未動手）

- 日期：2026-11-07
- 狀態：**S0–S4 已執行（2026-11-07），結果見 REPORT.md 第二部分；S5、S6 未做**
- 前提：v0.2 pilot 結束（`REPORT.md`）。xAI 不再比。Grok 的 pipeline 程式保留但不用。
- 已花：$2.88。本計劃另外預算見第 6 節。

---

## 0. 四個問題的答案（事實來源：Omni 指南 + 價格頁，2026-11-07 抓）

### Q1 畫面最高多高？能 1080p 嗎？
- 可以，`resolution` 接受 `360p`、`720p`（預設）、`1080p`、`4k`。
- 但 **720p 是模型原生，1080p / 4K 是「with upsampling」**，價格頁和指南都這樣標。所以 1080p 不是更多細節，是 Google 幫你放大。
- 價格：360p $0.023/s、720p $0.07/s、1080p $0.104/s、4K $0.209/s。

### Q2 可以先做 720p 再升 1080p 嗎？
- **API 沒有「把已生成影片升解析度」的操作。** 解析度是生成時用 `response_format.resolution` 決定的；文件沒有任何 upscale turn。
- 兩條可行路：
  - **A. Google 端重生成**：同 prompt 用 `previous_interaction_id` 開一輪，要求 1080p。**未驗證**會不會重畫內容（多半會變），而且整支按 1080p 費率再算一次（8 s ≈ $0.83）。
  - **B. 本機放大**：既然 Google 的 1080p 也是 upsampling，本機用 ffmpeg lanczos 或 Real-ESRGAN 放大 720p 是正當替代，**$0**。畫質差多少要實測一次（第 4 節 S5）。
- 建議流程：**360p 草稿迭代 → 720p 定稿 → 本機放大到 1080p**；只有在 S5 證明 Google 的 1080p 明顯更好時才改走 A。

### Q3 電影級和動畫都能生嗎？
- 都能，**靠 prompt 不靠參數**。沒有 style 參數；指南示範「Make this video anime」當編輯指令，Google 的 prompt guide 有「vibrant Japanese anime style」「1920s sepia film grain」這類範例。
- 鎖風格最可靠的方法是**先用圖像模型產一張風格定裝圖，當 reference image 丟進去**（Omni 最多 6 張參考圖）。純文字描述風格每支會漂。
- 2D 手繪／3D 渲染／實拍三種都可試，建議第一輪就各出一支 360p 看哪種最穩（第 4 節 S1）。

### Q4 像投影片那樣用影片做，很浪費 token 嗎？
- **是。** Omni 按秒計費，畫面靜不靜都一樣：一張 10 秒的靜態標題卡 720p = $0.70，而 ffmpeg `drawtext` 疊字 = $0。而且 Omni 的畫面文字會錯字，標題卡反而是它最不擅長的。
- 對照：Nano Banana 2（`gemini-3.1-flash-image`）一張 1K 圖 $0.067、2K $0.101；一張圖 + ffmpeg Ken Burns（慢推慢搖）就能當 5–10 秒的「偽影片」。
- 原則：**影片只買「需要真實運動」的鏡頭**（人物走動、鏡頭穿越、物件物理）；標題、字幕、靜態插畫、章節卡全部走圖 + ffmpeg；配樂走 Lyria 3.5（$0.08 一首）。

---

## 1. 目標與形式

- 產物：一支 **45–60 秒**的開場（電影 cold open 或遊戲 title sequence 二擇一，建議先做遊戲 title sequence，因為允許較多「圖 + 動態字」的省錢段落）。
- 故事：一枚古老指南針、一張地圖、一個尋寶者。指南針是貫穿物件，所以**物件一致性**是本計劃最重要的技術題（pilot 已證明 Omni 會把 compass 畫成懷錶）。
- 三個技術問題要一併回答：風格鎖定法、物件一致性法、省錢混搭法。

## 2. 鏡頭表（草案，S0 時定稿）

| # | 秒數 | 內容 | 做法 | 需要運動？ |
|---|---|---|---|---|
| 1 | 0–6 | 黑畫面 → 工作室名／「A ... production」 | ffmpeg 字卡 | 否 |
| 2 | 6–14 | 暴風雨海面，一艘船（establishing） | Omni 8 s | 是 |
| 3 | 14–20 | 船艙內，手打開木盒，露出指南針（hero shot） | Omni 6 s + 參考圖 | 是 |
| 4 | 20–26 | 指南針特寫：磁針擺動後指向「不是北」的方向 | Omni 6 s + 參考圖 | 是（這就是 pilot 翻車題） |
| 5 | 26–32 | 地圖攤開，鏡頭掃過插畫地圖（可用圖 + Ken Burns） | Nano Banana 2K 圖 + ffmpeg | 否 |
| 6 | 32–42 | 尋寶者踏上海島，回頭看鏡頭 | Omni 10 s + 人物參考圖 | 是 |
| 7 | 42–50 | 標題浮現「...」+ 指南針靜幀 | ffmpeg 字卡疊在 #4 的定格 | 否 |
| 配樂 | 全程 | Lyria 3.5 一首，ffmpeg 混音、ducking | | |

影片秒數合計 30 s（#2、#3、#4、#6），其餘 20 s 是圖和字卡。

## 3. 技術決策（要在小實驗裡驗證的）

| 決策 | 選項 | 怎麼驗 |
|---|---|---|
| 風格 | 實拍電影感 / 3D 動畫 / 2D 手繪 | S1：同一鏡頭 360p 各一支 |
| 指南針一致性 | (a) 純文字加強描述 (b) 參考圖 (c) 先 Nano Banana 出指南針圖再當 reference | S2：#4 鏡頭三種做法各一支 360p |
| 多鏡頭連續性 | (a) 每鏡頭獨立生成 + 共用參考圖 (b) 單次 15 s timecode 多鏡頭 (c) extend 鏈到 30 s | S3：#2→#3 用 (a) 與 (b) 各一次 360p |
| 1080p | Google upsample vs 本機 lanczos vs Real-ESRGAN | S5：#4 定稿一支，三種各出一版，盲看 |
| 音訊 | Omni 每支自帶音軌 vs 全關音樂只留環境音、配樂走 Lyria | S4：聽 S1–S3 產物的音軌能不能接；大概率選 Lyria |

## 4. 實驗順序與 cap

| 步 | 內容 | 估價 |
|---|---|---|
| S0 | 定鏡頭表、寫 prompt v1（版本化 `prompts/opening/*.yaml`）、用 Nano Banana 2 出：風格定裝圖 ×3 風格、指南針正面／側面 ×2、尋寶者 ×2、地圖 ×1（2K） | ~$0.70 |
| S1 | 風格測試：#6 鏡頭，3 風格 × 360p × 8 s | $0.55 |
| S2 | 指南針一致性：#4 鏡頭，3 做法 × 360p × 6 s | $0.42 |
| S3 | 連續性：(a) #2 + #3 各一支 360p；(b) 一支 15 s timecode 360p | $0.67 |
| **回報點** | 看 S1–S3 草稿，Clarence 選風格、做法 | |
| S4 | 定稿：#2、#3、#4、#6 共 30 s，720p，hero 鏡頭 #4 跑 2 reps | $2.52 |
| S5 | 1080p 對照：#4 定稿 Google 1080p 重生成 1 支（$0.62）+ 本機兩種放大 | $0.62 |
| S6 | 組裝：Lyria 一首 $0.08；ffmpeg 字卡、concat、crossfade、混音 | $0.08 |
| 緩衝 | 重試 2 次 720p | $1.00 |
| **合計** | | **≈ $6.6**，cap **$8** |

70% 回報點 $5.6 會落在 S4 後、S5 前。

## 5. 風險與已知坑

- **指南針**：pilot 兩個模型都畫錯。v2 prompt 要明寫「a magnetic compass with a single needle, letters N E S W, no clock numerals, no clock hands」，並以參考圖為主。
- **畫面文字**：不靠 Omni；標題全走 ffmpeg。
- **音樂跨鏡頭不連續**：每支 prompt 加「no music, ambient sound only」，配樂後製。
- **store=true**：要用 `previous_interaction_id` 編輯／延伸就必須 store=true（pilot 已踩到）。
- **延遲**：720p 10 s 約 40–60 s 一支，S4 四支可平行。
- **1080p 重生成會不會變畫面**：S5 才知道；若會，就代表 Google 的 1080p 路徑對「先 720p 再升級」沒用。

## 6. 需要 Clarence 現在決定的

1. 電影 cold open 還是遊戲 title sequence（建議後者）。
2. 風格先試三種，還是你已有偏好（實拍／3D／2D）。
3. 預算 cap $8 可不可以。
4. 要不要我先做 S0 的圖（約 $0.70），讓你在選風格前先看到定裝圖。

## 7. 技術備忘（執行時用）

- 參考圖請求格式：`input: [{type: image, data: <b64>, mime_type: image/png}, ..., {type: text, text: "..."}]`，最多 6 張；角色每人最多 3 張、最多 2 人。
- 延伸：`previous_interaction_id` + 文字；每輪 3–10 s；總長 30 s；只能往後接。
- 首尾幀：兩張圖按順序（first, last）+ 文字；3–10 s。
- Lyria：`lyria-3.5` 走 `generateContent`，$0.08／首（付費層）。
- 本機放大：`ffmpeg -vf scale=1920:1080:flags=lanczos`；Real-ESRGAN 要另裝（realesrgan-ncnn-vulkan，CPU 可跑但慢）。
