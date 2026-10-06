# state.json 與最終報告

> 來源：拜拜日曆 auto-article §7（全文），加上 plan-v5 §4.1 的欄位。

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
  "cover": {"type": "template-overlay", "file": null, "ref": null}
}
```

（例：拜拜日曆灶神那篇；原本的 `wp.post_id`、`wp.attachment_id` 對應現在的 `publish.ref`、`cover.ref`。）

## 最終報告格式

寫進 `{站}/runs/{slug}/report.md`，同時在對話裡輸出。

```markdown
# /sth-article-builder 完成報告 — {關鍵字}

✅ {平台} 草稿 {ref}（分類：{照 profile 的分類名稱}）
✅ 封面圖 {cover.ref 或檔案路徑}
⚠️ 有 N 項要你確認（見「要你親自確認的地方」）   ← 有人工檢查項才出現

## 我替你做的決定
| # | 決策點 | 選了什麼 | 理由 |
|---|---|---|---|

## 機器閘門
內鏈 x/x　引文 x/x　擴充檢查 {名稱} 通過／自動修／中止　主關鍵字必要位置 x/x

## last-mile 自動套用 X 處
改值 X　並列 X　降語氣 X　**刪除 X ← 建議抽查**
完整紀錄：{站}/runs/{slug}/review-log.md

## 沒把握的地方
（列出走到階梯 3 的每一條、以及規則沒涵蓋而選了保守落點的地方）

## 要你親自確認的地方（打勾才算通過）
- [ ] …

## 這次用的預設
（brand voice、writing guide、audit rule、keyword plan 哪些沒建、用了內建預設）

## 提醒
（SKILL.md §5，每則附要打的指令）
```

（例：拜拜日曆的報告開頭是「✅ WP 草稿 post {ID}（分類：拜拜知識＋神明介紹）」「✅ 封面圖 attachment {ID}」。）

多關鍵字模式：每個關鍵字一份，最後加一段合併摘要，**失敗的線要明列**。

篇數規則的樣本數少時（`profile.article_count.calibration_note`），「我替你做的決定」那張表要列出篇數判斷的依據數字，供使用者校準。
