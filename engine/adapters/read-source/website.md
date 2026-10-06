# 讀取來源：直接讀網站（預設）

> 不預設任何平台或框架。站專屬的讀取細節寫在 `profile.adapters.read_source.website`。

## 能力宣告

| 動作 | 支援 | 說明 |
|---|---|---|
| 列出 | 有 | 每篇的網址、標題、H1、描述、發布與更新日期、內容型態 |
| 抓回 | 有 | 網址 → 中立 md（只有網站上看得到的內容；要 JS 才產生的內容可能抓不到） |
| 涵蓋狀態 | 預設「未確認」 | 只靠 sitemap、feed 或沿連結爬時，sitemap 本身可能漏列 |

## 列出

依序試，前一種拿得到就不用下一種：

| 順序 | 方法 | 說明 |
|---|---|---|
| 1 | `profile.adapters.read_source.website.sitemap_url`；沒填就找 robots.txt 的 `Sitemap:` 行，再試 `/sitemap.xml`、`/sitemap_index.xml` | 幾乎所有 CMS 都會產生。sitemap index 要往下展開每個子 sitemap |
| 2 | RSS／Atom feed（`feed_url`，或首頁 `<link rel="alternate">`） | 大部分部落格都有，但通常只列最近 N 篇 |
| 3 | 從首頁或文章列表頁沿連結爬，限深度 2 | 前兩種都沒有時的保底 |

每頁讀 HTML 抽出：網址、`<title>`、H1、meta description、發布與更新日期（`article:published_time`、JSON-LD、`<time>`）、內容型態（文章／分類頁／標籤頁／其他，依網址樣式與頁面結構判斷），寫進 `content-inventory.csv`。**內文不存**，要用時再「抓回」。

### 抓不到時依序退

1. 一般請求（curl）
2. 帶瀏覽器 User-Agent：`curl -A "{profile 的 user_agent，沒填用 Mozilla/5.0}"`
3. 用瀏覽器開（Chrome MCP 或 Playwright）

- 遵守 robots.txt，限制請求速度（同一網域每秒最多 2 個請求）。
- **NEVER 用 HTTP 200 判斷頁面存在**：有些站未發布或已刪除的頁也回 200（例：拜拜日曆）。判斷頁面存在要看 sitemap 有沒有列，或頁面內容是不是正常文章（有 H1、有正文、不是 404 樣板）。
- WebFetch 會摘要內容、也可能被擋（例：拜拜日曆的 sitemap 用 WebFetch 會 403），所以列出與抓回一律用 curl 或瀏覽器拿原文。
- 動態產生的 sitemap（例：拜拜日曆的 `src/app/sitemap.js` 是從 WP API 抓已發布文章動態產生）不能 grep 原始碼，一律抓線上版。

## 抓回

網址 → 中立 md：

1. 照上面的退路拿到 HTML。
2. 取文章主體（`<article>`、`<main>`，或去掉 header／nav／footer 後最長的區塊）。
3. 轉成 markdown，保留標題層級、清單、表格、連結。
4. 字數明顯比預期少（例：比 inventory 記的描述還短、主要段落整段消失）→ 可能是要 JS 才產生的頁，改用瀏覽器開再抓一次；還是不完整就回報「抓回不完整」，呼叫端不要把它當完整內容用。

有加分來源（`profile.adapters.read_source.extra`）時，抓回優先用加分來源拿原生格式。

## 涵蓋狀態

每次「列出」都標記涵蓋狀態，寫在 content-inventory.csv 的開頭註解：

| 涵蓋狀態 | 什麼時候 |
|---|---|
| 已確認完整 | 從 CMS API 或 repo 拿到全部已發布內容，或使用者確認過清單 |
| 未確認 | 只靠 sitemap、feed 或沿連結爬 |
| 失敗 | 網站整個讀不到 |
| 網站未上線 | `site.domain` 是空的，沒有網站可讀 |
| 只收本系統 | `profile.content_inventory.include_existing` 為 false：使用者選擇不收網站上的既有文章，清單只有這套系統寫的文章。對這套系統來說清單是完整的 |

清單可以是空的（只有表頭）。空清單是正常狀態，用到清單的每一步都要照「清單是空的」的規則往下跑，不算錯誤。

任何「沒有」「零」「沒過期」「沒待處理」的結論，都要先確認涵蓋狀態是「已確認完整」或「只收本系統」；不是的話照「未確認」處理並在報告寫出來。**沒看到不等於不存在。**

## content-inventory.csv 格式

```
# coverage: 未確認
# read_at: 2026-10-05
# method: sitemap
url,title,h1,content_type,in_cannibalization_scope,guessed_main_keyword,written_by_engine,published_at,read_at
```

| 欄位 | 內容 |
|---|---|
| url | 完整網址 |
| title、h1 | 頁面標題、H1 |
| content_type | article／category／tag／page／other |
| in_cannibalization_scope | yes／no；照 `profile.cannibalization` 的 include／exclude 樣式，沒設定時 article 為 yes |
| guessed_main_keyword | 從 title、H1、網址 slug 推測的主關鍵字 |
| written_by_engine | 對得到 runs/ 裡某一篇就填那篇的 slug；設定當下已存在的舊文章填「基準」；之後新出現、不是這套系統寫的填「外部」 |
| published_at、read_at | 發布日、這次讀取日期 |

更新時以網址為鍵：新網址新增一列，舊網址更新 title、h1、日期，`written_by_engine` 不覆蓋。
