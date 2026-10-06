# 第 1 段：搜尋量工具

## 說明卡

**這段設定什麼**：寫文章前，用什麼工具查一個詞每個月大約有多少人搜。

**為什麼需要**：寫文章時查關鍵字、選主關鍵字都靠搜尋量。同一個主題有好幾種說法時（例：「咖啡豆保存」和「咖啡豆怎麼保存」），量決定選哪個詞當主關鍵字。沒有工具的話只能憑感覺選詞，報告會標 ⚠️。

**要決定什麼**：用哪個工具（可以多選，例：Keyword Planner 查量＋Keyword Surfer 補相關詞）。

**方法**：讀 `~/article-engine/adapters/keyword-volume/` 底下每個轉接器開頭的能力宣告，每個轉接器一列。目前是：

| 方法 | 做什麼 | 你要準備 | 費用與時間 | 會動到外部嗎 |
|---|---|---|---|---|
| A. Keyword Surfer | 在 Google 搜尋頁旁邊顯示每個詞的月搜尋量和相關詞 | Chrome＋Keyword Surfer 擴充 | 免費，但要在 Chrome 安裝 Keyword Surfer 擴充；5 分鐘 | 不會。連續查 80 個左右 Google 會跳驗證碼，要你手動點 |
| B. Google Keyword Planner | Google 官方的月搜尋量、近 12 個月趨勢、相關詞；帳號沒投廣告時量是粗略區間 | Google Ads 帳號、開發者權杖、Google Cloud 的 OAuth 用戶端 | 免費；第一次約 30 分鐘 | 不會 |
| C. 不用工具 | 沒有量，只看 Google 的「其他人也問了」 | 不用 | 0 | 不會 |

**推薦**：只有使用者已經說過手上有 Google Ads 帳號與開發者權杖時，推薦 B（官方數字、不會跳驗證碼）。其他情況不標。

不能跳過；不想用工具就選 C。可以多選。

## 方法 A 的做法（Keyword Surfer）

1. **確認 Chrome 連得上**：`tabs_context_mcp`。連不上 → 說明要開 Chrome 與 claude-in-chrome 擴充，問「準備好了再試一次」或「先改用 C」。
2. **偵測有沒有裝 Keyword Surfer**：開 `https://www.google.com/search?q={範例詞}&hl={hl}&gl={gl}`，用轉接器「查一個詞」的抓法讀頁面。
   - 範例詞固定用「天氣」（每個地區都查得到量，不會因為詞太冷門拿到 N/A）。
   - 地區用 `site.region`、`site.language`；第 2 段還沒做時用使用者的語言推測（繁體中文 → `hl=zh-TW&gl=tw`）。
   - 頁面上找不到 Keyword Surfer 的數字與相關詞表 → 判定沒裝：給安裝連結（Chrome 線上應用程式商店搜「Keyword Surfer」），說「裝好跟我說，我再試一次」。
   - 回傳 `CAPTCHA` → 請使用者在 Chrome 手動通過驗證，再試一次。
3. **試查結果**：拿到數字就算通過，不問使用者「合不合理」。完成訊息一行：「Keyword Surfer 可以用（試查『天氣』：每月約 {量} 次）」。
   - 主詞是 N/A（範例詞也查不到）→ 照實說「工具有裝，但這次沒拿到數字」，問要再試一次還是改用其他方法。N/A 不代表 0。

## 方法 B 的做法（Google Keyword Planner）

1. 照轉接器「要準備的東西」一項一項帶使用者做；憑證由使用者自己貼進 `~/.config/article-engine/google-ads.json`（精靈只建空的範本檔、不經手密鑰）。問帳號有沒有廣告花費，記 `has_spend`。地區與語言用第 2 段的 `site.region`、`site.language`；第 2 段還沒做時問使用者。
2. 前置檢查：照轉接器的「前置檢查」。不通過 → 照實說缺什麼，問「準備好了再試一次」或「先改用其他方法」。
3. 用範例詞「天氣」試查，規則同方法 A 第 3 步。

## 方法 C 的做法

不做任何事，直接寫檔。

## 寫檔

```yaml
adapters:
  keyword_volume:
    tools: [keyword-surfer]
    tested_with: "天氣"
    tested_at: "{YYYY-MM-DD}"
```

`setup.parts.keyword_tool`：選了工具且試查通過 → done；選 C → default。
