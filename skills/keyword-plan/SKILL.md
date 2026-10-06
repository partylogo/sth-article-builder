---
name: keyword-plan
description: 建立或匯入站的關鍵字規劃（主題總覽頁 pillar、底下的子頁、詞庫）。/sth-article-builder 用它回答「這個詞屬於哪個主題、該連去哪、量多少」，不是待寫清單。用法：匯入既有規劃檔、從種子詞新建、整理未分類的詞、看狀態。只能手動觸發。
disable-model-invocation: true
argument-hint: "[匯入 <檔案…> | 新建 <種子詞…> | 整理未分類 | 狀態] [--site 名稱]"
---

# /keyword-plan：關鍵字規劃

輸入：$ARGUMENTS


## 原則

1. **不是待寫清單**：不排優先順序、不排時程、不提「下一篇寫什麼」。它只回答一個詞屬於哪個主題、該連去哪幾篇、量多少。主關鍵字永遠由使用者給。
2. **原始檔只讀**：匯入時把來源檔原樣複製到 `{站}/keyword-plan/_source/`，在副本上轉格式，原檔一個字都不改。
3. **沒看到不等於不存在**：現有文章對不到的子頁標「未確認」，不標「未上線」，除非文章清單的涵蓋狀態是「已確認完整」。
4. 可以只建一兩個主題；主題頁和子頁可以「未上線」。
5. 這是使用者主動跑的工具，每個要決定的點都問；問法用選擇題，第一個選項是推薦值並寫理由。說白話（`~/article-engine/plain-terms.md`）。

## 0. 找站點設定

同 `/sth-article-builder` SKILL.md §1.1。找不到就停，提示先跑 `/sth-article-builder setup`。讀 `profile.yaml`、`content-inventory.csv`。清單檔不存在時：`profile.content_inventory.include_existing` 為 true（沒填＝true）→ 先照讀取來源轉接器「列出」建一份；false → 建只有表頭的空檔，**不讀網站**。清單是空的照常往下，對文章那一步就是全部對不到。

## 1. 判斷用法

| `$ARGUMENTS`（去掉 `--site`） | 行為 |
|---|---|
| 空白，`{站}/keyword-plan/` 不存在 | 問：匯入現有規劃檔（手上有就推薦）／從種子詞新建／先不建 |
| 空白，已存在 | 顯示狀態（§5） |
| `匯入 <檔案…>` | [import.md](import.md) |
| `新建 <種子詞…>` | [create.md](create.md)；已有規劃時，新的主題接在後面，不覆蓋既有主題 |
| `整理未分類` | §4 |
| `狀態` | §5 |

做完匯入或新建：profile 的 `keyword_plan.enabled: true`、`keyword_plan.dir: keyword-plan`；被 `/sth-article-builder setup` 呼叫時，`setup.parts.keyword_plan` 設 done。

## 2. 共用：查量

需要查量時，照 `profile.adapters.keyword_volume.tools` 的轉接器（`~/article-engine/adapters/keyword-volume/{tool}.md`）「查一個詞」或「批次查」。

- 先查 `keywords.csv` 裡已有的；查詢日期在 90 天內的不重查。
- 工具是「無」：量留空、`volume_type` 填「無」，主題分群改依現有文章與使用者列的類別（create.md 寫了怎麼做）。
- 查到一半工具連不上（例：Keyword Surfer 跳驗證碼）：已查到的先寫檔，請使用者處理後接著查。

## 3. 共用：對到現有文章

把 `content-inventory.csv` 的每一篇文章對到子頁：

1. 文章的推測主關鍵字、標題、H1 含子頁主關鍵字（含變體：同義、簡繁、有無空格、常見錯字、俗稱）→ 對到。
2. 一篇對到多個子頁 → 取主關鍵字最長、最具體的那個；其餘列進「衝突」給使用者看。
3. 對到的子頁填網址、狀態「已上線」。
4. 對不到的子頁：清單涵蓋狀態是「已確認完整」或「只收本系統」→ 狀態「未上線」；「未確認」「失敗」→ 「未確認」。
5. 有文章對不到任何子頁 → 列在狀態畫面的「沒有歸屬的文章」，不自動建子頁。

主關鍵字比對詞庫時一律認變體，變體寫進 keywords.csv 的同一個 `subpage`。

## 4. 整理未分類

`/sth-article-builder` 收尾時，主關鍵字不在任何子頁的，會放進 `_unsorted.md`。

1. 列出 `_unsorted.md` 的每個詞與它的文章網址。
2. 每個詞給建議：歸到哪個既有主題（理由一句話）／開新主題／維持未分類。
3. 使用者確認後搬過去，`_unsorted.md` 刪掉那列。

## 5. 狀態畫面

```
關鍵字規劃：{站}/keyword-plan/
詞庫 {N} 個詞（最舊的查詢日期 {YYYY-MM-DD}；{M} 個是推定日期）
文章清單涵蓋狀態：{已確認完整／未確認}

主題                 主題頁       子頁  已上線  未上線  未確認
拜拜知識（例）        已上線       12    8       2       2
…
未分類：3 個詞 → /keyword-plan 整理未分類
沒有歸屬的文章：5 篇
```

不列「建議接下來寫什麼」。
