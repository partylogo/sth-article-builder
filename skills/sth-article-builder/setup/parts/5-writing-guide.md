# 第 5 段：writing guide（要守什麼）


writing guide 管**要守什麼**：文章結構（FAQ、標題寫成問句、固定模板）、內容取捨、禁止事項、格式。用在 S5 大綱、S6 撰稿、S8 檢查。沒建時只用 core-principles＋seo-rules。

## 要決定的點

1. 匯入既有指南，還是填簡短問卷
2. frontmatter 欄位
3. 一個主關鍵字要不要依搜尋量拆成多篇

## 5.1 指南本身

| 建法 | 做法 |
|---|---|
| 匯入既有指南（推薦，使用者有的話） | 照 [import.md](import.md)，收「要守什麼」那類；裡面的流程或設定值同時填進 profile |
| 簡短問卷 | 下方 5 題，每題選擇題＋預設 |

問卷（偵測得到的先填預設，依據是 2.2 讀到的現有文章）：

| 題 | 選項（第一個是預設） |
|---|---|
| 文章要不要有 FAQ 段？ | 要（3–5 題，`### Q：` 格式）／不要 |
| H2 標題要不要寫成問句？ | 盡量寫成問句／不限 |
| 有沒有一定要放、或一定不能放的段落？ | 沒有／自己寫 |
| 有沒有固定模板的段落（例：操作步驟、價目表）？ | 沒有／自己貼模板 |
| 有沒有禁止事項（例：不提競品、不給投資建議）？ | 沒有／自己寫 |

答案寫成 writing-guide.md 的條列，每條一句規則＋一句為什麼。全部選預設 → 不建檔，`setup.parts.writing_guide` 記 default。

## 5.2 frontmatter 欄位

偵測：

1. 有網站程式碼（repo 加分來源）→ 用 repo.md 前置檢查讀到的 frontmatter 欄位。
2. 發佈平台是 WordPress → 預設 title／slug／date／modified／status／excerpt。
3. 都沒有 → 預設同上。

列出偵測結果請使用者確認，寫進 `frontmatter.fields`。偵測到的欄位名跟預設不同（例：`pubDate`、`description`）時照偵測到的寫，並記 `excerpt_is_meta_description` 該欄對應哪個。

## 5.3 篇數規則

問「同一個主關鍵字，搜尋量大的時候要不要拆成兩篇（例如一篇介紹、一篇教學）？」

1. 不拆，一律 1 篇（推薦，沒有歷史資料可以定門檻）
2. 拆：請使用者說門檻與拆法，寫進 `article_count.rules`、`split_types`，`calibration_note` 寫「門檻還沒用實際文章驗證過」

匯入的指南裡已經有規則時，直接用，不問。

## 寫檔

writing-guide.md 開頭寫建立方式、日期、來源。profile 寫 `frontmatter`、`article_count`、`writing.reference_recent_articles`（預設 2）。
