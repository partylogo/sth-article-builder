# Gate 協定

> 來源：拜拜日曆 auto-article §0 鐵則 1 的覆寫表、§3 決策規則表 #3、#5、#9–#11；draft-article Step 3；make-banner Mode B 與共用步驟；last-mile-review §1、§8；deity-content-pipeline Step 3。

所有「停下來確認」的點列在這裡。模式記在 state.json 的 `mode`。

- **auto 模式**：只有 S2 撞文會停，其他 gate 照「auto 處置」欄自動決定，**決定與理由寫進 state.json 的 `decisions`**，最終報告的「我替你做的決定」照列。
- **互動模式**：每個 gate 都停，照「互動怎麼問」欄問。問法一律白話選擇題，第一個選項是推薦值並寫理由。
- 被呼叫的 skill 或 stage 文件裡寫的「停下來確認」，一律照本表處置，不照它們自己的寫法。

| id | 原出處 | 在哪一步 | 互動怎麼問 | auto 處置 |
|---|---|---|---|---|
| `cannibalization` | auto-article S2、draft-article Step 1 | S2 | 列出撞到的頁（網址、標題、為什麼判定意圖相同），給 2–3 個選項：改寫舊文、換角度另寫、改成其他內容型態，附預設建議與理由 | **同樣停下來問**（auto 唯一保留的 gate）。意圖不同時不停，記錄 title/H1 要怎麼拉開角度 |
| `plan` | deity-content-pipeline Step 3 | S4 | 呈現篇數、每篇主／次關鍵字、分群理由，問要不要照這樣寫 | S4 查表（research.md 決策規則表），不問 |
| `outline` | draft-article Step 3；auto-article §3 #3 | S5 | 呈現大綱（H1、H2/H3、每段摘要、FAQ、內鏈目標）與切角理由，確認後才寫全文 | 自動通過，但必須把大綱**與切角理由**寫進 intent-report，最終報告要呈現 |
| `review-apply` | last-mile-review §8 | S8 | 照 last-mile-review §8 讓使用者選要套用哪些 | 全部自動套用，照 review.md 處置階梯 |
| `version-diff` | last-mile-review §1；auto-article §3 #5 | S8 | 不問（last-mile-review 已預設線上版） | **一律以線上版為準**，不問 |
| `cover-pick` | make-banner Mode B | S11 | 提 3 案主標／副標（角度要有差異：解釋型／帶問題勾子／條列承諾），用 AskUserQuestion 讓使用者選 | 照 profile 的主標樣板與副標規則生成一組，不提案不詢問 |
| `cover-overflow` | make-banner 字數檢查；auto-article §3 #9 | S11 | 警告「可能會壓到圖上的元素，是否仍要繼續？」，使用者堅持才繼續 | 自動縮寫至上限內，不問 |
| `cover-exists` | make-banner 執行產圖 3；auto-article §3 #10 | S11 | 問「覆蓋」「加 -v2 後綴」「取消」 | 一律加 `-v2` 後綴，**永不覆蓋** |
| `cover-featured` | make-banner 產圖後 3；auto-article §3 #11 | S11 | 文章目前沒有封面時問「要不要設為封面？」 | 原本沒封面才自動設；已有封面**不覆蓋**，記進報告 |
| `rewrite` | auto-article §1（processed-deities 已處理就停） | 開跑前 | 告知已寫過並停 | 同左。兩種模式都停；使用者明確指示「強制重寫」才繼續 |
| `schema-migrate` | plan-v5 §4.4 | 開跑前 | 白話說明要做的遷移與影響 | 同左。需要使用者決定時兩種模式都停；能自動遷移的不停 |

## 撞文停下時的回覆格式

```
「{主關鍵字}」站上已經有寫過：
- {網址}｜{標題}｜判斷：意圖相同，因為 {一句話}

建議：{改寫舊文／換角度另寫／改成其他內容型態}，理由：{一句話}
1. 改寫舊文（推薦）…
2. 換角度另寫：…
3. 改成其他內容型態：…
```

多關鍵字模式：**所有關鍵字的 S1/S2 都跑完，若有命中一次問完**，不要一個一個問。
