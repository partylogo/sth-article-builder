# profile.yaml 欄位定義

每個站一份 `profile.yaml`，是站點設定檔裡唯一必要的檔案。`/sth-article-builder setup` 建立與修改它，`/sth-article-builder`、`/keyword-plan` 讀它。

- 目前 schema 版本：**1**
- 欄位沒填 → 用本文件寫的預設值。預設值是「無」的欄位，引擎走「無」的路徑並在報告標 ⚠️。
- 敏感值（密碼、token、revalidate secret）不寫進 profile，只寫「去哪裡讀」（例：`.env.local` 的某個變數）。

## 站點設定檔放哪、讀哪些資料夾

**站點設定資料夾（以下叫 `{站}`）跟網站程式碼分開。** `{站}` 只放設定與每篇的工作檔；網站程式碼、參考文件放在哪裡都可以，路徑記在 profile 裡。

| 東西 | 放哪 | 記在 |
|---|---|---|
| 站點設定資料夾 `{站}` | 預設是你跑 `/sth-article-builder setup` 的那個資料夾；`--site <名稱>` 時是 `~/content-sites/{名稱}/` | —（profile.yaml 本身就在這裡） |
| 網站程式碼（repo） | 任何路徑，可以沒有 | `site.repo_path` |
| 其他參考資料夾（團隊文件、舊寫作指南、關鍵字表…） | 任何路徑，可以多個 | `workspace.resources` |

`/sth-article-builder` 找 `{站}` 的順序：

1. `--site <名稱>` → `~/content-sites/{名稱}/profile.yaml`
2. 目前資料夾有 `profile.yaml`（而且有 `schema_version`）→ 目前資料夾
3. 目前資料夾往上找，第一個有 `profile.yaml` 或 `content-ops/profile.yaml` 的資料夾
4. 都找不到就停，提示跑 `/sth-article-builder setup`。

**所有讀寫網站程式碼的動作一律用 `site.repo_path`，不用「目前資料夾」。** 目前資料夾只用來找 `{站}`。

同一個資料夾裡的其他檔：

| 檔案 | 必要？ | 沒有時 |
|---|---|---|
| profile.yaml | 必要 | 不能跑 |
| brand-voice.md | 可選 | 用語言包的預設語氣 |
| writing-guide.md | 可選 | 只用 core-principles＋seo-rules |
| audit-rule.md | 可選 | 用 `audit.preset` 指定的查核預設（預設 generic） |
| keyword-plan/ | 可選 | S4、S6 不做 pillar 歸屬與內連，報告標 ⚠️ |
| extensions/ | 可選 | 沒有擴充檢查 |
| content-inventory.csv | 自動 | 第一次開跑時建立 |
| runs/ | 自動 | 每篇一個 `runs/{slug}/` |
| setup-issues.md | 自動 | 設定精靈處理不了的地方（缺轉接器、偵測失敗），之後回頭修精靈用 |
| setup-log.md | 自動 | 匯入文件時的分類與行數核對紀錄 |
| publish-rules.md | 發佈平台選 repo 時必要 | setup 第 7 段讀 repo 後寫的發佈規則 |

## 欄位

```yaml
schema_version: 1

# ── 站點資料（setup 第 2 段）──────────────────────────
site:
  name: ""                 # 站的內部代號，用在 --site 與報告。例：baibai
  repo_path: ""            # 網站程式碼的絕對路徑；沒有 repo（例：純 WordPress）就留空。例：~/Documents/my-site
  domain: ""               # 正式網域，撞文搜尋 site: 用這個。例：fude.studio
  canonical_base: ""       # 文章網址的固定前綴。例：https://www.fude.studio
  article_url_pattern: ""  # 文章網址樣式，{slug} 會被替換。例：/blog/{slug}
  language: zh-TW          # 對應 language/ 底下的語言包
  region: TW               # 查量的國家、看哪一國的搜尋結果
  brand:
    name: ""               # 品牌名的正確寫法。例：拜拜日曆
    variants_to_fix: []    # S8 要統一掉的錯誤寫法。例：["Acme Shop", "acmeshop"]
  audience: ""             # 讀者是誰，一兩句話
  cta:                     # 讀完要去哪
    text: ""               # 文末行動呼籲文案
    url: ""                # 連結；可含 {slug}、{keyword} 等變數
    max_inline_mentions: 1 # 內文最多自然提到產品幾次
    angle_bias: ""         # S4 選切角時偏向什麼角度，可空

# ── 其他可以讀的資料夾 ─────────────────────────────────
workspace:
  resources: []            # 每項：path（絕對路徑）、note（裡面放什麼）。精靈匯入文件、/keyword-plan 匯入時從這裡找
                           # 例：[{path: ~/Documents/team-docs, note: 品牌規範與舊的寫作指南}]

# ── 撞文範圍 ─────────────────────────────────────────
content_inventory:
  include_existing: true   # true＝把網站上的既有文章收進 content-inventory.csv；false＝不收，清單只有這套系統寫的文章（可以從空的開始）
                           # 之後想收既有文章：改成 true，下次開跑時會讀網站補進來

cannibalization:
  include_url_patterns: [] # 哪些網址算文章、要算撞文。空＝內容型態為 article 的全部
  exclude_url_patterns: [] # 例：["/tag/", "/category/"]

# ── 篇數規則（S4）────────────────────────────────────
article_count:
  enabled: false           # false＝一律 1 篇
  rules: []                # 每條：條件、結果、說明。例：主詞月量 ≥ 3,000 且長尾合計 ≥ 1,000 → 2 篇
  split_types: []          # 拆篇類型：name、意圖範例、對應寫法
  calibration_note: ""     # 規則樣本數少時，報告要回報判斷結果供校準

# ── 意圖研究（S3）────────────────────────────────────
research:
  community_sources:       # 社群痛點來源；原生 URL 一律實際導航驗證
    - threads.net
    - ptt.cc
    - dcard.tw
  community_year_range: "" # 例：2020-2026；空＝近 6 年
  community_search_hints: []  # 例：["site:dcard.tw/f", "site:ptt.cc/bbs/Folklore"]

# ── 草稿 frontmatter 對應（S6、S9）────────────────────
frontmatter:
  fields:                  # 草稿必含欄位，依序
    - title
    - slug
    - date
    - modified
    - status
    - excerpt
  draft_status_value: draft
  excerpt_is_meta_description: true
  excerpt_length: "60-80"  # 中文字
  slug_style: ascii-hyphen # ascii-hyphen：英文小寫連字號

# ── 寫作 ─────────────────────────────────────────────
writing:
  reference_recent_articles: 2   # S6 參考最近幾篇已發布文章
  internal_link_format: markdown # markdown：[錨點](/blog/slug)

# ── 互動模式 ─────────────────────────────────────────
modes:
  force_interactive_first_n: 3   # 新站前 N 篇強制互動模式
  articles_written: 0            # 由 /sth-article-builder 收尾時累加

# ── 轉接器設定 ───────────────────────────────────────
adapters:
  keyword_volume:
    tools: [none]          # 可多選：keyword-surfer、google-keyword-planner、none
    tested_with: ""        # setup 時實際試查用的詞
    tested_at: ""          # YYYY-MM-DD
    google_keyword_planner:
      credentials_file: ~/.config/article-engine/google-ads.json  # 憑證放 repo 之外
      geo: "2158"          # 台灣
      lang: "1018"         # 中文繁體
      api_version: v25
      has_spend: false     # 帳號沒有廣告花費時量是區間
  read_source:
    primary: website       # website（預設）
    extra: []              # 加分來源：wp-rest、repo
    website:
      user_agent: ""       # 空＝先一般請求；被擋時填瀏覽器 UA。例：Mozilla/5.0
      sitemap_url: ""      # 空＝自動找（robots.txt → /sitemap.xml → /sitemap_index.xml）
      feed_url: ""
      notes: []            # 讀這個站要注意的事。例：「NEVER 用 HTTP 200 判斷頁面存在」
    wp_rest:
      api_base: ""         # 例：https://cms.example.com/wp-json/wp/v2
    repo:
      content_glob: """"     # 例：src/content/blog/**/*.mdx
      field_map:           # frontmatter 欄位名稱對應；setup 第 2 段偵測
        title: title
        slug: ""           # 空＝用檔名
        published_at: ""
        draft: ""
  publish:
    platform: file-only    # file-only（預設）、wordpress、repo、browser-session-api
    repo:
      rules_file: publish-rules.md   # setup 第 7 段讀 repo 後寫的發佈規則；repo 位置用 site.repo_path
    wordpress:
      ssh_host: ""         # 例：root@203.0.113.10
      wp_path: ""          # 例：/var/www/html
      wp_cli_flags: ""     # 例：--path=/var/www/html --allow-root
      markdown_converter: ""   # 例：node_modules/marked
      categories: []       # 每項：id、name、用途
      default_categories: []   # 新文章預設分類 id
      post_status: draft
      revalidate:
        url: ""            # 例：https://www.fude.studio/api/revalidate
        secret_source: ""  # 例：某個 env 變數名稱（只記去哪裡讀，不寫值）
      notes: []
    browser_session_api:   # 在已登入的瀏覽器分頁裡呼叫後台 API；欄位見 adapters/publish/browser-session-api.md
      admin_url: ""
      api_base: ""
      auth: {}             # type、storage_key_regex、resource
      check_path: ""
      create_draft: {}     # method、path、id_field、status_field
      upload_cover: {}     # 可省略
      payload_defaults: {}
      field_map: {}
      body_field: content
      body_rules: {}
      slug_regex: ""
      required: []
      checks: []
      publish: none
    file_only:
      output_dir: runs     # 預設就是 runs/{slug}/；填其他資料夾時另外複製一份過去
  cover:
    type: none             # none（預設）、template-overlay
    template_overlay:
      script: ""           # 產圖腳本絕對路徑
      base_image: ""       # 底圖絕對路徑
      output_dir: ""
      title_template: []   # 主標樣板。例：["{主關鍵字}是誰", "{主關鍵字}怎麼拜"]
      title_max_chars: 8
      subtitle_rule: ""    # 例：該篇差異化切角一句話
      subtitle_max_chars: 22
      overflow: shorten    # 超字數：shorten（自動縮寫）
      on_exists: suffix-v2 # 檔名已存在：加 -v2，永不覆蓋
      set_featured_only_if_empty: true
      notes: []            # 腳本參數跟預設不同時記在這裡

# ── 查核 ─────────────────────────────────────────────
audit:
  preset: generic          # 對應 audit-presets/ 底下的檔名

# ── 擴充 ─────────────────────────────────────────────
extensions:                # 每項：file、hook（目前只有 s9-check）
  []

# ── keyword plan ────────────────────────────────────
keyword_plan:
  enabled: false
  dir: keyword-plan

# ── setup 進度（狀態畫面用）───────────────────────────
setup:
  route: ""                # quick／full
  parts:                   # 每段：done／default／skipped／todo
    keyword_tool: todo
    site_data: todo
    keyword_plan: todo
    brand_voice: todo
    writing_guide: todo
    audit_rule: todo
    publish: todo
    cover: todo
```

## 版本遷移

- 引擎讀到 `schema_version` 比目前舊：能自動補的欄位補預設值，事後在報告說明。
- 需要使用者決定的遷移（例：欄位意義改變）由 `/sth-article-builder` 開跑前檢查擋下，白話說明要做什麼。
- 每次改這份 schema 都要同時改 `VERSION` 並在下方記錄。

| schema_version | 引擎版本 | 內容 |
|---|---|---|
| 1 | 0.1.0 | 第一版 |
| 1 | 0.1.1 | 新增可選欄位 `adapters.publish.browser_session_api` 與平台值 `browser-session-api`；舊 profile 不用改 |
| 1 | 0.1.2 | 新增可選欄位 `content_inventory.include_existing`（沒填＝true，行為同前）；清單涵蓋狀態多「網站未上線」「只收本系統」；清單可以是空的 |
