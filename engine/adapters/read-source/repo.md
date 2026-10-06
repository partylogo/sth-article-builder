# 讀取來源（加分）：repo 原始檔

> 來源：plan-v5 §4.2「加分來源：repo 原始檔」。不綁任何框架：只認 markdown 類內容檔（md、mdx、markdown）與它們的 frontmatter。
> 這是加分來源，不取代 [website.md](website.md)。有它時，content-inventory 的涵蓋狀態可以升為「已確認完整」，抓回拿得到原生格式。

## 能力宣告

| 動作 | 支援 | 說明 |
|---|---|---|
| 列出 | 有 | `content_glob` 對到的每個內容檔 |
| 抓回 | 有 | 原生檔案內容（含 frontmatter、MDX 元件） |
| 涵蓋狀態 | 已確認完整 | 已發布的內容都在 glob 裡、而且草稿能從 frontmatter 分出來時 |

## 前置檢查（setup 第 2 段用來找 glob）

1. 在 `site.repo_path` 找內容檔（**不是目前資料夾**），排除 `node_modules`、`.git`、`dist`、`build`、`.next`、`.astro`、`content-ops`、`docs`（`docs` 底下常是規格文件，不是網站內容；使用者說是才加回來）：

   ```bash
   cd "{site.repo_path}" && find . -type f \( -name '*.md' -o -name '*.mdx' -o -name '*.markdown' \) \
     -not -path '*/node_modules/*' -not -path './.git/*' -not -path './dist/*' -not -path './build/*' \
     -not -path './.next/*' -not -path './.astro/*' -not -path './content-ops/*' -not -path './docs/*' \
     | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn
   ```

2. 檔案數最多、而且檔案有 frontmatter（開頭是 `---`）的資料夾，就是內容資料夾的候選。列給使用者確認（「這個資料夾的 {N} 個檔是網站文章嗎？」），確認後寫進 `profile.adapters.read_source.repo.content_glob`（例：`src/content/blog/**/*.mdx`）。
3. 讀 3 個檔的 frontmatter，記下欄位名稱（標題、slug、日期、草稿旗標各叫什麼），寫進 `profile.adapters.read_source.repo.field_map`：

   ```yaml
   field_map:
     title: title          # 例
     slug: ""              # 空＝用檔名
     published_at: pubDate # 例
     draft: draft          # 例：draft: true 的不算已發布
   ```

4. 用 2 個檔的 slug 組出網址（`site.canonical_base` + `site.article_url_pattern`），實際打開確認是那篇文章。對不上 → 問使用者網址怎麼組。

## 列出

1. 列出 `{site.repo_path}/{content_glob}` 的所有檔。
2. 讀 frontmatter，草稿旗標為真的跳過。
3. 每檔一列寫進 content-inventory.csv：網址用 slug 組、`title`、`h1`（frontmatter 沒有就取內文第一個 `# `，再沒有就用 title）、`content_type` 填 article、`published_at`。
4. 跟網站讀到的清單合併（以網址為鍵）。

## 抓回

直接讀檔，回傳原生內容；需要中立 md 時去掉 frontmatter、把 MDX 元件換成一行 `[元件：名稱]` 標記（不刪內容）。

repo 裡的檔可能比網站新（還沒部署）也可能比網站舊。**已上線文章的評估以線上版為準**；repo 版本只拿來補網站看不到的部分（草稿、原生格式），兩邊不一致時報告寫出來。
