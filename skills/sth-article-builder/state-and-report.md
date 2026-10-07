# state.json 與最終報告


## 單次執行資料夾 `{站}/runs/{slug}/`

| 檔案 | 內容 |
|---|---|
| draft.md | 中立格式正文＋frontmatter |
| state.json | 目前步驟、模式、關鍵字數據、每個 gate 的決定、論斷分型、這次用了哪些預設 |
| intent-report.md | 意圖研究與大綱（含切角理由） |
| review-log.md | S8 自動修正的審計軌跡 |
| report.md | 最終報告 |
| cover.* | 封面圖（有的話；或記路徑） |

- runs/ 放在站點設定資料夾 `{站}` 裡，跟網站程式碼分開，不會進網站 repo。
- 多關鍵字並行時，子流程只寫自己的 runs/{slug}/。

## state.json

`{站}/runs/{slug}/state.json`，每個 stage 完成就寫。
單篇模式它是 context 爆掉時的續跑保險（配合 `/relay`）；多關鍵字模式它同時是**給 agent 的交接文件**。

```json
{
  "engine_version": "0.1.0",
  "schema_version": 1,
  "keyword": "灶神",
  "slug": "who-is-zaoshen",
  "mode": "auto",
  "stage": "S8",
  "defaults_used": ["brand-voice", "audit-rule"],
  "keyword_data": [{"kw": "灶神", "volume": 0, "volume_type": "精確", "source": "keyword-surfer", "overlap": 0}],
  "cannibalization": {"hit": false, "existing": [], "inventory_coverage": "未確認", "angle_note": ""},
  "decisions": [{"id": 1, "choice": "1 篇", "reason": "生日型長尾 0"}],
  "keyword_plan": {"pillar": "zaoshen", "subpage": "who-is-zaoshen", "pillar_url": null, "sibling_urls": []},
  "claims": [{"text": "", "type": "事實型", "status": "保留"}],
  "manual_checks": [],
  "artifacts": {"intent_report": "", "draft": "", "review_log": ""},
  "publish": {"platform": "wordpress", "ref": null, "url": null, "status": null},
  "cover": {"type": "template-overlay", "file": null, "ref": null},
  "process_issues": [{"stage": "S11", "category": "上稿與封面", "by": "agent", "text": "封面字數上限用字數算，中英混排被不必要地縮寫"}]
}
```

（例：拜拜日曆灶神那篇；原本的 `wp.post_id`、`wp.attachment_id` 對應現在的 `publish.ref`、`cover.ref`。）

`process_issues`：流程中碰到的流程問題，碰到當下就記（續跑或 context 被清掉也不會漏），S12 一起寫進 skill-issues.md。`by` 是 agent 或 user。

## 最終報告格式

寫進 `{站}/runs/{slug}/report.md`，同時在對話裡輸出。報告裡的字照 `~/article-engine/plain-terms.md`：不寫步驟代號（S1、S8……）、不寫內部用語（gate、階梯 3、fan-out），改寫成白話。

```markdown
# /sth-article-builder 完成報告 — {關鍵字}

✅ {平台} 草稿 {ref}（分類：{照 profile 的分類名稱}）
✅ 封面圖 {cover.ref 或檔案路徑}
⚠️ 有 N 項要你確認（見「要你親自確認的地方」）   ← 有人工檢查項才出現

## 我替你做的決定
| # | 決策點 | 選了什麼 | 理由 |
|---|---|---|---|

## 自動檢查
內部連結 x/x　引文 x/x　驗算 {名稱} 通過／自動修／中止　主關鍵字必要位置 x/x

## 審稿套用 X 處
改值 X　並列 X　降語氣 X　**刪除 X ← 建議抽查**
完整紀錄：{站}/runs/{slug}/review-log.md

## 沒把握的地方
（列出查不到資料而刪掉的每一條，以及規則沒涵蓋、選了最保守做法的地方）

## 要你親自確認的地方（打勾才算通過）
- [ ] …

## 這次用的預設
（品牌語氣、寫作指南、關鍵字規劃哪些沒建、用了內建預設。查核規則設定精靈目前不收，不列；state.json 的 `defaults_used` 照樣記 `audit-rule`）

## 這次碰到的流程問題
（skill 本身要改進的地方，不是這篇文章的內容問題。每條一行：分類｜誰記的｜一句話。沒有就寫「無」。寫完報告後照下方「寫進 skill-issues.md」記進去）

## 提醒
（SKILL.md §5，每則附要打的指令）
```

（例：拜拜日曆的報告開頭是「✅ WP 草稿 post {ID}（分類：拜拜知識＋神明介紹）」「✅ 封面圖 attachment {ID}」。）

多關鍵字模式：每個關鍵字一份，最後加一段合併摘要，**失敗的線要明列**。

篇數規則的樣本數少時（`profile.article_count.calibration_note`），「我替你做的決定」那張表要列出篇數判斷的依據數字，供使用者校準。

## 寫進 skill-issues.md

最終報告產出後，把「這次碰到的流程問題」每一條寫進 `{站}/skill-issues.md`，不另外問使用者（auto、互動模式都一樣）。設定精靈遇到處理不了的狀況、使用者在對話中叫你記的，也用同一個格式。

**什麼算流程問題**：skill、轉接器、工具哪裡不夠用或規則沒寫，讓這次要臨時判斷、手動補做、繞路或出錯（例：規則沒寫平手怎麼辦、轉接器抓錯欄位、後台回 403 流程只會說重新登入）。這篇文章本身的內容取捨、這個站的設定結論不記。

**分類**（擇一，選要改的檔在哪一段）：

| 分類 | 收什麼 |
|---|---|
| 設定精靈 | 7 段設定流程 |
| 研究與規劃 | 查關鍵字量、重複內容檢查、研究搜尋意圖、決定篇數 |
| 寫稿 | 列大綱、寫稿、查出處 |
| 審稿與檢查 | 審稿、自動檢查、要使用者確認的清單 |
| 上稿與封面 | 上草稿、做封面、收尾 |
| 工具與連線 | 查量工具、瀏覽器、後台連不上、電腦權限 |
| 其他 skill | keyword-plan、last-mile-review |

**誰記的**：`agent`（你自己發現、主動記的）／`user`（使用者在對話中叫你記的）。

**格式**（接在檔尾，編號接最後一條）：

```markdown
## {編號}. {一句話標題}

- 分類：{分類}｜誰記的：{agent／user}｜來源：《{主關鍵字}》{YYYY-MM-DD}
- 流程缺口：{哪裡不夠用}
- 這次怎麼發現的：{發生了什麼}
- 要怎麼改：{建議改哪個檔、怎麼改}
```

設定精靈記的，來源寫「設定精靈第 N 段 {YYYY-MM-DD}」。

**跟既有條目是同一件事**：不開新條，在原條目最後補一行「- {YYYY-MM-DD}《{主關鍵字}》又碰到：{一句話}」；誰記的不同時一起寫（例：「又碰到（user）」）。開新條前先讀過整份檔的標題。

寫完在報告最後一行註明「已記進 skill-issues.md 第 N、M 條」。
