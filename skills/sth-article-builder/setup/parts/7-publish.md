# 第 7 段：發佈平台設定


## 要決定的點

1. 寫進哪個平台
2. 連線資訊（偵測不到的部分）
3. 預設分類（平台有分類時）

## 步驟

1. **列出目前已有轉接器的平台**（讀 `~/article-engine/adapters/publish/` 底下的檔）：WordPress、repo 串接（網站內容放在 git repo 裡）、只產出檔案。
2. **推薦**依第 2 段偵測到的平台：

   | 偵測到 | 推薦 |
   |---|---|
   | WordPress | WordPress |
   | 有網站程式碼（`site.repo_path`），而且裡面有文章內容檔（第 2 段找到內容資料夾） | repo 串接 |
   | 其他平台（Ghost 等 CMS），目前沒有轉接器 | 只產出檔案；寫進 setup-issues.md「{平台} 還沒有發佈轉接器，先只產出檔案」 |
   | 還沒上線 | 只產出檔案 |

3. **WordPress**：
   1. 連線方式目前只支援 WP-CLI over SSH。問 SSH 主機（`user@host`）與 WordPress 安裝路徑；`site.repo_path` 的 `.env*` 裡有像主機 IP 的變數時列出來當候選，只讀不改。
   2. 試連：`ssh {host} "wp core version --path={wp_path} --allow-root"`（非 root 登入時不加 `--allow-root`，依結果決定 `wp_cli_flags`）。不通 → 照實說錯誤訊息，問要修好再試還是先只產出檔案。
   3. 讀分類：`wp term list category --fields=term_id,name,slug {flags}`，列出來問「新文章預設放哪個分類？」，寫進 `categories`、`default_categories`。
   4. 前端快取：網站跟 WordPress 不同網域（Headless）時，問「新文章上線後要不要打清快取的網址？」有的話記 `revalidate.url`，secret 只記「去哪裡讀」（例：某個 env 變數名稱）。
   5. markdown 轉 HTML：`site.repo_path` 裡有 `node_modules/marked` 就記絕對路徑；沒有就記空（轉接器會用 `npx -y marked`）。
   6. **不在平台上建測試文章**。試連只做唯讀指令。
4. **repo 串接**：照 `~/article-engine/adapters/publish/repo.md` 的 A1–A10 讀 repo、寫 `{站}/publish-rules.md`、給使用者確認、試跑（不寫進 repo）。這一步最多可以超過 3 個決定點（git 動作、每次要跑的指令、草稿怎麼表示），照轉接器的順序一個一個問。
5. **只產出檔案**：問輸出位置，預設 `runs`（每篇在 `{站}/runs/{slug}/draft.md`）。
6. **把 runs/ 對到網站文章**：`{站}/runs/` 已經有稿子時，用 slug 與標題對 content-inventory，填 `written_by_engine`；對不到的列出來請使用者貼網址。

寫進 profile 的 `adapters.publish`。`setup.parts.publish`：WordPress 試連成功 → done；repo 串接的規則使用者確認過 → done；只產出檔案 → done；跳過 → skipped（等同只產出檔案）。
