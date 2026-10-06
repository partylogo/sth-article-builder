# 多關鍵字模式（fan-out）


S1/S2 在主線跑完、gate 清完之後，用 Workflow tool fan-out（Workflow 不能用時，改用 Agent tool 一個關鍵字開一個 agent，同一則訊息裡並行送出）。

```
主線 ├─ 灶神 S1→S2 ┐
     └─ 月老 S1→S2 ┘ → 有命中就一次問完
                    ↓
        ═══ fan-out ═══
     ├─ agent A：灶神 S3→S12（S12 只寫自己的部分）
     └─ agent B：月老 S3→S12（S12 只寫自己的部分）
                    ↓
        主線收攏：統一寫共用檔 + 合併報告
```

（例：拜拜日曆一次跑灶神、月老。）

## 硬性約束

| # | 約束 | 理由 |
|---|---|---|
| 1 | **agent 一律不准修改共用檔**：`{站}/keyword-plan/`、`{站}/content-inventory.csv`、`{站}/profile.yaml` | 並行寫入會靜默覆蓋，會掉資料且不報錯。由主線在收攏後統一寫（publishing.md S12 的 1–3 項） |
| 2 | agent 只寫自己 slug 的專屬檔（`{站}/runs/{slug}/` 底下的 intent-report / 草稿 / review-log / state.json） | 檔名帶 slug 不會撞 |
| 3 | **一個關鍵字一個 agent，不再細拆** | S3-S12 步步相依，拆開要靠回傳值傳脈絡會失真。一個關鍵字出 2 篇時兩篇留在同一 agent（需互鏈） |
| 4 | 不用 `isolation: 'worktree'` | 檔名不會撞，且會讓上稿路徑複雜化 |
| 5 | agent 回傳 null（掛掉／被跳過）時，**在報告中明說哪條線失敗**，不可靜默略過 |  |
| 6 | 模式（auto／互動）由主線決定後寫進每個 state.json，agent 照 state.json 的 `mode` 跑 | 互動模式的 gate 要回到主線問，agent 不能自己問 |
| 7 | 發佈平台是 `repo` 時，agent 只寫自己那篇文章檔與封面；發佈規則裡「加文章時還要登記的地方」、「每次上稿要跑的指令」、git 動作，由主線收攏後統一做 | 登記檔（索引、術語表）是共用檔，並行寫會互蓋；格式化與 git 同時跑會互相干擾 |

互動模式下多關鍵字仍可 fan-out，但 agent 遇到 gate 時回傳「待決」，由主線一次彙整問完再重新派工。關鍵字少（2–3 個）時，互動模式改成主線依序跑比較單純。

## agent prompt 樣板

```
讀 ~/.claude/skills/sth-article-builder/SKILL.md，對關鍵字「{keyword}」執行 S3 到 S12。
站點設定檔在 {站}/profile.yaml。
S1/S2 已完成，關鍵字數據與撞文結論在 {站}/runs/{slug}/state.json。
禁止修改 {站}/keyword-plan/、{站}/content-inventory.csv、{站}/profile.yaml（由主線統一寫）。
S12 只產出這篇的報告，不寫共用檔。
回傳 JSON：{ publish_ref, publish_url, cover_ref, decisions[], gate_results, lastmile_summary, manual_checks[] }
```
