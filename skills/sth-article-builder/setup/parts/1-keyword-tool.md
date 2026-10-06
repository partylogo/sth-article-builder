# 第 1 段：Keyword 搜尋量工具

> 來源：plan-v5 §4.2 Keyword 搜尋量工具、§7.2 第 1 段。不預設任何一種工具（D6）。

## 要決定的點（最多 3 個）

1. 用哪個工具（可多選，或「無」）
2. （選了需要前置條件的工具）前置條件有沒有備好
3. 試查結果對不對

## 步驟

1. 列出**目前已有轉接器**的工具：讀 `~/article-engine/adapters/keyword-volume/` 底下的檔，每個檔開頭的能力宣告就是選單內容。用白話列：

   | 選項 | 能給什麼 | 要準備什麼 | 成本 |
   |---|---|---|---|
   | Keyword Surfer | 每個詞的月搜尋量、相關詞 | Chrome＋claude-in-chrome 擴充＋Keyword Surfer 擴充 | 免費 |
   | Google Keyword Planner | Google 官方的月搜尋量、近 12 個月趨勢、相關詞；沒投廣告時量是粗略區間 | Google Ads 帳號、開發者權杖、Google Cloud 的 OAuth 用戶端（第一次設定約 30 分鐘） | 免費 |
   | 無 | 沒有量，只看 Google 的「其他人也問了」 | 不用 | 0 |

   可以多選（例：Keyword Planner 查量＋Keyword Surfer 補相關詞）。

2. 推薦：
   - 使用者已經有 Google Ads 帳號與開發者權杖 → 推薦 Google Keyword Planner（官方數字、不會跳驗證碼）。
   - 沒有，但 Chrome 連得上（`tabs_context_mcp` 成功）→ 推薦 Keyword Surfer。
   - 都沒有 → 推薦「無」，並說之後可以改。
3. **只檢查選中工具的前置條件**：照該轉接器的「前置檢查」。不通過 → 說明要怎麼準備，問「準備好了再試一次」或「先用無」。
   - 選 Google Keyword Planner：照轉接器「要準備的東西」一項一項帶使用者做；憑證由使用者自己貼進 `~/.config/article-engine/google-ads.json`（精靈只建空的範本檔、不經手密鑰），再跑前置檢查。問帳號有沒有廣告花費，記 `has_spend`。地區與語言依第 2 段（或使用者的語言）填 `geo`、`lang`。
4. **用一個詞實際試查**：詞用站的品牌名或使用者給的一個主題詞（還沒有站點資料時，直接問「給我一個你想寫的詞」）。地區用 `site.region`；第 2 段還沒做時先用使用者的語言推測（中文繁體 → TW）。
   - 試查成功：把結果給使用者看（「『{詞}』每月約 {量} 次，相關詞：…」），確認看起來合理。
   - 試查失敗：照實說，問要換工具還是先用「無」。
5. 寫進 profile：

```yaml
adapters:
  keyword_volume:
    tools: [keyword-surfer]
    tested_with: "{詞}"
    tested_at: "{YYYY-MM-DD}"
```

`setup.parts.keyword_tool`：選了工具且試查成功 → done；選「無」→ default。
