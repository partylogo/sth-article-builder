# Keyword 搜尋量工具：Keyword Surfer（Chrome 擴充）


## 能力宣告

| 項目 | 值 |
|---|---|
| 量的型態 | 精確月量（Keyword Surfer 顯示的數字） |
| 相關詞 | 有（Keyword ideas 表，含 Overlap） |
| 其他人也問了（PAA） | 有（讀 Google 搜尋結果頁） |
| 地區 | 跟著 Google 搜尋參數 `gl`、`hl`；用 profile 的 `site.region`、`site.language` |
| 成本 | 免費 |
| 限制 | 連續查 80 個左右 Google 會跳 reCAPTCHA，要請使用者手動點 |

## 前置檢查

呼叫 `tabs_context_mcp` 確認 Chrome MCP 連線可用。失敗就提醒使用者開啟 Chrome + claude-in-chrome 擴充。
連不上時這次照 [none.md](none.md) 的路徑跑，報告標 ⚠️，不擋稿。

## 查一個詞

在 Chrome 中搜尋相關關鍵字並記錄搜尋量：

1. **主關鍵字搜尋**：用 Chrome navigate 到 Google 搜尋該詞（例：拜拜日曆查 `岳武穆王`）。
2. **讀取 Keyword Surfer 數據**：用 `read_page` 讀取頁面，從右側面板的 `Keyword ideas` 表格中擷取：
   - Keyword（關鍵字）
   - Volume（月搜尋量）
   - Overlap（重疊度）
3. **延伸搜尋**：針對高相關性的變體詞再搜一次（例：`岳武穆王生日`、`岳飛 拜拜`），同樣記錄 Keyword Surfer 數據。
4. 也記錄 Google SERP 上的「相關問題」（People Also Ask）作為文章大綱的參考。
5. 將所有關鍵字數據整理成表格暫存（寫進 state.json 的 `keyword_data`，`source` 填 `keyword-surfer`、`volume_type` 填 `精確`）。

**重要**：Keyword Surfer 數據在 `read_page` 的結果中會出現在底部的 table 區塊（包含 `Keyword`、`Overlap`、`Volume` 欄位）。

**更快的抓法（一個詞兩次呼叫）**：navigate 到 `https://www.google.com/search?q={詞}&hl={hl}&gl={gl}`（例：拜拜日曆是 `hl=zh-TW&gl=tw`）後，用 `javascript_tool` 跑下面這段，一次拿到搜尋框旁的主詞量與整張 ideas 表。回傳值只能是「中文 + 數字」，含 `=`、URL 或 token 會被工具擋掉。連續查 80 個左右 Google 會跳 reCAPTCHA，要請使用者手動點（auto 模式也一樣，這是工具限制，不是 gate；請使用者點完繼續）。

```js
await (async () => {
  if (location.pathname.startsWith('/sorry')) return 'CAPTCHA';
  const grab = () => {
    const form = document.querySelector('form');
    const main = form ? [...form.querySelectorAll('*')].filter(e => e.children.length === 0 && /^\d{1,3}(,\d{3})*$|^N\/A$/.test(e.textContent.trim())).map(e => e.textContent.trim()).join(',') : '';
    const tbl = [...document.querySelectorAll('table')].find(t => /Keyword/.test(t.textContent) && /Volume/.test(t.textContent));
    const rows = [];
    if (tbl) for (const tr of tbl.querySelectorAll('tr')) { const a = tr.querySelector('a'); if (!a) continue; const nums = [...tr.querySelectorAll('td')].map(x => x.textContent.trim()).filter(x => /^\d+$/.test(x)); rows.push(a.textContent.trim().replace(/\s+/g,'') + ' ' + nums.join(' ')); }
    return {main, rows, ok: !!tbl && main !== ''};
  };
  let r;
  for (let i = 0; i < 16; i++) { r = grab(); if (r.ok) break; await new Promise(res => setTimeout(res, 500)); }
  return 'MAIN ' + r.main + '\n' + (r.rows.length ? r.rows.join('\n') : 'NOTABLE');
})()
```

回傳 `CAPTCHA` → 請使用者在 Chrome 手動通過後再跑一次。回傳 `NOTABLE` → 這個詞 Keyword Surfer 沒有 ideas 表，主詞量照 `MAIN` 那行記。
