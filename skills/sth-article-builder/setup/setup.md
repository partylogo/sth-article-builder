# /sth-article-builder setup：站點設定精靈

> 由 `/sth-article-builder` SKILL.md §1.2 帶進來：使用者打 `/sth-article-builder setup …` 時讀這份照做。下文的「參數」是 `setup` 後面的字（去掉 `--site`）。

> 精靈的目標：**任何站都能靠它設定完成，不需要人工補檔**。精靈搞不定的站，是精靈的缺口，回頭修精靈。

## 原則

1. **先給說明卡，使用者選了方法才動手。** 每段（第 2 段是每張小卡）開始時只給說明卡（格式見 §2），卡片給出之前不讀網站、不讀程式碼、不搜尋、不開瀏覽器。
2. **調查是一種方法，不是前置動作。** 「讀網站推測」「讀網站程式碼推測」「幫我查」都列在方法表裡，使用者選了才做。調查完把結果和依據給使用者確認，確認後才寫檔。
3. **一次一段。** 這段寫完檔才給下一段的卡，不一次丟好幾段的問題。
4. **推薦看情況。** 有具體理由才標推薦（例：使用者說過手上有指南、前一段已經讀過網站），理由寫在推薦後面。沒有理由就不標，不要為了有推薦而去調查。
5. **不預設任何站點知識。** 不因為站名、產業、使用者是誰就假設平台、框架、讀者或規則。調查得到的值都附依據；沒調查、使用者也沒說的，就問。
6. **每段做完馬上寫檔**，更新 `profile.setup.parts`，可以中斷續跑。
7. **使用者已有的文件整份匯入，不摘要、不刪減**（見 [parts/import.md](parts/import.md)）。
8. 對使用者說白話，用 `~/article-engine/plain-terms.md` 的說法；選項用 AskUserQuestion，畫面上的字全部用使用者的語言。
9. 不寫進任何敏感值（密碼、token、secret），只記「去哪裡讀」。
10. 所有對外的寫入（在平台建文章、改網站 repo 的檔）都先問；精靈對網站 repo 與參考資料夾只讀，只寫 `{站}`。

## 0. 設定放哪（`{站}`）

開場唯一的問題。照下表找，找得到就不問：

| 情況 | 位置 |
|---|---|
| `--site <名稱>` | `~/content-sites/{名稱}/` |
| 目前資料夾已經有 `profile.yaml` | 目前資料夾（接著設定） |
| 目前資料夾往上找得到 `profile.yaml` 或 `content-ops/profile.yaml` | 那個資料夾 |
| 都沒有（第一次設定） | 問「設定檔要放在哪裡？」：1. 目前這個資料夾（{目前路徑}）2. 另外指定一個資料夾。目前資料夾是 git repo（代表可能在網站程式碼裡面）時，在選項 1 後面註明「這裡是 git repo，`runs/` 建議加進 .gitignore」 |

`{站}` 是設定與每篇工作檔（runs/）的家，跟網站程式碼分開。不自己改 .gitignore。

**資源資料夾不在開場問。** 網站程式碼（`site.repo_path`）、團隊文件（`workspace.resources`）等到某個方法需要時才問路徑，問到就記進 profile，之後的段落直接用、不再問。要加或改：`/sth-article-builder setup 資源`（問「網站程式碼在哪？」「還有其他要我讀的資料夾嗎？」，各記一句話說裡面放什麼）。

## 1. 判斷用法

| 參數 | 行為 |
|---|---|
| 空白，沒有 `{站}/profile.yaml` | 給總覽（§3）並問要做哪幾段 |
| 空白，有 profile 但選定的段落還有 `todo` | 說「上次做到第 N 段」，從第一個 `todo` 的段落接著給卡 |
| 空白，都設好了 | 顯示狀態（§5） |
| `狀態` | 顯示狀態（§5） |
| 段落名稱 | 只跑那一段（補建或修改），直接給那段的卡；名稱對照見 §3 |
| `資源` | 見 §0 最後一段 |

## 2. 說明卡

每段開始時給一張卡，格式固定：

```
**第 N 段：{名稱}**

**這段設定什麼**：{一句白話}

**為什麼需要**：{寫文章時哪一步會用到；沒設定的話會怎樣}

**要決定什麼**：{這段結束時會定下來的值，條列}

**方法**
| 方法 | 做什麼 | 你要準備 | 時間 | 會動到外部嗎 |
|---|---|---|---|---|
| A. … | … | … | … | 不會／只讀／會：{做什麼} |

**推薦**：{方法}，因為 {理由}　← 沒有具體理由就整行不寫

**跳過的話**：{用什麼預設}／不能跳過
```

接著用 AskUserQuestion 問「選哪個？」，選項就是方法表的每一列（可多選的段落註明）。

- 方法表的每一列都要寫「會動到外部嗎」：純問答寫「不會」，讀網站、讀 repo、開後台頁面寫「只讀」，建文章、改 repo 寫「會：…」。
- 選項超過 4 個時（AskUserQuestion 上限），卡片照列全部，問題拆成兩層（例：先選「我自己提供」或「讓你查」，再選細項）。
- 選完照該段 parts 檔的「方法 X 的做法」做。做完把結果給使用者確認（調查類附依據），確認後寫檔。

## 3. 總覽與段落

第一次設定時，在 §0 之後給這張總覽：

| 段 | 名稱（也是指令參數） | 設定什麼 | 必要？ | 做法 | 寫哪些檔 |
|---|---|---|---|---|---|
| 1 | 搜尋量工具 | 用什麼工具查關鍵字的搜尋量 | 必要 | [parts/1-keyword-tool.md](parts/1-keyword-tool.md) | profile `adapters.keyword_volume` |
| 2 | 站點資料 | 網站基本資料、讀者與導流、既有文章要不要收（三張小卡） | 必要 | [parts/2-site-data.md](parts/2-site-data.md) | profile `site`、`content_inventory`、`cannibalization`、`research`、`adapters.read_source`；content-inventory.csv |
| 3 | 關鍵字規劃 | 哪些詞屬於哪個主題 | 可跳過 | [parts/3-keyword-plan.md](parts/3-keyword-plan.md) | keyword-plan/ |
| 4 | 品牌語氣 | 文章怎麼說話 | 可跳過 | [parts/4-brand-voice.md](parts/4-brand-voice.md) | brand-voice.md |
| 5 | 寫作指南 | 文章要守哪些規矩 | 可跳過 | [parts/5-writing-guide.md](parts/5-writing-guide.md) | writing-guide.md；profile `article_count`、`frontmatter`、`writing` |
| 6 | 查核規則 | 哪些內容一定要查證 | 可跳過 | [parts/6-audit-rule.md](parts/6-audit-rule.md) | audit-rule.md、extensions/；profile `audit`、`extensions` |
| 7 | 上稿方式 | 寫好的文章怎麼送進網站 | 建議 | [parts/7-publish.md](parts/7-publish.md) | profile `adapters.publish`；寫進 repo 時另寫 publish-rules.md |
| 8 | 封面 | 要不要自動產封面圖 | 可跳過 | [parts/8-cover.md](parts/8-cover.md) | profile `adapters.cover`；cover-template/ |

畫面上給使用者看「段、設定什麼、必要？」三欄就好，接著問：

1. 全部，從第 1 段開始
2. 只做必要的（第 1、2 段），其他之後再補
3. 自己挑（接著用多選列出 8 段）

答案記進 `setup.route`（all／required／custom）與 `setup.selected`（段落清單）。沒選到的段落記 `skipped`。

段落名稱比對寬鬆：`搜尋量`、`站點`、`網站資料`、`讀者`、`既有文章`（第 2 段第 3 張卡）、`關鍵字規劃`、`語氣`、`寫作指南`、`查核`、`上稿`、`發佈`、`封面` 都認得。

## 4. 每段的固定流程

1. 讀對應的 parts 檔。
2. 給說明卡，問選哪個方法。
3. 照「方法 X 的做法」做。需要資源資料夾而 profile 還沒有 → 這時才問路徑。
4. 結果給使用者確認。
5. 寫檔（含 profile.yaml，保留其他段已寫的欄位，不整檔覆蓋別段的值）。
6. `setup.parts.{段}` 設成 `done`（照使用者的選擇設好）、`default`（用內建預設）或 `skipped`。
7. 印一行「第 N 段完成：{一句話結果}。寫進了 {檔名}」。
8. 還有選定的段落 → 問「接著做第 {下一段}（{名稱}），還是先停在這裡？」；沒有了 → §6。

**跳過的段落**照下表用預設，`setup.parts` 記 `skipped`，狀態畫面顯示要打的指令：

| 段 | 跳過時 |
|---|---|
| 3 | 沒有 keyword plan：S4、S6 不做 pillar 歸屬與內連，報告標 ⚠️ |
| 4 | 用語言包的預設語氣 |
| 5 | 只用 core-principles＋seo-rules；frontmatter 用預設欄位；一律 1 篇 |
| 6 | 用通用查核預設 |
| 7 | 只產出檔案 |
| 8 | 不產封面 |

第一次建立 profile 時，`schema_version` 填 profile-schema.md 的目前版本，`modes.force_interactive_first_n` 填 3、`modes.articles_written` 填 0。

## 5. 狀態畫面

```
站點設定：{站}（{site.name}，{site.domain}）
引擎 {VERSION}｜設定檔格式 {schema_version}

1 搜尋量工具   ✅ Keyword Surfer（2026-10-05 試查過）
2 站點資料     ✅ example.com；既有文章不收，清單只收之後寫的
3 關鍵字規劃   ⏭ 跳過 → /sth-article-builder setup 關鍵字規劃
4 品牌語氣     ⚙ 用預設語氣 → /sth-article-builder setup 語氣
5 寫作指南     ⚙ 用預設 → /sth-article-builder setup 寫作指南
6 查核規則     ⚙ 用通用查核 → /sth-article-builder setup 查核
7 上稿方式     ✅ 只產出檔案
8 封面        ⏭ 不產 → /sth-article-builder setup 封面

已寫文章：0 篇（前 3 篇會每一步都問你）
```

圖示：✅ 已完成、⚙ 用預設、⏭ 跳過、⬜ 還沒做。每一項沒完成的都附要打的指令。

## 6. 結束時

印出：設定資料夾路徑、這次寫了哪些檔、跳過的段落與補設定的指令、接下來可以打 `/sth-article-builder <主關鍵字>` 寫第一篇。

設定過程中遇到精靈處理不了的狀況（調查失敗又問不出答案、轉接器不支援這個平台），**照實告訴使用者卡在哪**，記進 `{站}/setup-issues.md`。這份檔記的是**流程缺口**（精靈哪裡要改、這次怎麼發現的、要怎麼改），不記這個站的設定結論。不要自己捏造設定值讓它看起來完成。
