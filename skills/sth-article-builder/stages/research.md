# 研究：S1–S4

> 來源：拜拜日曆 auto-article S1–S4、§3 決策規則表 #1、#2；draft-article Step 1–2；deity-content-pipeline Step 2–3。
> 拜拜日曆的值（3,000／1,000 門檻、認識篇＋拜拜篇、分群類型）放在拜拜的站設定，這裡只留規則。

---

## S1　關鍵字研究

照 `~/article-engine/adapters/keyword-volume/{tool}.md`（`profile.adapters.keyword_volume.tools`，可多個）：搜主關鍵字 → 抓主詞量與相關詞 → 變體詞再查 → 記錄「其他人也問了」（PAA）。

1. **先查詞庫**：站有 keyword plan 時，先讀 `{站}/keyword-plan/keywords.csv`（格式見 `~/.claude/skills/keyword-plan/format.md`）。主詞量、俗稱量直接從詞庫拿，工具只用來查詞庫沒有的長尾變體。詞庫的查詢日期超過一季就重查主詞。新查到的詞**不寫進詞庫**（共用檔只在 S12 由主線寫），先記在 state.json。
   （例：拜拜日曆的 deity-volume-master.md 有 90 位神明的主詞量、俗稱量、相關詞前 4。）
2. **主關鍵字搜尋**：查主關鍵字的量與相關詞。
3. **延伸搜尋**：針對高相關性的變體詞再查一次（例：`岳武穆王生日`、`岳飛 拜拜`），同樣記錄。
4. 也記錄 Google 搜尋結果上的「相關問題」（People Also Ask）作為文章大綱的參考。
5. 將所有關鍵字數據整理成表格，寫進 state.json 的 `keyword_data`，每筆標量的型態（精確／區間／相對／無）與來源工具。

**依工具能力調整**（轉接器檔開頭的能力宣告）：

| 能力 | S4 怎麼用 |
|---|---|
| 精確或區間月量 | 照決策規則表 #1 決定篇數 |
| 只有相對熱度 | 篇數規則改用排名比較（同群裡誰最熱），報告標 ⚠️ |
| 只有自己的曝光（Search Console） | 詞沒出現不代表沒有搜尋量，S4 不把它當 0 |
| 無 | S4 不依量決定篇數，一律 1 篇，報告標 ⚠️ |

所有選中的工具都連不上時，照「無」的路徑跑並標 ⚠️，不擋稿。

---

## S2　撞文（cannibalization）檢查　★auto 模式唯一 gate

兩種方法都要跑，兩邊對到的頁都算：

1. **每篇都搜** `site:{profile.site.domain} <主關鍵字>`（WebSearch）。`site.domain` 是空的（網站還沒上線）→ 跳過這一項，報告寫「網站未上線，沒有搜 site:」。
2. **比對 content-inventory**：用主關鍵字（含變體）比對 `{站}/content-inventory.csv` 的標題、H1、推測主關鍵字三欄，只看「算不算撞文範圍」為是的列。清單是空的 → 這一項沒有命中，照常往下。

```
沒查到 → 繼續
查到了 → 判斷搜尋意圖
   ├─ 意圖不同 → 繼續（自動判斷，不停），並記錄 title/H1 要怎麼拉開角度
   └─ 意圖相同 → 停下來問使用者（gate-protocol.md `cannibalization`）
```

- 意圖相同時，建議更新既有文章而非另起新文（來源：draft-article Step 1）。
- 意圖不同時，告知使用者需注意 title/H1 的角度區分，寫進 state.json 的 `cannibalization.angle_note`。
- content-inventory 的涵蓋狀態是「未確認」或「失敗」→ 照常跑，報告註明「清單未確認、可能有漏」。「只收本系統」是使用者選的範圍，不註明；這時 `site:` 搜到的既有文章照樣判斷意圖（使用者只是不把舊文章收進清單，撞到時仍要知道）。

多關鍵字模式：**所有關鍵字的 S1/S2 都跑完，若有命中一次問完**，不要一個一個問。

結果寫進 state.json 的 `cannibalization`。

---

## S3　意圖研究

照 [../writing/intent-report-guide.md](../writing/intent-report-guide.md)：

1. **Google 搜尋主關鍵字和次要關鍵字**，分析前 3-5 名搜尋結果：
   - 提取重要段落
   - 分析為何這些內容排名靠前
   - 找出使用者意圖、長尾問題、真實痛點
2. 社群痛點：來源用 `profile.research.community_sources`（預設 Dcard／PTT／Threads），**原生 URL 需實際導航驗證**。
3. PAA。
4. 讀者輪廓用 `profile.site.audience`：決定哪些競品內容和問題要回答、大綱深度、哪些術語第一次出現要白話解釋。

輸出 → `{站}/runs/{slug}/intent-report.md`

---

## S4　規劃（查表，不問）

見下方決策規則表 #1、#2。決定篇數與主／次關鍵字後，記進 state.json 的 `decisions`。互動模式在這裡停（gate `plan`）。

有 keyword plan 時，同時決定這篇歸到哪個 pillar／子頁（來源：draft-article Step 1「讀取 Topic Cluster 架構，確認目標關鍵字所屬的 Pillar」）：用 keywords.csv 的 `subpage` 找（認變體）；子頁表有這個主關鍵字就用它的次要關鍵字當參考。詞不在表上 → state.json 記 `pillar: null`，S12 放進 `_unsorted.md` 並提醒 `/keyword-plan 整理未分類`。結果寫進 state.json 的 `keyword_plan`（`pillar`、`subpage`、`pillar_url`、`sibling_urls`）。

讀者「讀完要去哪」（`profile.site.cta.angle_bias`）有填時，選切角偏向接得到產品的角度。

### 決策規則表（查表，不做判斷）

| # | 決策點 | 規則 |
|---|---|---|
| 1 | 幾篇 | `profile.article_count.enabled` 為 false → 1 篇。為 true → 照 `profile.article_count.rules` 逐條比對，第一條成立的就是答案；都不成立 → 1 篇 |
| 2 | 主關鍵字 | 該群搜尋量最高者。次要關鍵字取 2-5 個 |

> 例：拜拜日曆的規則 #1：主詞月量 **≥ 3,000** 且 生日型長尾合計 **≥ 1,000** → 2 篇（認識篇＋拜拜篇，兩篇互鏈）；否則 1 篇（生日／拜拜寫成子章節）。
> 門檻由歷史案例反推（飛天大聖 480／長尾 0 → 1 篇；雷祖 2,900／生日型 0 → 1 篇；廣澤尊王 22,200／生日 3,600 → 2 篇）。
> 規則的樣本數少時（`profile.article_count.calibration_note` 有寫），跑第一篇時要在報告中回報判斷結果，供使用者校準。

### 分群（拆篇類型）

根據搜尋意圖將關鍵字分群，決定應產出幾篇文章。分群類型用 `profile.article_count.split_types`。

> 例：拜拜日曆的常見分群邏輯（來源：deity-content-pipeline Step 3）：
> - **認識型**：「XX是誰」「XX的故事」→ 介紹文
> - **拜拜型**：「XX生日」「XX怎麼拜」「XX供品」→ 拜拜指南
> - **禁忌/注意型**：「XX禁忌」「XX注意事項」→ 可併入拜拜指南或獨立
> - **時效型**：「2026 XX」→ 年度更新文

為每篇文章決定主關鍵字（搜尋量最高）和次要關鍵字（2-5 個）。

一個主關鍵字拆成 2 篇時，兩篇在同一條流程裡寫完並互鏈（多關鍵字模式時留在同一個 agent，見 multi-keyword.md）。
