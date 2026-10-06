# 發佈平台：WordPress（WP-CLI over SSH）

> 來源：拜拜日曆 `docs/guideline/wordpress-publish.md`（全文）；「設封面」動作另合併 make-banner「產圖後：檢查 WordPress 封面圖」。
> 連線資訊、分類、revalidate 改從 `profile.adapters.publish.wordpress` 讀。原文的拜拜日曆數值保留成「例」。
> 下文指令裡的 `{ssh_host}`、`{wp_path}`、`{wp_flags}` 分別是 profile 的 `ssh_host`、`wp_path`、`wp_cli_flags`（例：`root@203.0.113.10`、`/var/www/html`、`--path=/var/www/html --allow-root`）。

這份文件是給 AI agent 看的操作手冊，說明如何把一篇新文章發佈到站的 WordPress 後端。

## 能力宣告

| 動作 | 支援 | 對應段落 |
|---|---|---|
| 建草稿 | 有 | 「發佈一篇新文章的完整流程」，`--post_status` 用 profile 的 `post_status`（預設 draft） |
| 精準修改 | 有 | 「常用 WP-CLI 指令」的更新文章內容；last-mile-review 的專案檔另有規定時照專案檔 |
| 傳圖、設封面 | 有 | 「設定文章封面圖」 |
| 回傳 | `{ref: post ID, url: 前端網址, status}` | url 用 `profile.site.canonical_base` + `article_url_pattern` 組 |

## 前置檢查

`ssh {ssh_host} "wp core version {wp_flags}"` 拿得到版本號。拿不到 → S10 跳過、草稿留在 runs/，報告寫原因（不算 abort）。

## 整體架構（先搞懂這件事）

例：拜拜日曆是 **Headless WordPress** 架構（其他站可能是一般 WordPress，前端就是 WP 本身，沒有 revalidate 這一步）：

```
寫文章                      讀文章
──────                      ──────
WordPress (cms.example.com)  →  WordPress REST API  →  Next.js 前端 (fude.studio)
    ↑                                                        ↑
    用 WP-CLI 透過 SSH 操作                              用 src/lib/wordpress.js 讀取
```

簡單說：
- **WordPress** 只負責「存文章」，它是一個純後端 CMS
- **Next.js** 負責「顯示文章」，它會透過 REST API 去 WordPress 拿資料
- 兩者之間靠 API 溝通，WordPress 不負責前端頁面渲染

## 連線資訊

| 項目 | 值 | 來源 |
|---|---|---|
| 項目 | profile 欄位 | 例：拜拜日曆 |
|---|---|---|
| WordPress 站台 | `read_source.wp_rest.api_base` | `https://cms.example.com`（例：專案 env 檔裡的 WordPress API 網址變數） |
| SSH 登入 | `publish.wordpress.ssh_host` | `{ssh_host}`（例：專案 env 檔裡的主機 IP 變數；用本機 SSH key，不需密碼） |
| WordPress 安裝路徑 | `publish.wordpress.wp_path` | `/var/www/html`（在 VPS 上） |
| WP-CLI 旗標 | `publish.wordpress.wp_cli_flags` | `{wp_flags}`（SSH 是用 root 登入的，所以要 `--allow-root`） |

所有 WP-CLI 指令都要加 `{wp_flags}`。

## 發佈一篇新文章的完整流程

### 第一步：準備 Markdown 文章

文章用 markdown 寫，sth-article-builder 的草稿在 `{站}/runs/{slug}/draft.md`（先去掉 frontmatter，title、slug、excerpt 從 frontmatter 讀）。格式範例：

```markdown
# 文章標題

<!-- SEO Meta -->
<!-- Title: 給搜尋引擎看的標題（60 字元內） -->
<!-- Meta Description: 搜尋結果的摘要（160 字元內） -->
<!-- URL: /blog/your-slug-here -->

文章內文開始...

## 第一個段落標題

...

## 常見問題

### Q：問題一？

答案一。

### Q：問題二？

答案二。
```

**重要的格式約定**（會影響 Google Schema 自動偵測）：

- **FAQ 區塊**：用 `### Q：問題文字` 作為 h3 標題，後面接答案段落（例：拜拜日曆的前端會自動產生 `FAQPage` schema）。**繼續這樣寫**，理由見 sth-article-builder `writing/seo-rules.md` FAQ 格式（AI 引用與讀者查找，不再是 rich result）
- **HowTo 區塊**：不要用 `### 步驟一：步驟名稱` 作為 h3 標題（例：拜拜日曆的前端會據此產生 `HowTo` schema）。Google 在 2023 年 9 月已移除 HowTo 複合式結果，步驟改用數字編號加粗體小標題
- H1 標題不會進入 WordPress 內文（WordPress 用 title 欄位）
- HTML 註解（`<!-- -->`）會在轉換時自動移除

### 第二步：把 Markdown 轉成 HTML

用 `marked` 套件轉換（profile 的 `markdown_converter`，例：拜拜日曆 repo 的 `node_modules/marked`；沒有時先 `npx -y marked`）。在本機執行：

```javascript
const { marked } = require('./node_modules/marked');
const fs = require('fs');

let md = fs.readFileSync('你的文章.md', 'utf-8');
md = md.replace(/<!--[\s\S]*?-->/g, '');   // 移除 HTML 註解
md = md.replace(/^#\s+.*\n+/, '');          // 移除 H1
md = md.replace(/^---$/gm, '');             // 移除分隔線

const html = marked.parse(md.trim());
fs.writeFileSync('/tmp/article.html', html);
```

或者直接用 bash one-liner：

```bash
node -e "
const { marked } = require('./node_modules/marked');
const fs = require('fs');
let md = fs.readFileSync('{站}/runs/{slug}/draft.md', 'utf-8');
md = md.replace(/^---[\s\S]*?---\n/, '');   // 移除 frontmatter
md = md.replace(/<!--[\s\S]*?-->/g, '').replace(/^#\s+.*\n+/, '').replace(/^---$/gm, '');
fs.writeFileSync('/tmp/article.html', marked.parse(md.trim()));
"
```

### 第三步：上傳 HTML 到 VPS

```bash
scp /tmp/article.html {ssh_host}:/tmp/article.html
```

### 第四步：用 WP-CLI 建立文章

```bash
ssh {ssh_host} 'wp post create /tmp/article.html \
  --post_type=post \
  --post_title="你的文章標題" \
  --post_name="your-slug-here" \
  --post_excerpt="文章摘要，會顯示在列表頁" \
  --post_status={post_status} \
  --post_category={categories} \
  {wp_flags} \
  --porcelain'
```

`{post_status}` 用 profile 的 `post_status`（sth-article-builder 一律 draft）；`{categories}` 用 profile 的 `default_categories`，或依分類用途挑（分類表在 profile 的 `categories`）。回傳的數字就是 post ID，記成 ref。

參數說明：

| 參數 | 說明 |
|---|---|
| `--post_title` | 文章標題（顯示在頁面 h1 和搜尋結果） |
| `--post_name` | URL slug（英文，用連字號分隔，如 `how-to-worship-tiangong`） |
| `--post_excerpt` | 文章摘要（顯示在 blog 列表頁和 meta description） |
| `--post_status` | `publish`（直接發佈）或 `draft`（草稿） |
| `--post_category` | 分類 ID，用逗號分隔（見下方分類表） |
| `--porcelain` | 只回傳文章 ID，方便後續腳本使用 |

### 第五步：清理暫存檔

```bash
ssh {ssh_host} 'rm /tmp/article.html'
rm /tmp/article.html
```

### 第六步：清除前端快取（profile 有設 `revalidate.url` 才做）

前端有快取時，新文章不會馬上出現。呼叫 revalidate API：

```bash
curl -X POST {revalidate.url} \
  -H "x-revalidate-secret: {從 revalidate.secret_source 讀到的值}"
```

> 例：拜拜日曆的 Next.js fetch 有 1 小時快取（`revalidate: 3600`），revalidate 網址是 `https://www.fude.studio/api/revalidate`。`fude.studio` 會 307 redirect 到 `www.fude.studio`，所以要直接打 `www.fude.studio`。本機開發環境則是刪掉 `.next` 資料夾然後重啟 dev server（`rm -rf .next && npm run dev`）。
>
> sth-article-builder 只建草稿，草稿不會出現在前端，所以 S10 這一步可以跳過；設封面後、或改已發布文章時才需要打。

## 分類對照表

分類寫在 profile 的 `categories`（每項：id、name、用途）。setup 第 7 段會用下面的指令查一次寫進去。查詢最新分類：

```bash
ssh {ssh_host} 'wp term list category --fields=term_id,name,slug {wp_flags}'
```

例：拜拜日曆截至 2026-02-02 的分類：

| ID | 名稱 | 建議用途 |
|---|---|---|
| 2 | 拜拜知識 | 教人怎麼拜拜的實用指南 |
| 3 | 節慶介紹 | 特定節日相關（天公生、初五、元宵等） |
| 4 | 民俗文化 | 信仰概念類（太歲、金紙種類等） |

如果需要建立新分類：

```bash
ssh {ssh_host} 'wp term create category "新分類名稱" {wp_flags}'
```

## 常用 WP-CLI 指令

```bash
# 列出所有文章
ssh {ssh_host} 'wp post list --post_type=post --post_status=any --fields=ID,post_title,post_name,post_status {wp_flags}'

# 更新文章標題
ssh {ssh_host} 'wp post update 10 --post_title="新標題" {wp_flags}'

# 更新文章內容（從檔案）
scp /tmp/updated.html {ssh_host}:/tmp/updated.html
ssh {ssh_host} 'wp post update 10 /tmp/updated.html {wp_flags}'

# 刪除文章
ssh {ssh_host} 'wp post delete 10 --force {wp_flags}'

# 改文章狀態（草稿 ↔ 已發佈）
ssh {ssh_host} 'wp post update 10 --post_status=draft {wp_flags}'
ssh {ssh_host} 'wp post update 10 --post_status=publish {wp_flags}'

# 列出所有分類
ssh {ssh_host} 'wp term list category --fields=term_id,name {wp_flags}'
```

## 設定文章封面圖（Featured Image）

封面圖在 WordPress 是用 `_thumbnail_id` 這個 post meta 指向一個 media attachment。發文流程本身不會設封面圖，要另外處理。

**單獨補封面時（`/sth-article-builder cover`），先找對應的文章**（來源：make-banner「產圖後」第 1 步）：

- 有文章 slug（從 runs/ 的 frontmatter 或 content-inventory 拿）→ 直接用。
- 不確定 → `ssh {ssh_host} "wp post list --post_status=any --fields=ID,post_title,post_name {wp_flags}"` 比對標題；或 `wp post list --name=<slug> --post_status=any --fields=ID,post_title,post_name`。
- 找不到相符文章 → 跳過這段，只交付圖檔，並告知使用者「沒找到對應的文章」。

### 1. 查目前封面圖

```bash
ssh {ssh_host} "wp post meta get <POST_ID> _thumbnail_id {wp_flags}"
# 空白 = 沒設封面圖；有數字 = 該 attachment ID
```

### 2. 上傳圖檔並設為封面（一步完成）

```bash
# 先 scp 上去（建議用 ascii 檔名，避免中文檔名編碼問題）
scp "<本機圖檔路徑>" {ssh_host}:/tmp/<slug>-cover.jpg

# --featured_image 會在匯入後自動綁定為該文章封面，--porcelain 回傳 attachment ID
ssh {ssh_host} 'wp media import /tmp/<slug>-cover.jpg \
  --post_id=<POST_ID> --featured_image \
  --title="圖片標題" --alt="替代文字" \
  {wp_flags} --porcelain'
```

### 3. 驗證 + 清暫存 + 清快取

```bash
ssh {ssh_host} "wp post meta get <POST_ID> _thumbnail_id {wp_flags}"  # 應等於上一步的 attachment ID
ssh {ssh_host} "rm -f /tmp/<slug>-cover.jpg"
curl -X POST {revalidate.url} -H "x-revalidate-secret: {secret}"   # profile 有設 revalidate 才打
```

> 注意：已有封面圖時，`wp media import --featured_image` 會直接覆蓋舊的 `_thumbnail_id`（舊 attachment 不會被刪，只是不再當封面）。覆蓋前先用第 1 步確認。
> **`_thumbnail_id` 有值 → 不要主動覆蓋**（gate `cover-featured`）；要替換需使用者明確要求。
> `--title` 用主標，`--alt` 用「主標，副標」（來源：make-banner）。
> 下架或刪除文章前，先查有沒有 attachment 的 `post_parent` 指向它，避免封面圖跟著失效。

回報：文章、attachment ID（記成 cover.ref）、圖檔 URL。

## 站專屬的發佈細節

前端怎麼從文章 HTML 產生結構化資料、站上有沒有既有的批次發佈腳本，這類只屬於某個站的細節寫在 profile 的 `publish.wordpress.notes`。

> 例：拜拜日曆的 `scripts/publish-to-wp.mjs` 批次發佈腳本、前端 `src/app/blog/[slug]/page.js` 由 `### Q：` 自動產生 FAQPage schema，整段原文移到拜拜的站設定。

## 完整操作範例（複製貼上就能用）

例：拜拜日曆發佈一篇叫做「中元普渡拜拜指南」的文章（原文範例；sth-article-builder 的草稿路徑是 `{站}/runs/{slug}/draft.md`，狀態用 draft）：

```bash
# 1. 轉換 markdown 為 HTML
node -e "
const { marked } = require('./node_modules/marked');
const fs = require('fs');
let md = fs.readFileSync('docs/260715-zhongyuan/guide.md', 'utf-8');
md = md.replace(/<!--[\s\S]*?-->/g, '').replace(/^#\s+.*\n+/, '').replace(/^---$/gm, '');
fs.writeFileSync('/tmp/article.html', marked.parse(md.trim()));
"

# 2. 上傳到 VPS
scp /tmp/article.html {ssh_host}:/tmp/article.html

# 3. 建立並發佈文章（分類 2=拜拜知識, 3=節慶介紹）
ssh {ssh_host} 'wp post create /tmp/article.html \
  --post_type=post \
  --post_title="中元普渡怎麼拜？供品、流程、禁忌完整指南" \
  --post_name="zhongyuan-guide" \
  --post_excerpt="中元普渡拜拜完整指南，詳解供品清單、祭拜流程與禁忌。" \
  --post_status=publish \
  --post_category=2,3 \
  {wp_flags} \
  --porcelain'

# 4. 清理暫存
ssh {ssh_host} 'rm /tmp/article.html'
rm /tmp/article.html

# 5. 清前端快取（profile 有設 revalidate 才做）
```

## 常見問題排除

| 問題 | 原因 | 解法 |
|---|---|---|
| 本機前端看不到新文章 | 前端快取（例：拜拜日曆 Next.js fetch 快取 1 小時） | 例：拜拜日曆 `rm -rf .next` 然後重啟 dev server |
| SSH 連不上 | 主機 IP 變了或 SSH key 問題 | 確認 profile 的 `ssh_host`，確認 SSH key 存在 |
| WP-CLI 報「running as root」 | 忘了加 `--allow-root` | 所有 wp 指令都要加 `--allow-root` |
| 文章內容亂碼或格式跑掉 | markdown 轉 HTML 問題 | 先用 `marked` 轉完後打開 HTML 檔檢查，確認格式正確再上傳 |
| slug 已存在 | 同名文章已發佈過 | 用 `wp post list` 檢查，要更新就用 `wp post update` |
| 正式環境文章沒更新 | 前端快取（例：拜拜日曆是 Vercel） | 打 revalidate API 或等快取過期 |
