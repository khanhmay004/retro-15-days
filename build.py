#!/usr/bin/env python3
"""Dựng site tĩnh từ content/*.json + assets/ vào public/. Chạy: python3 build.py [--out thư_mục]"""
import json, os, sys, shutil, html, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(ROOT, 'public')
SITE = json.load(open(os.path.join(ROOT, 'content', 'site.json'), encoding='utf-8'))
DAYS = [json.load(open(p, encoding='utf-8')) for p in sorted(glob.glob(os.path.join(ROOT, 'content', 'ngay-*.json')))]
DAYS.sort(key=lambda d: d['ngay'])
BY_N = {d['ngay']: d for d in DAYS}
CM = {c['so']: c for c in SITE['cot_moc']}
URL = SITE['url'].rstrip('/')

def e(s): return html.escape(str(s), quote=True)
def nn(n): return f'{n:02d}'
def day_href(n): return f'/ngay/ngay-{nn(n)}'
def cm_label(c): return f"Cột mốc {c['so']}" if c['so'] <= 4 else 'Điểm kết'
def cm_range(c): return f"Ngày {c['tu']}–{c['den']}" if c['tu'] != c['den'] else f"Ngày {c['tu']}"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500&family=JetBrains+Mono:wght@500;600&display=swap">')
THEME_JS = "<script>(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t)}catch(e){}})()</script>"

def dots(cur=None):
    out, last = [], None
    for d in DAYS:
        if last is not None and d['cot_moc'] != last: out.append('<span class="dot-gap" aria-hidden="true"></span>')
        last = d['cot_moc']
        on = ' on' if d['ngay'] == cur else ''
        cur_attr = ' aria-current="page"' if on else ''
        out.append(f'<a class="dot cm-{d["cot_moc"]}{on}" href="{day_href(d["ngay"])}" aria-label="Ngày {d["ngay"]}: {e(d["ten_ngan"])}" title="Ngày {d["ngay"]} · {e(d["ten_ngan"])}"{cur_attr}>{d["ngay"]}</a>')
    return ''.join(out)

def page(title, desc, path, body, cm=0, cur=None, extra_attr=''):
    full_title = f'{title} · {SITE["ten"]}' if title != SITE['ten'] else f'{SITE["ten"]} · {SITE["chuong_trinh"]}'
    return f'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="vi_VN">
<meta property="og:site_name" content="{e(SITE['ten'])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(URL + path)}">
<meta property="og:image" content="{e(URL)}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2747c8">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
{THEME_JS}
{FONTS}
<link rel="stylesheet" href="/assets/style.css">
</head>
<body class="cm-{cm}"{extra_attr}>
<a class="skip" href="#noi-dung">Bỏ qua thanh điều hướng</a>
<header class="bar">
  <div class="bar-in">
    <a class="brand" href="/"><span class="brand-mark" aria-hidden="true">15</span><span class="brand-t">{e(SITE['ten'])}</span></a>
    <nav class="dots" aria-label="15 ngày">{dots(cur)}</nav>
    <div class="bar-act">
      <a class="bar-link" href="/ca-khoa">Cả khoá</a>
      <button class="theme" id="theme" type="button" aria-label="Đổi giao diện sáng / tối" title="Sáng / tối"><span aria-hidden="true"></span></button>
    </div>
  </div>
</header>
<main id="noi-dung">
{body}
</main>
<footer class="foot"><div class="wrap">{e(SITE['chuong_trinh'])} · {e(SITE['ten'])}</div></footer>
<script src="/assets/app.js" defer></script>
</body>
</html>
'''

def chips(xs, cls='chip'): return ''.join(f'<span class="{cls}">{e(x)}</span>' for x in xs)

# ---------- trang chủ ----------
def home():
    tl = ''.join(f'''<li class="tl-i cm-{c['so']}">
  <span class="tl-n">{c['so'] if c['so'] <= 4 else 15}</span>
  <span class="tl-k">{cm_label(c)} · {cm_range(c).replace('Ngày ', 'D')}</span>
  <span class="tl-t">{e(c['ten'])}</span>
  <span class="tl-o">{e(c['dau_ra'])}</span>
</li>''' for c in SITE['cot_moc'])
    groups = []
    for c in SITE['cot_moc']:
        ds = [d for d in DAYS if d['cot_moc'] == c['so']]
        if c['so'] == 5:
            d = ds[0] if ds else None
            if not d: continue
            groups.append(f'''<section class="grp cm-5" aria-labelledby="g5">
  <a class="final" href="{day_href(15)}">
    <span class="pill">Ngày 15 · {e(c['ten'])}</span>
    <h2 id="g5">{e(d['ten'])}</h2>
    <p class="q">{e(d['cau_hoi'])}</p>
    <span class="more">Xem bài học, 3 track Phase 2 và Track Decision Memo →</span>
  </a>
</section>''')
            continue
        cards = ''.join(f'''<a class="card" href="{day_href(d['ngay'])}">
  <span class="card-k">Ngày {nn(d['ngay'])}</span>
  <span class="card-t">{e(d['ten_ngan'])}</span>
  <span class="card-s">{e(d['ten'])}</span>
  <span class="card-q">{e(d['cau_hoi'])}</span>
  <span class="chips">{chips(d['tu_khoa'][:4])}</span>
</a>''' for d in ds)
        groups.append(f'''<section class="grp cm-{c['so']}" aria-labelledby="g{c['so']}">
  <div class="grp-h">
    <span class="pill">{cm_label(c)} · {cm_range(c)}</span>
    <h2 id="g{c['so']}">{e(c['ten'])}</h2>
    <p>{e(c['mo_ta'])} <span class="arrow">→</span> <strong>{e(c['dau_ra'])}</strong></p>
  </div>
  <div class="cards">{cards}</div>
</section>''')
    tracks = ''.join(f'''<article class="trk">
  <span class="trk-k">{e(t['ma'])}</span>
  <h3>{e(t['ten'])}</h3>
  <p>{e(t['mo_ta'])}</p>
  <p class="trk-fit">{e(t['hop_neu'])}</p>
  <p class="trk-days"><span>Nối từ</span>{''.join(f'<a class="dchip cm-{BY_N[n]["cot_moc"]}" href="{day_href(n)}">D{n}</a>' for n in t['ngay'] if n in BY_N)}</p>
</article>''' for t in SITE['track'])
    body = f'''<section class="hero wrap">
  <p class="eyebrow">{e(SITE['chuong_trinh'])}</p>
  <h1>Retro <span class="grad">15 ngày</span></h1>
  <p class="lead">{e(SITE['khau_hieu'])}.</p>
  <p class="sub">{e(SITE['gioi_thieu'])}</p>
  <div class="cta"><a class="btn" href="{day_href(1)}">Bắt đầu từ Ngày 1 →</a><a class="btn ghost" href="/ca-khoa">Cả khoá trên một trang</a></div>
</section>
<section class="wrap" aria-label="4 cột mốc"><ol class="tl">{tl}</ol></section>
<div class="wrap">{''.join(groups)}</div>
<section class="wrap tracks" aria-labelledby="trk-h">
  <div class="grp-h"><span class="pill neutral">Sau Phase 1</span><h2 id="trk-h">3 track cho Phase 2</h2><p>Mỗi track nối tiếp những ngày bạn đã học. <a href="{day_href(15)}#track">Chi tiết và 6 kỹ năng nền ở Ngày 15 →</a></p></div>
  <div class="trk-grid">{tracks}</div>
</section>'''
    return page(SITE['ten'], f"{SITE['khau_hieu']}. {SITE['gioi_thieu']}", '/', body)

# ---------- trang ngày ----------
def track_block():
    cards = ''.join(f'''<article class="trk">
  <span class="trk-k">{e(t['ma'])}</span>
  <h3>{e(t['ten'])}</h3>
  <p>{e(t['mo_ta'])}</p>
  <p class="trk-lbl">Đi sâu</p><p class="chips">{chips(t['di_sau'])}</p>
  <p class="trk-lbl">Role tiêu biểu</p><ul class="roles">{''.join(f'<li>{e(r)}</li>' for r in t['role'])}</ul>
  <p class="trk-fit">{e(t['hop_neu'])}</p>
  <p class="trk-days"><span>Nối từ</span>{''.join(f'<a class="dchip cm-{BY_N[n]["cot_moc"]}" href="{day_href(n)}">D{n}</a>' for n in t['ngay'] if n in BY_N)}</p>
</article>''' for t in SITE['track'])
    kn = ''.join(f'<li><strong>{e(k["ten"])}</strong><span>{e(k["y"])}</span></li>' for k in SITE['ky_nang_nen'])
    td = SITE['thong_diep']
    return f'''<section class="block" id="track" aria-labelledby="track-h">
  <h2 class="block-h" id="track-h">3 track Phase 2</h2>
  <div class="trk-grid">{cards}</div>
  <p class="note">{e(SITE['track_ghi_chu'])}</p>
  <h3 class="sub-h">Mọi role đều cần 6 kỹ năng nền</h3>
  <ul class="base">{kn}</ul>
  <p class="src">{e(SITE['ky_nang_nen_nguon'])}</p>
  <div class="msg"><p class="msg-q">{e(td['cau'])}</p><ol>{''.join(f'<li>{e(b)}</li>' for b in td['buoc'])}</ol></div>
</section>'''

def day_page(i, d):
    c = CM[d['cot_moc']]
    n = d['ngay']
    toc = ''.join(f'<a href="#m{k}"><span>{k}</span>{e(m["ten"])}</a>' for k, m in enumerate(d['module'], 1))
    lessons = ''.join(f'<li>{e(x)}</li>' for x in d['bai_hoc'])
    mods = ''.join(f'''<section class="mod" id="m{k}" aria-labelledby="m{k}-h">
  <div class="mod-h"><span class="mod-n">{nn(k)}</span><h2 id="m{k}-h">{e(m['ten'])}</h2></div>
  <div class="mod-b">
    <div class="kt"><p class="lbl">Kiến thức chính</p><ul>{''.join(f'<li>{e(x)}</li>' for x in m['kien_thuc'])}</ul></div>
    <div class="kn"><p class="lbl">Kỹ năng</p><ul>{''.join(f'<li>{e(x)}</li>' for x in m['ky_nang'])}</ul></div>
  </div>
</section>''' for k, m in enumerate(d['module'], 1))
    lab = d['lab']
    lq = ''.join(f'<a class="rel cm-{BY_N[x["ngay"]]["cot_moc"]}" href="{day_href(x["ngay"])}"><strong>Ngày {x["ngay"]} · {e(BY_N[x["ngay"]]["ten_ngan"])}</strong><span>{e(x["ghi_chu"])}</span></a>' for x in d['lien_quan'] if x['ngay'] in BY_N)
    prev_d = DAYS[i - 1] if i > 0 else None
    next_d = DAYS[i + 1] if i < len(DAYS) - 1 else None
    pn = (f'<a class="pn-a prev" href="{day_href(prev_d["ngay"])}" rel="prev"><span>← Ngày {prev_d["ngay"]}</span><strong>{e(prev_d["ten_ngan"])}</strong></a>' if prev_d else '<a class="pn-a prev" href="/"><span>← Trang chủ</span><strong>Hành trình 15 ngày</strong></a>')
    pn += (f'<a class="pn-a next" href="{day_href(next_d["ngay"])}" rel="next"><span>Ngày {next_d["ngay"]} →</span><strong>{e(next_d["ten_ngan"])}</strong></a>' if next_d else '<a class="pn-a next" href="/ca-khoa"><span>Cả khoá →</span><strong>15 ngày trên một trang</strong></a>')
    body = f'''<div class="wrap day">
<header class="dh">
  <p class="pill">Ngày {nn(n)} · {cm_label(c)} · {e(c['ten'])}</p>
  <h1>{e(d['ten'])}</h1>
  <blockquote class="q">{e(d['cau_hoi'])}</blockquote>
  <p class="goal"><span class="lbl">Mục tiêu</span>{e(d['muc_tieu'])}</p>
  <p class="chips">{chips(d['tu_khoa'])}</p>
</header>
<section class="lessons" aria-labelledby="bh-h">
  <h2 id="bh-h">Bài học của ngày</h2>
  <ol>{lessons}</ol>
</section>
<nav class="toc" aria-label="Các module">{toc}</nav>
{mods}
{track_block() if n == 15 else ''}
<section class="lab" aria-labelledby="lab-h">
  <p class="lbl">{'Thời gian xây' if n in (6, 15) else 'Lab'}</p>
  <h2 id="lab-h">{e(lab['ten'])}</h2>
  <p>{e(lab['tom_tat'])}</p>
  <p class="out"><span>Đầu ra</span>{e(lab['dau_ra'])}</p>
</section>
<section class="soi" aria-labelledby="soi-h">
  <h2 class="lbl" id="soi-h">Tự soi</h2>
  <p>{e(d['tu_soi'])}</p>
</section>
{f'<section class="rels" aria-labelledby="lq-h"><h2 class="lbl" id="lq-h">Liên quan</h2><div class="rel-list">{lq}</div></section>' if lq else ''}
<nav class="pn" aria-label="Ngày trước và sau">{pn}</nav>
</div>'''
    attrs = f' data-prev="{day_href(prev_d["ngay"]) if prev_d else "/"}" data-next="{day_href(next_d["ngay"]) if next_d else "/ca-khoa"}"'
    return page(f"Ngày {n} · {d['ten']}", d['cau_hoi'], day_href(n), body, cm=d['cot_moc'], cur=n, extra_attr=attrs)

# ---------- cả khoá ----------
def all_days():
    out = []
    for c in SITE['cot_moc']:
        ds = [d for d in DAYS if d['cot_moc'] == c['so']]
        if not ds: continue
        rows = ''.join(f'''<article class="ak cm-{d['cot_moc']}">
  <a class="ak-h" href="{day_href(d['ngay'])}"><span class="ak-n">{nn(d['ngay'])}</span><span><strong>{e(d['ten'])}</strong><em>{e(d['cau_hoi'])}</em></span></a>
  <ul>{''.join(f'<li>{e(x)}</li>' for x in d['bai_hoc'])}</ul>
  <p class="ak-soi"><span>Tự soi</span>{e(d['tu_soi'])}</p>
</article>''' for d in ds)
        out.append(f'<section class="ak-g cm-{c["so"]}"><h2><span class="pill">{cm_label(c)} · {cm_range(c)}</span>{e(c["ten"])}</h2>{rows}</section>')
    body = f'''<div class="wrap all">
<header class="dh">
  <p class="pill neutral">{e(SITE['chuong_trinh'])}</p>
  <h1>Cả khoá trên một trang</h1>
  <p class="goal">Câu hỏi, bài học và câu tự soi của 15 ngày. In ra làm handout, hoặc dùng Ctrl+F để tìm nhanh.</p>
  <p class="cta"><button class="btn ghost" type="button" data-print>In trang này</button></p>
</header>
{''.join(out)}
</div>'''
    return page('Cả khoá trên một trang', 'Câu hỏi, bài học và câu tự soi của 15 ngày Phase 1 AI Thực Chiến trên một trang.', '/ca-khoa', body)

def not_found():
    body = f'''<div class="wrap nf"><p class="pill neutral">404</p><h1>Không có trang này</h1><p class="goal">Đường dẫn có thể đã gõ sai. Quay về hành trình 15 ngày nhé.</p><p class="cta"><a class="btn" href="/">Về trang chủ</a></p></div>'''
    return page('Không tìm thấy trang', SITE['gioi_thieu'], '/404', body)

def write(rel, s):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(s)

if __name__ == '__main__':
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    write('index.html', home())
    write('ca-khoa.html', all_days())
    write('404.html', not_found())
    for i, d in enumerate(DAYS): write(f'ngay/ngay-{nn(d["ngay"])}.html', day_page(i, d))
    print(f'đã dựng {3 + len(DAYS)} trang vào {os.path.relpath(OUT, ROOT) if OUT.startswith(ROOT) else OUT} · {len(DAYS)} ngày')
