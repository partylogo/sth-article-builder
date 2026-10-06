---
name: sth-article-builder
description: 通用文章產線。`/sth-article-builder setup` 建立或修改站點設定（設定精靈）。輸入主關鍵字（可多個），照站點設定檔跑完關鍵字研究、撞文檢查、意圖研究、規劃、大綱、撰稿、出處稽核、last-mile 審稿、機器檢查、上草稿或產出檔案、封面、收尾。任何網站都能用，站的規矩放在站點設定檔（content-ops/profile.yaml）。`/sth-article-builder cover <文章>` 單獨補封面。只能手動觸發。
disable-model-invocation: true
argument-hint: "主關鍵字（多個以空白分隔）[--interactive] [--site 名稱] [強制重寫] ｜ setup [狀態｜段落名稱] ｜ cover <文章>"
---

# /sth-article-builder：主關鍵字進，草稿出

輸入：$ARGUMENTS

> 來源：拜拜日曆 `.claude/skills/auto-article/SKILL.md`（§0、§1、§2 總覽）通用化，加上 plan-v5 §8.1、§8.1b 的開跑前檢查與產出後提醒。
> 這個 skill 只管順序、關卡與續跑。每一步的做法在 `stages/`，站的規矩在站點設定檔，平台與工具的差異在 `~/article-engine/adapters/`。

---

## § 0　鐵則（讀完整份 skill 前先記住這三條）

### 鐵則 1：auto 模式下，除了 S2，**任何情況都不准停下來問使用者**

本 skill 在 auto 模式**覆寫**所有被呼叫的 skill 與 stage 文件內「停下來確認」「等待確認」「用 AskUserQuestion 詢問」的指示。每個被覆寫的 gate 在 auto 模式怎麼處置、在互動模式怎麼問，列在 [gate-protocol.md](gate-protocol.md)。

**auto 模式唯一保留的 gate 是 S2 撞文（cannibalization）。**

互動模式（見 §1）則是每個 gate 都停。開跑前檢查（§2）擋下的兩種情況不算 gate，兩種模式都會停。

### 鐵則 2：「自動決定」不等於「自己編一個答案」

每個被拿掉的 gate，都必須有**明文規則**或**處置階梯**接手。
遇到規則沒涵蓋、階梯也走不到底的情況：**選最保守的落點（降語氣或刪除），並記進報告**。
NEVER 為了讓流程跑完而捏造出處、日期、地址或引文。

### 鐵則 3：拿掉人的檢查，就要補上機器的檢查

S9 的機器閘門是硬性的。**AI 自我宣稱「我檢查過了」不算通過。**
（例：拜拜日曆飛天大聖那篇有一條錯誤通過了出處稽核仍是錯的，把維基的句子加引號歸給廟方官網。）
還沒有機器檢查的論斷類型，S9 轉成白話人工檢查清單，使用者打勾才算通過；AI 不能自己宣告通過（見 [stages/checks.md](stages/checks.md)）。

---

## § 1　找站點設定、輸入解析與模式判定

### 1.1 找站點設定檔

依序找，找到第一個就用：

1. `$ARGUMENTS` 有 `--site <名稱>` → `~/content-sites/{名稱}/profile.yaml`
2. 目前資料夾有 `profile.yaml`（而且有 `schema_version`）→ 目前資料夾
3. 目前資料夾往上找，第一個有 `profile.yaml` 或 `content-ops/profile.yaml` 的資料夾
4. 都找不到 → 停，說「這個專案還沒有站點設定，先跑 `/sth-article-builder setup`」。（子指令是 `setup` 時不停，交給 setup.md 建資料夾。）

讀進 `profile.yaml`，欄位定義見 `~/article-engine/profile-schema.md`。以下把站點設定檔所在資料夾叫做 `{站}`。同時讀 `~/article-engine/VERSION`。

**站點設定資料夾跟網站程式碼是分開的。** 網站程式碼在 `site.repo_path`，其他參考資料夾在 `workspace.resources`。所有讀寫網站程式碼的動作一律用 `site.repo_path`，不要把目前資料夾當成網站 repo。

可選檔有就讀，沒有就用內建預設，**並把「這次用了哪些預設」記進 state.json 的 `defaults_used`**：

| 檔 | 沒有時 |
|---|---|
| `{站}/brand-voice.md` | `~/article-engine/language/{language}.md` 的預設語氣 |
| `{站}/writing-guide.md` | 只用 [writing/core-principles.md](writing/core-principles.md)＋[writing/seo-rules.md](writing/seo-rules.md) |
| `{站}/audit-rule.md` | `~/article-engine/audit-presets/{audit.preset}.md`（預設 generic） |
| `{站}/keyword-plan/` | S4、S6 不做 pillar 歸屬與內連，報告標 ⚠️ |
| `{站}/extensions/` | 沒有擴充檢查 |

### 1.2 輸入解析

切分 `$ARGUMENTS`（空白分隔），拿掉 `--interactive`、`--site <名稱>`、`強制重寫` 這幾個旗標後，剩下的是主關鍵字：

| 關鍵字數 | 模式 |
|---|---|
| — | 第一個字是 `setup` → 讀 [setup/setup.md](setup/setup.md) 照做，後面的字是它的參數，不跑文章流程 |
| — | 第一個字是 `cover` → 走 §4 補封面 |
| 0 個 | 問使用者要寫哪個主關鍵字 |
| 1 個 | **單篇模式**：全程主線序列，S1 → S12 |
| 2 個以上 | **多關鍵字模式**：S1/S2 主線做完 → fan-out 跑 S3-S12 → 主線收攏（見 [multi-keyword.md](multi-keyword.md)） |

### 1.3 auto 或互動

| 模式 | 什麼時候 | 行為 |
|---|---|---|
| 互動 | `profile.modes.articles_written` < `profile.modes.force_interactive_first_n`（新站前 3 篇強制）；或使用者加 `--interactive` | 每個 gate 都停：規劃、大綱、審稿套用、封面三案（見 gate-protocol.md） |
| auto | 其他情況（預設） | 照鐵則 1：只有 S2 撞文命中且意圖相同時停 |

模式寫進 state.json 的 `mode`。

**互動模式的輸入要求**（來源：draft-article 輸入段）：若使用者未同時提供「主關鍵字」和「次要關鍵字」，S4 規劃完要停下來把主／次關鍵字給使用者確認，不可自行假設就往下寫。auto 模式由 S4 依規則決定次要關鍵字。

---

## § 2　開跑前檢查

只擋**真正跑不下去**的事，其他一律不說（提醒放 §5，產出結束後才列）。

### 2.1 擋下的情況（兩種模式都停）

| 擋下的情況 | 行為 |
|---|---|
| 站點設定檔版本落後，而且遷移需要使用者決定 | 停，白話說明要做什麼、選了會怎樣 |
| **這個主關鍵字已經寫過** | **告知使用者並停下**（重複處理沒有意義）。使用者在指令裡加 `強制重寫`、或回覆明確說強制重寫才繼續，產出照「永遠建新檔」存成新版本（slug 加 `-v2`、`-v3`） |

「已經寫過」的判定（任一成立就算；來源：auto-article §1 讀 processed-deities.md 的通用版）：

1. `{站}/runs/` 裡有同一主關鍵字、`stage` 已到 S12 的 state.json
2. `{站}/keyword-plan/` 的子頁表（格式見 `~/.claude/skills/keyword-plan/format.md`），這個主關鍵字（含變體，查 keywords.csv 的 `subpage`）的狀態是「草稿」「已上線」或已有網址
3. `{站}/content-inventory.csv` 有一列「是不是這套系統寫的」填了 slug，且「推測主關鍵字」等於這個主關鍵字

網站上早就存在的舊文章（content-inventory 裡填「基準」的）不在這裡擋，交給 S2 撞文檢查判斷意圖。

### 2.2 固定動作（不停、不提醒）

1. **自動版本遷移**：`schema_version` 比 profile-schema.md 舊、而且能自動補 → 補預設值，記進報告。
2. **更新現有內容清單**：先看 `profile.content_inventory.include_existing`（沒填＝true）。
   - **清單檔不存在** → 先建一個只有表頭的空檔（格式見 `~/article-engine/adapters/read-source/website.md`）。清單是空的是正常狀態，後面每一步都要照「清單是空的」的規則跑，不算錯誤。
   - **true（收網站上的既有文章）**：照 `~/article-engine/adapters/read-source/{profile.adapters.read_source.primary}.md` 讀網站，再照 `extra` 列的每個加分來源（例：wp-rest、repo）的「列出」合併，把新增與改過的頁寫進 `{站}/content-inventory.csv`，記下涵蓋狀態。`site.domain` 是空的（網站還沒上線）→ 不讀，涵蓋狀態記「網站未上線」。讀取失敗不擋，涵蓋狀態記「失敗」。
   - **false（只收這套系統寫的文章）**：**不讀網站、不加既有文章**。清單裡只有這套系統寫的文章（S12 加進來的），涵蓋狀態記「只收本系統」。
3. **回填**：
   - include_existing 為 true：用網址裡的 slug 與標題，把 `{站}/runs/` 的稿子對到清單裡的文章，填「是不是這套系統寫的」。
   - include_existing 為 false：只處理清單裡網址還空著的列，照 `site.canonical_base` + `article_url_pattern` 用 slug 組出網址，打開確認是正常文章（有 H1、有正文、不是 404 樣板；NEVER 用 HTTP 200 判斷）才填網址。
   - 有 keyword plan 時，兩種都回填子頁狀態與網址。
4. **確認搜尋量工具可用**：照 `~/article-engine/adapters/keyword-volume/{tool}.md` 的「前置檢查」。連不上時照 `none` 的路徑跑並記 ⚠️，**不擋稿**。

---

## § 3　流程 S1 → S12

每一步開始前讀對應的 stage 文件，照做。每個 stage 完成就寫 `{站}/runs/{slug}/state.json`（欄位見 [state-and-report.md](state-and-report.md)）。中斷後再跑同一個主關鍵字，從 state.json 的 `stage` 接著做。

| 段 | 步驟 | 做法 |
|---|---|---|
| 研究 | S1 關鍵字研究 | [stages/research.md](stages/research.md) S1：呼叫搜尋量工具轉接器 |
| | S2 撞文檢查　★auto 唯一 gate | research.md S2：每篇都搜 `site:{domain}`，加上比對 content-inventory |
| | S3 意圖研究 | research.md S3：照 [writing/intent-report-guide.md](writing/intent-report-guide.md) |
| | S4 規劃（查表，不問） | research.md S4：篇數與主／次關鍵字 |
| 寫作 | S5 大綱 | [stages/drafting.md](stages/drafting.md) S5 |
| | S6 撰稿 | drafting.md S6：讀 brand voice、writing guide、core-principles、seo-rules、keyword-layout |
| | S7 出處稽核 | drafting.md S7：只稽核 audit rule 列的高風險段落，論斷分型 |
| 審稿 | S8 last-mile-review | [stages/review.md](stages/review.md)：呼叫 `/last-mile-review`，auto 全部自動套用 |
| 檢查 | S9 機器閘門（硬性） | [stages/checks.md](stages/checks.md)＋站的 extensions。**不通過就不上稿。** |
| 上線 | S10 上草稿或產出檔案 | [stages/publishing.md](stages/publishing.md) S10：呼叫發佈平台轉接器 |
| | S11 封面 | publishing.md S11：呼叫封面轉接器 |
| | S12 收尾 | publishing.md S12：更新 keyword plan、content-inventory、`articles_written`，產出最終報告 |

---

## § 4　子指令：`/sth-article-builder cover <文章>`

單獨補封面（原 make-banner 的入口）。

1. 找站點設定（§1.1），讀 `profile.adapters.cover.type`。
2. `none` → 告知「這個站沒有設定封面」並結束。
3. 其他 → 照 `~/article-engine/adapters/cover/{type}.md` 的「單獨使用」段落跑（含 Mode A：`主標 | 副標`、Mode B：文章名稱提 3 案）。單獨使用時是互動模式，3 案要給使用者選。
4. 產圖後照發佈平台轉接器的「設封面」動作；平台不支援就只交付圖檔。

---

## § 5　產出結束後的提醒

每篇產出結束，最終報告最後列「提醒」，每則附要打的指令，**不停下來**：

- 未完成或正在用預設的設定段落（例：「brand voice 用預設語氣 → `/sth-article-builder setup brand voice`」）
- 產出後還沒對到網址的稿子（「N 篇產出後還沒對到網址，請貼網址」）
- 內容清單的涵蓋狀態是「未確認」或「失敗」（「已確認完整」「只收本系統」「網站未上線」都不提醒）
- 查量工具連不上（這次照「無」的路徑跑）

開跑前**不判斷查核缺口**。這篇有哪些論斷要寫完才知道；S7 分型後，缺機器檢查的論斷一律轉人工檢查清單。

---

## § 6　檔案地圖

| 檔 | 內容 |
|---|---|
| [gate-protocol.md](gate-protocol.md) | 所有 gate：互動怎麼問、auto 怎麼處置 |
| [multi-keyword.md](multi-keyword.md) | 多關鍵字並行與硬性約束 |
| [state-and-report.md](state-and-report.md) | state.json 欄位、最終報告格式 |
| [stages/](stages/) | research、drafting、review、checks、publishing |
| [writing/](writing/) | core-principles、seo-rules、keyword-layout、intent-report-guide |
| [setup/](setup/) | `/sth-article-builder setup` 設定精靈：setup.md 與 8 段的 parts/ |
| `~/article-engine/` | profile-schema、轉接器、語言包、查核預設、白話對照表 |
| `{站}/` | profile.yaml 與可選設定、content-inventory.csv、runs/ |
