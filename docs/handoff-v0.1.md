# Handoff：Google 影片生成 API 實測（Gemini Omni Flash vs Veo 3.1）

- 版本：v0.1 · 2026-11-07
- 接手：Claude Code（網頁版）
- 建議 repo 名：`omnipoc`（可改）
- 所有「已知事實」截至 2026-11-07；標 **待驗證** 的，E0 先查清楚再花錢

---

## 0. 目標

用同一組 prompt 實測 Gemini Omni 1.2 / 1.1 Flash 與 Veo 3.1 各層，回答三題：

1. **品質**：Omni 1.2 Flash 能不能當預設？哪些場景 Veo 3.1 仍有優勢？
2. **成本**：實際帳單 vs 牌價；Omni 回應裡的 `thought` 步驟有沒有另外計費？
3. **風險**：zh-TW prompt／對白／畫面字卡能不能用；1.1 → 1.2 自動導流前的行為回歸。

**非目標**：不做產品、不做 UI、不做 HTML 報告（盲測審片頁除外）、不比非 Google 模型。

---

## 1. 背景：目前已知

| 項目 | 內容 | 來源等級 |
|---|---|---|
| 官方定位 | 影片生成預設用 Omni Flash；Veo 3.1 留給 scene extension、last-frame control、舊管線 | 官方文件 |
| 文件矛盾 | Omni 頁自己也支援首尾幀插補（`<FIRST_FRAME>` `<LAST_FRAME>`）與延伸（每次 3–10 s、總長 40 s，1.1 時代文件） | 官方文件 → **E5 驗證** |
| Omni 1.2 Flash | `gemini-omni-1.2-flash`，GA 2026-11-05；3–15 s 整秒、預設 10 s；360p/720p，1080p/4K 為 upscale；16:9 / 9:16；只走 Interactions API（不支援 generateContent、grounding、function calling） | 官方（Cloud docs） |
| Omni 1.2 價格 | 720p 約 $0.07/s（影片輸出 $12 / 1M tokens × 5,792 tok/s），比 1.1 低 30% | 官方 + 第三方 |
| Omni 1.1 價格 | 影片輸出 $17.50 / 1M tokens → 720p 約 $0.10/s | 第三方 |
| 1.1 → 1.2 導流 | 2026-12-03 起打 `gemini-omni-1.1-flash` 會被導到 1.2、以 1.2 計價 | 第三方 → **待驗證（官方 deprecations 頁）** |
| Omni 不支援 | system instructions、temperature、top_p、stop sequences、negative prompt 參數；上傳音訊／音訊參考；語音編輯 | 官方文件 |
| 語言 | 只完整支援英文，其他語言未評估 | 官方文件 |
| `thought` step | REST 回應的 `steps` 內有 `"type": "thought"` | 官方文件 → **E1 查是否計費** |
| `store=false` | 會讓產出影片無法在後續 turn 用 `previous_interaction_id` 編輯 | 官方文件 |
| 大檔 | >4MB 用 `response_format.delivery = "uri"`；`GET /interactions/{id}` 仍回 inline base64 | 官方文件 |
| 上傳影片編輯／延伸 | EEA／瑞士／英國不可；上傳影片 ≤10 s | 官方文件 |
| 參考素材上限 | 最多 5 張圖 + 3 段影片（影片參考每段 ≤3 s，音訊被忽略） | 官方 + 第三方 |
| Veo 3.1 | `generateVideos` + long-running operation 輪詢；8 s；720p/1080p/4K；原生音訊；首尾幀、reference images、extension；有 Fast、Lite 變體 | 官方 |
| Veo 3.1 Lite 價格 | 720p $0.05/s（Google 最便宜的影片選項） | 官方 |
| Veo 確切 model ID、Standard/Fast 牌價、是否支援 seed | — | **待驗證（E0）** |
| 品質爭議 | 實測評論多說 Veo 3.1 Standard 單鏡頭電影感較好；第三方引用 Arena 盲測 T2V：Omni 1.1 Flash 1516 vs Veo 3.1 1364 | 第三方，互相矛盾 → **E2 自己盲測** |
| Omni Pro | 已預告、未發布 | 第三方 |

---

## 2. 前置

- **Secret**：`GEMINI_API_KEY`（付費層；Omni 沒有 free tier）。不 commit、不印進 log。
- **連線**：先確認 sandbox 連得到 `generativelanguage.googleapis.com`。被擋就停下回報，不要找別的路繞。
- **地區**：記錄 sandbox egress 國家。若在 EEA/UK/CH，E6 上傳編輯會失敗；遇到 `User location is not supported` 類 400 記為環境問題，不是模型問題。
- **套件**：Python + 最新 `google-genai`（要有 `client.interactions`）；`ffmpeg`/`ffprobe` 量實際時長、解析度、音軌、抽影格。
- **文件抓取**：ai.google.dev 部分頁面擋自動抓取，可試 `.md.txt` 版本，例如 `https://ai.google.dev/gemini-api/docs/video.md.txt`。
- **Model ID 規矩**：先 `GET /v1beta/models` 確認存在才寫進 config，不准憑記憶填。

---

## 3. 花錢保險絲（任何付費呼叫之前先做完）

1. **單一事實來源** `config.yaml`：model IDs、價表（用牌價不用促銷價，可覆寫）、全域預算、各實驗 cap。
2. **全專案上限 US$80**（建議值，Clarence 可改）；各實驗 cap 見第 5 節。超過就停並回報，不自動加碼。
3. **先估價 → 寫 ledger → 呼叫 → 影片與 usage metadata 先落檔 → 才能發下一筆**。
4. **重試上限 2**；同一 spec 連續失敗標 `failed` 不再重排；重排不得重置計數。
5. `ledger/spend.jsonl` 每筆：`ts, exp, model, prompt_id, rep, params, est_cost, usage{input, output, thought, video}, latency_s, status, error`。
6. 一支指令即時印出累計花費（按實驗 × 模型拆）。
7. 預設不跑 4K、不大量跑 Veo Standard；某實驗真的需要才開，並先回報。
8. 預算用到 70% 時停下回報。

---

## 4. 方法論規矩

- **同設定至少 3 reps**，先量同設定的自然變異，再談模型差異（n=1 可能給出反向結論）。
- **一致 ≠ 正確**：自動指標（ffprobe、影格 embedding 相似度、SSIM）只當輔助，必須配人工目視。
- **盲測**：審片頁隨機排序、隱藏模型名；Clarence 打完分才揭曉。
- **對齊條件**：主要對照用 8 s（Veo 上限）、720p、16:9，除非實驗本身在測長度或解析度。
- **Prompt 版本化**：放 `prompts/*.yaml`，`prompt_id` 不變；改字就開新 id。
- **可重現**：Veo 若支援 seed 就固定並記錄；Omni 不支援 temperature，接受隨機性，靠 reps 補。

---

## 5. 實驗清單

建議順序：**E0 → E1 →（回報）→ E7 → E2 → E3 → E4 → E5 → E6 → E8**。E7 有 12/3 期限，提前。

### E0 環境／ID／價格驗證（cap $3）
- `GET /v1beta/models`：列出可用的 Omni 與 Veo ID，寫入 config。
- 官方 pricing 頁：抓 Omni 1.1/1.2、Veo 3.1 Standard/Fast/Lite 各解析度價格。
- 官方 deprecations 頁：確認 12/3 導流是否屬實。
- 查 Veo 是否支援 seed、negative prompt。
- 每個模型 smoke 1 次（最短秒數、最低解析度）。
- **出口**：config 完整；單次實際成本 vs 牌價誤差；若與第 1 節不符就更新本文件，並重算第 5 節預算。

### E1 計費解剖（cap $3）
- Omni 1.2 同一 prompt 跑 3 次：記錄所有 usage 欄位（有沒有 thought tokens）、延遲。
- `background` / `store` / `stream` 組合 2–3 種，比延遲。
- Clarence 隔天手動對 AI Studio / Cloud Billing 用量。
- **出口**：每秒實際成本公式；thought 是否另計。
- **E1 做完停下回報**，再開 E2 之後的實驗。

### E7 1.1 → 1.2 回歸（cap $6，**2026-12-03 前完成**）
- 3 個 prompt：timecode 語法（`[0-3s] ...`）、單一連續鏡頭指令、畫面文字渲染。
- 1.1 vs 1.2 各 3 reps；比較鏡頭切法、節奏、實際時長、文字正確率。
- 若跑的時候導流已生效，在結果裡標註「1.1 結果不可信」。

### E2 文字生影片品質盲測（cap $30）
- 6 個 prompt（見第 6 節）。
- `{Omni 1.2, Veo 3.1 Lite}` × 3 reps；`{Omni 1.1, Veo 3.1 Fast, Veo 3.1 Standard}` × 1 rep。
- 指標：人評 1–5（畫質、prompt 遵循、物理合理、音訊）、遵循 checklist、每支成本／延遲、ffprobe 實際規格。
- 產出：盲測審片頁。

### E3 中文（cap $8）
- 3 個 prompt × EN / zh-TW 兩版 × Omni 1.2 × 3 reps；Veo 3.1 Lite 各 1 rep 當對照。
- 檢查：zh-TW 對白（會不會變成簡中用語或大陸腔）、畫面繁中字卡正確率、zh prompt 的遵循度 vs EN。
- **出口**：中文 prompt 能不能直接用？字卡能不能信？

### E4 參考一致性（cap $8）
- 1 張商品圖 + 1 張人物圖（自己拍或有授權的素材；不用名人，可辨識人物本來就不支援）。
- 3 個不同場景 × {Omni 1.2, Veo 3.1 reference images} × 3 reps。
- 指標：人評一致性；抽影格與參考圖的 embedding 相似度（輔助）。

### E5 首尾幀 + 延伸：驗證文件矛盾（cap $10）
- **首尾幀**：同一組兩張圖；Omni 用 tag，Veo 用參數；比首尾幀命中度（SSIM + 人評）。
- **延伸**：8 s 基底延伸到約 30 s；Omni multi-turn extend vs Veo extension；看接縫、角色漂移、音訊連續性。
- **出口**：「延伸和尾幀控制要用 Veo」這條官方建議還成不成立。

### E6 對話式編輯（Omni only，cap $6）
- 生成 1 支 → 連續 3 輪編輯（換顏色 → 換背景 → 改光線），每輪都加 "Keep everything else the same."；量未提及元素的漂移。
- 1.1 vs 1.2 各一輪對照（官方說 1.2 的多輪編輯更穩）。
- 上傳一支 ≤10 s 的影片編輯 1 次（素材由 Clarence 提供，或用 E2 產物）。

### E8 草稿 → upscale 成本路徑（cap $4）
- 360p 草稿 + upscale 到 1080p vs 直接產 1080p：比成本與畫質。

**合計 cap 約 $78 → 全專案上限 $80。**

---

## 6. 種子 prompt（E2 用，英文；CC 可微調，但要版本化）

| id | 類型 | 種子 |
|---|---|---|
| p01 | 商品 hero 單鏡頭 | Continuous single shot, slow orbit around a matte black wireless earbud case on a wet stone surface, soft rim light, shallow depth of field. No dialogue, subtle ambient sound. |
| p02 | 人物對白 | Medium shot, a woman in a small café says: "I didn't expect you to come back." Natural lip-sync, room tone, light rain outside. |
| p03 | 複雜運鏡 | One continuous unbroken drone shot that starts above a night market, descends through hanging lanterns, and ends at eye level on a food stall. No cuts. |
| p04 | 多鏡頭敘事 | [0-3s] A runner ties her shoes at dawn. [3-6s] Close-up of feet hitting pavement. [6-8s] Wide shot of her crossing a bridge as the sun rises. Upbeat music. |
| p05 | 物理互動 | A glass of water is knocked off a table in slow motion; water splashes and the glass shatters realistically on a tiled floor. |
| p06 | 工業場景 | Factory floor, an autonomous mobile robot carries a tray of PCBs past an SMT line; operators in ESD smocks; steady tracking shot; machine hum. |

E3 的 zh-TW 版由 CC 從 p01、p02 加一個「畫面文字」prompt 翻成台灣用語版本；畫面文字要指定確切內容，例如招牌寫「台北夜市」。

---

## 7. Repo 結構（建議）

```
omnipoc/
  config.yaml            # model IDs、價表、預算（單一事實來源）
  prompts/*.yaml
  assets/                # 參考圖（大檔 gitignore）
  src/
    clients/omni.py      # Interactions API
    clients/veo.py       # generateVideos + 輪詢
    common.py            # 統一介面 generate(spec) -> Result
    budget.py            # 估價、ledger、cap
    probe.py             # ffprobe／抽影格
    run.py               # 依實驗跑矩陣
  runs/<exp>/<run_id>/meta.json   # 影片本體 gitignore
  ledger/spend.jsonl     # 要 commit
  review/index.html      # 盲測審片頁（純靜態，手機能看）
  REPORT.md
  docs/decisions.md
```

**待決（開工前問 Clarence）**：影片放哪裡讓他在 Chromebook／手機上審片？
- A：Cloudflare R2 + 靜態審片頁
- B：轉成 360p 低碼率預覽進 repo，總量壓在 200MB 內

---

## 8. 交付物

- `REPORT.md`：每個實驗一段結論 + 數字表，所有數字附 `run_id`；最後一節是「場景 → 模型」建議表。若跟本文件第 1 節的推論衝突，明寫推翻了什麼。
- `ledger/spend.jsonl` + 花費總表（按實驗 × 模型）。
- `review/index.html` 盲測頁 + 評分紀錄。
- 不做 HTML 報告；之後若要對外發布，另外處理。

---

## 9. 什麼時候停下來問 Clarence

- E1 完成時（固定回報點）。
- 預算用到 70%。
- E0 查到的 ID 或價格跟本文件不符，導致預算估算差距超過 30%。
- API 連不到，或被地區限制擋下。
- 需要真人素材或上傳素材。
- 要開 4K，或要大量跑 Veo Standard。

---

## 10. Sources

- Video generation overview — https://ai.google.dev/gemini-api/docs/video
- Gemini Omni Flash guide — https://ai.google.dev/gemini-api/docs/omni
- Omni 1.2 Flash model page (Cloud) — https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/omni-1-2-flash
- Omni 1.2 Flash GA (Google Cloud Blog) — https://cloud.google.com/blog/products/ai-machine-learning/gemini-omni-1-2-flash-generally-available
- Omni 1.2 Flash (Google Blog) — https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-omni-1-2-flash/
- Unite.AI GA 報導（價格與 token 計量）— https://www.unite.ai/googles-gemini-omni-1-2-flash-reaches-general-availability/
- 1.1 → 1.2 導流（第三方，待驗證）— https://dev.to/hassann/what-is-gemini-omni-12-flash-j4l
- Arena 對照（第三方）— https://unifically.com/ja/blogs/gemini-omni-1.1-flash-vs-veo-3.1
- Veo 3.1 Lite 價格 — https://wavespeed.ai/blog/ko/posts/ai-video-generation-news-2026/
