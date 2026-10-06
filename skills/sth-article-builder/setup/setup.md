# /sth-article-builder setup：站點設定精靈

> 由 `/sth-article-builder` SKILL.md §1.2 帶進來：使用者打 `/sth-article-builder setup …` 時讀這份照做。下文的「參數」是 `setup` 後面的字（去掉 `--site`）。

> 精靈的目標：**任何站都能靠它設定完成，不需要人工補檔**。精靈搞不定的站，是精靈的缺口，回頭修精靈。

## 原則

1. **能偵測就不問。** 偵測以直接讀網站為主；有網站程式碼（`site.repo_path`）就加讀 repo；有 CMS 權限再加讀 CMS。
2. **設定放一處，資源可以在任何資料夾。** 設定檔放在 `{站}`；網站程式碼、團隊文件、舊的指南放哪都可以，問到路徑就記進 profile（`site.repo_path`、`workspace.resources`），之後都從那裡讀。**不要把目前資料夾當成網站 repo。**
3. **不預設任何站點知識。** 不因為站名、產業、使用者是誰就假設平台、框架、讀者或規則。每一項都要有偵測到的證據，證據寫在該段的摘要裡；偵測不到就問。
4. **要問就用選擇題**，第一個選項是偵測或推薦的值並寫理由。每段只給摘要和**最多 3 個要決定的點**。
5. **每段做完馬上寫檔**，更新 `profile.setup.parts`，可以中斷續跑。
6. **使用者已有的文件整份匯入，不摘要、不刪減**（見 [parts/import.md](parts/import.md)）。
7. 對使用者說白話，用 `~/article-engine/plain-terms.md` 的說法。
8. 不寫進任何敏感值（密碼、token、secret），只記「去哪裡讀」。
9. 所有對外的寫入（在平台建文章、改網站 repo 的檔）都先問；精靈對網站 repo 與參考資料夾只讀，只寫 `{站}`。

## 0. 站點設定資料夾與資源資料夾

### 0.1 設定放哪（`{站}`）

| 情況 | 位置 |
|---|---|
| `--site <名稱>` | `~/content-sites/{名稱}/` |
| 目前資料夾已經有 `profile.yaml` | 目前資料夾（接著設定） |
| 目前資料夾往上找得到 `profile.yaml` 或 `content-ops/profile.yaml` | 那個資料夾 |
| 都沒有（第一次設定） | 問一次：「設定檔放在目前這個資料夾（{目前路徑}）嗎？」推薦：目前資料夾不是 git repo → 就放這裡；是 git repo（代表你在網站程式碼裡面）→ 推薦另外開一個資料夾，或放 `{repo}/content-ops/` |

`{站}` 是設定與每篇工作檔（runs/）的家，跟網站程式碼分開。`{站}` 剛好在某個 git repo 裡時，提醒一句「`runs/` 是每篇的工作檔，建議加進 .gitignore」，不自己改 .gitignore。

### 0.2 資源在哪（第一次設定時，在第 1 段之前問）

1. **網站程式碼在哪？**
   1. 沒有（例：網站是 WordPress 或其他 CMS，沒有程式碼可讀）
   2. 給路徑（可以拖資料夾進來）
   3. 幫我找：在 `~/Documents`、`~/Projects` 底下找名字或 `package.json` 的 name 含站名的資料夾，列出候選
   給了路徑 → 確認資料夾存在、是 git repo（不是也可以，只是 git 相關動作不能用），寫進 `site.repo_path`（絕對路徑）。
2. **還有其他要我讀的資料夾嗎？**（例：團隊的文件、舊的寫作指南、關鍵字表）沒有就跳過；有就逐一記進 `workspace.resources`（路徑＋一句話說裡面放什麼）。

之後任何一段要讀網站程式碼，一律到 `site.repo_path`；要找使用者的既有文件（匯入），先看 `workspace.resources`。之後要加資源資料夾或改路徑：`/sth-article-builder setup 資源`。

## 1. 判斷用法

| 參數 | 行為 |
|---|---|
| 空白，沒有 `{站}/profile.yaml` | 問路線：**快速開始**（第 1、2 段，其他全用預設，最快寫出第一篇）或**完整**（第 1–8 段，第 3–6、8 段可跳過）。推薦：站上已經有寫作指南或品牌規範文件 → 完整；沒有 → 快速開始 |
| 空白，有 profile 但 `setup.parts` 還有 `todo` | 從第一個 `todo` 的段落接著跑（快速開始路線只看第 1、2 段） |
| 空白，都設好了 | 顯示狀態（§3） |
| `狀態` | 顯示狀態（§3） |
| 段落名稱 | 只跑那一段（補建或修改），名稱對照見 §2 |

## 2. 八個段落

| 段 | 名稱（也是指令參數） | 做法 | 必要？ | 寫哪些檔 |
|---|---|---|---|---|
| 1 | Keyword 搜尋量工具 | [parts/1-keyword-tool.md](parts/1-keyword-tool.md) | 必要 | profile `adapters.keyword_volume` |
| 2 | 站點資料 | [parts/2-site-data.md](parts/2-site-data.md) | 必要 | profile `site`、`cannibalization`、`research`、`adapters.read_source`；content-inventory.csv |
| 3 | keyword-plan | [parts/3-keyword-plan.md](parts/3-keyword-plan.md) | 可跳過 | keyword-plan/ |
| 4 | brand voice | [parts/4-brand-voice.md](parts/4-brand-voice.md) | 可跳過 | brand-voice.md |
| 5 | writing guide | [parts/5-writing-guide.md](parts/5-writing-guide.md) | 可跳過 | writing-guide.md；profile `article_count`、`frontmatter`、`writing` |
| 6 | audit rule | [parts/6-audit-rule.md](parts/6-audit-rule.md) | 可跳過 | audit-rule.md、extensions/；profile `audit`、`extensions` |
| 7 | 發佈平台設定 | [parts/7-publish.md](parts/7-publish.md) | 建議 | profile `adapters.publish`；repo 串接時另寫 publish-rules.md |
| 8 | 封面設定 | [parts/8-cover.md](parts/8-cover.md) | 可跳過 | profile `adapters.cover` |

段落名稱比對寬鬆（`資源` 另外對到 §0.2）：`搜尋量`、`站點`、`關鍵字規劃`、`語氣`、`寫作指南`、`查核`、`發佈`、`封面` 都認得。

每段開始前讀對應的 parts 檔照做。每段結束：

1. 寫檔（含 profile.yaml，保留其他段已寫的欄位，不整檔覆蓋別段的值）。
2. `setup.parts.{段}` 設成 `done`（照使用者的選擇設好）、`default`（用內建預設）或 `skipped`。
3. 印一行「第 N 段完成：{一句話結果}。寫進了 {檔名}」。
4. 完整路線 → 問「接著做第 N+1 段，還是先停在這裡？」；快速開始 → 第 2 段做完就結束。

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

## 3. 狀態畫面

```
站點設定：{站}（{site.name}，{site.domain}）
引擎 {VERSION}｜設定檔格式 {schema_version}

1 Keyword 搜尋量工具   ✅ Keyword Surfer（2026-10-05 試查過）
2 站點資料             ✅ 42 篇文章，清單未確認完整（從網站地圖讀的）
3 keyword-plan        ⏭ 跳過 → /sth-article-builder setup keyword-plan
4 brand voice         ⚙ 用預設語氣 → /sth-article-builder setup brand voice
5 writing guide       ⚙ 用預設 → /sth-article-builder setup writing guide
6 audit rule          ⚙ 用通用查核 → /sth-article-builder setup audit rule
7 發佈平台設定         ✅ 只產出檔案
8 封面設定             ⏭ 不產 → /sth-article-builder setup 封面設定

已寫文章：0 篇（前 3 篇會每一步都問你）
```

圖示：✅ 已完成、⚙ 用預設、⏭ 跳過、⬜ 還沒做。每一項沒完成的都附要打的指令。

## 4. 結束時

印出：設定資料夾路徑、這次寫了哪些檔、接下來可以打 `/sth-article-builder <主關鍵字>` 寫第一篇。

設定過程中遇到精靈處理不了的狀況（偵測失敗又問不出答案、轉接器不支援這個平台），**照實告訴使用者卡在哪**，記進 `{站}/setup-issues.md`（日期、哪一段、發生什麼、暫時怎麼處理），不要自己捏造設定值讓它看起來完成。
