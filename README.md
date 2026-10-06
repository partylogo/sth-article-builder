# sth-article-builder

給 Claude Code 用的通用 SEO 文章產線。輸入主關鍵字，照站點設定跑完：關鍵字研究 → 撞文檢查 → 搜尋意圖研究 → 規劃 → 大綱 → 撰稿 → 出處稽核 → 審稿 → 機器檢查 → 上稿 → 封面 → 收尾。

任何網站都能用。站的規矩（讀者、語氣、寫作指南、查核規則、發佈方式）放在每個站自己的設定資料夾，平台與工具的差異放在轉接器。

## 指令

| 指令 | 用途 |
|---|---|
| `/sth-article-builder setup` | 設定精靈：讀網站偵測語言、品牌、平台與現有文章，只問偵測不到的事。8 段，可中斷續跑 |
| `/sth-article-builder setup 狀態` | 看設定進度 |
| `/sth-article-builder <主關鍵字>` | 寫一篇文章 |
| `/sth-article-builder cover <文章>` | 單獨補封面 |
| `/keyword-plan` | 匯入或從種子詞新建關鍵字規劃（主題頁、子頁、詞庫） |
| `/last-mile-review` | 發布前審稿：錯字、事實與邏輯、通用風格、SEO，加專案特別檢查 |

## 結構

```
skills/
├─ sth-article-builder/   指揮者：流程順序、關卡、續跑；stages/ 各步驟做法；writing/ 寫作與 SEO 規則；setup/ 設定精靈
├─ keyword-plan/          關鍵字規劃
└─ last-mile-review/      審稿
engine/                   共用引擎
├─ profile-schema.md      站點設定檔欄位
├─ adapters/              轉接器
│   ├─ keyword-volume/    Keyword Surfer、Google Keyword Planner、無
│   ├─ read-source/       讀網站、WordPress REST、repo 原始檔
│   ├─ publish/           WordPress、repo 串接、瀏覽器登入狀態的後台 API、只產出檔案
│   └─ cover/             模板疊字、無
├─ language/              語言包（zh-TW）
├─ audit-presets/         查核預設
└─ plain-terms.md         報告用語白話對照
```

## 安裝

```bash
git clone https://github.com/partylogo/sth-article-builder.git ~/Projects/sth-article-builder
cd ~/Projects/sth-article-builder && ./install.sh
```

`install.sh` 會把三個 skill 連到 `~/.claude/skills/`，引擎連到 `~/article-engine`。已經有同名的檔案或資料夾時會停下來，不覆蓋。

## 站點設定放哪

站點設定資料夾跟網站程式碼分開：在哪個資料夾跑 `/sth-article-builder setup`，設定就放那裡；網站程式碼路徑與其他參考資料夾記在設定檔裡。站點設定（profile.yaml、草稿 runs/）不要放進這個 repo。

## 狀態

- 版本見 `engine/VERSION`。
- 寫作規則與範例來自一個實際運作的中文民俗網站，見 [PROVENANCE.md](PROVENANCE.md)。
- 繁體中文為主；其他語言包還沒做。
