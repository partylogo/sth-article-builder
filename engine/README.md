# article-engine

`/sth-article-builder`（含 `/sth-article-builder setup`）與 `/keyword-plan` 共用的引擎目錄。

| 路徑 | 內容 |
|---|---|
| VERSION | 引擎版本號 |
| profile-schema.md | 站點設定檔 profile.yaml 的欄位定義 |
| adapters/keyword-volume/ | Keyword 搜尋量工具轉接器 |
| adapters/read-source/ | 讀取來源轉接器（讀網站、CMS API、repo） |
| adapters/publish/ | 發佈平台轉接器 |
| adapters/cover/ | 封面轉接器 |
| language/ | 語言包 |
| audit-presets/ | 查核預設 |
| plain-terms.md | 報告與提醒的白話對照表 |

每個轉接器檔開頭都有「能力宣告」，引擎依能力調整行為。
