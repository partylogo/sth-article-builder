# 第 2 段：站點資料

> 這一段最重要的原則：**每一個值都要有偵測證據，偵測不到才問**。不靠站名或產業猜。

## 要決定的點（最多 2 個；偵測都成功時只剩第 1 個）

1. 四個問題裡偵測不到的那幾題（讀者是誰、讀完要去哪，幾乎都要問）
2. 偵測不確定時：哪些區塊算文章

## 步驟

### 2.1 找網域

依序找，找到就停，把證據記下：

1. 使用者在指令或對話裡給過網址。
2. 有網站程式碼（`site.repo_path`）：到那個資料夾讀設定檔裡的正式網址（例：`astro.config.*` 的 `site`、`next.config.*`、`package.json` 的 `homepage`、`CNAME`、`.env*` 裡名字含 `SITE_URL`／`BASE_URL` 的變數、`src/app/sitemap.*` 或 `robots.*` 裡寫死的網域）。只讀，不改。
3. 都沒有 → 問「網站網址是什麼？還沒上線就說還沒上線」。

**還沒上線**：`site.domain` 留空，涵蓋狀態記「失敗」，撞文只靠 runs/ 與 repo（有的話），報告標 ⚠️。其餘照常設定。

### 2.2 讀網站

照 `~/article-engine/adapters/read-source/website.md` 的「列出」：

1. 抓首頁 HTML。被擋就照轉接器的退路（帶 UA → 瀏覽器）。哪一種方法成功就記進 `adapters.read_source.website`（例：需要 UA 就填 `user_agent`）。
2. 偵測（每一項記證據）：

   | 偵測項 | 從哪裡看 |
   |---|---|
   | 語言 | `<html lang>`、內文字元 |
   | 品牌名 | `og:site_name`、`<title>` 的固定後綴、logo 的 alt |
   | 平台 | `<meta name="generator">`、`/wp-json/` 有沒有回應、`/ghost/api/`、`__NEXT_DATA__`、`astro-` 開頭的 class 或 `/_astro/` 路徑、HTTP 標頭 |
   | 文章網址樣式 | sitemap 裡文章頁的共同前綴（例：`/blog/{slug}`） |
   | 網址正式版本 | 有沒有 www、http 轉 https、redirect 到哪 |

3. 照轉接器「列出」把現有內容寫進 `{站}/content-inventory.csv`，所有列的 `written_by_engine` 填「基準」。
4. 判斷內容型態（文章／分類頁／標籤頁／其他）。**判斷不確定**時（例：有 `/blog/`、`/learn/`、`/guide/` 三種前綴），列出各前綴的頁數與一兩個標題，問「哪些算文章？」，答案寫進 `cannibalization.include_url_patterns`。

### 2.3 加分來源

依偵測結果提議，使用者同意才加：

| 偵測到 | 提議 | 試讀 |
|---|---|---|
| WordPress（`/wp-json/` 有回應） | 加讀 WordPress REST API，文章清單可以確認完整 | 照 `adapters/read-source/wp-rest.md` 的前置檢查 |
| 有網站程式碼（`site.repo_path`），而且裡面有 md／mdx／markdown 內容檔 | 加讀 repo 原始檔，文章清單可以確認完整，也拿得到原生格式 | 照 `adapters/read-source/repo.md` 的前置檢查，找出內容檔的 glob |
| 其他 CMS（Ghost 等），目前沒有轉接器 | 不提議；記進 setup-issues.md「{平台} 還沒有讀取轉接器，清單只能從網站讀」 | |

加讀成功 → 照該轉接器重新「列出」，跟 2.2 的清單合併（以網址為鍵），涵蓋狀態升為「已確認完整」（轉接器寫的條件成立時）。
兩邊數量對不上 → 摘要裡寫出差幾篇、各舉一個例子，不自己判斷誰對。

### 2.4 四個問題

偵測到的直接填成預設值，使用者只要確認；偵測不到的才問。

| 問題 | 偵測 | 寫進 | 答案會變成什麼 |
|---|---|---|---|
| **讀者是誰？** | 幾乎偵測不到；可以從首頁標語、關於頁抓一句當候選 | `site.audience` | 意圖報告的讀者輪廓、大綱深度、哪些術語要白話解釋、預設語氣深淺 |
| **讀完要去哪？** | 首頁主要按鈕、導覽列最醒目的連結（下載、註冊、產品頁）當候選 | `site.cta`（text、url） | 文末行動呼籲、內文最多 1 處提到產品、S4 選切角偏向接得到產品的角度 |
| **語言與地區？** | `<html lang>` | `site.language`、`site.region` | 查量的國家、看哪一國的搜尋結果、語言包、用語 |
| **品牌名稱怎麼寫？** | og:site_name、title 後綴 | `site.brand.name`；不同寫法並存時列出來問哪個對，其餘進 `variants_to_fix` | 行動呼籲與內文的寫法、S8 專名一致性、撞文搜尋用的站名 |

問法範例：

```
讀者是誰？我從首頁看到「{標語}」，猜是：
1. {候選}（推薦，依首頁標語）
2. 自己寫一句
```

`site.language` 對應不到 `~/article-engine/language/` 底下的語言包時，照實說「目前只有 zh-TW 語言包」，寫進 setup-issues.md。

### 2.5 社群來源（不問，摘要裡列出）

依 `site.language` 填 `research.community_sources` 的預設：

| 語言 | 預設社群來源 |
|---|---|
| zh-TW | threads.net、ptt.cc、dcard.tw |
| 其他 | reddit.com、quora.com（之後語言包補齊） |

`community_search_hints` 留空（S3 用 `site:{網域}`）；使用者說了特定看板就填進去。

### 2.6 寫檔

寫進 profile 的 `site`、`cannibalization`、`research`、`adapters.read_source`。摘要範例：

```
第 2 段完成：fude.studio，42 篇文章（清單從網站地圖讀的，可能有漏）。
偵測：語言 zh-TW（html lang）、品牌「拜拜日曆」（og:site_name）、平台 WordPress（/wp-json/ 有回應）。
寫進了 profile.yaml、content-inventory.csv
```

`setup.parts.site_data` 設 done。
