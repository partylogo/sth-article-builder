# 發佈平台：repo 串接

> 網站內容放在 git repo 裡的站（Astro、Next、Hugo、Jekyll、Eleventy…）用這個。
> 引擎不寫死任何框架。做法分兩半：**setup 時讀懂 repo、寫成這個站的發佈規則**；**/sth-article-builder 上線時照規則做**。
> 規則寫在站設定 `{站}/publish-rules.md`，路徑記在 `profile.adapters.publish.repo.rules_file`。
> 網站 repo 的位置一律用 `site.repo_path`，跟站點設定資料夾分開。下文的 `{repo}` 就是它；所有指令都在 `{repo}` 跑（`cd "{repo}"` 或 `git -C "{repo}"`），**不在目前資料夾跑**。

## 能力宣告

| 動作 | 支援 | 說明 |
|---|---|---|
| 建草稿 | 有 | 照發佈規則把文章寫進 repo 的內容資料夾（草稿旗標照規則） |
| 精準修改 | 有 | 直接改 repo 裡那個檔 |
| 傳圖、設封面 | 依規則 | 規則有寫封面放哪、frontmatter 哪個欄位指過去就支援；沒寫就只把圖放進 runs/ |
| 回傳 | `{ref: 寫進 repo 的檔案路徑, url: 依規則組的網址, status: "repo-draft"}` | |

---

## A. setup：讀 repo、寫發佈規則（setup 第 7 段呼叫）

目標：回答「一篇新文章要怎樣才能出現在網站上」，每一條都要有證據（檔案路徑＋行號或指令輸出）。**只讀，不改 repo 任何檔。**

### A1. 先讀 repo 自己寫的規範

在 `{repo}` 找這些檔，有就全文讀：`README*`、`CONTRIBUTING*`、`CLAUDE.md`、`AGENTS.md`、`.cursorrules`、`.github/pull_request_template.md`，以及 `docs/` 底下檔名或內容提到 blog、post、article、content、文章、發文、寫作的檔。

裡面寫到的發文規定直接當規則（引用原文與出處），後面幾步拿來核對。

### A2. 內容放哪、檔名怎麼取

1. 用讀取來源 `adapters/read-source/repo.md` 的前置檢查找出內容資料夾與 glob（第 2 段做過就沿用 `profile.adapters.read_source.repo`）。
2. 看最近 5 篇的檔名與路徑樣式：
   - 一篇一個檔（`{slug}.mdx`）還是一篇一個資料夾（`{slug}/index.mdx`）
   - 檔名有沒有日期前綴、語言代碼
   - 副檔名（md／mdx）
3. 有多個語言或多個內容集合時，列出來問這套文章寫進哪一個。

### A3. frontmatter 規格

1. **找機器檢查的定義**（有的話它就是準）：內容集合的 schema 設定檔（例：Astro 的 `src/content/config.*`、`src/content.config.*`；Contentlayer 的 `contentlayer.config.*`；Nuxt Content、Hugo archetypes `archetypes/*.md`）。記下每個欄位：名稱、型態、必填與否、允許的值（enum）、預設值。
2. **看實際用法**：最近 5 篇的 frontmatter，記下 schema 沒寫但大家都有填的欄位、日期格式、標籤與分類實際用了哪些值。
3. **對照 sth-article-builder 的欄位**：title、slug、date、modified、status（草稿）、excerpt 各對到 repo 的哪個欄位；repo 沒有的欄位怎麼處理（例：沒有 slug 欄位 → 用檔名）。寫進 `profile.frontmatter.fields`（setup 第 5 段沒做過的話）。
4. **草稿怎麼表示**：有 `draft: true` 這類欄位就用；沒有的話，問使用者新文章寫進去之前要怎麼避免直接上線（例：先不 commit、放另一個分支）。

### A4. 內文慣例

從最近 5 篇看：

- 內部連結的寫法（相對路徑 `/blog/{slug}`、還是元件）
- 圖片語法與放置位置
- MDX 有沒有 import 元件、常用哪些元件、元件放在哪裡
- 開頭或結尾有沒有固定區塊（作者卡、行動呼籲元件、相關文章）

### A5. 圖片與封面

- 圖片放哪（`public/`、`src/assets/`、跟文章同資料夾）、檔名規則
- 封面用哪個欄位指過去、要不要另外產別的尺寸或格式（例：webp）
- 產圖或轉檔有沒有現成的腳本（`package.json` scripts、`scripts/` 資料夾）

### A6. 加一篇文章時還要改哪些地方

拿一篇現有文章的 slug 在整個 repo 搜（排除內容資料夾本身、`node_modules`、建置輸出）：

```bash
grep -rln "{現有文章 slug}" "{repo}" --exclude-dir={node_modules,.git,dist,build,.next,.astro} | grep -v "{內容資料夾}"
```

再換兩篇做一次。三篇都出現的檔，就是「加文章要一起登記的地方」候選（例：文章索引、術語表、導覽、轉址表、sitemap 設定）。逐一打開看它怎麼登記、是手動還是程式自動產生；自動產生的不用動。

### A7. 加完之後要跑的指令

讀 `{repo}/package.json`（或 Makefile、justfile）的 scripts，挑出跟內容有關的：格式化、lint、內容檢查、型別檢查、建置、測試。每一個記：

- 指令
- 做什麼
- 會不會改檔（格式化會）
- 大約多久、有沒有對外連線

**問使用者每次上稿要跑哪幾個**。預設只推薦「不對外、只檢查或格式化本機檔案」的那幾個；建置與部署不推薦。

### A8. git

- 看 `git -C "{repo}" log -20 --oneline` 的 commit 訊息慣例、有沒有分支命名慣例
- 問使用者：
  1. 只寫檔、不碰 git，由你自己 commit（推薦）
  2. 開一個分支並 commit，不推送
  3. 開分支、commit、推送並開 PR
- 選 2、3 時記下分支命名與 commit 訊息格式。選 3 需要 `gh` 已登入，前置檢查要試 `gh auth status`。

### A9. 寫成發佈規則、給使用者確認

寫 `{站}/publish-rules.md`（格式見下方 C）。每一條附證據。整份給使用者看，問「有要改的嗎？」，確認後才算這一段完成。

### A10. 試跑（不寫進 repo）

用一篇假文章（標題「測試文章」、slug `sth-article-builder-test`）照規則產生：會寫到哪個路徑、frontmatter 長什麼樣、要登記哪些地方、要跑哪些指令。**只印出來給使用者看，不寫檔、不跑指令**。schema 有必填欄位的，逐一核對假文章都有填。

---

## B. /sth-article-builder：照規則上稿（S10、S11）

### 前置檢查

- `rules_file` 存在。
- repo 的 git 工作區乾淨，或至少要寫的那幾個路徑沒有未 commit 的改動（`git -C "{repo}" status --porcelain -- {路徑}`）。有改動 → 不覆蓋，S10 跳過，報告寫原因。
- 規則選了 git 動作 2、3 時，目前分支不是規則說不能直接改的分支（例：main）。

### 建草稿（S10）

1. 讀 `{站}/publish-rules.md`。
2. 把 `runs/{slug}/draft.md` 轉成規則要的格式：
   - frontmatter 照規則的欄位對應換名稱、補必填欄位、草稿旗標設好
   - 內部連結、圖片語法照規則改寫
   - 規則要求的固定區塊照加
3. 寫到規則指定的路徑。**檔案已存在就不覆蓋**，改用 `{slug}-v2`，報告寫出來。
4. 照規則登記其他地方（A6 找到的）。
5. 照規則跑指令（A7 使用者選的那幾個）。指令失敗 → 不回滾已寫的檔，報告列出失敗的指令與錯誤訊息，標 ⚠️。
6. 照規則做 git 動作（A8）。
7. 回傳 ref（寫進 repo 的路徑）、url（依 `site.canonical_base` + `article_url_pattern` 組）、status `repo-draft`。
8. 報告列出這次動過的每個檔（`git -C "{repo}" status --porcelain` 的輸出）。

### 設封面（S11）

規則有寫封面放哪、哪個欄位指過去：把封面圖放到規則指定位置、照規則產其他尺寸或格式、更新 frontmatter 欄位。規則沒寫：只把圖放在 runs/，報告寫「這個站的規則沒有封面欄位」。

### 精準修改

直接改 repo 裡的檔。last-mile-review 套用修改時用這個（專案檔的「怎麼套用修改」寫：改 repo 裡的檔）。

---

## C. publish-rules.md 格式

```markdown
# 發佈規則：{站名}

> 由 /sth-article-builder setup 第 7 段讀 repo 產生，{日期}。repo：{site.repo_path}，HEAD {short sha}
> 這份是給 /sth-article-builder 照著做的。repo 改了寫法時，重跑 `/sth-article-builder setup 發佈平台設定`。

## repo 自己寫的規範
（A1 找到的原文與出處）

## 文章放哪
- 路徑樣式：…（證據：…）
- 副檔名：…

## frontmatter
| repo 欄位 | 型態 | 必填 | 允許值 | sth-article-builder 對應 | 證據 |
|---|---|---|---|---|---|

草稿怎麼表示：…

## 內文慣例
- 內部連結：…
- 圖片：…
- 元件：…
- 固定區塊：…

## 圖片與封面
…

## 加文章時還要登記的地方
| 檔 | 怎麼登記 | 證據 |
|---|---|---|

## 每次上稿要跑的指令
| 指令 | 做什麼 | 會改檔嗎 |
|---|---|---|

## git
（1／2／3 哪一種、分支與 commit 格式）

## 試跑結果
（A10 的輸出）
```
