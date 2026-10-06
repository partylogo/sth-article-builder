# 發佈平台：在已登入的瀏覽器分頁裡呼叫後台 API

> 來源：2026-10-05 一個站在設定第 7 段的調研與唯讀測試（該站後台沒有公開 API，只能沿用瀏覽器登入狀態）。
> 適用：站有自己的後台，後台網頁用使用者的登入身分呼叫一組寫入 API，而使用者已經在 Chrome 登入那個後台。
> 站專屬的值全部寫在 `profile.adapters.publish.browser_session_api`，這份文件不寫任何一個站的網址或欄位。

## 原理

後台網頁登入後，瀏覽器裡存著使用者的登入憑證，後台按「儲存」時就是帶著它呼叫 API。這個轉接器在**同一個分頁裡**執行一段程式，用同一份憑證呼叫同一組 API，一次送出整篇，不模擬填表。

- 憑證只在網頁裡使用，**程式的回傳值不能含憑證**，只回傳結果（成功與否、草稿編號、錯誤訊息）。
- 用的是使用者本人的身分與權限，平台上的紀錄掛在使用者名下。
- 只建草稿，**不呼叫發布**。發布由使用者在後台按。

## 能力宣告

| 動作 | 支援 | 說明 |
|---|---|---|
| 建草稿 | 有 | 「建草稿」段 |
| 精準修改 | 沒有（第一版） | 要改就請使用者在後台改，或之後補「更新」動作 |
| 傳圖、設封面 | 有，建草稿時一起送 | 「上傳封面」段；profile 沒設 `upload_cover` 就只交付圖檔 |
| 回傳 | `{ref: 草稿編號, url: 公開網址（發布後才有效）, status: draft}` | url 用 `site.canonical_base` + `article_url_pattern` 組 |

## profile 設定

```yaml
adapters:
  publish:
    platform: browser-session-api
    browser_session_api:
      admin_url: ""            # 後台網址，分頁要開在這個網域
      api_base: ""             # API 網址
      auth:
        type: logto-localstorage   # 目前只支援這一種，見下方「登入資訊的位置」
        storage_key_regex: ""      # 例：^logto:.+:accessToken$
        resource: ""               # 憑證要發給哪個 API，例：https://api.example.com
      check_path: ""           # 唯讀呼叫用的路徑，確認身分有效，例：/api/ops/posts?limit=1
      create_draft:
        method: POST
        path: ""               # 例：/api/ops/posts
        id_field: id           # 回應裡草稿編號的欄位
        status_field: status
      upload_cover:            # 不支援上傳封面就整段刪掉
        presign_path: ""       # 例：/api/upload/presign
        presign_body: {}       # 固定要帶的欄位，例：{bucket: public}；name、content_type、file_size 由腳本補
        confirm_path: ""       # 例：/api/files/{file_id}/confirm
        payload_field: ""      # 草稿裡放封面編號的欄位，例：cover_file_id
        max_bytes: 0
        mime_types: []
      payload_defaults: {}     # 每篇固定的欄位值，例：{type: article, is_featured: false}
      field_map: {}            # 草稿 frontmatter 欄位 → API 欄位
      body_field: content      # 內文放哪個 API 欄位
      body_rules:
        strip_h1: true         # 平台有獨立標題欄位時，去掉內文第一個 H1
      slug_regex: ""           # 平台的 slug 規則；空＝不檢查
      required: []             # 送出前不能是空的 API 欄位，例：[title, slug, summary]
      checks: []               # 每項：field、max_chars 或 min_body_chars、why（送出前檢查，不通過就停）
      publish: none            # 固定 none：這個轉接器不發布
```

### 登入資訊的位置（`auth.type`）

| type | 讀法 |
|---|---|
| `logto-localstorage` | `localStorage` 裡符合 `storage_key_regex` 的鍵，值是 JSON，鍵的格式是「{權限範圍}@{API 網址}」（權限範圍可能是空的，例：`@https://api.example.com`），取 API 網址等於 `resource` 那筆的 `token`；有 `expiresAt`（秒）且已過期就停，請使用者重新整理後台頁面 |

其他登入方式（cookie、別家登入服務）還沒做：遇到時寫進 setup-issues，不要自己猜。

## 前置檢查（設定時做一次，每次開跑也做）

1. `tabs_context_mcp` 拿得到分頁；找一個網址在 `admin_url` 網域的分頁，沒有就開一個新分頁到 `admin_url`。
2. 分頁停在登入頁（例：公司門禁、後台登入）→ **停，請使用者自己登入**。不替使用者選帳號或輸入密碼。
3. 跑一次唯讀呼叫確認身分有效：

   ```bash
   ruby ~/article-engine/adapters/publish/scripts/bsapi.rb js-check {站}/profile.yaml
   ```

   把印出的程式用 `javascript_tool` 在分頁裡執行（GET `check_path`，只讀不寫）。回 `ok: true` 才算通過。
4. 不通過 → S10 跳過，草稿留在 runs/，報告寫原因（不算 abort）。

## 建草稿

1. **組送出內容**（只在本機，不送）：

   ```bash
   ruby ~/article-engine/adapters/publish/scripts/bsapi.rb payload {站}/profile.yaml {站}/runs/{slug}/draft.md
   ```

   - 照 `field_map` 從 frontmatter 取欄位，加上 `payload_defaults`，內文照 `body_rules` 處理後放進 `body_field`。
   - 照 `slug_regex`、`checks` 檢查，不通過就停並列出原因。
   - 寫出 `{站}/runs/{slug}/publish-payload.json`，並印出給使用者看的預覽（每個欄位一行、內文字數、前 200 字）。

2. **給使用者看預覽，等同意**（兩種模式都停，這是對外寫入，不是 gate）。auto 模式也一樣。
3. 有封面且 profile 有 `upload_cover` → 先照「上傳封面」拿到檔案編號，加進 payload 的 `payload_field`。
4. **產生送出程式**：

   ```bash
   ruby ~/article-engine/adapters/publish/scripts/bsapi.rb js-create {站}/profile.yaml {站}/runs/{slug}/publish-payload.json
   ```

   用 `javascript_tool` 在後台分頁執行印出的程式。
5. 回應 `ok: true` → 記 `{ref: id, status}` 進 state.json 的 `publish`。告訴使用者「草稿已建立，請到後台檢查後按發布」，附後台網址。
6. 回應 `ok: false` → 照錯誤處理表處置，不重送同一份內容，除非表上寫可以。

## 上傳封面

1. 產生「建立暫存檔案欄位」的程式並在分頁執行：`ruby …/bsapi.rb js-cover-input`。它會在網頁加一個隱藏的檔案欄位（`#nap-cover-input`），不碰後台原本的表單。
2. 用 `file_upload` 工具把封面圖檔放進 `#nap-cover-input`。
3. `ruby …/bsapi.rb js-cover-upload {站}/profile.yaml`，在分頁執行：檢查格式與大小 → presign → 上傳圖檔 → confirm，回傳檔案編號。程式結束時移除暫存欄位。
4. 失敗 → 草稿照樣建（不帶封面），報告寫原因，封面圖留在 runs/。

## 錯誤處理

| 回應 | 意思 | 處置 |
|---|---|---|
| `step: token` | 分頁裡找不到登入資訊，或已過期 | 請使用者重新整理後台頁面或重新登入，再跑一次 |
| 401 | 憑證無效 | 同上 |
| 403 | 這個帳號沒有後台權限 | 停，告訴使用者 |
| 409 | slug 已存在 | 停。不自動改 slug；問使用者要換 slug 還是去後台改那篇 |
| 400、422 | 欄位驗證失敗 | 照錯誤訊息修 payload，給使用者看修了什麼，再問一次 |
| 5xx、網路錯誤 | 平台暫時有問題 | 先用唯讀呼叫查這個 slug 有沒有已經建好，避免重複建立；沒有才問使用者要不要重送 |

## 不做的事

- 不把憑證印出、回傳、寫進檔案或交給終端機的程式。
- 不呼叫發布、排程、刪除。
- 不點後台頁面上的按鈕（刪除鈕常會跳瀏覽器確認框，會卡住操作）。
- 不替使用者登入。
