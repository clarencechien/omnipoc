# omnipoc REPORT — 總結（2026-11-07 告一段落）

專案狀態：**告一段落**。兩段工作都做完到預定停點，總花費 **$7.53**（明細見文末帳表）。接續點：第二部分第 4 節的 S5／S6。

## 0. 結論（場景 → 做法）

| 問題 | 結論 | 依據 |
|---|---|---|
| Veo 還能不能用 Gemini key 叫？ | **不能。** Veo 3.1 三個 preview ID 於 2026-10-22 從 Gemini API 下架，replacement 是 `gemini-omni-1.2-flash`；Veo 只剩 Vertex（需 GCP 專案）或 Runway／fal／Replicate 轉售 | 官方 deprecations 頁 + `GET /models` 實測 |
| Omni 1.2 能不能當影片預設？ | **可以，而且目前是唯一用 Gemini key 能叫的影片模型。** 12 支生成零失敗；usage 可完全重建帳單（誤差 < 6%，來自 thought 與參考圖輸入 token） | 第一、二部分全部 run |
| Omni vs Grok 1.5（同 prompt、720p、5 s） | 紅大衣電影場景：Clarence 與 Claude 獨立看都認為 **Omni 較真實**。指南針：**兩邊都畫錯**（Omni 畫成懷錶、Grok 盤面崩壞）。Grok 720p 實價 $0.14/s 是 Omni 的 2 倍。n=1，只算觀察 | 第一部分 3、3b |
| 物件一致性（指南針翻車）怎麼解？ | **先用 Nano Banana 2 出物件參考圖，再餵給 Omni。** 之後 8 支指南針相關影片盤面全部正確 | 第二部分 S0、S2、S3、S4 |
| 人物／調色一致性 | 餵一張定裝圖即可鎖人物、裝備、場景、調色；不餵就換人換色 | S1 對照、S4 |
| 多鏡頭 | 一支 15 s 用 `[0-8s] … [8-15s] …` timecode，切點準確、調色一致，價格與分開生成相同 | S3b、S4 |
| 草稿→定稿流程 | 360p 草稿（$0.023/s）驗 prompt，720p 定稿（$0.07/s），行為一致沒翻車 | S1–S3 → S4 |
| 1080p / 4K | 都是 Google 端 upsampling（$0.104／$0.209 /s），API 無「升級既有影片」操作；建議本機放大。未實測（S5 未做） | 價格頁、Omni 指南 |
| 投影片式靜態畫面 | 不要用影片，按秒計費、畫面文字會錯；用 Nano Banana 圖（1K $0.067）+ ffmpeg | 價格頁 + S0 |
| 已知坑 | (1) 模型會自己加 letterbox 黑邊，prompt 禁止無效，要用 `cropdetect` 量；(2) 「No text」指令圖像模型不一定聽；(3) `delivery=uri` 必須 `store=true`；(4) 探 schema 不可送合法 body（xAI 意外 $0.70） | 各節 |

## 0b. 花費總表

| 段落 | 內容 | 實際 |
|---|---|---|
| S0（意外） | xAI 探針生成 1 支 | $0.70 |
| M0 | Omni smoke 360p 3 s | $0.08 |
| M1 | Omni ×2 + Grok ×2，720p 5 s | $2.11 |
| O0 | Nano Banana 2 定裝圖 9 張 | $0.64 |
| O1 | Omni 360p 草稿 8 支 | $1.53 |
| O4 | Omni 720p 定稿 4 支 | $2.47 |
| **合計** | 12 支 Omni 影片、3 支 Grok、9 張圖 | **$7.53** |

Omni 影片 12 支實際 $4.86，估價 $4.73（+2.7%）。待 Clarence 對 Cloud Billing 確認 thought token 費率（目前以 $9/1M 入帳，影響 < 2%）。

---

# 第一部分 — Omni 1.2 Flash vs Grok Imagine Video 1.5（M1 pilot）

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

## 3b. Clarence 初評（2026-11-07，看盲測頁口述，尚未填分數表）

| 盲測碼 | 模型 | Clarence 的話 | Claude 核對（放大最後一格，`review/media/C-dial.jpg`、`D-dial.jpg`） |
|---|---|---|---|
| A | Omni 1.2 · redcoat | A 比較真實 | — |
| B | Grok 1.5 · redcoat | B 看起來像假的 | — |
| C | Grok 1.5 · compass | 不像指南針，物理怪 | 盤面有 N/E/S/W 與羅盤玫瑰，但左側 N 字鏡像、字體崩壞；沒有獨立的指針，只有一個固定的星形玫瑰在「轉」，不是磁針運動 |
| D | Omni 1.2 · compass | **被當成時鐘了**；不像指南針，物理怪 | **確認**：盤面是 I–XII 羅馬數字 + 5/10/15/30 分鐘刻度 + 三根時鐘指針（含紅尖秒針），中間疊一個羅盤玫瑰。是「懷錶 × 指南針」混合體。指針在 6 格裡方向亂跳，不是磁針的擺動 |

### 這改寫了第 3 節 P1 的結論

- 第 3 節我寫「兩邊都完全遵循」是錯的：我只核了鏡頭與構圖，沒放大看盤面。**兩個模型都把 "compass" 畫錯**，Omni 錯得更明顯（整個變懷錶）。
- 原因推測（未驗證）：prompt 只有一句、「ancient / mysterious」+「dusty map」把兩個模型都帶往「古董懷錶 / 寶藏地圖」的視覺先驗；P1 這句是 Google 官方 prompt guide 的範例，官方範例本身沒有約束盤面內容。
- 給下一輪的 prompt 修正方向（不另開 id，開 `obj-compass-v2`）：明寫 "a magnetic compass with a single needle that swings and settles pointing north, cardinal letters N E S W, **no clock numerals, no clock hands**"。這題正好可以順便測 negative 描述在兩邊的效果（Omni 不支援 negative prompt 參數，只能寫進正文）。
- P2 紅大衣：Clarence 的「A 真、B 假」與我的觀察方向一致（Omni 現代實景感、Grok 偏 CG 調色）。n=1，但這是目前唯一一個兩人獨立看都指向同一邊的結果。


## 4. 這次 $2.9 能說和不能說的

能說：
1. 同設定 **Grok 1.5 720p 單價是 Omni 1.2 的 2 倍**（$0.14 vs $0.07 /s），而且 Grok 文件上的單價會讓人低估。
2. Omni 的計費可完全從 usage 欄位重建，誤差 < 2%；thought tokens 有獨立欄位。
3. P2（紅大衣）兩邊遵循度都高，Clarence 與 Claude 都認為 Omni 較真實。**P1（指南針）兩邊都畫錯物件**：Omni 畫成懷錶、Grok 盤面字體崩壞且沒有可動磁針（見 3b）。
4. 延遲 Omni 約 30 s、Grok 約 47 s（各 n=2）。

不能說：
- 哪個「畫質較好」——要等 Clarence 盲測，而且 n=1 連同模型自身變異都量不到。
- 對白 / lip-sync（P3 沒跑）、中文、參考圖一致性、編輯、延伸：都還沒測。

## 5. 建議的下一步（都要再花錢，先問）

- 若要下「預設用哪個」的結論：同兩題各加 2 reps（Omni +$1.40、Grok +$2.80）。
- 若要測 Grok 的強項：跑 P3 對白題一次（Omni $0.35、Grok $0.70）。
- 若要壓 Grok 成本：試 480p 一支確認是否真的 $0.40/5 s，再決定 480p 對照是否可接受。


---

# 第二部分 — 尋寶遊戲開場（Omni 1.2 only，計劃 v0.3，做到 S4）

- 日期：2026-11-07 · 計劃：`docs/PLAN-opening.md` · 風格：1 實拍（Clarence 選）
- 花費：S0 $0.64、S1–S3 $1.53、S4 $2.47，**合計 $4.64 / cap $8**（已過 70% 回報點，依指示停在 S4）
- 畫廊：S0 `review/opening/s0/`、S1–S3 `review/opening/s1s3/`、S4 `review/opening/s4/`

## 1. 做了什麼

| 步 | 產物 | 結果 |
|---|---|---|
| S0 | Nano Banana 2 定裝圖 9 張（3 風格、指南針 5 張、地圖 2K） | 全部可用；指南針參考圖正確（N E S W、度數環、單針、無時鐘元素） |
| S1 | 上島鏡頭 360p，有／無參考圖 | 有參考圖：人物、裝備、船、海岸與定裝圖一致。無：換人、換調色 |
| S2 | 指南針特寫 360p，純文字／1 張參考／2 張參考 | 三支都沒變時鐘、針都指 W；純文字盤面字母錯位；2 張參考最穩 |
| S3 | 海面＋船艙 360p，分開 2 支 vs 15 秒 timecode 1 支 | timecode 在第 8 秒準確切換、調色一致；價格與分開相同 |
| S4 | 720p 定稿：海面＋船艙 15 s、指南針 6 s × 2 reps、上島 8 s | 4 支全部可用；指南針 2 reps 幾乎相同 |

## 2. 證明了的

1. **「先出物件參考圖，再餵給影片模型」解決了 pilot 的指南針翻車。** 8 支指南針相關影片（S2 ×3、S3 ×2、S4 ×3）盤面全部正確。
2. **參考圖同時鎖人物與調色。** S1 對照一支即可見；S4 720p 再次一致。
3. **timecode 多鏡頭可當正式手段。** 360p 和 720p 都在指定秒數切換。
4. **720p 與 360p 行為一致。** 草稿在 360p 驗過的 prompt 升到 720p 沒有翻車，草稿→定稿的流程成立（360p 是 720p 價格的 1/3）。
5. **同設定重跑變異小**（指南針 2 reps 幾乎同構圖），至少在有兩張參考圖強約束時如此。
6. **計費**：12 支影片實際成本比估價高 3–6%，全部來自 thought tokens（每支 500–1,200）與參考圖輸入 tokens（每張約 1,100）。

## 3. 沒解決的

- **Letterbox 黑邊**：模型會自己加上下黑邊，S1–S3 有 4/8，S4 有 2/4（海面船艙 64 px、指南針 r1 18 px）。prompt 寫「Full-frame 16:9, no letterbox or black bars」**沒有用**。ffprobe 看不出來，要用 `cropdetect`。組裝時擇一：裁掉、或整支統一加 2.15:1 黑邊（電影感反而合理）。
- **No text 指令**：圖像模型不一定聽（船身文字、地圖真字）。
- **未做**：S5 1080p 對照、S6 組裝（Lyria 配樂、字卡、地圖 Ken Burns、混音）。

## 4. 定稿素材清單（給 S6 用）

| 鏡頭 | 檔案 | 秒數 | 備註 |
|---|---|---|---|
| #2+#3 海面→船艙 | `runs/O4/omni_12-s4-sea-cabin-r1-ddf8bc/video.mp4` | 15.04 | 裁 crop=1280:594:0:64 |
| #4 指南針 | `runs/O4/omni_12-s4-compass-r2-fffbc7/video.mp4` | 6.04 | 無黑邊；r1 備用 |
| #6 上島回頭 | `runs/O4/omni_12-s4-hunter-r1-0eff0a/video.mp4` | 8.04 | 無黑邊 |
| 地圖 | `review/opening/s0/map.jpg` | — | 2K，Ken Burns |
| 字卡 | ffmpeg drawtext | — | 標題待定 |


---

# 第三部分 — 愛情短片（playbill 陶土風），參考圖與 360p 測試

- 日期：2026-11-13 · 分鏡：`prompts/wedding/storyboard.yaml`（v7）→ `docs/storyboard-wedding.md` · 審片：`review/wedding/w1/`（參考圖）、`review/wedding/w2/`（影片）
- 花費：婚禮部分 $7.04 / 上限 $8（絕對上限 $10）；其中參考圖與修臉約 $4.1、檢查約 $0.5、360p 測試影片 $1.72

## 學到的事

1. **參考圖只是引導，鎖不住臉。** 19 張場景參考圖中有 12 張的臉跑掉，症狀一致：眼睛縮成小黑點、沒有亮點。原因是 1K 圖裡臉只有 100–250 px，且只附全身設定圖。
2. **對策有效：** 2K 臉部設定圖（正面、3/4、側面）＋「只修臉」局部重繪（每張約 $0.07，只改 0.3–2.7% 像素）。修完 21/21 張通過臉部檢查。
3. **自動檢查要對準問題：** 整張圖丟給視覺模型比臉不可靠（小臉、表情都會誤判）。有效做法是先框出臉、放大裁切，再明列已知的跑掉方式（眼睛變小點、沒亮點、鼻子變長、臉變窄）。
4. **影片第一格是最強的鎖。** 6 支 360p 測試全程沒有換人，眼鏡、髮型、服裝、捧花都穩定。
5. **360p 不適合判斷臉。** 人物小時臉只剩 60–110 px，分數偏低；判斷臉要用 720p 或人工觀看。
6. **頭尾給圖控制運鏡比 prompt 準。** 單支 15 秒「360° 環繞」只繞約 90°；拆成兩段 8 秒、頭尾都給圖，確實繞到背面再精準落回起點，臉也都通過。
7. **成本：** 附 6 張參考圖時，360p 實際約 $0.025/s，比只有文字時高約 10–13%（參考圖輸入 token）。

| 測試鏡頭 | 秒數 | 實際 | 結果 |
|---|---|---|---|
| 剝皮寮背影走路 | 15 | $0.393 | 穩定 |
| 台北賓館牽手 | 12 | $0.299 | 小指碰觸到牽手完整 |
| 圖書館 360° 單支 | 15 | $0.370 | 只繞約 90° |
| 四四南村舉證書 | 10 | $0.251 | 臉四格全過、證書與 101 正確 |
| 環繞・頭尾給圖 A＋B | 16 | $0.403 | 完整 360°、落點精準 |


> 婚禮微 MV 的完整製作過程、花費拆解與 lessons learned 見 `docs/wedding-mv-lessons.md`。
