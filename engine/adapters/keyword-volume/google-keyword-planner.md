# Keyword 搜尋量工具：Google Keyword Planner（Google Ads API）

> 來源：plan-v5 §4.2 搜尋量工具表「Google 官方：Keyword Planner（Google Ads API）」；Google Ads API 官方文件（2026-09 查證，現行版本 v25）：
> - Generate Historical Metrics：developers.google.com/google-ads/api/docs/keyword-planning/generate-historical-metrics
> - Generate Keyword Ideas：developers.google.com/google-ads/api/docs/keyword-planning/generate-keyword-ideas
> - REST 驗證與標頭：developers.google.com/google-ads/api/rest/auth
>
> 狀態：腳本已寫好、錯誤處理測過；**還沒用真的帳號跑過**（沒有憑證）。setup 第 1 段的試查就是第一次實測。

## 能力宣告

| 項目 | 值 |
|---|---|
| 量的型態 | 帳號有廣告花費：精確（近 12 個月平均月量）。沒有花費：區間（Google 給的是粗略分級的數字），`volume_type` 填「區間」 |
| 相關詞 | 有（`ideas`，由種子詞產生，附量） |
| 其他人也問了（PAA） | 沒有。要 PAA 時另外讀 Google 搜尋結果頁（同 none.md 的做法） |
| 地區 | 任何國家；`--geo` 用 geo target constant（台灣 2158、美國 2840） |
| 語言 | `--lang` 用 language constant（中文繁體 1018、英文 1000） |
| 成本 | API 免費；要 Google Ads 帳號與開發者權杖 |
| 每月趨勢 | 有（近 12 個月逐月量） |

## 要準備的東西（setup 第 1 段逐項帶使用者做）

1. **Google Ads 帳號**（有沒有投過廣告都可以；沒有花費時量是區間）。
2. **開發者權杖（developer token）**：在 Google Ads 管理員帳號的「API 中心」申請。剛申請的權杖只能用測試帳號，要申請 Basic Access 才能查真實資料。
3. **Google Cloud 專案**：啟用 Google Ads API，建立 OAuth 用戶端（桌面應用程式），記下 client ID、client secret。
4. **refresh token**：用 OAuth 桌面流程、scope `https://www.googleapis.com/auth/adwords` 拿到。
5. **customer ID**：要查量的那個 Google Ads 帳號 ID（10 位數，去掉連字號）。用管理員帳號登入時另外填 `login_customer_id`。

憑證寫成 JSON 檔放在 **repo 之外**（預設 `~/.config/article-engine/google-ads.json`），格式見腳本開頭說明。profile 只記路徑：

```yaml
adapters:
  keyword_volume:
    tools: [google-keyword-planner]
    google_keyword_planner:
      credentials_file: ~/.config/article-engine/google-ads.json
      geo: "2158"
      lang: "1018"
      api_version: v25
      has_spend: false     # 帳號有沒有廣告花費；false 時量標「區間」
```

## 前置檢查

```bash
python3 ~/article-engine/adapters/keyword-volume/scripts/gkp.py check --creds {credentials_file} --api {api_version}
```

- 回 `{"ok": true, …}` → 通過。
- 回 `{"error": …}` → 照錯誤訊息說明缺什麼（找不到憑證檔、換 token 失敗、權杖沒權限）。這次照 [none.md](none.md) 的路徑跑，報告標 ⚠️，不擋稿。
- 回 404 或版本相關錯誤 → API 版本可能已停用，到官方文件查目前版本，改 profile 的 `api_version`。

## 查一個詞（或一批詞）

```bash
python3 ~/article-engine/adapters/keyword-volume/scripts/gkp.py metrics "{詞1}" "{詞2}" \
  --creds {credentials_file} --geo {geo} --lang {lang} --api {api_version}
```

每行一個 JSON：`keyword`、`volume`（平均月量）、`monthly`（近 12 個月逐月）、`competition`、`close_variants`（Google 視為同一個詞的變體）。

寫進 state.json 的 `keyword_data`：`source` 填 `google-keyword-planner`，`volume_type` 依 `has_spend` 填「精確」或「區間」。`close_variants` 記進同一筆，S4 判斷變體時用。

## 拿相關詞

```bash
python3 ~/article-engine/adapters/keyword-volume/scripts/gkp.py ideas "{種子詞}" \
  --creds {credentials_file} --geo {geo} --lang {lang} --api {api_version} --limit 50
```

回傳的相關詞附量，S1 的「延伸搜尋」與 `/keyword-plan 新建` 的擴充都用這個。

## 注意

- 量每月更新一次，同一個月內重查結果一樣，不用重複查。
- 一次 `metrics` 可以帶多個詞，S1 把主關鍵字與變體一起查，省請求數。
- 沒有 PAA：S3 的「其他人也問了」照樣要讀 Google 搜尋結果頁。
