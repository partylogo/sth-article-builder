# 第 1 段：搜尋量工具

## 說明卡

**這段設定什麼**：寫文章前，用什麼工具查一個詞每個月大約有多少人搜。

**為什麼需要**：S1 關鍵字研究、S4 選主關鍵字都靠搜尋量。同一個主題有好幾種說法時（例：「咖啡豆保存」和「咖啡豆怎麼保存」），量決定選哪個詞當主關鍵字。沒有工具的話只能憑感覺選詞，報告會標 ⚠️。

**要決定什麼**：
- 用哪個工具（可以多選，例：Keyword Planner 查量＋Keyword Surfer 補相關詞）
- 要不要用一個詞試查

**方法**：讀 `~/article-engine/adapters/keyword-volume/` 底下每個轉接器開頭的能力宣告，每個轉接器一列。目前是：

| 方法 | 做什麼 | 你要準備 | 時間 | 會動到外部嗎 |
|---|---|---|---|---|
| A. Keyword Surfer | 在 Google 搜尋頁旁邊顯示每個詞的月搜尋量和相關詞 | Chrome＋claude-in-chrome 擴充＋Keyword Surfer 擴充 | 5 分鐘 | 不會。連續查 80 個左右 Google 會跳驗證碼，要你手動點 |
| B. Google Keyword Planner | Google 官方的月搜尋量、近 12 個月趨勢、相關詞；帳號沒投廣告時量是粗略區間 | Google Ads 帳號、開發者權杖、Google Cloud 的 OAuth 用戶端 | 第一次約 30 分鐘 | 不會 |
| C. 不用工具 | 沒有量，只看 Google 的「其他人也問了」 | 不用 | 0 | 不會 |

**推薦**：只有使用者已經說過手上有 Google Ads 帳號與開發者權杖時，推薦 B（官方數字、不會跳驗證碼）。其他情況不標推薦。

**跳過的話**：不能跳過；不想用工具就選 C。

可以多選。

## 方法 A／B 的做法

1. **前置檢查**：照該轉接器的「前置檢查」。
   - A：`tabs_context_mcp` 連得上 Chrome。連不上 → 說明要開 Chrome 與 claude-in-chrome 擴充，問「準備好了再試一次」或「先改用 C」。
   - B：照轉接器「要準備的東西」一項一項帶使用者做；憑證由使用者自己貼進 `~/.config/article-engine/google-ads.json`（精靈只建空的範本檔、不經手密鑰），再跑前置檢查。問帳號有沒有廣告花費，記 `has_spend`。地區與語言用第 2 段的 `site.region`、`site.language`；第 2 段還沒做時問使用者。
2. **問要不要試查**：
   1. 要，詞我來給
   2. 不用，直接存設定（`tested_with` 留空，第一篇文章的 S1 就是第一次實際使用）
3. **試查**：用使用者給的詞查。地區用 `site.region`；還沒有時用使用者的語言推測（中文繁體 → TW），並在結果裡寫明用的是哪個地區。
   - 成功：「『{詞}』每月約 {量} 次，相關詞：…」，問「看起來合理嗎？」1. 合理，存起來 2. 不對，換工具
   - 失敗：照實說錯在哪，問要換工具還是先用 C。

## 方法 C 的做法

不做任何事，直接寫檔。

## 寫檔

```yaml
adapters:
  keyword_volume:
    tools: [keyword-surfer]
    tested_with: "{詞，沒試查就留空}"
    tested_at: "{YYYY-MM-DD，沒試查就留空}"
```

`setup.parts.keyword_tool`：選了工具 → done（沒試查也算 done，狀態畫面註明「還沒試查」）；選 C → default。
