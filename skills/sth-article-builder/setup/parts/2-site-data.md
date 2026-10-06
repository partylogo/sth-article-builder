# 第 2 段：站點資料（三張小卡）

這段拆成三張小卡，照順序一張一張給，每張寫完檔才給下一張：

| 小卡 | 設定什麼 | 寫進 |
|---|---|---|
| 2a | 網站基本資料：網址、語言地區、品牌名、新文章的網址樣式 | `site.domain`、`canonical_base`、`article_url_pattern`、`language`、`region`、`brand` |
| 2b | 讀者與導流：讀者是誰、讀完要去哪 | `site.audience`、`site.cta` |
| 2c | 既有文章要不要收進清單 | `content_inventory`、`cannibalization`、`adapters.read_source`；content-inventory.csv |

三張都寫完，`setup.parts.site_data` 設 done。單獨補某一張：`/sth-article-builder setup 網站資料`／`讀者`／`既有文章`。

---

## 2a　網站基本資料

### 說明卡

**這段設定什麼**：網站的網址、語言地區、品牌名怎麼寫、新文章的網址長什麼樣。

**為什麼需要**：
- 撞文檢查用 `site:{網址}` 搜站上有沒有寫過
- 查搜尋量、看搜尋結果用的國家和語言
- 文章裡的品牌名、內部連結的網址格式、發布後去哪裡確認文章上線

**要決定什麼**：
- 網址（還沒上線就說還沒上線）
- 語言與地區（例：繁體中文、台灣）
- 品牌名的正確寫法；網站上有好幾種寫法並存時，哪個對
- 新文章的網址樣式（例：`/blog/{代稱}/`）

**方法**

| 方法 | 做什麼 | 你要準備 | 時間 | 會動到外部嗎 |
|---|---|---|---|---|
| A. 你直接告訴我 | 我照你說的填 | 四個值 | 1 分鐘 | 不會 |
| B. 我讀網站推測 | 讀首頁、網站地圖，推測四個值附依據給你確認 | 網址 | 1–2 分鐘 | 只讀 |
| C. 我讀網站程式碼推測 | 讀程式碼裡的設定檔與路由，推測四個值附依據給你確認 | 網站程式碼資料夾 | 2–3 分鐘 | 只讀 |

**跳過的話**：不能跳過。

B、C 可以一起選，兩邊結果對照。

### 方法 A 的做法

依序問網址、語言地區、品牌名、新文章網址樣式。網址樣式不確定時說「不確定」，在 2c 或第一篇文章發布後再補，`article_url_pattern` 先留空並在狀態畫面標 ⚠️。

### 方法 B 的做法

照 `~/article-engine/adapters/read-source/website.md`：

1. 抓首頁 HTML。被擋就照轉接器的退路（帶 UA → 瀏覽器）。哪一種方法成功就記進 `adapters.read_source.website`（例：需要 UA 就填 `user_agent`）。
2. 偵測，每一項記依據：

   | 項目 | 從哪裡看 |
   |---|---|
   | 網址正式版本 | 有沒有 www、http 轉 https、redirect 到哪 |
   | 語言 | `<html lang>`、內文字元 |
   | 品牌名 | `og:site_name`、`<title>` 的固定後綴、logo 的 alt |
   | 網址樣式 | sitemap 裡文章頁的共同前綴（例：`/blog/{slug}`） |
   | 平台（附帶，給第 7 段用） | `<meta name="generator">`、`/wp-json/` 有沒有回應、`/ghost/api/`、`__NEXT_DATA__`、`/_astro/` 路徑、HTTP 標頭 |

3. 結果整理成一張表（項目、推測、依據）給使用者確認。網址樣式有好幾種（例：`/blog/` 和 `/news/`）時，列出各前綴的頁數與一兩個標題，問「新文章要放哪一種？」

### 方法 C 的做法

1. profile 還沒有 `site.repo_path` → 問網站程式碼在哪（給路徑／幫我找：在 `~/Documents`、`~/Projects` 底下找名字或 `package.json` 的 name 含使用者說的站名的資料夾，列出候選）。確認資料夾存在，寫進 `site.repo_path`。
2. 只讀，找：
   - 正式網址：`astro.config.*` 的 `site`、`next.config.*`、`package.json` 的 `homepage`、`CNAME`、`.env*` 裡名字含 `SITE_URL`／`BASE_URL` 的變數、`sitemap.*`、`robots.*`
   - 語言：框架的 i18n 設定、根 layout 的 `lang`
   - 品牌名：layout 的 `<title>` 樣板、manifest 的 `name`
   - 網址樣式：路由資料夾（例：`src/pages/blog/[slug].astro`、`app/news/[slug]/page.tsx`）；內容不在 repo 而是從 API 來時（路由檔裡有 fetch），記下 API 位置，給第 7 段用
3. 結果表格給使用者確認，同 B。

### 寫檔

profile 的 `site.domain`、`canonical_base`、`article_url_pattern`、`language`、`region`、`brand.name`、`brand.variants_to_fix`。還沒上線：`site.domain` 留空，2c 的方法只剩「先空著」。

`site.language` 對應不到 `~/article-engine/language/` 底下的語言包時，照實說「目前只有 zh-TW 語言包」，寫進 setup-issues.md。

`research.community_sources` 依語言填預設，不問，在完成訊息裡列出：

| 語言 | 預設社群來源 |
|---|---|
| zh-TW | threads.net、ptt.cc、dcard.tw |
| 其他 | reddit.com、quora.com |

---

## 2b　讀者與導流

### 說明卡

**這段設定什麼**：文章寫給誰看，讀者看完你希望他去哪裡。

**為什麼需要**：
- 讀者決定意圖研究看哪些問題、大綱寫多深、哪些術語要白話解釋
- 導流決定文末的行動呼籲寫什麼、連去哪；內文最多自然提到產品 1 次
- 有「切角偏好」時，選題角度會偏向接得到產品的方向

**要決定什麼**：
- 讀者是誰（一句話）
- 讀完要去哪：按鈕文字、網址
- 選題切角要不要偏向產品（不偏＝照搜尋成效最大的角度寫）

**方法**

| 方法 | 做什麼 | 你要準備 | 時間 | 會動到外部嗎 |
|---|---|---|---|---|
| A. 你直接告訴我 | 我照你說的填 | 三個答案 | 2 分鐘 | 不會 |
| B. 我讀首頁和關於頁提候選 | 從標語、關於頁、首頁最醒目的按鈕抓候選，附出處給你挑或改 | 網址（2a 已經有就不用） | 1–2 分鐘 | 只讀 |

**推薦**：2a 選了 B（已經讀過網站）時推薦 B，因為首頁已經抓過，只要多讀關於頁。其他情況不標。

**跳過的話**：不能跳過。

### 方法 A 的做法

依序問三題。導流沒有就說沒有，`site.cta` 留空（文末不放行動呼籲）。

### 方法 B 的做法

1. 讀首頁標語、`/about` 或關於頁、導覽列與首頁最醒目的按鈕（下載、註冊、產品頁）。
2. 讀者給 1–2 個候選，每個附出處原文；導流列出找到的按鈕文字與網址。
3. 問：
   ```
   讀者是誰？我從 {出處} 看到「{原文}」，候選：
   1. {候選 1}
   2. {候選 2}
   3. 自己寫一句
   ```
   導流同樣列候選＋「自己寫」。切角偏好一律問使用者，不推測。

### 寫檔

`site.audience`、`site.cta.text`、`site.cta.url`、`site.cta.max_inline_mentions`（預設 1）、`site.cta.angle_bias`（不偏就留空）。

---

## 2c　既有文章要不要收進清單

### 說明卡

**這段設定什麼**：網站上已經有的文章，要不要列進「內容清單」（`content-inventory.csv`）。

**為什麼需要**：清單有三個用途：
- 寫新文章前檢查有沒有撞題
- 內部連結只連清單裡的文章
- 撰稿時參考清單裡最近的文章怎麼寫

**要決定什麼**：
- 收不收既有文章
- 收的話，怎麼讀出文章清單、哪些網址算文章

**方法**

| 方法 | 會怎樣 | 你要準備 | 時間 | 會動到外部嗎 |
|---|---|---|---|---|
| A. 全部收 | 舊文章參與撞文檢查、可以被連結、會被當寫作參考。接著選怎麼讀（見下表） | 看讀法 | 看文章數，幾分鐘到十幾分鐘 | 只讀 |
| B. 不收，只收之後這套系統寫的 | 清單從空的開始。舊文章不會被連結、不會被當參考；撞文檢查仍會用 `site:` 搜站上，搜到舊文章照樣提醒 | 不用 | 0 | 不會 |
| C. 先空著，之後再加 | 跟 B 一樣從空的開始；之後打 `/sth-article-builder setup 既有文章` 選 A 補進來 | 不用 | 0 | 不會 |

選 A 時接著問讀法（可多選，多個來源會合併）：

| 讀法 | 做什麼 | 你要準備 | 清單能不能確認完整 |
|---|---|---|---|
| 讀網站 | 從網站地圖、RSS、列表頁讀出文章 | 不用 | 不能，可能有漏 |
| 讀 WordPress API | 從 WordPress 的公開 API 讀出所有已發布文章 | 網站要是 WordPress | 可以 |
| 讀網站程式碼 | 讀 repo 裡的文章原始檔（md／mdx） | 網站程式碼資料夾；文章要存在 repo 裡 | 可以 |

**推薦**：使用者說過「舊文章不要當參考」之類的話時推薦 B。其他情況不標。

**跳過的話**：等於 C。

### 方法 A 的做法

1. 照選的每個讀法的轉接器「列出」：讀網站 → `~/article-engine/adapters/read-source/website.md`；WordPress API → `wp-rest.md`（先跑前置檢查，`/wp-json/` 沒回應就照實說「這個站不是 WordPress，或 API 被關掉」，問要不要改用其他讀法）；網站程式碼 → `repo.md`（profile 還沒有 `site.repo_path` 時這時才問路徑；找不到 md／mdx 內容檔就照實說「文章不在 repo 裡」）。
2. 寫進 `{站}/content-inventory.csv`，所有列的 `written_by_engine` 填「基準」。多個來源以網址為鍵合併；兩邊數量對不上 → 寫出差幾篇、各舉一個例子，不自己判斷誰對。
3. 判斷內容型態（文章／分類頁／標籤頁／其他）。有好幾種前綴（例：`/blog/`、`/learn/`、`/news/`）時，列出各前綴的頁數與一兩個標題，問「哪些算文章？」，答案寫進 `cannibalization.include_url_patterns`。
4. 結果給使用者確認：「收了 N 篇，涵蓋狀態：{已確認完整／未確認}」。

### 方法 B／C 的做法

不讀網站。建一個只有表頭的 `content-inventory.csv`（格式見 `website.md`），開頭註解寫 `# coverage: 只收本系統`（`site.domain` 空的時候寫 `網站未上線`）。

### 寫檔

```yaml
content_inventory:
  include_existing: true    # A＝true；B、C＝false
adapters:
  read_source:
    primary: website        # A 選了哪些讀法；B、C 也填 website（之後補收時用）
    extra: []               # 例：[wp-rest]、[repo]
```

B 與 C 寫進檔的內容一樣，差別只在完成訊息：C 會提醒之後補收的指令，狀態畫面也一直顯示。`cannibalization.include_url_patterns` 只有 A 會填。
