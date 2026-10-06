# 讀取來源（加分）：WordPress REST API

> 這是加分來源，不取代 [website.md](website.md)。有它時，content-inventory 的涵蓋狀態可以升為「已確認完整」，抓回可以拿到原生 HTML。

## 能力宣告

| 動作 | 支援 | 說明 |
|---|---|---|
| 列出 | 有 | 全部已發布文章（REST API 分頁拿完） |
| 抓回 | 有 | 原生 HTML（`content.rendered`），不受前端 JS 影響 |
| 涵蓋狀態 | 已確認完整 | 分頁全部拿完、總數等於 `X-WP-Total` 時 |

## 前置檢查

`curl -s "{profile.adapters.read_source.wp_rest.api_base}/posts?per_page=1" -I` 看得到 `X-WP-Total` 標頭。
拿不到 → 這次只用 website.md，涵蓋狀態維持「未確認」，報告寫原因。

## 列出

```bash
curl -s "{api_base}/posts?per_page=100&page={n}&status=publish&_fields=id,link,slug,title,date,modified,excerpt"
```

- 從 page=1 拿到 `X-WP-TotalPages` 為止。
- 拿到的筆數等於 `X-WP-Total` → 涵蓋狀態「已確認完整」；不等 → 「未確認」，報告寫差幾筆。
- 寫進 content-inventory.csv 的欄位同 website.md；`content_type` 一律 article；`h1` 用 `title.rendered`。
- 網址以前端的正式網址為準：`link` 是 CMS 網域時，改用 `profile.site.canonical_base` + `profile.site.article_url_pattern` 組出來（例：拜拜日曆的 CMS 在 cms.example.com，前端網址是 https://www.fude.studio/blog/{slug}）。

## 抓回

```bash
curl -s "{api_base}/posts?slug={slug}&_fields=id,title,content,excerpt,modified"
```

`content.rendered` 是原生 HTML，轉成中立 md 給呼叫端；需要原生格式的（例：last-mile-review 精準替換）直接用 HTML。

已發布文章的評估、盤點、改稿一律以這裡（或發佈平台的原始碼）為準，不看本地 md（會落後），也不信前端抽取（會掉字）。
