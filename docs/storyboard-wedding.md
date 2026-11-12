# 分鏡完整描述 — 兩條河之間（暫名）（v1）

> 由 `src/storyboard.py` 從 `prompts/wedding/storyboard.yaml` 產生，改內容請改 YAML 後重跑。
> 原始分鏡由 Clarence 提供；本文件補上每個鏡頭的製作方式、Omni prompt、參考圖、聲音與字幕時間。

## 0. 總覽

| 項目 | 數值 |
|---|---|
| 片長 | 300 秒，14 段 |
| Omni 影片鏡頭 | 24 支，共 267 秒（單支 3–15 秒） |
| 圖片鏡頭 | 3 張（Ken Burns／合成底圖） |
| 參考圖 | 角色 6 張（生成）＋地點 9 張（8 張建議用實拍照片） |
| 旁白／口白 | 7 句，TTS（gemini-3.8-flash-tts） |
| 配樂 | 5 段 Lyria |
| 輸出 | 16:9，草稿 360p，定稿 720p |

**估價（美金）**

| 項目 | 算法 | 費用 |
|---|---|---|
| Omni 草稿 | 267 秒 × 2 支 × $0.0243/s（360p，measured） | $12.98 |
| Omni 定稿 720p | 267 秒 × 1.2 支 × $0.0707/s（measured） | $22.65 |
| 參考圖＋圖片鏡頭 | 10 張 × 2 次 × $0.0673 | $1.35 |
| TTS | 約 100 字 ÷ 4.5 字/秒 × 3 次 | $0.01 |
| 配樂 | Lyria × 2 次 | $0.72 |
| **合計（720p 定稿＋本機放大到 1080p）** | | **$37.71** |
| 合計（改用 Google 1080p 定稿，$0.1061/s） | | $49.05 |
| 若地點也全部用生成（沒有照片） | 另加 8 張 × 2 次 | +$1.08 |

估價假設每支影片 2 支 360p 草稿、平均 1.2 支定稿；草稿和定稿是分開生成的兩支，不是把草稿放大。單價取自 `ledger/spend.jsonl` 的實測。

## 1. 製作流程

1. **參考圖**：角色 6 張用 Nano Banana 2 生成（`prompts/wedding/refs.yaml`），先出正面再用它當參考出 3/4 與全身；地點優先放實拍照片到 `refs/wedding/`。
2. **草稿**：每支 Omni 鏡頭用 360p 跑 2 支（`python3 src/run.py --exp W1 --model omni_12 --spec prompts/wedding/videos.yaml --res 360p`），挑方向。
3. **定稿**：選定的鏡頭用同一組 prompt 和參考圖跑 720p；每支過 `cropdetect` 檢查 letterbox。
4. **圖片鏡頭與圖形**：`stills.yaml` 出圖；聊天泡泡、字幕、拍立得、心型、Married! 都在後製做，不讓 Omni 寫字。
5. **聲音**：Omni 只留環境音（每支 prompt 已禁止對白與音樂）；旁白用 TTS，配樂用 Lyria，ffmpeg 混音並在旁白下 ducking。
6. **組裝**：ffmpeg 依本文件的時間軸剪接、疊字、混音，最後放大到 1080p。

## 2. 全片設定

**風格（自動附加到每支 Omni prompt）**

```text
Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame.
```

**角色**

- **she**：女主・永和女生，20 代後半，及肩黑直髮、空氣瀏海，淡妝，纖細
- **he**：男主・三重男生（雲林出身），20 代後半，短黑髮、細黑框眼鏡，笑容親切，中等身材

**聲音角色（TTS）**

- **旁白**：成熟溫暖的女聲或中性聲（也可直接用女主聲音，見待決問題）
- **女主**：年輕、柔和、帶笑意的女聲
- **男主**：年輕、溫和、略害羞的男聲

**字型**

- 一般字幕：Noto Sans TC / Noto Serif TC（OFL）
- 2D 文青字體（第 11 段）：jf open 粉圓 或 芫荽 Iansui（OFL）
- 拍立得手寫（第 6 段）：芫荽 Iansui（OFL）

**參考圖清單**

| id | 類型 | 內容 | 來源 |
|---|---|---|---|
| `she-front` | 角色 | 女主・永和女生 | Nano Banana 生成 |
| `she-34` | 角色 | 女主・永和女生 | Nano Banana 生成 |
| `she-full` | 角色 | 女主・永和女生 | Nano Banana 生成 |
| `he-front` | 角色 | 男主・三重男生（雲林出身） | Nano Banana 生成 |
| `he-34` | 角色 | 男主・三重男生（雲林出身） | Nano Banana 生成 |
| `he-full` | 角色 | 男主・三重男生（雲林出身） | Nano Banana 生成 |
| `loc-bridge` | 地點 | 新北大橋（大漢溪） | **實拍照片**（備案：生成） |
| `loc-bopiliao` | 地點 | 剝皮寮歷史街區 | **實拍照片**（備案：生成） |
| `loc-guesthouse` | 地點 | 台北賓館外（夜） | **實拍照片**（備案：生成） |
| `loc-4444` | 地點 | 四四南村 | **實拍照片**（備案：生成） |
| `loc-park4` | 地點 | 永和四號公園噴水池（夜） | **實拍照片**（備案：生成） |
| `loc-riverside` | 地點 | 永和河濱公園／河堤 | **實拍照片**（備案：生成） |
| `loc-sanheyuan` | 地點 | 雲林老家三合院 | **實拍照片**（備案：生成） |
| `loc-school` | 地點 | 男主母校（男校）校門 | **實拍照片**（備案：生成） |
| `loc-paddy` | 地點 | 雲林稻田晨光 | Nano Banana 生成 |

## 3. 逐段分鏡

### 01 · 0–15 秒 · 日出・新北大橋

- **原分鏡畫面**：【日出】新北大橋遠景，橋面車流慢速疊化至大漢溪水面反射
- **劇情／字幕／旁白**：旁白「在兩條河的交會，一座橋讓兩顆心每天相遇。」
- **鏡頭運動與轉場**：航拍→輕推進；淡入
- **音樂／環境音**：純鋼琴・溫暖前奏

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w01-bridge` | Omni 影片 | 15 | 0–15 全段；0–2 秒由黑淡入 | `loc-bridge` | $2.00 |

**`w01-bridge`**：日出航拍新北大橋，車流緩慢；後段鏡頭下搖到大漢溪水面，橋與朝霞的倒影。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location (match this place). Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. [0-9s] Aerial drone shot at sunrise of the long river bridge from the location reference, light traffic moving slowly across it, golden early light and thin mist over the wide river; the drone glides forward and gently descends. [9-15s] The camera tilts down from the bridge deck to the calm river surface, where the bridge, the pink sky and the rising sun are mirrored, soft ripples breaking the reflection. Slow, smooth, one continuous shot. Audio: only ambient sound — soft morning wind, distant traffic hum, water lapping. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 3–10 | 旁白／口白（旁白） | 在兩條河的交會，一座橋讓兩顆心每天相遇。 | TTS 語氣：warm, calm, unhurried |
| | 配樂 | M1 開始（鋼琴前奏） | |

> ⚠️ 地理：新北大橋跨的是大漢溪、連接板橋與新莊，並不在永和與三重之間；大漢溪與新店溪的「兩河交會」在華江橋一帶。旁白是象徵用法可以保留，但在地觀眾會注意到。

### 02 · 15–35 秒 · 她，永和；他，三重（分割畫面）

- **原分鏡畫面**：左：永和女方準備出門，窗外台北 101。右：三重男方背包上肩，踏出宿舍
- **劇情／字幕／旁白**：字幕「她，永和；他，三重。」101 映入眼簾→女方微笑
- **鏡頭運動與轉場**：兩邊各自手持跟拍；中線滑動推近收成單畫面
- **音樂／環境音**：鍋鏟聲、拉拉鍊細節→淡化回音樂

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w02a-she-ready` | Omni 影片 | 10 | 15–25 分割畫面左半（裁中間 640×720） | `she-front`, `she-34`, `she-full` | $1.33 |
| `w02b-he-leave` | Omni 影片 | 10 | 15–25 分割畫面右半（裁中間 640×720） | `he-front`, `he-34`, `he-full` | $1.33 |
| `w02c-she-101` | Omni 影片 | 8 | 25–27 中線滑開轉場、27–35 全畫面 | `she-front`, `she-34` | $1.07 |

**`w02a-she-ready`**：永和小公寓清晨，她綁頭髮、檢查包包、從架上拿鑰匙；廚房傳來鍋鏟聲。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 to 3 show the woman (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Early morning in a small, cozy apartment in Yonghe. The woman from the reference images, wearing the cream knit cardigan, ties her hair back, checks her tan crossbody bag and picks up her keys from a shelf. Handheld follow shot. Keep her and all of her action inside the central third of the frame at all times, because the frame will be cropped to a narrow vertical strip. Audio: only ambient sound — a frying pan sizzling and a spatula scraping in the kitchen nearby, keys jingling. No dialogue, no speech, no singing, no music.
```
</details>

**`w02b-he-leave`**：三重宿舍清晨，他把黑色背包甩上肩、拉上拉鍊，開門走進走廊。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 to 3 show the man (keep the same face, hair and build). The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Early morning in a simple shared university dormitory room in Sanchong. The man from the reference images swings his black backpack onto his shoulder, zips its front pocket shut, opens the door and steps out into the corridor. Handheld follow shot. Keep him and all of his action inside the central third of the frame at all times, because the frame will be cropped to a narrow vertical strip. Audio: only ambient sound — a zipper closing, the door latch, footsteps, distant scooters outside. No dialogue, no speech, no singing, no music.
```
</details>

**`w02c-she-101`**：她走到窗邊，遠方晨霧中的台北 101；鏡頭從肩後推到側臉，她微微一笑。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. The woman from the reference images steps to her apartment window; far away through the glass, Taipei 101 rises above the city in soft morning haze. She pauses and smiles softly. Slow push-in from behind her shoulder around to her smiling profile. Audio: only ambient sound — quiet room tone, faint city outside. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 16–24 | 字幕 | 她，永和； | 左半下方 |
| 16–24 | 字幕 | 他，三重。 | 右半下方 |
| | 配樂 | M1 持續（壓低，讓鍋鏟與拉鍊聲出來） | |

**剪接**：15–25 左右並排；25–27 中線往右滑把右半推出畫面，收成 w02c 單畫面；兩支的環境音在 25–28 淡出、鋼琴回來。

> ⚠️ 分割畫面裁切：每支 1280×720 只取中間 640 寬，prompt 已要求動作留在中間三分之一；仍要用草稿確認。

### 03 · 35–55 秒 · 橋上錯身

- **原分鏡畫面**：公車駛上新北大橋→橋上對向車窗內，兩人視線交錯；遠景中正橋、河濱、自行車道
- **劇情／字幕／旁白**：旁白「走過大橋，看見 101，就像回到家。」
- **鏡頭運動與轉場**：車內搖鏡→Cut 連跳；最後定格 101
- **音樂／環境音**：弦樂層次加入

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w03-buses` | Omni 影片 | 15 | 35–50 全段 | `she-front`, `she-34`, `he-front`, `he-34`, `loc-bridge` | $2.00 |
| `w03-freeze` | 定格（ffmpeg） | 5 | 50–55 取 w03 最後一格定格 + 緩慢推近 | — | $0 |

**`w03-buses`**：公車上橋→她在車窗邊→兩車在橋上交會、隔著兩層車窗四目相接→連跳河濱、自行車道、遠方另一座橋，停在 101。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build); image 5 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. [0-4s] Exterior, morning: a city bus drives up onto the long river bridge from the location reference, the river and riverside bike paths below, another bus approaching from the opposite direction. [4-8s] Inside the first bus: the woman sits by the window in morning light, watching the river; the camera pans slowly along the window. [8-11s] The two buses pass each other on the bridge; through two layers of bus windows, the woman and the man, who sits in the other bus, catch each other's eyes for a brief moment. [11-15s] Quick jump cuts seen through the bus window: the riverside park, cyclists on the bike path, another bridge in the distance, ending on a clear view of Taipei 101 on the skyline. Audio: only ambient sound — bus engine, air brakes hissing, soft city hum. No dialogue, no speech, no singing, no music.
```
</details>

**`w03-freeze`**：定格在 101，ffmpeg 慢推。

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 44–50 | 旁白／口白（旁白） | 走過大橋，看見 101，就像回到家。 | TTS 語氣：warm, smiling |
| | 配樂 | M1 在 ~40 秒加入弦樂 | |

> ⚠️ 遠景的中正橋不點名（模型不認得），prompt 寫成 another bridge。

### 04 · 55–70 秒 · 聊天泡泡

- **原分鏡畫面**：手機聊天泡泡動畫覆疊：男方「妳喜歡日式水果蛋糕嗎？」→女方「女生拒絕不了甜點呀！」
- **劇情／字幕／旁白**：卡通 Pop-up 字卡
- **鏡頭運動與轉場**：Push in 至手機→閃白轉場
- **音樂／環境音**：木琴可愛點綴

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `st-phone` | 圖片（Ken Burns） | 15 | 55–69 Ken Burns 推近；聊天泡泡合成在螢幕區；69–70 閃白 | — | $0.13 |

**`st-phone`**：她手拿手機的特寫照（螢幕留白），泡泡和貼圖後製貼上去，不用影片。

<details><summary>Nano Banana prompt</summary>

```text
Close-up of the woman's hands (from the reference image) holding a smartphone upright in a cozy room at night, warm lamp light. The phone screen faces the camera, is in sharp focus, and is completely blank, plain light grey, with no interface, no text and no icons. Background softly blurred. Photo-real, no text.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 58 | 圖形 | 妳喜歡日式水果蛋糕嗎？ | 左側灰泡泡（他） |
| 61–62 | 圖形 | 「…」輸入中 | 右側 |
| 63 | 圖形 | 女生拒絕不了甜點呀！ | 右側綠泡泡（她） |
| 65 | 圖形 | 卡通蛋糕／愛心 pop-up 貼圖 | 螢幕外緣彈出 |
| | 配樂 | M2（木琴短曲） | |

> ⚠️ 泡泡用 HTML 排版再以 Playwright 逐格輸出 PNG 序列，或 ffmpeg drawbox+drawtext；字型用 Noto Sans TC。

### 05 · 70–90 秒 · 初次見面・日式蛋糕店

- **原分鏡畫面**：近鏡：叉子切下草莓蛋糕；拉出 2 Shot 對坐
- **劇情／字幕／旁白**：女方旁白「甜點，是我們的序章。」
- **鏡頭運動與轉場**：Slide Out 至 45° 高角度
- **音樂／環境音**：Café ambience

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w05a-cake` | Omni 影片 | 12 | 70–82 | `she-front`, `she-34`, `he-front`, `he-34` | $1.60 |
| `w05b-cake-high` | Omni 影片 | 8 | 82–90 | `she-front`, `she-34`, `he-front`, `he-34` | $1.07 |

**`w05a-cake`**：叉子切草莓鮮奶油蛋糕的微距→平順拉遠，兩人在窗邊小木桌對坐，有點害羞地笑。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. [0-5s] Macro close-up: a fork slices into a Japanese strawberry shortcake, soft sponge, whipped cream and a glossy strawberry. [5-12s] The camera pulls back smoothly in one continuous move to reveal the woman and the man sitting across from each other at a small wooden table by the window of a bright, minimal Japanese-style cake shop, both a little shy, smiling at each other. Audio: only ambient sound — café chatter murmuring, cups and saucers clinking, a soft espresso machine. No dialogue, no speech, no singing, no music.
```
</details>

**`w05b-cake-high`**：鏡頭側滑並升到 45° 俯角，兩人邊吃邊笑。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. The camera slides sideways and rises to a 45-degree high angle above the small table in the Japanese cake shop; the woman and the man share the strawberry shortcake, laughing easily together. Audio: only ambient sound — café chatter murmuring, cups and saucers clinking. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 78–84 | 旁白／口白（女主） | 甜點，是我們的序章。 | TTS 語氣：soft, smiling, intimate |
| | 配樂 | M3 開始（輕木吉他，壓在 café 環境音下） | |

### 06 · 90–110 秒 · 剝皮寮漫步

- **原分鏡畫面**：剝皮寮紅磚巷道漫步；逆光剪影對談
- **劇情／字幕／旁白**：字幕「歷史裡，寫下新的我們。」
- **鏡頭運動與轉場**：手持跟隨→定格拍立得效果
- **音樂／環境音**：Acoustic guitar

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w06-bopiliao` | Omni 影片 | 15 | 90–105 | `she-front`, `he-front`, `loc-bopiliao` | $2.00 |
| `w06-polaroid` | 定格（ffmpeg） | 5 | 105–110 定格→加白框、微傾、陰影變拍立得，快門聲 | — | $0 |

**`w06-bopiliao`**：午後紅磚騎樓巷，兩人背對鏡頭並肩慢走、逆光成剪影、邊走邊聊；手持從後跟拍。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the woman (keep the same face, hair and build); image 2 shows the man (keep the same face, hair and build); image 3 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Late afternoon in the old red-brick arcade street from the location reference. The woman and the man walk slowly side by side away from the camera toward the low sun, backlit into near-silhouettes, talking and gesturing as they go. Handheld follow shot from behind. Audio: only ambient sound — footsteps on brick, distant city murmur, a bicycle bell far away. No dialogue, no speech, no singing, no music.
```
</details>

**`w06-polaroid`**：取 w06 一格做成拍立得，字幕寫在相紙下緣。

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 105–110 | 字幕 | 歷史裡，寫下新的我們。 | 拍立得下緣，手寫感字體 |
| | 音效 | 拍立得快門聲（105） | |
| | 配樂 | M3 木吉他 | |

### 07 · 110–130 秒 · 三重迴轉壽司

- **原分鏡畫面**：迴轉壽司吧檯：男方趁空位把女方抱到大腿上；女方臉紅特寫
- **劇情／字幕／旁白**：無字幕，放大心跳聲 FX
- **鏡頭運動與轉場**：慢動作＋疊化心型動畫
- **音樂／環境音**：BGM 弱化，加入心跳

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w07a-sushi` | Omni 影片 | 10 | 110–120 | `she-front`, `she-34`, `he-front`, `he-34` | $1.33 |
| `w07b-blush` | Omni 影片 | 10 | 120–130 | `she-front`, `she-34`, `she-full` | $1.33 |

**`w07a-sushi`**：午餐尖峰，吧檯只剩一張椅子，他坐下拍拍大腿，她猶豫一下坐上去，又窘又笑；壽司盤從面前滑過。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. A busy conveyor-belt sushi bar in Sanchong at lunchtime. Every stool along the counter is taken except one. The man sits down on it, laughs and pats his lap; the woman hesitates, then sits on his lap, embarrassed and smiling, as plates of sushi glide past on the belt in front of them. Medium two-shot from across the belt. Audio: only ambient sound — restaurant buzz, the conveyor belt clattering softly, plates clinking. No dialogue, no speech, no singing, no music.
```
</details>

**`w07b-blush`**：慢動作臉部特寫，她臉紅低頭再抬眼害羞一笑。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 to 3 show the woman (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Extreme slow motion, close-up of the woman's face as she blushes and looks down, then lifts her eyes with a shy smile; warm light, the conveyor belt softly blurred behind her. Audio: only ambient sound — muffled restaurant buzz. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| | 疊加動畫 | 心型動畫疊化（120–130，跟心跳同步脈動） | |
| | 音效 | 心跳聲（118–130，逐漸放大） | |
| | 配樂 | M3 壓低到 −18 dB | |

### 08 · 130–150 秒 · 台北賓館外・牽手

- **原分鏡畫面**：台北賓館外夜色：兩人並肩而行，男方小指碰觸→牽手成功
- **劇情／字幕／旁白**：男方旁白「原來手心的溫度，是這樣的剛好。」
- **鏡頭運動與轉場**：移動長鏡頭→鏡頭上移對剪塔尖
- **音樂／環境音**：弦樂再次漸起

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w08-guesthouse` | Omni 影片 | 15 | 130–145 | `she-front`, `she-34`, `he-front`, `he-34`, `loc-guesthouse` | $2.00 |
| `st-tower` | 圖片（Ken Burns） | 5 | 145–150 對剪塔尖，慢速上推 | — | $0.13 |

**`w08-guesthouse`**：夜裡沿台北賓館鐵欄外的人行道並肩走（側面長鏡頭）→手部特寫：小指碰到、牽起→鏡頭從牽著的手上搖到夜空。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build); image 5 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. [0-8s] Night, outside the ornate white mansion behind its black iron fence from the location reference: the woman and the man walk side by side along the tree-lined sidewalk; a long, smooth tracking shot from the side. [8-12s] Close-up of their hands swinging between them: his little finger brushes hers, hesitates, then their hands clasp. [12-15s] The camera tilts up from their joined hands to the treetops and the night sky. Audio: only ambient sound — quiet night traffic far away, footsteps, leaves rustling. No dialogue, no speech, no singing, no music.
```
</details>

**`st-tower`**：塔尖夜景照片做 Ken Burns。

<details><summary>Nano Banana prompt</summary>

```text
Low-angle night view of the illuminated central tower of the red-brick Presidential Office Building in Taipei, deep blue night sky, photo-real, no readable text.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 138–145 | 旁白／口白（男主） | 原來手心的溫度，是這樣的剛好。 | TTS 語氣：shy, tender, low |
| | 配樂 | M3 弦樂漸起 | |

> ⚠️ 「塔尖」解讀為台北賓館旁總統府的中央塔；台北賓館本身沒有塔。若指別的建築要改。

### 09 · 150–180 秒 · 戲院→四四南村

- **原分鏡畫面**：戲院黑場→舞台燈亮；Cut 到四四南村戲後空地，兩人背靠背坐著笑談
- **劇情／字幕／旁白**：字幕「一次場景，兩段劇本，變成共同人生。」
- **鏡頭運動與轉場**：Hard-cut 隨鼓點
- **音樂／環境音**：BGM 一段高潮

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w09a-theatre` | Omni 影片 | 6 | 150–156 | `she-front`, `he-front` | $0.80 |
| `w09b-4444-wide` | Omni 影片 | 12 | 156–168（依鼓點切成 2–3 段） | `she-front`, `she-34`, `he-front`, `he-34`, `loc-4444` | $1.60 |
| `w09c-4444-close` | Omni 影片 | 12 | 168–180（依鼓點切） | `she-front`, `she-34`, `he-front`, `he-34`, `loc-4444` | $1.60 |

**`w09a-theatre`**：全黑→舞台燈啪地亮起；從後方看兩人坐在觀眾席的剪影。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the woman (keep the same face, hair and build); image 2 shows the man (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Inside a theatre: complete darkness, then the stage lights snap on and warm spotlights flood the stage. Seen from behind, the woman and the man sit side by side in the audience, silhouetted against the bright stage. Audio: only ambient sound — an audience hush, the clunk of stage lights switching on. No dialogue, no speech, no singing, no music.
```
</details>

**`w09b-4444-wide`**：黃昏四四南村草地，背後就是 101；兩人背靠背坐著大笑，鏡頭繞弧。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build); image 5 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Dusk at the old village houses and lawn from the location reference, Taipei 101 rising directly behind. The woman and the man sit back to back on the grass, laughing and leaning their weight against each other. Slow arc shot around them. Audio: only ambient sound — evening breeze, distant city, crickets starting. No dialogue, no speech, no singing, no music.
```
</details>

**`w09c-4444-close`**：三個近景：她笑、他笑、兩人肩膀相靠。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build); image 5 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. [0-4s] Close-up of the woman laughing, head tilted back against the man's shoulder, 101 softly out of focus behind. [4-8s] Close-up of the man laughing, eyes closed. [8-12s] Close-up of their shoulders and backs pressed together, her hand finding his on the grass. Audio: only ambient sound — evening breeze, crickets. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 160–170 | 字幕 | 一次場景，兩段劇本，變成共同人生。 | 下方置中 |
| | 配樂 | M4 高潮段 | |

**剪接**：全部 hard-cut 對齊 M4 的鼓點（用 librosa 抓 beat 或手動標）。

### 10 · 180–205 秒 · 永和四號公園・告白

- **原分鏡畫面**：夜幕中的永和四號公園噴水池：男方在燈光前告白；女方點頭
- **劇情／字幕／旁白**：男方口白＋女方輕笑
- **鏡頭運動與轉場**：手持環繞 360°→煙火閃光轉場
- **音樂／環境音**：鋼琴與弦樂交織

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w10a-fountain` | Omni 影片 | 15 | 180–195 | `she-front`, `she-34`, `he-front`, `he-34`, `loc-park4` | $2.00 |
| `w10b-fireworks` | Omni 影片 | 10 | 195–205；最後一格閃白接下一段 | `she-front`, `she-34`, `he-front`, `he-34` | $1.33 |

**`w10a-fountain`**：噴水池燈光前，他對她認真說話（大多從他肩後看她的反應），手持繞兩人一整圈；她掩嘴輕笑、點頭。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build); image 5 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Night in the neighborhood park from the location reference, the lit fountain shooting colored jets of water behind them. The man stands facing the woman and speaks to her earnestly; we mostly see him from behind his shoulder and see her reaction. The handheld camera slowly orbits a full 360 degrees around the two of them. She covers her mouth, laughs softly, then nods. Audio: only ambient sound — splashing fountain water, a quiet park at night. No dialogue, no speech, no singing, no music.
```
</details>

**`w10b-fireworks`**：她含淚笑著點頭、兩人擁抱，天空煙火炸開照亮臉，最後一道閃光把畫面刷白。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. The woman nods with a teary smile and the two embrace; fireworks burst in the sky above the park, bright flashes lighting up their faces. In the final second a bright flash fills the whole frame with white. Audio: only ambient sound — fireworks booming and crackling, the fountain splashing. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 186–196 | 旁白／口白（男主） | （告白台詞，待 Clarence 提供） | TTS 語氣：earnest, nervous, warm |
| 197–199 | 旁白／口白（女主） | <laugh> | TTS 語氣：soft laugh |
| | 配樂 | M4 收成鋼琴＋弦樂 | |

> ⚠️ 告白是正面說話的戲：TTS 對不上嘴型，所以構圖以他的肩後、她的反應為主。原分鏡沒寫台詞，需要補。

### 11 · 205–225 秒 · 永和河濱・雙載

- **原分鏡畫面**：腳踏車雙載、風鈴聲；鏡頭帶出遠處 101
- **劇情／字幕／旁白**：無旁白，慢速 2D 文青字體「在河風裡，我們任意奔跑」
- **鏡頭運動與轉場**：穿越鏡
- **音樂／環境音**：清風與單車鏈條聲

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w11a-bike` | Omni 影片 | 12 | 205–217 | `she-front`, `she-34`, `he-front`, `he-34`, `loc-riverside` | $1.60 |
| `w11b-bike-away` | Omni 影片 | 8 | 217–225 | `she-front`, `he-front`, `loc-riverside` | $1.07 |

**`w11a-bike`**：鏡頭穿過前景的高草，出來後跟著他們：他騎車、她側坐後座扶著他的腰，頭髮被風吹起；對岸遠處 101。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build); image 5 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Golden late afternoon on the riverside bike path from the location reference. The camera pushes forward through tall riverside grass in the foreground and emerges tracking alongside a bicycle: the man pedals and the woman sits sideways on the rear rack, one hand on his waist, her hair blowing in the wind. Taipei 101 stands small on the distant skyline across the river. Audio: only ambient sound — a light breeze, the bicycle chain ticking, faint wind chimes. No dialogue, no speech, no singing, no music.
```
</details>

**`w11b-bike-away`**：輪子高度側跟，接著兩人騎遠、朝向天際線。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the woman (keep the same face, hair and build); image 2 shows the man (keep the same face, hair and build); image 3 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Low tracking shot at wheel height beside the bicycle on the riverside path, then the camera slows and lets the couple ride away toward the city skyline and the low sun. Audio: only ambient sound — a light breeze, the bicycle chain ticking, faint wind chimes. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 208–220 | 字幕 | 在河風裡，我們任意奔跑 | 畫面右側直排或下方，逐字淡入，2D 文青手寫字體 |
| | 配樂 | M5 開始（輕快木吉他） | |

### 12 · 225–255 秒 · 雲林老家・母校

- **原分鏡畫面**：雲林老家三合院門口合影；Cut 到男方大學男校門口；舊制服彩蛋
- **劇情／字幕／旁白**：字幕「從這裡啟程，載著所有祝福回台北。」
- **鏡頭運動與轉場**：Drone Rising→L-cut
- **音樂／環境音**：鄉村蟲鳴＋吉他

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w12a-sanheyuan` | Omni 影片 | 14 | 225–239 | `she-front`, `she-34`, `he-front`, `he-34`, `loc-sanheyuan` | $1.87 |
| `w12b-school` | Omni 影片 | 10 | 239–249；前 2 秒延續上一段的蟲鳴（L-cut） | `she-front`, `he-front`, `he-34`, `he-full`, `loc-school` | $1.33 |
| `st-uniform` | 圖片（Ken Burns） | 6 | 249–255 舊照片 Ken Burns（舊制服彩蛋），紙相片質感邊框 | — | $0.13 |

**`w12a-sanheyuan`**：三合院正門前，兩人和長輩們排好合影；空拍慢慢往後上升，露出整個院子和周圍稻田。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build); image 5 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Morning in rural Yunlin at the red-brick courtyard house from the location reference. The woman and the man stand at the main doorway with smiling elderly grandparents and parents, posing together for a family photo. The drone camera rises slowly up and back to reveal the whole courtyard and the green rice fields around it. Audio: only ambient sound — insects buzzing, a rooster far away, a soft breeze over the fields. No dialogue, no speech, no singing, no music.
```
</details>

**`w12b-school`**：母校校門前，他指著校門跟她講當年的事，她笑出來。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the woman (keep the same face, hair and build); images 2 to 4 show the man (keep the same face, hair and build); image 5 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. In front of the school gate from the location reference on a sunny day, the man points at the gate and tells the woman an old story; she laughs. Medium two-shot, gentle handheld. Audio: only ambient sound — cicadas, a quiet street, distant school bell. No dialogue, no speech, no singing, no music.
```
</details>

**`st-uniform`**：高中時期的他穿舊制服的「老照片」。

<details><summary>Nano Banana prompt</summary>

```text
A faded, slightly overexposed snapshot photo from about ten years ago: the man from the reference image as a 17-year-old high-school student, same face, younger, grinning at the camera in a light khaki short-sleeve Taiwanese school uniform shirt, standing in front of a school building. Film-photo look with soft vignetting. No readable text, name tag blank.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 228–236 | 字幕 | 從這裡啟程，載著所有祝福回台北。 | 下方置中 |
| | 配樂 | M5 鄉村吉他 | |

**剪接**：w12a → w12b 用 L-cut，蟲鳴延續到 w12b 前 2 秒。

> ⚠️ 母校名稱與校門牌匾若入鏡，Omni 會寫錯中文字；prompt 已要求無字，若出現就裁掉或後製蓋掉。

> ⚠️ 合影中的長輩是生成的路人臉；若要真的家人入鏡，需用照片並取得同意。

### 13 · 255–275 秒 · 戶政事務所

- **原分鏡畫面**：簽字、蓋章、領證書特寫；門口新人證書舉高
- **劇情／字幕／旁白**：女方旁白「紙張薄薄，愛卻滿溢。」
- **鏡頭運動與轉場**：閃亮字幕「Married！」
- **音樂／環境音**：管樂短暫歡呼

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w13a-registry` | Omni 影片 | 10 | 255–265 | `she-front`, `he-front` | $1.33 |
| `w13b-door` | Omni 影片 | 10 | 265–275 | `she-front`, `she-34`, `he-front`, `he-34` | $1.33 |

**`w13a-registry`**：筆簽名（字跡看不清）→紅印章蓋下抬起→櫃檯遞出證書，兩人的手接過。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the woman (keep the same face, hair and build); image 2 shows the man (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Inside a bright household registration office. [0-3s] Macro: a pen signs a form, the handwriting illegible. [3-6s] A red seal stamp presses down onto the paper and lifts away. [6-10s] A clerk's hands pass a certificate across the counter, and the woman's and the man's hands receive it together. No readable text on any document. Audio: only ambient sound — quiet office murmur, the soft thud of the stamp, paper rustling. No dialogue, no speech, no singing, no music.
```
</details>

**`w13b-door`**：戶政事務所門口，兩人一起把證書舉高、笑得燦爛，朋友在旁拍手。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: images 1 and 2 show the woman (keep the same face, hair and build); images 3 and 4 show the man (keep the same face, hair and build). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Outside the entrance of a household registration office on a sunny day, the woman and the man hold up their certificate together, beaming, as a few friends clap and cheer around them. The certificate faces away from the camera. Audio: only ambient sound — friends clapping and cheering, street ambience. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 257–263 | 旁白／口白（女主） | 紙張薄薄，愛卻滿溢。 | TTS 語氣：tender, quietly happy |
| 268–273 | 字幕 | Married! | 置中，閃亮粒子效果 |
| | 配樂 | M5 中段管樂短歡呼（~266） | |

### 14 · 275–300 秒 · 河堤日落 × 稻田晨光

- **原分鏡畫面**：① 永和河堤日落 ② 雲林稻田晨光，兩人牽手向前走→白屏字卡「to be continued…」
- **劇情／字幕／旁白**：無旁白，只聽腳步＋心跳，最後留白 1 秒
- **鏡頭運動與轉場**：Cross-fade
- **音樂／環境音**：音樂漸弱收尾

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w14a-levee` | Omni 影片 | 10 | 275–295 與 w14b 每 5 秒交錯 cross-fade | `she-front`, `he-front`, `loc-riverside` | $1.33 |
| `w14b-paddy` | Omni 影片 | 10 | 275–295 與 w14a 交錯 | `she-front`, `he-front`, `loc-paddy` | $1.33 |

**`w14a-levee`**：永和河堤日落，從背後看兩人牽手往夕陽走。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the woman (keep the same face, hair and build); image 2 shows the man (keep the same face, hair and build); image 3 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Sunset on the river levee path from the location reference. Seen from behind, the woman and the man walk forward hand in hand toward the setting sun, golden backlight, long shadows. Audio: only ambient sound — slow footsteps, a light breeze. No dialogue, no speech, no singing, no music.
```
</details>

**`w14b-paddy`**：雲林稻田清晨，從背後看兩人牽手走在田埂上，薄霧。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the woman (keep the same face, hair and build); image 2 shows the man (keep the same face, hair and build); image 3 shows the location (match this place). The woman is a Taiwanese woman in her late 20s with shoulder-length straight black hair and soft see-through bangs, light natural makeup, gentle eyes, slim build. The man is a Taiwanese man in his late 20s with short neat black hair and thin black rectangular glasses, a friendly smile, medium build. Live-action romantic short-film footage shot on location in Taipei and New Taipei, Taiwan. Natural, warm, slightly desaturated color grade with soft peach highlights and teal shadows, subtle 35mm film grain, shallow depth of field, cinematic 24fps look. Realistic people and places. No readable text, signs, captions or logos anywhere in the frame. Dawn over the misty green rice paddies from the location reference. Seen from behind, the woman and the man walk hand in hand along a narrow earthen ridge path into the soft morning light. Audio: only ambient sound — slow footsteps, morning birds, a light breeze. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 295–299 | 字幕 | to be continued… | 白屏置中，打字機式逐字出現 |
| | 音效 | 腳步聲＋心跳（275–299） | |
| | 音效 | 299–300 完全無聲 | |
| | 配樂 | M5 從 ~290 漸弱，297 前收完 | |

## 4. 聲音總表

**旁白／口白（TTS）**

| 時碼 | 聲音 | 台詞 | 語氣 |
|---|---|---|---|
| 3–10 | 旁白 | 在兩條河的交會，一座橋讓兩顆心每天相遇。 | warm, calm, unhurried |
| 44–50 | 旁白 | 走過大橋，看見 101，就像回到家。 | warm, smiling |
| 78–84 | 女主 | 甜點，是我們的序章。 | soft, smiling, intimate |
| 138–145 | 男主 | 原來手心的溫度，是這樣的剛好。 | shy, tender, low |
| 186–196 | 男主 | （告白台詞，待 Clarence 提供） | earnest, nervous, warm |
| 197–199 | 女主 | <laugh> | soft laugh |
| 257–263 | 女主 | 紙張薄薄，愛卻滿溢。 | tender, quietly happy |

**配樂（Lyria）**

| cue | 時碼 | 模型 | prompt |
|---|---|---|---|
| M1 | 0–55 | `lyria-3.5` | Warm, tender solo piano intro at about 72 bpm, hopeful and intimate; strings gently join after about 40 seconds |
| M2 | 55–70 | `lyria-3-clip-preview` | Playful, cute xylophone and pizzicato strings ditty, light and bouncy |
| M3 | 70–150 | `lyria-3.5` | Light romantic acoustic guitar with soft brushed drums, café feeling; warm strings slowly rise near the end |
| M4 | 150–205 | `lyria-3.5` | Cinematic romantic pop build with driving drums and a big emotional climax, then resolving into piano and strings |
| M5 | 205–300 | `lyria-3.5` | Breezy acoustic guitar with a pastoral countryside feel, a short joyful brass flourish in the middle, gentle fade-out ending |

**字幕與圖形**

| 時碼 | 內容 | 位置／樣式 |
|---|---|---|
| 16–24 | 她，永和； | 左半下方 |
| 16–24 | 他，三重。 | 右半下方 |
| 58 | 妳喜歡日式水果蛋糕嗎？ | 左側灰泡泡（他） |
| 61–62 | 「…」輸入中 | 右側 |
| 63 | 女生拒絕不了甜點呀！ | 右側綠泡泡（她） |
| 65 | 卡通蛋糕／愛心 pop-up 貼圖 | 螢幕外緣彈出 |
| 105–110 | 歷史裡，寫下新的我們。 | 拍立得下緣，手寫感字體 |
| 160–170 | 一次場景，兩段劇本，變成共同人生。 | 下方置中 |
| 208–220 | 在河風裡，我們任意奔跑 | 畫面右側直排或下方，逐字淡入，2D 文青手寫字體 |
| 228–236 | 從這裡啟程，載著所有祝福回台北。 | 下方置中 |
| 268–273 | Married! | 置中，閃亮粒子效果 |
| 295–299 | to be continued… | 白屏置中，打字機式逐字出現 |

## 5. 風險

- **兩個角色 × 24 支的一致性還沒驗證。** 我們只證明過 1 個角色加 1 個道具在 4 支定稿裡穩定。建議先用 360p 跑 3–4 支雙人鏡頭確認。
- **真實地標。** 台北 101 模型認得；其他地點沒有照片就只會「像」。
- **畫面中文字。** Omni 會把招牌、證書、校名寫錯；prompt 已要求無字，所有中文字一律後製。
- **正面說話的戲。** TTS 對不上嘴型；第 10 段告白已改成肩後與反應鏡頭。
- **Letterbox 黑邊。** prompt 禁止無效，定稿每支都要 `cropdetect`，有黑邊就裁切或全片統一加黑邊。
- **分割畫面裁切。** 第 2 段兩支要裁成窄條，動作必須留在中間三分之一。

## 6. 待決問題

- 這是真實的一對新人嗎？如果是，要用兩人的照片當角色參考圖（並取得兩人同意）；目前以 Nano Banana 生成的虛構角色撰寫。真人照片能否被 Omni 穩定還原、會不會被政策擋，需要先用 1 支草稿測。
- 地點照片：新北大橋、剝皮寮、台北賓館、四四南村、永和四號公園、永和河濱、雲林三合院、男主母校，最好用自己拍的照片當參考；生成的地點會「像」但不會是真的那個地方。台北 101 模型認得，不需要照片。
- 第 10 段告白台詞要補。
- 旁白要獨立一個聲音，還是直接用女主的聲音？
- 第 8 段「塔尖」是否指總統府中央塔？
- 新北大橋的地理位置（見第 1 段註記）要不要改成真正在兩河交會附近的橋？
