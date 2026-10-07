# 第 6 段：上稿方式

## 說明卡

**這段設定什麼**：文章寫好、檢查完之後，怎麼送進你的網站。

**為什麼需要**：寫完文章後照這裡上草稿、掛封面；文章開頭要填哪些欄位，也照這裡的上稿方式自動帶出。沒設定的話，每篇只產出一個檔案，要你自己複製貼上到後台。

**要決定什麼**：
- 送去哪裡
- 用誰的身分送
- 草稿要填哪些欄位、送出前檢查什麼（例：摘要字數上限）：照選的方法自動帶出，給你確認

不管選哪個方法，都是**一律建草稿、不發布**，送出前先給你看內容、等你同意。

**方法**：讀 `~/article-engine/adapters/publish/` 底下每個轉接器的能力宣告，每個一列，再加一列「幫我查」。目前是：

| 方法 | 做什麼 | 你要準備 | 時間 | 會動到外部嗎 |
|---|---|---|---|---|
| A. WordPress | 用 SSH 連主機，用 WP-CLI 建草稿、掛封面 | 主機帳號（`user@host`）、WordPress 安裝路徑 | 10 分鐘 | 設定時只讀（試連）；寫文章時會：建草稿 |
| B. 寫進網站程式碼 | 文章存成 repo 裡的檔案，照 repo 的規矩登記、跑檢查 | 網站程式碼資料夾；文章要存在 repo 裡 | 20 分鐘 | 設定時只讀；寫文章時會：改 repo 的檔 |
| C. 用你登入的後台 | 在你已登入的後台分頁裡，用你的身分呼叫後台的 API 建草稿 | 在 Chrome 登入後台；後台要有寫入 API | 15 分鐘 | 設定時只讀（唯讀呼叫）；寫文章時會：建草稿 |
| D. 只產出檔案（跳過） | 草稿留在 `{站}/runs/`，你自己貼 | 不用 | 0 | 不會 |
| E. 我不知道選哪個，幫我查 | 只讀不寫：查網站背後是什麼系統、後台有沒有 API，查完把 A–D 標上可不可行，回到這張卡再選 | 網站程式碼資料夾或後台網址（有的話） | 5–15 分鐘 | 只讀 |

方法之間的取捨（卡片上照寫）：用你本人登入的身分（A 的主機帳號、C）> 另外申請的機器金鑰 > 只產出檔案。逐格模擬填表太脆弱，這套不做。

**推薦**：第 2 段已經偵測到平台時：WordPress → A；文章存在 repo 裡 → B；其他不標。

不想設定就選 D。

## 方法 A 的做法（WordPress）

1. 連線方式目前只支援 WP-CLI over SSH。問 SSH 主機（`user@host`）與 WordPress 安裝路徑；`site.repo_path` 的 `.env*` 裡有像主機 IP 的變數時列出來當候選，只讀不改。
2. 試連：`ssh {host} "wp core version --path={wp_path} --allow-root"`（非 root 登入時不加 `--allow-root`，依結果決定 `wp_cli_flags`）。不通 → 照實說錯誤訊息，問要修好再試、改用其他方法，還是先 D。
3. 讀分類：`wp term list category --fields=term_id,name,slug {flags}`，列出來問「新文章預設放哪個分類？」，寫進 `categories`、`default_categories`。
4. 前端快取：網站跟 WordPress 不同網域（Headless）時，問「新文章上線後要不要打清快取的網址？」有的話記 `revalidate.url`，secret 只記「去哪裡讀」（例：某個 env 變數名稱）。
5. markdown 轉 HTML：`site.repo_path` 裡有 `node_modules/marked` 就記絕對路徑；沒有就記空（轉接器會用 `npx -y marked`）。
6. **不在平台上建測試文章**。試連只做唯讀指令。

## 方法 B 的做法（寫進網站程式碼）

profile 還沒有 `site.repo_path` 時先問路徑。照 `~/article-engine/adapters/publish/repo.md` 的 A1–A10 讀 repo、寫 `{站}/publish-rules.md`、給使用者確認、試跑（不寫進 repo）。這個方法要決定的點比較多（git 動作、每次要跑的指令、草稿怎麼表示），照轉接器的順序一個一個問。

找不到文章內容檔（文章不在 repo，而是從 API 或資料庫來）→ 照實說「這個站的文章不在程式碼裡，B 不適用」，回到卡片。

## 方法 C 的做法（用你登入的後台）

1. 問後台網址（`admin_url`）。
2. 找出 API 的設定值，問使用者要用哪種方式找（可多選）：
   1. 讀網站程式碼：後台的原始碼在 `site.repo_path` 裡時，找 API 網址、建草稿的路徑與欄位、上傳圖片的流程、欄位長度限制、登入資訊存在哪
   2. 看後台實際的請求：請使用者在 Chrome 登入後台，我打開後台頁面，用 `read_network_requests` 看後台自己發出的請求（只看，不按任何按鈕、不送出表單）
   3. 手動輸入（照工程師給的 API 文件填）
3. 照 `~/article-engine/adapters/publish/browser-session-api.md` 的「profile 設定」填齊欄位。登入資訊的存放方式不在轉接器支援的清單裡（目前只有 `logto-localstorage`）→ 照實說，記進 skill-issues.md，回到卡片。
4. 前置檢查：照轉接器的「前置檢查」。分頁停在登入頁 → 停，請使用者自己登入，**不替使用者選帳號或輸入密碼**。登入後跑唯讀呼叫（`js-check`），回 `ok: true` 才算通過。
5. **不建測試文章**。第一篇文章上草稿時才是第一次真的寫入，那時也會先給使用者看內容。
6. 欄位整理成表給使用者確認：送出前檢查哪些欄位、上限多少、依據（程式碼哪一行，或哪個請求）。

## 方法 D 的做法（只產出檔案）

問輸出位置，預設 `runs`（每篇在 `{站}/runs/{slug}/draft.md`）。

## 方法 E 的做法（幫我查）

只讀，查完回到同一張卡。

1. 問要從哪裡查（可多選）：
   1. 讀網站（第 2 段讀過就沿用結果）：平台訊號（`/wp-json/`、generator、框架特徵）、文章網址從哪來
   2. 讀網站程式碼：文章是 repo 裡的檔，還是從 API 讀；有沒有後台程式；後台用什麼登入
   3. 打開後台頁面看：使用者給網址並自己登入，看後台頁面發出的請求
2. 把 A–D 每一列標上「可行／不可行／不確定」與一句依據，例：
   ```
   A. WordPress        不可行：/wp-json/ 沒有回應，程式碼裡沒有 WordPress
   B. 寫進網站程式碼    不可行：文章從 API 讀，不在 repo 裡
   C. 用你登入的後台    可行：後台程式碼裡有建文章的 API，登入方式轉接器支援
   D. 只產出檔案        可行
   ```
3. 回到卡片的「選哪個？」，這次有依據就標推薦。
4. 查到的平台沒有對應的轉接器 → 寫進 skill-issues.md「{平台} 還沒有發佈轉接器」。

## 文章開頭的欄位（每個方法做完都要做）

照選的方法自動帶出 `frontmatter.fields`，整理成表（欄位、對到平台的哪個欄位、必填、字數上限、依據）給使用者確認，不另外問欄位清單：

| 方法 | 欄位從哪裡來 |
|---|---|
| A. WordPress | 預設 title／slug／date／modified／status／excerpt；excerpt 對到 WordPress 的摘要 |
| B. 寫進網站程式碼 | repo.md A3 讀到的欄位定義（content collection schema 等）；欄位名照 repo（例：`description`、`pubDate`），記 `excerpt_is_meta_description` 對應哪個欄位 |
| C. 用你登入的後台 | 後台建文章 API 的欄位（`field_map`）；送出前檢查（`checks`）的字數上限要對照網站前台的程式碼（例：摘要超過幾字會被截斷、內文少於幾字不被收錄），只看後台程式會漏 |
| D. 只產出檔案 | 內建預設 title／slug／date／modified／status／excerpt |

## 把 runs/ 對到網站文章

`{站}/runs/` 已經有稿子時（例：之前用 D 跑過幾篇），用 slug 與標題對 content-inventory，填 `written_by_engine`；對不到的列出來請使用者貼網址。

## 寫檔

寫進 profile 的 `adapters.publish`。`setup.parts.publish`：A 試連成功、B 的規則使用者確認過、C 的唯讀呼叫通過、D → done；跳過 → skipped（等同 D）。
