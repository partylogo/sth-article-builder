#!/usr/bin/env ruby
# frozen_string_literal: true

# browser-session-api 轉接器的輔助腳本。只在本機組資料、產生要在瀏覽器分頁裡執行的程式；
# 本身不連網、不碰任何憑證。說明見 ../browser-session-api.md。
#
# 用法：
#   bsapi.rb payload        <profile.yaml> <draft.md>   組送出內容、檢查、寫 publish-payload.json、印預覽
#   bsapi.rb js-check       <profile.yaml>              唯讀呼叫，確認分頁裡的登入身分有效
#   bsapi.rb js-create      <profile.yaml> <payload.json>  建草稿
#   bsapi.rb js-cover-input                             在分頁加一個隱藏的檔案欄位
#   bsapi.rb js-cover-upload <profile.yaml>             上傳暫存欄位裡的封面，回傳檔案編號

require 'yaml'
require 'json'

def die(msg)
  warn "錯誤：#{msg}"
  exit 1
end

def load_cfg(profile_path)
  profile = YAML.safe_load(File.read(profile_path)) || {}
  pub = profile.dig('adapters', 'publish') || {}
  die "profile 的 adapters.publish.platform 不是 browser-session-api" unless pub['platform'] == 'browser-session-api'
  cfg = pub['browser_session_api'] || die('profile 缺 adapters.publish.browser_session_api')
  %w[api_base check_path].each { |k| die "browser_session_api.#{k} 沒填" if cfg[k].to_s.empty? }
  die 'browser_session_api.create_draft.path 沒填' if cfg.dig('create_draft', 'path').to_s.empty?
  auth = cfg['auth'] || {}
  die "auth.type #{auth['type'].inspect} 還沒支援，只支援 logto-localstorage" unless auth['type'] == 'logto-localstorage'
  %w[storage_key_regex resource].each { |k| die "auth.#{k} 沒填" if auth[k].to_s.empty? }
  [profile, cfg]
end

def split_frontmatter(text)
  m = text.match(/\A---\s*\n(.*?)\n---\s*\n(.*)\z/m) || die('草稿開頭沒有 frontmatter（--- 包起來的欄位）')
  [YAML.safe_load(m[1]) || {}, m[2]]
end

# 跟網站算「純文字字數」的方式接近：去掉 Markdown 標記、連結只留文字、不算空白。是近似值。
def plain_len(md)
  t = md.gsub(/!\[[^\]]*\]\([^)]*\)/, '')
        .gsub(/\[([^\]]*)\]\([^)]*\)/, '\1')
        .gsub(/^\s{0,3}(#+|>|[-*+]|\d+\.)\s+/, '')
        .gsub(/[*_`|]/, '')
        .gsub(/\s+/, '')
  t.length
end

# 送出前要在網頁裡跑的「取登入資訊」程式片段。憑證只放在區域變數，不回傳。
def token_js(auth)
  <<~JS
    const __readToken = () => {
      const re = new RegExp(#{auth['storage_key_regex'].to_json});
      const res = #{auth['resource'].to_json};
      const now = Date.now() / 1000;
      for (const k of Object.keys(localStorage)) {
        if (!re.test(k)) continue;
        try {
          const m = JSON.parse(localStorage.getItem(k)) || {};
          // Logto 的鍵是「{scope}@{resource}」，scope 可能是空字串
          const key = Object.keys(m).find((x) => x === res || x.endsWith('@' + res));
          const v = key && m[key];
          if (v && v.token) return (v.expiresAt && v.expiresAt < now) ? 'EXPIRED' : v.token;
        } catch (e) {}
      }
      return null;
    };
  JS
end

def wrap(body)
  "await (async () => {\n#{body}\n})()"
end

def result_js
  <<~JS
    const __result = async (r, extra) => {
      const text = await r.text();
      let body; try { body = JSON.parse(text); } catch (e) { body = text.slice(0, 300); }
      if (!r.ok) return JSON.stringify({ ok: false, status: r.status, error: (body && body.error) || body });
      return JSON.stringify(Object.assign({ ok: true, status: r.status }, extra(body)));
    };
  JS
end

def token_guard
  <<~JS
    let token = __readToken();
    if (!token) return JSON.stringify({ ok: false, step: 'token', error: '分頁裡找不到登入資訊，請重新整理後台頁面或重新登入' });
    if (token === 'EXPIRED') return JSON.stringify({ ok: false, step: 'token', error: '登入已過期，請重新整理後台頁面' });
  JS
end

cmd = ARGV.shift
case cmd
when 'payload'
  profile_path, draft_path = ARGV
  die '用法：payload <profile.yaml> <draft.md>' unless draft_path
  profile, cfg = load_cfg(profile_path)
  fm, body = split_frontmatter(File.read(draft_path))
  payload = (cfg['payload_defaults'] || {}).dup
  (cfg['field_map'] || {}).each do |from, to|
    payload[to] = fm[from] if fm.key?(from)
  end
  if cfg.dig('body_rules', 'strip_h1')
    body = body.sub(/\A\s*#\s+[^\n]*\n+/, '')
  end
  payload[cfg['body_field'] || 'content'] = body.strip

  problems = []
  slug = payload['slug'].to_s
  if !cfg['slug_regex'].to_s.empty? && slug !~ Regexp.new(cfg['slug_regex'])
    problems << "slug「#{slug}」不符合平台規則 #{cfg['slug_regex']}"
  end
  (cfg['checks'] || []).each do |c|
    if c['max_chars']
      n = payload[c['field']].to_s.length
      problems << "#{c['field']} #{n} 字，超過 #{c['max_chars']}（#{c['why']}）" if n > c['max_chars']
    end
    if c['min_body_chars']
      n = plain_len(payload[cfg['body_field'] || 'content'].to_s)
      problems << "內文純文字約 #{n} 字，少於 #{c['min_body_chars']}（#{c['why']}）" if n < c['min_body_chars']
    end
  end
  (cfg['required'] || []).each { |f| problems << "#{f} 是空的" if payload[f].to_s.strip.empty? }

  out = File.join(File.dirname(draft_path), 'publish-payload.json')
  puts '── 要送出的內容（預覽，還沒送）──'
  payload.each do |k, v|
    next if k == (cfg['body_field'] || 'content')
    puts "#{k}: #{v.is_a?(String) ? v : v.to_json}"
  end
  b = payload[cfg['body_field'] || 'content'].to_s
  puts "#{cfg['body_field'] || 'content'}: 純文字約 #{plain_len(b)} 字，開頭：#{b[0, 200].gsub("\n", '⏎')}"
  site = profile['site'] || {}
  if site['canonical_base'] && site['article_url_pattern']
    puts "發布後網址：#{site['canonical_base']}#{site['article_url_pattern'].sub('{slug}', slug)}"
  end
  if problems.empty?
    File.write(out, JSON.pretty_generate(payload) + "\n")
    puts "檢查：通過。已寫出 #{out}"
  else
    puts '檢查：不通過，沒有寫出 payload'
    problems.each { |p| puts "- #{p}" }
    exit 2
  end

when 'js-check'
  _, cfg = load_cfg(ARGV[0] || die('用法：js-check <profile.yaml>'))
  puts wrap(<<~JS)
    #{token_js(cfg['auth'])}#{result_js}#{token_guard}
    const r = await fetch(#{(cfg['api_base'] + cfg['check_path']).to_json}, { headers: { Authorization: 'Bearer ' + token } });
    token = null;
    return __result(r, (b) => ({ items: Array.isArray(b && b.items) ? b.items.length : undefined }));
  JS

when 'js-create'
  profile_path, payload_path = ARGV
  die '用法：js-create <profile.yaml> <payload.json>' unless payload_path
  _, cfg = load_cfg(profile_path)
  payload = JSON.parse(File.read(payload_path))
  cd = cfg['create_draft']
  id_f = cd['id_field'] || 'id'
  st_f = cd['status_field'] || 'status'
  puts wrap(<<~JS)
    #{token_js(cfg['auth'])}#{result_js}#{token_guard}
    const payload = #{JSON.generate(payload)};
    const r = await fetch(#{(cfg['api_base'] + cd['path']).to_json}, {
      method: #{(cd['method'] || 'POST').to_json},
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
      body: JSON.stringify(payload),
    });
    token = null;
    return __result(r, (b) => ({ id: b[#{id_f.to_json}], post_status: b[#{st_f.to_json}], slug: b.slug }));
  JS

when 'js-cover-input'
  puts wrap(<<~JS)
    let el = document.getElementById('nap-cover-input');
    if (!el) { el = document.createElement('input'); el.type = 'file'; el.id = 'nap-cover-input'; el.style.display = 'none'; document.body.appendChild(el); }
    return 'ready: #nap-cover-input';
  JS

when 'js-cover-upload'
  _, cfg = load_cfg(ARGV[0] || die('用法：js-cover-upload <profile.yaml>'))
  up = cfg['upload_cover'] || die('profile 沒有 upload_cover，這個站不支援上傳封面')
  puts wrap(<<~JS)
    #{token_js(cfg['auth'])}#{token_guard}
    const el = document.getElementById('nap-cover-input');
    const file = el && el.files && el.files[0];
    if (!file) return JSON.stringify({ ok: false, step: 'file', error: '暫存欄位裡沒有檔案' });
    const types = #{(up['mime_types'] || []).to_json};
    if (types.length && !types.includes(file.type)) return JSON.stringify({ ok: false, step: 'file', error: '格式不支援：' + file.type });
    if (#{up['max_bytes'].to_i} > 0 && file.size > #{up['max_bytes'].to_i}) return JSON.stringify({ ok: false, step: 'file', error: '檔案太大：' + file.size });
    const api = #{cfg['api_base'].to_json};
    const auth = { Authorization: 'Bearer ' + token };
    const pre = await fetch(api + #{up['presign_path'].to_json}, {
      method: 'POST', headers: Object.assign({ 'Content-Type': 'application/json' }, auth),
      body: JSON.stringify(Object.assign(#{(up['presign_body'] || {}).to_json}, { name: file.name, content_type: file.type, file_size: file.size })),
    });
    if (!pre.ok) { token = null; return JSON.stringify({ ok: false, step: 'presign', status: pre.status, error: (await pre.text()).slice(0, 300) }); }
    const p = await pre.json();
    const put = await fetch(p.upload_url, { method: 'PUT', body: file, headers: { 'Content-Type': file.type, 'If-None-Match': '*' } });
    if (!put.ok) { token = null; return JSON.stringify({ ok: false, step: 'upload', status: put.status }); }
    const conf = await fetch(api + #{up['confirm_path'].to_json}.replace('{file_id}', p.file_id), { method: 'POST', headers: auth });
    token = null;
    el.remove();
    if (!conf.ok) return JSON.stringify({ ok: false, step: 'confirm', status: conf.status, error: (await conf.text()).slice(0, 300) });
    return JSON.stringify({ ok: true, file_id: String(p.file_id) });
  JS

else
  die '指令只有：payload、js-check、js-create、js-cover-input、js-cover-upload'
end
