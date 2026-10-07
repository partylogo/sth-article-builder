# 第 6 段：上稿方式

## 說明卡

**這段設定什麼**：文章寫好、檢查完之後，怎麼送進你的網站。

**為什麼需要**：寫完文章後照這裡上草稿、掛封面；文章開頭要填哪些欄位，也照這裡的上稿方式自動帶出。沒設定的話，每篇只產出一個檔案，要你自己複製貼上到後台。

**要決定什麼**：
- 送去哪裡
- 用誰的身分送
- 草稿要填哪些欄位、送出前檢查什麼（例：摘要字數上限）：照選的方法自動帶出，給你確認

不管選哪個方法，都是**一律建草稿、不發布**，送出前先給你看內容、等你同意。

**方法**

| 方法 | 做什麼 | 你要準備 | 時間 | 會動到外部嗎 |
|---|---|---|---|---|
| A. WordPress | 用 SSH 連主機，用 WP-CLI 建草稿、掛封面 | 主機帳號（`user@host`）、WordPress 安裝路徑 | 10 分鐘 | 設定時只讀（試連）；寫文章時會：建草稿 |
| B. 只產出檔案（跳過） | 草稿留在 `{站}/runs/`，你自己貼 | 不用 | 0 | 不會 |
| C. 讀程式碼看怎麼串接 | 讀網站和後台的程式碼，找出文章要怎麼送進網站，找到就直接設好：文章是 repo 裡的檔案 → 寫進 repo；後台有建文章的 API → 用你登入的後台建草稿 | 網站程式碼資料夾 | 15–30 分鐘 | 設定時只讀；寫文章時會：改 repo 的檔，或在後台建草稿 |

**推薦**：第 2 段偵測到 WordPress → A；第 2 段已經記了網站程式碼位置 → C。其他不標。

## 方法 B 的做法（只產出檔案）

問輸出位置，預設 `runs`（每篇在 `{站}/runs/{slug}/draft.md`）。

## 方法 C 的做法（讀程式碼看怎麼串接）

只讀程式碼，不打開網站、不打開後台頁面、不看後台的請求。

1. profile 還沒有 `site.repo_path` 時問「網站程式碼在哪？」（直接輸入，不給選項）。拿不到程式碼 → 照實說 C 做不了，回到卡片選 A 或 B。後台的程式碼在另一個資料夾時，問「後台的程式碼在哪？」，記進 `workspace.resources`。
2. **找文章從哪來**：新文章放的網址前綴（`site.article_url_pattern`）對到哪個路由檔，路由檔讀的是 repo 裡的內容檔，還是呼叫 API。
3. **依結果走一條**，結果和依據（檔案路徑＋行號）先給使用者確認再往下：

   | 查到 | 接著做 |
   |---|---|
   | 文章是 repo 裡的檔案 | 照下方「寫進 repo」 |
   | 文章從 API 來，程式碼裡有後台、後台有建文章的 API | 照下方「用你登入的後台」 |
   | 程式碼裡有 WordPress 的線索（`wp-json`、WordPress 主機變數） | 說「看起來是 WordPress」，改走 A |
   | 都不是，或找不到建文章的地方 | 照實說卡在哪，記進 skill-issues.md「{平台} 還沒有發佈轉接器」，回到卡片選 A 或 B |

### 寫進 repo

照 `~/article-engine/adapters/publish/repo.md` 的 A1–A10 讀 repo、寫 `{站}/publish-rules.md`、給使用者確認、試跑（不寫進 repo）。這條要決定的點比較多（git 動作、每次要跑的指令、草稿怎麼表示），照轉接器的順序一個一個問。

### 用你登入的後台

1. 從後台程式碼找：後台網址（`admin_url`）、API 網址、建草稿的路徑與欄位、上傳圖片的流程、欄位長度限制、登入資訊存在哪。
   - API 網址寫在 `.env*` 時，只讀名稱含 `API_BASE_URL`／`API_URL` 的那一個變數的值，其他變數只讀名稱。
   - 後台網址找不到時（例：只寫在部署設定外面），問使用者。
2. 照 `~/article-engine/adapters/publish/browser-session-api.md` 的「profile 設定」填齊欄位。登入資訊的存放方式不在轉接器支援的清單裡（目前只有 `logto-localstorage`）→ 照實說，記進 skill-issues.md，回到卡片。
3. 前置檢查：照轉接器的「前置檢查」。分頁停在登入頁 → 停，請使用者自己登入，**不替使用者選帳號或輸入密碼**。登入後跑唯讀呼叫（`js-check`），回 `ok: true` 才算通過。
4. **不建測試文章**。第一篇文章上草稿時才是第一次真的寫入，那時也會先給使用者看內容。

## 方法 A 的做法（WordPress）

1. 連線方式目前只支援 WP-CLI over SSH。問 SSH 主機（`user@host`）與 WordPress 安裝路徑；`site.repo_path` 的 `.env*` 裡有像主機 IP 的變數時列出來當候選，只讀不改。
2. 試連：`ssh {host} "wp core version --path={wp_path} --allow-root"`（非 root 登入時不加 `--allow-root`，依結果決定 `wp_cli_flags`）。不通 → 照實說錯誤訊息，問要修好再試、改用其他方法，還是先 B（只產出檔案）。
3. 讀分類：`wp term list category --fields=term_id,name,slug {flags}`，列出來問「新文章預設放哪個分類？」，寫進 `categories`、`default_categories`。
4. 前端快取：網站跟 WordPress 不同網域（Headless）時，問「新文章上線後要不要打清快取的網址？」有的話記 `revalidate.url`，secret 只記「去哪裡讀」（例：某個 env 變數名稱）。
5. markdown 轉 HTML：`site.repo_path` 裡有 `node_modules/marked` 就記絕對路徑；沒有就記空（轉接器會用 `npx -y marked`）。
6. **不在平台上建測試文章**。試連只做唯讀指令。

## 文章開頭的欄位（每個方法做完都要做）

照選的方法自動帶出 `frontmatter.fields`，整理成表（欄位、對到平台的哪個欄位、必填、字數上限、依據）給使用者確認，不另外問欄位清單：

| 方法 | 欄位從哪裡來 |
|---|---|
| A. WordPress | 預設 title／slug／date／modified／status／excerpt；excerpt 對到 WordPress 的摘要 |
| B. 只產出檔案 | 內建預設 title／slug／date／modified／status／excerpt |
| C 走「寫進 repo」 | repo.md A3 讀到的欄位定義（content collection schema 等）；欄位名照 repo（例：`description`、`pubDate`），記 `excerpt_is_meta_description` 對應哪個欄位 |
| C 走「用你登入的後台」 | 後台建文章 API 的欄位（`field_map`）；送出前檢查（`checks`）的字數上限要對照網站前台的程式碼（例：摘要超過幾字會被截斷、內文少於幾字不被收錄），只看後台程式會漏 |

## 把 runs/ 對到網站文章

`{站}/runs/` 已經有稿子時（例：之前選 B 跑過幾篇），用 slug 與標題對 content-inventory，填 `written_by_engine`；對不到的列出來請使用者貼網址。

## 寫檔

寫進 profile 的 `adapters.publish`。`setup.parts.publish`：A 試連成功、C 寫進 repo 的規則使用者確認過、C 用後台的唯讀呼叫通過、B 選好輸出位置 → done；沒選任何方法就離開 → skipped（等同 B）。C 查完但唯讀檢查還沒過 → 欄位先寫進去，記 todo，下次打 `setup 上稿` 從前置檢查接著做。
