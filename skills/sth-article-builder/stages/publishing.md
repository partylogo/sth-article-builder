# 上線：S10–S12

> 各平台的完整操作在 `~/article-engine/adapters/publish/`；封面產圖步驟在 `~/article-engine/adapters/cover/`。

---

## S10　上草稿或產出檔案

照 `~/article-engine/adapters/publish/{profile.adapters.publish.platform}.md` 的「建草稿」動作。

（例：拜拜日曆是 WordPress：markdown → HTML → scp → `wp post create --post_status=draft` → 設分類 → 打 revalidate → 清暫存。）

- 記下轉接器回傳的 `{ref, url, status}`，寫進 state.json 的 `publish`（WordPress 的 ref 就是 post ID）。
- 一律建草稿（`profile.adapters.publish.wordpress.post_status`，預設 draft），不直接發布。
- 轉接器不支援的動作，跳過並寫進報告。
- `file-only`：草稿就是 `runs/{slug}/draft.md`，ref 填檔案路徑，url 留空。
- `repo`：照 `{站}/publish-rules.md` 寫進網站 repo（轉接器 B 段），報告列出動過的每個檔。

---

## S11　封面圖

照 `~/article-engine/adapters/cover/{profile.adapters.cover.type}.md`，主副標依下方規則生成（auto 模式不提案不詢問；互動模式照 gate `cover-pick` 提 3 案），產圖後：

- 發佈平台轉接器支援「設封面」：
  - 文章原本沒封面（WordPress：`_thumbnail_id` 空）→ 自動上傳並設為封面
  - 已有值 → **不覆蓋**，記進報告
- 不支援 → 只交付圖檔路徑，寫進報告
- `cover.type: none` → 跳過，報告寫「這個站沒有設定封面」

### 封面規則（查表，不做判斷）

| # | 決策點 | 規則 |
|---|---|---|
| 8 | 主標 | 照 `profile.adapters.cover.template_overlay.title_template` 選最合這篇的樣板，≤ `title_max_chars` 字 |
| 8b | 副標 | 照 `subtitle_rule`（預設：該篇差異化切角一句話），≤ `subtitle_max_chars` 字 |
| 9 | 主副標超字數 | 自動縮寫至上限內，不問（gate `cover-overflow`） |
| 10 | 檔名已存在 | 一律加 `-v2` 後綴，**永不覆蓋**（gate `cover-exists`） |
| 11 | 設封面圖 | 原本沒封面才自動設；已有值不覆蓋（gate `cover-featured`） |

> 例：拜拜日曆的主標樣板是「{主關鍵字}是誰」或「{主關鍵字}怎麼拜」，≤ 8 字；副標 ≤ 22 字。

---

## S12　收尾

只有主線能寫共用檔。多關鍵字模式時由主線收攏後統一寫（見 multi-keyword.md 硬性約束 1）。

1. **keyword plan**（有的話，格式見 `~/.claude/skills/keyword-plan/format.md`）：
   - S4 有對到子頁 → 更新該子頁的狀態與網址（還沒有網址就狀態「草稿」、網址留空）。
   - 沒對到 → 在 `_unsorted.md` 加一列（詞、runs 路徑或網址、日期），報告提醒 `/keyword-plan 整理未分類`。
   - S1 新查到的詞（state.json `keyword_data`）補進 keywords.csv：已有的詞只在新的查詢日期較新時更新量；`subpage` 填這篇的子頁（沒對到就留空）。
2. **content-inventory.csv**：檔案不存在就先建（表頭與開頭註解照 `~/article-engine/adapters/read-source/website.md`；`include_existing` 為 false 時涵蓋狀態寫「只收本系統」）。新增一列，網址留空（或填平台回傳的 url）、「是不是這套系統寫的」填 slug。
3. **profile.yaml**：`modes.articles_written` 加 1。
4. 產出最終報告，見 [../state-and-report.md](../state-and-report.md)，最後附 SKILL.md §5 的提醒。
