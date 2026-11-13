# 分鏡完整描述 — 兩條河之間（暫名）（v9）

> 由 `src/storyboard.py` 從 `prompts/wedding/storyboard.yaml` 產生，改內容請改 YAML 後重跑。
> 原始分鏡由 Clarence 提供；本文件補上每個鏡頭的製作方式、Omni prompt、參考圖、聲音與字幕時間。

## 0. 總覽

| 項目 | 數值 |
|---|---|
| 片長 | 300 秒，14 段 |
| Omni 影片鏡頭 | 28 支，共 282 秒（單支 3–15 秒） |
| 圖片鏡頭 | 0 張（Ken Burns／合成底圖） |
| 參考圖 | 34 張（已完成 32、待生成 2） |
| 旁白／口白 | 7 句，TTS（gemini-3.8-flash-tts） |
| 配樂 | 5 段 Lyria |
| 輸出 | 16:9，草稿 360p，定稿 720p |

**估價（美金）**

| 項目 | 算法 | 費用 |
|---|---|---|
| Omni 草稿 | 282 秒 × 2 支 × $0.0248/s（360p，measured） | $13.99 |
| Omni 定稿 720p | 282 秒 × 1.2 支 × $0.071/s（measured） | $24.03 |
| 參考圖＋圖片鏡頭 | 2 張 × 2 次 × $0.0673 | $0.27 |
| TTS | 約 141 字 ÷ 4.5 字/秒 × 3 次 | $0.02 |
| 配樂 | Lyria × 2 次 | $0.72 |
| **合計（720p 定稿＋本機放大到 1080p）** | | **$39.02** |
| 合計（改用 Google 1080p 定稿，$0.1066/s） | | $51.07 |

估價假設每支影片 2 支 360p 草稿、平均 1.2 支定稿；草稿和定稿是分開生成的兩支，不是把草稿放大。單價取自 `ledger/spend.jsonl` 的實測。

## 1. 製作流程

1. **參考圖**：角色取自 theplaybillv2 定案人物，用 Nano Banana 2 出便服三視圖；地點用維基共享資源的 CC 照片轉繪成同一風格；缺照片的地點直接生成（`prompts/wedding/refs.yaml`）。
2. **草稿**：每支 Omni 鏡頭用 360p 跑 2 支（`python3 src/run.py --exp W1 --model omni_12 --spec prompts/wedding/videos.yaml --res 360p`），挑方向。
3. **定稿**：選定的鏡頭用同一組 prompt 和參考圖跑 720p；每支過 `cropdetect` 檢查 letterbox。
4. **圖片鏡頭與圖形**：`stills.yaml` 出圖；聊天泡泡、字幕、拍立得、心型、Married! 都在後製做，不讓 Omni 寫字。
5. **聲音**：Omni 只留環境音（每支 prompt 已禁止對白與音樂）；旁白用 TTS，配樂用 Lyria，ffmpeg 混音並在旁白下 ducking。
6. **組裝**：ffmpeg 依本文件的時間軸剪接、疊字、混音，最後放大到 1080p。

## 2. 全片設定

**風格（自動附加到每支 Omni prompt）**

```text
Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow.
```

**角色**

- **she**：女主（取自 theplaybillv2 定案人物）：約 4 頭身，公主頭半束深棕波浪長髮、圓臉腮紅、閉嘴微笑。便服＝燕麥色針織毛衣、鼠尾草綠百褶長裙、白布鞋、棕色斜背小包；登記日＝粉色針織外套、象牙白長洋裝、象牙白瑪莉珍鞋、捧花
- **he**：男主（取自 theplaybillv2 定案人物）：約 4 頭身，黑框方眼鏡、後梳短黑髮、圓臉。便服＝海軍藍襯衫外套敞開、白 T、卡其褲、白布鞋、黑後背包；登記日＝黑色休閒西裝、白色圓領 T、黑皮鞋

**聲音角色（TTS）**

- **旁白**：獨立的第三個聲音（Clarence 指定）：沉穩、溫暖、略帶說書感的中性聲線，跟男女主都明顯不同
- **女主**：年輕、柔和、帶笑意的女聲
- **男主**：年輕、溫和、略害羞的男聲

**字型**

- 一般字幕：Noto Sans TC / Noto Serif TC（OFL）
- 2D 文青字體（第 11 段）：jf open 粉圓 或 芫荽 Iansui（OFL）
- 拍立得手寫（第 6 段）：芫荽 Iansui（OFL）

**參考圖清單**

| id | 類型 | 內容 | 檔案 | 狀態 |
|---|---|---|---|---|
| `she-face` | 角色 | 女主臉部設定（正面、3/4、側面，2K） | `refs/wedding/she-face.jpg` | 已完成 |
| `he-face` | 角色 | 男主臉部設定（正面、3/4、側面，2K） | `refs/wedding/he-face.jpg` | 已完成 |
| `he-sheet` | 角色 | 男主便服三視圖 | `refs/wedding/he-sheet.jpg` | 已完成 |
| `she-sheet` | 角色 | 女主便服三視圖 | `refs/wedding/she-sheet.jpg` | 已完成 |
| `couple-casual` | 雙人 | 雙人便服全身 | `refs/wedding/couple-casual.jpg` | 已完成 |
| `couple-wedding` | 雙人 | 雙人登記日服裝（playbill 定案圖） | `refs/wedding/source/playbill-couple-4heads.png` | 已完成 |
| `style-clay` | 風格 | 風格錨點（playbill 謝幕畫面：陶土人物在繪本場景裡） | `refs/wedding/source/playbill-finale-clay-in-scene.png` | 已完成 |
| `kf01` | 地點 | 第 1、3 段・新北大橋日出（Commons 照片轉繪） | `refs/wedding/kf01-bridge.jpg` | 已完成 |
| `kf02a` | 地點 | 第 2 段・她的房間（已修臉），窗外 101 | `refs/wedding/kf02a-she-room-facefix.jpg` | 已完成 |
| `kf02b` | 地點 | 第 2 段・他的三重房間（Clarence 照片簡化）（已修臉） | `refs/wedding/kf02b-he-room-ff.jpg` | 已完成 |
| `kf05` | 地點 | 第 5 段・日式蛋糕店（已修臉） | `refs/wedding/kf05-cake-ff.jpg` | 已完成 |
| `kf06` | 地點 | 第 6 段・剝皮寮紅磚騎樓（Commons 照片轉繪） | `refs/wedding/kf06-bopiliao-v2.jpg` | 已完成 |
| `kf08` | 地點 | 第 8 段・台北賓館夜（Commons 照片轉繪）（已修臉） | `refs/wedding/kf08-guesthouse-v2-ff.jpg` | 已完成 |
| `kf09a` | 地點 | 第 9 段・南村劇場看 LPC（Clarence 照片＋playbill 舞台）（已修臉） | `refs/wedding/kf09a-lpc-ff2.jpg` | 已完成 |
| `kf09b` | 地點 | 第 9 段・四四南村黃昏背靠背（2K，鎖臉重畫） | `refs/wedding/kf09b-4444-v4.jpg` | 已完成 |
| `kf10` | 地點 | 第 10 段・四號公園國立臺灣圖書館前夜（Clarence 照片＋Commons）（已修臉） | `refs/wedding/kf10-library-ff.jpg` | 已完成 |
| `kf11` | 地點 | 第 11 段・永和河濱，各騎一台 YouBike 一前一後（已修臉） | `refs/wedding/kf11-ubike-v3-ff.jpg` | 已完成 |
| `kf12a` | 地點 | 第 12 段・雲林透天老家（Clarence 提供街景轉繪）（已修臉） | `refs/wedding/kf12a-home-ff2.jpg` | 已完成 |
| `kf12b` | 地點 | 第 12 段・雲林科技大學校門（Commons 照片轉繪） | `refs/wedding/kf12b-yuntech.jpg` | 已完成 |
| `kf13a` | 地點 | 第 13 段・戶政事務所，櫃檯遞出證書（你們證書的簡化版）（已修臉） | `refs/wedding/kf13a-registry-v2-ff.jpg` | 已完成 |
| `kf13b` | 地點 | 第 13 段・開頭：四四南村舉證書、張眼微笑（色調與其他場景一致） | `refs/wedding/kf13b-first.jpg` | 已完成 |
| `kf14a` | 地點 | 第 14 段・永和河堤日落 | `refs/wedding/kf14a-levee.jpg` | 已完成 |
| `kf14b` | 地點 | 第 14 段・雲林稻田晨光（Commons 照片轉繪）（已修臉） | `refs/wedding/kf14b-paddy-ff.jpg` | 已完成 |
| `kf02c` | 地點 | 第 2 段・他的三重住處大樓門口（街景轉繪） | `refs/wedding/kf02c-he-entrance.jpg` | 已完成 |
| `kf03a` | 地點 | 第 3 段・左半：她在永和市區公車上望向右方遠處（已修臉） | `refs/wedding/kf03a-she-bus-ff.jpg` | 已完成 |
| `kf03b` | 地點 | 第 3 段・右半：他在新北大橋的公車上望向左方遠處 | `refs/wedding/kf03b-he-bus-bridge.jpg` | 已完成 |
| `kf07a` | 地點 | 第 7 段・三重藏壽司包廂（盤子參考 Commons 照片）（已修臉） | `refs/wedding/kf07a-kura-ff.jpg` | 已完成 |
| `kf07b` | 地點 | 第 7 段・新北大都會公園長椅（Commons 照片轉繪） | `refs/wedding/kf07b-metropark-v2.jpg` | 已完成 |
| `cert` | 地點 | 證書設計（Clarence 提供，畫面中只做簡化版） | `refs/wedding/source/certificate-design.jpg` | 已完成 |
| `kf10mid` | 地點 | 第 10 段・環繞到背面的中間畫面（頭尾給圖用） | `refs/wedding/kf10-mid.jpg` | 已完成 |
| `kf07b-start` | 地點 | 第 7 段・頭尾給圖的開頭：兩人沿大都會公園步道走來 | `refs/wedding/kf07b-start.jpg` | 待生成 |
| `kf08-roof` | 地點 | 第 8 段・頭尾給圖的結尾：鏡頭升起，台北賓館亮燈屋頂與星空，兩人在下方變小 | `refs/wedding/kf08-roof.jpg` | 待生成 |
| `kf12a-high` | 地點 | 第 12 段・頭尾給圖的結尾：空拍升高，整條透天厝街道，兩人在門口變小 | `refs/wedding/kf12a-high.jpg` | 已完成 |
| `kf13b-last` | 地點 | 第 13 段・結尾：兩人靠頭一起笑瞇眼 | `refs/wedding/kf13b-last.jpg` | 已完成 |

地點照片來源與授權見 `refs/wedding/ATTRIBUTION.md`。

## 3. 逐段分鏡

### 01 · 0–15 秒 · 日出・新北大橋

- **原分鏡畫面**：【日出】新北大橋遠景，橋面車流慢速疊化至大漢溪水面反射
- **劇情／字幕／旁白**：旁白「在兩條河的交會，一座橋讓兩顆心每天相遇。」
- **鏡頭運動與轉場**：航拍→輕推進；淡入
- **音樂／環境音**：純鋼琴・溫暖前奏

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w01-bridge` | Omni 影片 | 15 | 0–15 全段；0–2 秒由黑淡入 | `kf01`, `style-clay` | $2.02 |

**`w01-bridge`**：日出航拍新北大橋，車流緩慢；後段鏡頭下搖到大漢溪水面，橋與朝霞的倒影。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. [0-9s] Aerial drone shot at sunrise of the long river bridge from the location reference, light traffic moving slowly across it, golden early light and thin mist over the wide river; the drone glides forward and gently descends. [9-15s] The camera tilts down from the bridge deck to the calm river surface, where the bridge, the pink sky and the rising sun are mirrored, soft ripples breaking the reflection. Slow, smooth, one continuous shot. Audio: only ambient sound — soft morning wind, distant traffic hum, water lapping. No dialogue, no speech, no singing, no music.
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
| `w02a-she-ready` | Omni 影片 | 10 | 15–25 分割畫面左半（裁中間 640×720） | `kf02a`, `she-face`, `she-sheet`, `style-clay` | $1.35 |
| `w02b-he-leave` | Omni 影片 | 10 | 15–25 分割畫面右半（裁中間 640×720） | `kf02b`, `he-face`, `kf02c`, `he-sheet`, `style-clay` | $1.35 |
| `w02c-she-101` | Omni 影片 | 8 | 25–27 中線滑開轉場、27–35 全畫面 | `kf02a`, `she-face`, `she-sheet`, `style-clay` | $1.08 |

**`w02a-she-ready`**：永和小公寓清晨，她綁頭髮、檢查包包、從架上拿鑰匙；廚房傳來鍋鏟聲。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 4 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Early morning in a small, cozy apartment in Yonghe. The woman from the reference images, in her casual outfit, ties her hair back, checks her tan crossbody bag and picks up her keys from a shelf. Handheld follow shot. Keep her and all of her action inside the central third of the frame at all times, because the frame will be cropped to a narrow vertical strip. Audio: only ambient sound — a frying pan sizzling and a spatula scraping in the kitchen nearby, keys jingling. No dialogue, no speech, no singing, no music.
```
</details>

**`w02b-he-leave`**：三重高樓的房間裡，他把背包甩上肩→走出現代大樓的玻璃門口（石材雨遮、行道樹、機車）。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the location, lighting and art direction for this scene: match this place; image 4 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. [0-5s] Morning in the man's tidy high-floor bedroom from image 1: he swings his black backpack onto his shoulder and heads for the door. [5-10s] Cut to the entrance of his modern apartment building from image 2: he walks out through the glass doors under the dark stone canopy onto the sidewalk. Handheld follow shot. Keep him and all of his action inside the central third of the frame at all times, because the frame will be cropped to a narrow vertical strip. Audio: only ambient sound — a zipper closing, the door latch, footsteps, distant scooters outside. No dialogue, no speech, no singing, no music.
```
</details>

**`w02c-she-101`**：她走到窗邊，遠方晨霧中的台北 101；鏡頭從肩後推到側臉，她微微一笑。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 4 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. The woman from the reference images steps to her apartment window; far away through the glass, Taipei 101 rises above the city in soft morning haze. She pauses and smiles softly. Slow push-in from behind her shoulder around to her smiling profile. Audio: only ambient sound — quiet room tone, faint city outside. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 16–24 | 字幕 | 她，永和； | 左半下方 |
| 16–24 | 字幕 | 他，三重。 | 右半下方 |
| | 配樂 | M1 持續（壓低，讓鍋鏟與拉鍊聲出來） | |

**剪接**：15–25 左右並排；25–27 中線往右滑把右半推出畫面，收成 w02c 單畫面；兩支的環境音在 25–28 淡出、鋼琴回來。

> ⚠️ 分割畫面裁切：每支 1280×720 只取中間 640 寬，prompt 已要求動作留在中間三分之一；仍要用草稿確認。

### 03 · 35–55 秒 · 各自出發・左右分割對望

- **原分鏡畫面**：左：她在永和市區的公車上；右：他搭公車上新北大橋。兩人其實看不到彼此，畫面左右分割，各自望向不存在的遠方，像在對看
- **劇情／字幕／旁白**：旁白「走過大橋，看見 101，就像回到家。」
- **鏡頭運動與轉場**：左右分割畫面，兩邊各自緩慢推近；接河濱、自行車道、101 的快速剪接；最後定格 101
- **音樂／環境音**：弦樂層次加入

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w03a-she-bus` | Omni 影片 | 12 | 35–47 分割畫面左半（裁中間 640×720） | `kf03a`, `she-face`, `she-sheet`, `style-clay` | $1.62 |
| `w03b-he-bridge` | Omni 影片 | 12 | 35–47 分割畫面右半（裁中間 640×720） | `kf03b`, `he-face`, `he-sheet`, `kf01`, `style-clay` | $1.62 |
| `w03c-cutaways` | Omni 影片 | 5 | 47–52 快速剪接 | `kf01`, `style-clay` | $0.67 |
| `w03-freeze` | 定格（ffmpeg） | 3 | 52–55 w03c 最後一格定格 101＋緩慢推近 | — | $0 |

**`w03a-she-bus`**：她坐在永和市區公車窗邊，望向畫面右方的遠處，淺淺地笑。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 4 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Morning inside a city bus moving through the streets of Yonghe: the woman sits at the window seat and gazes far off toward screen-right with a soft, wistful smile, as if looking at someone very far away. Shops and scooters slide past the window. Slow push-in. Keep her inside the central third of the frame at all times, because the frame will be cropped to a narrow vertical strip. Audio: only ambient sound — bus engine, city traffic, a stop bell. No dialogue, no speech, no singing, no music.
```
</details>

**`w03b-he-bridge`**：他坐在過新北大橋的公車窗邊，望向畫面左方的遠處，淺淺地笑；窗外是單塔斜張橋和河面。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 4 shows the location, lighting and art direction for this scene: match this place; image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Morning inside a city bus crossing the cable-stayed bridge: the man sits at the window seat and gazes far off toward screen-left with a soft smile, as if looking at someone very far away; through the window the single tall pylon, the fanned cables and the wide river pass by. Slow push-in. Keep him inside the central third of the frame at all times, because the frame will be cropped to a narrow vertical strip. Audio: only ambient sound — bus engine humming over the bridge, wind. No dialogue, no speech, no singing, no music.
```
</details>

**`w03c-cutaways`**：河濱公園、自行車道、遠方另一座橋，停在 101。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Quick jump cuts, about one second each, of the riverside seen from a moving bus: the riverside park, cyclists on the bike path, another bridge in the distance, ending on a clear view of Taipei 101 on the skyline. No characters. Audio: only ambient sound — bus engine, wind. No dialogue, no speech, no singing, no music.
```
</details>

**`w03-freeze`**：定格 101。

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 44–50 | 旁白／口白（旁白） | 走過大橋，看見 101，就像回到家。 | TTS 語氣：warm, smiling |
| | 配樂 | M1 在 ~40 秒加入弦樂 | |

**剪接**：35–47 左右並排（左 w03a、右 w03b），兩人視線朝向中線，像隔著畫面對望；47 起切全畫面。

> ⚠️ 兩人其實看不見彼此：她在永和市區，他在新北大橋上。對望只靠分割畫面的視線方向成立。

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

已完成：`refs/wedding/st-phone.jpg`
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
| `w05a-cake` | Omni 影片 | 12 | 70–82 | `kf05`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.62 |
| `w05b-cake-high` | Omni 影片 | 8 | 82–90 | `kf05`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.08 |

**`w05a-cake`**：叉子切草莓鮮奶油蛋糕的微距→平順拉遠，兩人在窗邊小木桌對坐，有點害羞地笑。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. [0-5s] Macro close-up: a fork slices into a Japanese strawberry shortcake, soft sponge, whipped cream and a glossy strawberry. [5-12s] The camera pulls back smoothly in one continuous move to reveal the woman and the man sitting across from each other at a small wooden table by the window of a bright, minimal Japanese-style cake shop, both a little shy, smiling at each other. Audio: only ambient sound — café chatter murmuring, cups and saucers clinking, a soft espresso machine. No dialogue, no speech, no singing, no music.
```
</details>

**`w05b-cake-high`**：固定 45° 俯角，兩人分著吃蛋糕、笑。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Locked-off high-angle shot looking down at 45 degrees on the small table in the Japanese cake shop; the woman and the man share the strawberry shortcake and laugh together. No camera movement. Audio: only ambient sound — café chatter murmuring, cups and saucers clinking. No dialogue, no speech, no singing, no music.
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
| `w06-bopiliao` | Omni 影片 | 15 | 90–105 | `kf06`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $2.02 |
| `w06-polaroid` | 定格（ffmpeg） | 5 | 105–110 定格→加白框、微傾、陰影變拍立得，快門聲 | — | $0 |

**`w06-bopiliao`**：午後紅磚騎樓巷，兩人背對鏡頭並肩慢走、逆光成剪影、邊走邊聊；手持從後跟拍。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the exact first frame of this shot: begin the video from this image and keep its composition, characters, lighting and clay storybook style; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Late afternoon in the old red-brick arcade street from the location reference. The woman and the man walk slowly side by side away from the camera toward the low sun, backlit into near-silhouettes, talking and gesturing as they go. Handheld follow shot from behind. Audio: only ambient sound — footsteps on brick, distant city murmur, a bicycle bell far away. No dialogue, no speech, no singing, no music.
```
</details>

**`w06-polaroid`**：取 w06 一格做成拍立得，字幕寫在相紙下緣。

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 105–110 | 字幕 | 歷史裡，寫下新的我們。 | 拍立得下緣，手寫感字體 |
| | 音效 | 拍立得快門聲（105） | |
| | 配樂 | M3 木吉他 | |

### 07 · 110–130 秒 · 三重藏壽司→新北大都會公園

- **原分鏡畫面**：三重藏壽司（土藏造型店）吃壽司；之後去新北大都會公園散步，坐在長椅上靠得很近
- **劇情／字幕／旁白**：無字幕
- **鏡頭運動與轉場**：壽司店內近景→公園跟拍→長椅輕推近
- **音樂／環境音**：BGM 弱化，加入輕輕的心跳

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w07a-kura` | Omni 影片 | 8 | 110–118 | `kf07a`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.08 |
| `w07b-metropark` | Omni 影片 | 10 | 118–128 | `kf07b-start`, `kf07b`, `she-face`, `he-face`, `style-clay` | $1.35 |
| `w07b-hold` | 定格（ffmpeg） | 2 | 128–130 最後一格停住 | — | $0 |

**`w07a-kura`**：簡化版：桌上固定兩盤壽司兩杯茶、不增不減；她夾壽司吃、笑，他看著她笑。固定機位。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Inside the Kura Sushi booth. A simple, calm shot: on the table in front of them there are exactly TWO plates of sushi and two cups of green tea, and nothing on the table changes during the shot - no plates are added or removed, no dome covers, no chopsticks appear or vanish. The woman takes a bite of sushi with her chopsticks and laughs; the man smiles at her. The conveyor lane behind them moves slowly in the background. Locked-off medium two-shot, no camera movement. Audio: only ambient sound — restaurant buzz, the conveyor lane clicking softly, plates clinking. No dialogue, no speech, no singing, no music.
```
</details>

**`w07b-metropark`**：頭尾給圖：兩人沿步道走來→坐上長椅、肩靠肩，她把頭輕輕靠向他。固定機位。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the exact first frame of this shot: begin the video from this image and keep its composition, characters, lighting and clay storybook style; image 2 shows the exact LAST frame of this shot: end the video exactly on this image; image 3 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Late afternoon at the riverside park. The woman and the man stroll along the curving path to the bench, sit down very close together, shoulders touching, and she gently leans her head toward his shoulder. Locked-off camera. Audio: only ambient sound — evening breeze over the grass, distant traffic on the expressway, birds. No dialogue, no speech, no singing, no music.
```
</details>

**`w07b-hold`**：停在兩人靠在一起。

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| | 音效 | 輕輕的心跳聲（124–130） | |
| | 配樂 | M3 壓低到 −15 dB | |

### 08 · 130–150 秒 · 台北賓館外・牽手

- **原分鏡畫面**：台北賓館外夜色：兩人並肩而行，男方小指碰觸→牽手成功
- **劇情／字幕／旁白**：男方旁白「原來手心的溫度，是這樣的剛好。」
- **鏡頭運動與轉場**：移動長鏡頭→牽手特寫→鏡頭從牽著的手升起，停在台北賓館亮燈的屋頂（原「塔尖」改為台北賓館本身）
- **音樂／環境音**：弦樂再次漸起

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w08a-guesthouse` | Omni 影片 | 12 | 130–142 | `kf08`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.62 |
| `w08b-guesthouse-rise` | Omni 影片 | 8 | 142–150 | `kf08`, `kf08-roof`, `she-face`, `he-face`, `style-clay` | $1.08 |

**`w08a-guesthouse`**：沿台北賓館鐵欄外的人行道並肩走（側面跟拍）→ 手部特寫：他的小指碰到她的，猶豫一下，牽起來。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the exact first frame of this shot: begin the video from this image and keep its composition, characters, lighting and clay storybook style; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. [0-7s] Night, outside the ornate white mansion behind its black iron fence: the woman and the man walk slowly side by side along the lamp-lit sidewalk; a smooth side-on tracking shot moving with them. [7-12s] The camera eases down into a close-up of their hands swinging between them: his little finger brushes hers, hesitates, then their hands clasp and hold. Audio: only ambient sound — quiet night street far away, footsteps on stone, leaves rustling. No dialogue, no speech, no singing, no music.
```
</details>

**`w08b-guesthouse-rise`**：頭尾給圖：從兩人牽手的人行道，鏡頭慢慢升高，停在台北賓館亮燈屋頂與星空，兩人變小。第一格可直接用 w08a 定稿的最後一格（修臉後）。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the exact LAST frame of this shot: end the video exactly on this image; image 3 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. The couple walk slowly hand in hand along the lamp-lit sidewalk by the iron fence; the camera rises slowly and steadily in one simple crane move until the glowing mansard roof and starry sky fill the frame and the couple are tiny below. Audio: only ambient sound — a soft night breeze, distant city hum. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 138–145 | 旁白／口白（男主） | 原來手心的溫度，是這樣的剛好。 | TTS 語氣：shy, tender, low |
| | 配樂 | M3 弦樂漸起 | |

> ⚠️ 「塔尖」解讀為台北賓館旁總統府的中央塔；台北賓館本身沒有塔。若指別的建築要改。

### 09 · 150–180 秒 · 戲院→四四南村

- **原分鏡畫面**：南村劇場看 LPC（《I Love You, You're Perfect, Now Change》）黑場→舞台燈亮；Cut 到四四南村戲後空地，兩人背靠背坐著笑談
- **劇情／字幕／旁白**：字幕「一次場景，兩段劇本，變成共同人生。」
- **鏡頭運動與轉場**：Hard-cut 隨鼓點
- **音樂／環境音**：BGM 一段高潮

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w09a-theatre` | Omni 影片 | 6 | 150–156 | `kf09a`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $0.81 |
| `w09b-4444-wide` | Omni 影片 | 12 | 156–168（依鼓點切成 2–3 段） | `kf09b`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.62 |
| `w09c-4444-close` | Omni 影片 | 12 | 168–180（依鼓點切） | `kf09b`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.62 |

**`w09a-theatre`**：南村劇場看 LPC：全暗→舞台燈亮，紅牆、燈串、白色網架屋頂；從後方看兩人坐在圓桌旁的觀眾席。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Inside the small PLAYground Nancun Theater: total darkness, then the stage lights snap on, warm string lights glow under the white mesh roof and the red back wall and empty wooden frames of the set light up. Seen from behind, the woman and the man sit side by side at a small round table in the audience, silhouetted against the bright stage. No performers. Audio: only ambient sound — an audience hush, the clunk of stage lights switching on. No dialogue, no speech, no singing, no music.
```
</details>

**`w09b-4444-wide`**：黃昏四四南村，兩人背靠背坐著笑；固定機位慢推近。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Golden dusk at the village from the reference: the woman and the man sit back to back on the ground, laughing and leaning against each other. Locked-off medium shot with a very slow push-in. Audio: only ambient sound — evening breeze, distant city, crickets starting. No dialogue, no speech, no singing, no music.
```
</details>

**`w09c-4444-close`**：三個近景：她笑、他笑、兩人肩膀相靠。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. [0-4s] Close-up of the woman laughing, head tilted back against the man's shoulder, 101 softly out of focus behind. [4-8s] Close-up of the man laughing, eyes closed. [8-12s] Close-up of their shoulders and backs pressed together, her hand finding his on the grass. Audio: only ambient sound — evening breeze, crickets. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 160–170 | 字幕 | 一次場景，兩段劇本，變成共同人生。 | 下方置中 |
| | 配樂 | M4 高潮段 | |

**剪接**：全部 hard-cut 對齊 M4 的鼓點（用 librosa 抓 beat 或手動標）。

### 10 · 180–205 秒 · 四號公園・國立臺灣圖書館前告白

- **原分鏡畫面**：夜晚的四號公園，國立臺灣圖書館前廣場：男方告白；女方點頭
- **劇情／字幕／旁白**：男方口白＋女方輕笑
- **鏡頭運動與轉場**：頭尾給圖兩段環繞（A 正面→背面、B 背面→正面並拉遠）→ 煙火閃光轉場
- **音樂／環境音**：鋼琴與弦樂交織

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w10a-library-a` | Omni 影片 | 8 | 180–188 | `kf10`, `kf10mid`, `she-face`, `he-face`, `style-clay` | $1.08 |
| `w10a-library-b` | Omni 影片 | 8 | 188–196（與 A 以 0.25 秒交叉淡化接成一鏡） | `kf10mid`, `kf10`, `she-face`, `he-face`, `style-clay` | $1.08 |
| `w10b-fireworks` | Omni 影片 | 9 | 196–205；最後一格閃白接下一段 | `kf10`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.21 |

**`w10a-library-a`**：頭尾給圖 A：從圖書館正面繞 180° 到背面，看到她在他肩後掩嘴笑（測試版已驗證）。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the exact first frame of this shot: begin the video from this image and keep its composition, characters, lighting and clay storybook style; image 2 shows the exact LAST frame of this shot: end the video exactly on this image; image 3 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Night on the plaza in front of the library. The man looks at the woman earnestly, mouth closed, as if his words are heard in voice-over; she raises one hand to cover her smiling mouth. The handheld camera orbits smoothly 180 degrees around the two of them, from the side that shows the library to the opposite side where we see her face over his shoulder. Audio: only ambient sound — a quiet park at night, insects, leaves rustling. No dialogue, no speech, no singing, no music.
```
</details>

**`w10a-library-b`**：頭尾給圖 B：從背面繞回正面並拉遠，兩人在圖書館前變小，電影感收尾。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the exact first frame of this shot: begin the video from this image and keep its composition, characters, lighting and clay storybook style; image 2 shows the exact LAST frame of this shot: end the video exactly on this image; image 3 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Night on the plaza in front of the library. Over his shoulder she smiles behind her hand, then lowers it and nods. The camera keeps orbiting another 180 degrees and gently pulls back, until the two of them stand small in front of the glowing library facade. Audio: only ambient sound — a quiet park at night, insects, leaves rustling. No dialogue, no speech, no singing, no music.
```
</details>

**`w10b-fireworks`**：她含淚笑著點頭、兩人擁抱；圖書館上空煙火一發接一發炸開（可以小小浮誇），照亮兩人的臉，最後一道閃光把畫面刷白。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. The woman nods with a teary smile and the two embrace. Above the library and the park, a generous, slightly over-the-top burst of fireworks goes off one after another in gold, pink and teal, lighting up their faces and the glass facade. In the final second a bright flash fills the whole frame with white. Audio: only ambient sound — fireworks booming and crackling, the fountain splashing. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 183–196 | 旁白／口白（男主） | 如果把妳和我，連成一條線，我想再靠近一點，跨過這條線。如果把兩隻手，牽成一個圓，妳願不願意，讓我再勇敢一點——牽起這段緣？ | TTS 語氣：earnest, nervous, warm, unhurried |
| 197–199 | 旁白／口白（女主） | <laugh> | TTS 語氣：soft laugh |
| | 配樂 | M4 收成鋼琴＋弦樂 | |

**剪接**：A、B 以 0.25 秒交叉淡化接成一個 16 秒鏡頭（測試版 review/wedding/w2/w10a-library-fl-ab.mp4）。

> ⚠️ 告白詞依 Clarence 給的語境潤飾：「線」呼應開場的橋，「圓」接到牽手，最後一句改成問她，好接她點頭。約 51 字、約 12 秒。

> ⚠️ 四號公園沒有水池噴泉，依 Clarence 指示改到國立臺灣圖書館前廣場。

### 11 · 205–225 秒 · 永和河濱・雙載

- **原分鏡畫面**：永和河濱公園：兩人各騎一台 YouBike，一前一後、風鈴聲；鏡頭帶出遠處 101
- **劇情／字幕／旁白**：無旁白，慢速 2D 文青字體「在河風裡，我們任意奔跑」
- **鏡頭運動與轉場**：穿越鏡
- **音樂／環境音**：清風與單車鏈條聲

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w11a-bike` | Omni 影片 | 12 | 205–217 | `kf11`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.62 |
| `w11b-bike-away` | Omni 影片 | 8 | 217–225 | `kf11`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.08 |

**`w11a-bike`**：側面平移跟拍，前景高草滑過；他在前、她在後，各騎一台 YouBike。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Golden late afternoon on the riverside bike path. Side-on tracking shot moving with two YouBike 2.0 bicycles riding in single file in the same direction, tall grass sliding past in the foreground: the man rides in front, the woman follows two bike lengths behind, smiling at his back, her hair blowing in the wind. Taipei 101 small on the distant skyline across the river. Audio: only ambient sound — a light breeze, the bicycle chain ticking, faint wind chimes. No dialogue, no speech, no singing, no music.
```
</details>

**`w11b-bike-away`**：固定機位，兩台 YouBike 一前一後騎遠變小。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Locked-off camera on the riverside path: the two YouBikes, he in front and she behind, ride away from the camera toward the city skyline and the low sun until they are small. Audio: only ambient sound — a light breeze, the bicycle chain ticking, faint wind chimes. No dialogue, no speech, no singing, no music.
```
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 208–220 | 字幕 | 在河風裡，我們任意奔跑 | 畫面右側直排或下方，逐字淡入，2D 文青手寫字體 |
| | 配樂 | M5 開始（輕快木吉他） | |

### 12 · 225–255 秒 · 雲林・他帶她回家看看

- **原分鏡畫面**：雲林老家透天厝門口，只有男女主，男方帶她回家看看；Cut 到男方母校雲林科技大學校門；大學時期騎 MTB／freeride 的老照片彩蛋
- **劇情／字幕／旁白**：字幕「從這裡啟程，載著所有祝福回台北。」
- **鏡頭運動與轉場**：Drone Rising→L-cut
- **音樂／環境音**：鄉村蟲鳴＋吉他

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w12a-home` | Omni 影片 | 10 | 225–235 | `kf12a`, `kf12a-high`, `she-face`, `he-face`, `style-clay` | $1.35 |
| `w12a-hold` | 定格（ffmpeg） | 2 | 235–237 高處畫面停住 | — | $0 |
| `w12b-yuntech` | Omni 影片 | 12 | 237–249；前 2 秒延續上一段的蟬聲（L-cut） | `kf12b`, `she-face`, `he-face`, `she-sheet`, `he-sheet`, `style-clay` | $1.62 |
| `st-oldphoto` | 圖片（Ken Burns） | 6 | 249–255 老照片 Ken Burns（大學時期彩蛋） | — | $0.13 |

**`w12a-home`**：頭尾給圖：他比著房子介紹、她抬頭看，鏡頭慢慢升高，停在整條透天厝街道的高處，兩人變小。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the exact first frame of this shot: begin the video from this image and keep its composition, characters, lighting and clay storybook style; image 2 shows the exact LAST frame of this shot: end the video exactly on this image; image 3 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. A sunny afternoon in Yunlin in front of the man's narrow three-story family townhouse. He gestures proudly toward the house and she looks up at it, then smiles at him. The camera rises slowly and steadily like a drone in one simple move, ending high above the quiet street of townhouses. Audio: only ambient sound — cicadas, a scooter passing far away, a light breeze. No dialogue, no speech, no singing, no music.
```
</details>

**`w12a-hold`**：停在整條街。

**`w12b-yuntech`**：雲科大校門前，他指著校門講當年的事，她笑出來。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the woman's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 5 shows the man's character model sheet (front, three-quarter and back views): keep exactly this face, hairstyle, accessories and outfit; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. A sunny day at the university gate with the round stone gatehouse and red flower planter. The man points at the gate and tells the woman about his student days; she laughs. Medium two-shot, gentle handheld. Audio: only ambient sound — cicadas, birds in the trees, a quiet campus. No dialogue, no speech, no singing, no music.
```
</details>

**`st-oldphoto`**：他大學時期穿白色車衣、扶著登山車的老照片。

<details><summary>Nano Banana prompt</summary>

已完成：`refs/wedding/st-oldphoto-v3.jpg`
</details>

| 時碼 | 層 | 內容 | 說明 |
|---|---|---|---|
| 228–236 | 字幕 | 從這裡啟程，載著所有祝福回台北。 | 下方置中 |
| | 配樂 | M5 鄉村吉他 | |

**剪接**：w12a → w12b 用 L-cut，蟬聲延續到 w12b 前 2 秒。

> ⚠️ 老照片：他大學時期穿白色車衣、扶著下坡登山車、手拿全罩安全帽（大學時都在騎 MTB＋freeride）。

> ⚠️ 雲科大校門參考圖上有 YunTech 標誌字樣，是校方真實標誌；其他看板留白。

### 13 · 255–275 秒 · 登記日・戶政事務所→回到四四南村

- **原分鏡畫面**：簽字、蓋章、領證書（你們證書的簡化版）；回到四四南村，彩色門窗老屋前、背景 101，新人舉起證書正面
- **劇情／字幕／旁白**：女方旁白「紙張薄薄，愛卻滿溢。」
- **鏡頭運動與轉場**：閃亮字幕「Married！」
- **音樂／環境音**：管樂短暫歡呼

| 鏡頭 | 做法 | 秒數 | 時間軸用法 | 參考圖 | 草稿＋定稿估價 |
|---|---|---|---|---|---|
| `w13a-registry` | Omni 影片 | 10 | 255–265 | `kf13a`, `she-face`, `he-face`, `couple-wedding`, `cert`, `style-clay` | $1.35 |
| `w13b-4444-cert` | Omni 影片 | 10 | 265–275 | `kf13b`, `kf13b-last`, `she-face`, `he-face`, `cert`, `style-clay` | $1.35 |

**`w13a-registry`**：筆簽名（字跡看不清）→紅印章蓋下抬起→櫃檯遞出證書，兩人的手接過。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the couple in the outfits for this scene: keep exactly these faces, hairstyles and outfits; image 5 shows the location, lighting and art direction for this scene: match this place; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Inside a bright household registration office. [0-3s] Macro: a pen signs a form, the handwriting illegible. [3-6s] A red seal stamp presses down onto the paper and lifts away. [6-10s] The clerk slides the new marriage certificate across the counter and the couple's hands receive it together, its front facing the camera. The certificate is a SIMPLIFIED version of the couple's own illustrated card: top half a cheerful blue illustrated night sky with tiny fireworks, a little city skyline and a tiny waving cartoon couple; bottom half white with a few faint lines; no readable words, names or numbers. Audio: only ambient sound — quiet office murmur, the soft thud of the stamp, paper rustling. No dialogue, no speech, no singing, no music.
```
</details>

**`w13b-4444-cert`**：頭尾給圖：四四南村舉證書張眼微笑→靠頭一起笑瞇眼，停在笑瞇眼到最後一格。固定機位，色調與其他場景一致。重要場景，直接出 720p。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the exact first frame of this shot: begin the video from this image and keep its composition, characters, lighting and clay storybook style; image 2 shows the exact LAST frame of this shot: end the video exactly on this image; image 3 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 5 shows the location, lighting and art direction for this scene: match this place; image 6 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. A gentle sunny afternoon back at Four Four South Village, soft warm light and a pale soft-blue sky, colors muted and warm, never oversaturated. The couple in their registration-day outfits hold their marriage certificate up together, its front facing the camera, she holds her bouquet in her other hand; they smile at the camera, then lean their heads together and both burst into a happy laugh with their eyes squeezed shut into curved crescents, and they HOLD that eyes-closed laugh until the very last frame; neither of them opens their eyes again. Locked-off camera, no camera movement. The certificate keeps the same simple illustration on top and faint plain lines below, with no letters. Audio: only ambient sound — birds, a light breeze, distant city. No dialogue, no speech, no singing, no music.
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
| `w14a-levee` | Omni 影片 | 10 | 275–295 與 w14b 每 5 秒交錯 cross-fade | `kf14a`, `she-face`, `he-face`, `couple-wedding`, `style-clay` | $1.35 |
| `w14b-paddy` | Omni 影片 | 10 | 275–295 與 w14a 交錯 | `kf14b`, `she-face`, `he-face`, `couple-wedding`, `style-clay` | $1.35 |

**`w14a-levee`**：永和河堤日落，從背後看兩人牽手往夕陽走。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the couple in the outfits for this scene: keep exactly these faces, hairstyles and outfits; image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Sunset on the river levee path from the location reference. Seen from behind, the woman and the man walk forward hand in hand toward the setting sun, golden backlight, long shadows. Audio: only ambient sound — slow footsteps, a light breeze. No dialogue, no speech, no singing, no music.
```
</details>

**`w14b-paddy`**：雲林稻田清晨，從背後看兩人牽手走在田埂上，薄霧。

<details><summary>Omni prompt（完整，含自動附加的參考圖說明、風格、音訊規則）</summary>

```text
Reference images, in order: image 1 shows the location, lighting and art direction for this scene: match this place; image 2 shows the woman's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 3 shows the man's FACE reference sheet: copy this face exactly (eye size and catchlights, nose, cheeks, mouth); image 4 shows the couple in the outfits for this scene: keep exactly these faces, hairstyles and outfits; image 5 shows the approved art style: sculpted matte clay figurines placed in a painted storybook set. The woman is about four heads tall with half-up princess-style wavy dark-brown hair, rounded blushing cheeks and a small gentle smile. The man is about four heads tall with black rectangular glasses, short swept black hair, rounded cheeks and a small gentle smile. Animated 3D storybook short film in the approved style of The Playbill: the couple are about four heads tall, adult, rendered as sculpted matte clay figurines with painted gouache texture and fine fabric grain and rounded dimensional hands, placed inside painted storybook versions of real places in Taipei, New Taipei and Yunlin, warm soft golden lighting, gentle cinematic camera, 24fps. Keep faces, glasses, hairstyles and outfits identical to the references in every frame. The characters do not talk: mouths stay closed in small gentle smiles unless they laugh softly. No readable text, signs, captions or logos anywhere in the frame; any sign or plaque is blank. No photorealism, no glossy plastic. Faces are rigid sculpted figurine faces: keep eye size, the white catchlights in the eyes, the small button nose and the round blushing cheeks identical to the face reference sheets in every frame; never shrink the eyes into small dots. Colors are soft and natural like a warm storybook, never oversaturated; skies are gentle, not electric blue. Camera moves are simple and slow. Dawn over the misty green rice paddies from the location reference. Seen from behind, the woman and the man walk hand in hand along a narrow earthen ridge path into the soft morning light. Audio: only ambient sound — slow footsteps, morning birds, a light breeze. No dialogue, no speech, no singing, no music.
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
| 183–196 | 男主 | 如果把妳和我，連成一條線，我想再靠近一點，跨過這條線。如果把兩隻手，牽成一個圓，妳願不願意，讓我再勇敢一點——牽起這段緣？ | earnest, nervous, warm, unhurried |
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

## 5. 360p 測試鏡頭（等 Clarence 說 go）

| 鏡頭 | 秒數 | 測什麼 | 第一格 | 估價 |
|---|---|---|---|---|
| `w06-bopiliao` | 15 | 雙人背影走路：陶土質感與人物在動態中是否穩定 | `refs/wedding/kf06-bopiliao-v2.jpg` | $0.37 |
| `w08a-guesthouse` | 12 | 新運鏡＋手部互動：小指碰觸到牽手是最容易崩的細節 | `refs/wedding/kf08-guesthouse-v2-ff.jpg` | $0.30 |
| `w10a-library-a` | 8 | 頭尾給圖環繞（已驗證，作為全片的運鏡範本） | `refs/wedding/kf10-library-ff.jpg` | $0.20 |
| `w13b-4444-cert` | 10 | 登記日服裝＋真實地點＋101：換裝參考與地標能不能守住 | `refs/wedding/kf13b-first.jpg` | $0.25 |
| **合計** | 45 | | | **$1.12** |

單價 $0.0248/s 是我們帳本裡 360p 的實測值（含 thought 與參考圖輸入 token）。同四支升 720p 定稿約 $3.19。
跑法：`python3 src/run.py --exp W2 --model omni_12 --spec prompts/wedding/videos-test.yaml --res 360p`

## 5b. 全片預算（用實測單價）

影片 28 支、282 秒。單價：360p $0.0232/s、720p $0.0695/s，每支另加約 $0.023（附 5–6 張參考圖時的 thought 與圖片輸入，W2 實測）。
草稿每支平均 1.5 次、定稿 1.3 次；圖片含新增的頭尾圖與約 10 張修改；另加 15% 預備。

| 項目 | 全部打草稿 | 只對複雜鏡頭打草稿 |
|---|---|---|
| 360p 草稿 | $10.78 | $4.80（12 支、126 秒：頭尾給圖、手部、分割裁切、微距等） |
| 720p 定稿 | $26.32 | $26.32 |
| 參考圖／頭尾圖／修臉 | $1.25 | $1.25 |
| 影格檢查 | $1.82 | $1.82 |
| TTS＋配樂 | $0.74 | $0.74 |
| 小計 | $40.90 | $34.92 |
| **含 15% 預備** | **$47.04** | **$40.16** |
| 改用 Google 1080p 定稿 | +$14.67 | +$14.67 |

## 6. 風險

- **兩個角色 × 28 支的一致性還沒驗證。** 靜態參考圖已經一致；影片端只證明過 1 個角色加 1 個道具。建議先用 360p 跑 3–4 支雙人鏡頭確認。
- **風格漂移。** 只拿空景當風格參考時，人物會變成平面插畫；每支都要附 `style-clay`（陶土人物在場景裡的畫面）。
- **畫面中文字。** Omni 會把招牌、證書、校名寫錯；prompt 已要求無字，所有中文字一律後製。
- **正面說話的戲。** 全片人物不開口（沿用 playbill 的閉嘴微笑）；台詞全由 TTS 旁白承接。
- **Letterbox 黑邊。** prompt 禁止無效，定稿每支都要 `cropdetect`，有黑邊就裁切或全片統一加黑邊。
- **分割畫面裁切。** 第 2 段兩支要裁成窄條，動作必須留在中間三分之一。

## 7. 待決問題

- 第 9 段 LPC 劇場那張修臉時多了兩位觀眾，要保留嗎？
