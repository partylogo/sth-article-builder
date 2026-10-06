# 關鍵字規劃的檔案格式

> 來源：plan-v5 §5.3。`/sth-article-builder` 讀這些檔（S1 查詞庫、開跑前判斷已寫過、S4 歸屬、S6 內連、S12 回填），欄位名稱不要改。

```
{站}/keyword-plan/
├─ keywords.csv     詞庫
├─ pillars.md       主題清單
├─ {pillar-id}.md   每個主題一份：子頁表
├─ _unsorted.md     還沒歸屬的詞（/sth-article-builder 收尾時放進來）
└─ _source/         匯入時原樣複製的來源檔（只讀）
```

## keywords.csv

```
keyword,volume,volume_type,source,region,queried_at,date_estimated,subpage
灶神,8100,精確,keyword-surfer,TW,2026-09-14,no,zaoshen/who-is-zaoshen
```

| 欄位 | 內容 |
|---|---|
| keyword | 詞 |
| volume | 月搜尋量；區間值寫成 `1000-10000`；沒有就留空 |
| volume_type | 精確／區間／相對／無 |
| source | 查量的工具（keyword-surfer、google-keyword-planner、none、匯入時填 `import:{來源檔名}`） |
| region | 地區，例：TW |
| queried_at | 查詢日期 YYYY-MM-DD |
| date_estimated | yes＝查詢日期是推定的（匯入時缺日期，用檔案修改時間）；no |
| subpage | 歸屬的子頁，寫成 `{pillar-id}/{子頁 id}`；變體與次要關鍵字也指向同一個子頁；還沒歸屬就留空 |

## pillars.md

```markdown
# 主題清單

| pillar-id | 主題 | 主題頁主關鍵字 | 主題頁網址 | 狀態 | 檔 |
|---|---|---|---|---|---|
| zaoshen | 灶神 | 灶神 | https://… | 已上線 | zaoshen.md |
```

## {pillar-id}.md

```markdown
# {主題}

主題頁：{主關鍵字}｜{網址或「未上線」}

| 子頁 id | 主關鍵字 | 量 | 次要關鍵字 | 狀態 | 網址 | 近 28 天成效 |
|---|---|---|---|---|---|---|
| who-is-zaoshen | 灶神是誰 | 2900 | 灶神由來、灶君 | 已上線 | https://… | |
```

- 子頁 id：英文小寫連字號，有網址時用網址的 slug。
- 狀態：未上線／草稿（/sth-article-builder 已產出、還沒網址）／已上線／未確認（清單不完整，對不到不代表沒有）。
- 近 28 天成效：有 Search Console 工具時填「點擊／曝光／平均排名」，沒有就留空。

## _unsorted.md

```markdown
# 未分類

| 詞 | 文章 | 加入日期 |
|---|---|---|
```

## 頁面規格（S6 內連用）

| 連結方向 | 數量 | 硬／參考 |
|---|---|---|
| 子頁 → 主題頁 | 至少 1 個，建議 2–3 個 | 至少 1 個是硬條件 |
| 子頁 ↔ 同主題子頁 | 1–3 個 | 參考 |
| 跨主題 | 0–2 個 | 參考 |

只連「已上線」（有網址）的頁；指向「未上線」的只寫進報告，不擋稿。
