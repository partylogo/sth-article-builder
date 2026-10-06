# 第 6 段：audit rule（這種說法對不對、要不要查）

> 來源：plan-v5 §6 查核模型、§7.2 第 6 段。產出 `{站}/audit-rule.md`、`{站}/extensions/`，設定 profile 的 `audit`、`extensions`。

audit rule 決定 S7 稽核哪些段落、每種論斷怎麼處置。沒建時用 `~/article-engine/audit-presets/generic.md`。

## 要決定的點

1. 用哪種方式建（可疊加）
2. 要不要建 last-mile-review 的專案檔

## 6.1 建法（任選、可疊加）

| 建法 | 做法 |
|---|---|
| 產業預設 | 列出 `~/article-engine/audit-presets/` 底下有的預設（目前只有 generic）。選了就寫 `audit.preset` |
| 匯入既有清單 | 照 [import.md](import.md)，收「對不對、要不要查」與「可以用程式檢查」兩類 |
| 簡短問卷 | 下方 3 題 |

問卷：

| 題 | 選項（第一個是預設） |
|---|---|
| 這個站的文章，哪種段落最容易寫錯、一定要查？ | 用通用清單（定義與由來、功能與效果、規則與限制、數字日期）／自己列（例：「X 管什麼」「X 的機率」） |
| 有沒有合規要注意的（醫療、投資、法律、賭博）？ | 沒有／有：哪一種 |
| 有沒有數字或日期是可以算出來驗證的（例：機率、曆法換算）？ | 沒有／有：寫哪一種 |

- 第 1 題自己列 → 寫進 audit-rule.md 的「要稽核的段落」。
- 第 2 題有 → 寫進「合規」處置，必要時加免責區塊的文字。
- 第 3 題有 → 在 audit-rule.md 記「{哪一種}：推算型，目前沒有自動驗算，S9 轉人工檢查」，並寫進 setup-issues.md「可以做成擴充檢查：{哪一種}」。**不在這裡寫程式**。

## 6.2 audit-rule.md 格式

```markdown
# 查核規則：{站名}

> 建立方式：{產業預設 generic＋問卷／匯入 {檔}}，{日期}

## 要稽核的段落（S7.1）
- …

## 論斷分型的站專屬處置（沒寫的照 generic）
| 論斷類型 | 這個站的處置 |
|---|---|

## 來源分級的站專屬補充
（匯入的原文照抄在這裡）

## 擴充檢查
| 擴充 | 檔 | 掛在哪 |
|---|---|---|
```

匯入時有「可以用程式檢查」的段落 → 原文整段抄進 `{站}/extensions/{名稱}.md`，profile 的 `extensions` 加一項 `{file, hook: s9-check}`。擴充檔開頭要寫三種結果（放行／自動修／中止）各在什麼情況。

## 6.3 last-mile-review 專案檔

S8 呼叫 last-mile-review，它會找 `.claude/review-project.md` 或 `docs/review-project.md`。

1. 已經有（`{站}` 或 `site.repo_path` 底下的 `.claude/review-project.md`、`docs/review-project.md`）→ 摘要裡寫「last-mile-review 專案檔：{路徑}，沿用」，不改；在網站 repo 裡的，另外複製一份到 `{站}/docs/review-project.md`，讓從 `{站}` 跑時找得到。
2. 沒有 → 問「要不要建一份 last-mile-review 的專案檔？它告訴審稿怎麼抓文章、怎麼套用修改、站的專名寫法」：
   1. 建（推薦）：寫到 `{站}/docs/review-project.md`（放在站點設定資料夾，不放進網站 repo）；內容從 profile 組：怎麼取得文章（讀取來源轉接器）、怎麼套用修改（發佈平台轉接器的精準修改；repo 串接就是改 repo 裡的檔）、內鏈怎麼驗證（content-inventory）、品牌名寫法、audit-rule.md 的要稽核段落。寫之前先講清楚路徑。
   2. 不建：last-mile-review 只做通用檢查，報告會註明。

`setup.parts.audit_rule`：有 audit-rule.md → done；只選 generic → default；跳過 → skipped。
