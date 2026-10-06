#!/usr/bin/env python3
"""Google Keyword Planner（Google Ads API REST）查量。只用標準函式庫。

用法：
  gkp.py metrics <詞> [<詞>…]   查每個詞的月搜尋量（GenerateKeywordHistoricalMetrics）
  gkp.py ideas <詞> [<詞>…]     由種子詞拿相關詞與量（GenerateKeywordIdeas）
  gkp.py check                  只換 access token 並列出可用的帳號，用來做前置檢查

參數：
  --creds 路徑   憑證檔（預設 ~/.config/article-engine/google-ads.json）
  --geo ID       地區（geo target constant，預設 2158＝台灣）
  --lang ID      語言（language constant，預設 1018＝中文繁體）
  --api 版本     API 版本（預設 v25）
  --limit N      ideas 最多回幾個（預設 50）

憑證檔格式（JSON，放在 repo 之外，不要 commit）：
  {"developer_token": "...", "client_id": "...", "client_secret": "...",
   "refresh_token": "...", "customer_id": "1234567890", "login_customer_id": "（用管理員帳號才填）"}

輸出：每行一個 JSON：{"keyword", "volume", "monthly": [[年, 月, 量], …], "competition"}
"""
import argparse, json, os, sys, urllib.request, urllib.parse, urllib.error

def die(msg, code=2):
    print(json.dumps({"error": msg}, ensure_ascii=False)); sys.exit(code)

def load_creds(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        die(f"找不到憑證檔 {path}")
    c = json.load(open(path))
    for k in ("developer_token", "client_id", "client_secret", "refresh_token", "customer_id"):
        if not c.get(k):
            die(f"憑證檔缺 {k}")
    c["customer_id"] = c["customer_id"].replace("-", "")
    if c.get("login_customer_id"):
        c["login_customer_id"] = c["login_customer_id"].replace("-", "")
    return c

def access_token(c):
    data = urllib.parse.urlencode({"grant_type": "refresh_token", "client_id": c["client_id"],
        "client_secret": c["client_secret"], "refresh_token": c["refresh_token"]}).encode()
    try:
        r = urllib.request.urlopen("https://www.googleapis.com/oauth2/v3/token", data, timeout=30)
    except urllib.error.HTTPError as e:
        die(f"換 access token 失敗：{e.code} {e.read().decode()[:300]}")
    return json.load(r)["access_token"]

def call(c, tok, api, method, url_suffix, body=None):
    url = f"https://googleads.googleapis.com/{api}/{url_suffix}"
    h = {"Authorization": f"Bearer {tok}", "developer-token": c["developer_token"], "Content-Type": "application/json"}
    if c.get("login_customer_id"):
        h["login-customer-id"] = c["login_customer_id"]
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers=h, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        die(f"API 錯誤 {e.code}：{e.read().decode()[:500]}")

def row(text, m):
    m = m or {}
    monthly = [[v.get("year"), v.get("month"), int(v.get("monthlySearches", 0))] for v in m.get("monthlySearchVolumes", [])]
    vol = m.get("avgMonthlySearches")
    return {"keyword": text, "volume": int(vol) if vol is not None else None,
            "monthly": monthly, "competition": m.get("competition")}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["metrics", "ideas", "check"])
    ap.add_argument("keywords", nargs="*")
    ap.add_argument("--creds", default="~/.config/article-engine/google-ads.json")
    ap.add_argument("--geo", default="2158")
    ap.add_argument("--lang", default="1018")
    ap.add_argument("--api", default="v25")
    ap.add_argument("--limit", type=int, default=50)
    a = ap.parse_args()
    c = load_creds(a.creds)
    tok = access_token(c)
    if a.cmd == "check":
        r = call(c, tok, a.api, "GET", "customers:listAccessibleCustomers")
        print(json.dumps({"ok": True, "accessible": r.get("resourceNames", [])}, ensure_ascii=False)); return
    if not a.keywords:
        die("至少給一個詞")
    common = {"geoTargetConstants": [f"geoTargetConstants/{a.geo}"], "language": f"languageConstants/{a.lang}",
              "keywordPlanNetwork": "GOOGLE_SEARCH"}
    cid = c["customer_id"]
    if a.cmd == "metrics":
        r = call(c, tok, a.api, "POST", f"customers/{cid}:generateKeywordHistoricalMetrics", dict(common, keywords=a.keywords))
        for res in r.get("results", []):
            out = row(res.get("text"), res.get("keywordMetrics"))
            out["close_variants"] = res.get("closeVariants", [])
            print(json.dumps(out, ensure_ascii=False))
    else:
        body = dict(common, includeAdultKeywords=False, keywordSeed={"keywords": a.keywords}, pageSize=a.limit)
        r = call(c, tok, a.api, "POST", f"customers/{cid}:generateKeywordIdeas", body)
        for res in r.get("results", [])[: a.limit]:
            print(json.dumps(row(res.get("text"), res.get("keywordIdeaMetrics")), ensure_ascii=False))

if __name__ == "__main__":
    main()
