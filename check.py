#!/usr/bin/env python3
"""Rà nội dung content/*.json và HTML trong public/. Chạy: python3 check.py [ngay ...]
Lỗi (✗) phải sửa hết trước khi build/deploy; cảnh báo (!) đọc lại cho chắc."""
import json, os, re, sys, glob, subprocess, tempfile, filecmp
ROOT = os.path.dirname(os.path.abspath(__file__))
SO_MODULE = {1: 5, 2: 6, 3: 6, 4: 6, 5: 4, 6: 3, 7: 5, 8: 6, 9: 6, 10: 5, 11: 6, 12: 6, 13: 6, 14: 6, 15: 3}
KHOA = ['ngay', 'ten', 'ten_ngan', 'cot_moc', 'cau_hoi', 'muc_tieu', 'tu_khoa', 'bai_hoc', 'tu_soi', 'module', 'lab', 'lien_quan']
CAM = ['Nhà → Lớp', 'Phương án thay thế', 'học viên', 'giảng viên', '●', 'quiz', 'kiwi', 'slide', 'mô phỏng:', 'thực hành:',
       'mô hình ngôn ngữ', 'nhiệt độ', 'tác tử', 'máy chủ mcp', 'bộ test vàng', 'câu lệnh', 'mã thông báo', 'phần trăm']
NHAC = ['video', 'phút', 'mô hình', 'ngữ cảnh']
HTML_CAM = ['github.com', '.md"', ".md'", 'slide']
_THEM = os.path.join(ROOT, '_nguon', 'chuoi-cam.txt')  # tên repo/kho nguồn riêng, không commit
if os.path.exists(_THEM): HTML_CAM += [l.strip().lower() for l in open(_THEM, encoding='utf-8') if l.strip()]
loi, nhac = [], []

def kiem_chuoi(ngay, cho, s, toi_da):
    if not isinstance(s, str) or not s.strip(): loi.append(f'N{ngay} {cho}: rỗng hoặc không phải chuỗi'); return
    if len(s) > toi_da: loi.append(f'N{ngay} {cho}: {len(s)} ký tự > {toi_da}')
    t = s.lower()
    for w in CAM:
        if w.lower() in t: loi.append(f'N{ngay} {cho}: có từ cấm "{w}"')
    for w in NHAC:
        if re.search(r'(?<!\w)' + re.escape(w) + r'(?!\w)', t): nhac.append(f'N{ngay} {cho}: có "{w}"')

def kiem_list(ngay, cho, xs, it, nhieu, toi_da):
    if not isinstance(xs, list) or not (it <= len(xs) <= nhieu): loi.append(f'N{ngay} {cho}: cần {it}–{nhieu} ý, đang có {len(xs) if isinstance(xs, list) else "?"}'); return
    for i, x in enumerate(xs): kiem_chuoi(ngay, f'{cho}[{i}]', x, toi_da)

def so_trong(s): return set(re.findall(r'\d+(?:[.,]\d+)?', s))

def kiem_ngay(n, site):
    p = os.path.join(ROOT, 'content', f'ngay-{n:02d}.json')
    if not os.path.exists(p): loi.append(f'N{n}: thiếu file content/ngay-{n:02d}.json'); return
    try: d = json.load(open(p, encoding='utf-8'))
    except Exception as e: loi.append(f'N{n}: JSON hỏng: {e}'); return
    for k in KHOA:
        if k not in d: loi.append(f'N{n}: thiếu khoá "{k}"')
    for k in d:
        if k not in KHOA: loi.append(f'N{n}: khoá lạ "{k}"')
    if d.get('ngay') != n: loi.append(f'N{n}: "ngay" = {d.get("ngay")}')
    cm = next((c['so'] for c in site['cot_moc'] if c['tu'] <= n <= c['den']), None)
    if d.get('cot_moc') != cm: loi.append(f'N{n}: cot_moc = {d.get("cot_moc")}, phải là {cm}')
    kiem_chuoi(n, 'ten', d.get('ten'), 80); kiem_chuoi(n, 'ten_ngan', d.get('ten_ngan'), 40)
    kiem_chuoi(n, 'cau_hoi', d.get('cau_hoi'), 260); kiem_chuoi(n, 'muc_tieu', d.get('muc_tieu'), 330)
    kiem_list(n, 'tu_khoa', d.get('tu_khoa'), 4, 8, 28)
    kiem_list(n, 'bai_hoc', d.get('bai_hoc'), 2, 4, 160)
    kiem_chuoi(n, 'tu_soi', d.get('tu_soi'), 170)
    mods = d.get('module') or []
    if len(mods) != SO_MODULE[n]: loi.append(f'N{n}: {len(mods)} module, khung có {SO_MODULE[n]}')
    hi = 4 if SO_MODULE[n] >= 6 else 5
    src = os.path.join(ROOT, '_nguon', 'khung', f'ngay-{n:02d}.md')
    src_so = so_trong(open(src, encoding='utf-8').read()) if os.path.exists(src) else None
    for i, m in enumerate(mods, 1):
        kiem_chuoi(n, f'M{i}.ten', m.get('ten'), 110)
        kiem_list(n, f'M{i}.kien_thuc', m.get('kien_thuc'), 3, hi, 240)
        kiem_list(n, f'M{i}.ky_nang', m.get('ky_nang'), 2, 3, 120)
        for j, x in enumerate(m.get('kien_thuc') or []):
            if isinstance(x, str) and len(x) > 210: nhac.append(f'N{n} M{i}.kien_thuc[{j}]: {len(x)} ký tự, nên rút dưới 210')
            if src_so is not None and isinstance(x, str):
                la = [s for s in so_trong(x) if s not in src_so and s.replace(',', '.') not in src_so and s.replace('.', ',') not in src_so]
                if la: nhac.append(f'N{n} M{i}.kien_thuc[{j}]: số {la} không thấy trong khung')
        for j, x in enumerate(m.get('ky_nang') or []):
            if isinstance(x, str) and x[:1].islower(): nhac.append(f'N{n} M{i}.ky_nang[{j}]: nên viết hoa chữ đầu (động từ)')
    lab = d.get('lab') or {}
    kiem_chuoi(n, 'lab.ten', lab.get('ten'), 90); kiem_chuoi(n, 'lab.tom_tat', lab.get('tom_tat'), 300); kiem_chuoi(n, 'lab.dau_ra', lab.get('dau_ra'), 170)
    lq = d.get('lien_quan')
    if not isinstance(lq, list) or len(lq) > 3: loi.append(f'N{n}: lien_quan cần 0–3 mục')
    else:
        for x in lq:
            if not isinstance(x, dict) or x.get('ngay') not in range(1, 16) or x.get('ngay') == n: loi.append(f'N{n}: lien_quan trỏ ngày không hợp lệ: {x}')
            else: kiem_chuoi(n, 'lien_quan.ghi_chu', x.get('ghi_chu'), 90)

def kiem_html():
    pub = os.path.join(ROOT, 'public')
    if not os.path.exists(os.path.join(ROOT, 'build.py')) or not os.path.isdir(pub): return
    tmp = tempfile.mkdtemp()
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'build.py'), '--out', tmp], capture_output=True, text=True)
    if r.returncode: loi.append(f'build.py lỗi: {r.stderr.strip()[-400:]}'); return
    for dp, _, fns in os.walk(tmp):
        for fn in fns:
            a = os.path.join(dp, fn); rel = os.path.relpath(a, tmp); b = os.path.join(pub, rel)
            if not os.path.exists(b) or not filecmp.cmp(a, b, shallow=False): loi.append(f'public/{rel} cũ hơn nội dung: chạy python3 build.py')
    for dp, _, fns in os.walk(pub):
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), pub)
            if not os.path.exists(os.path.join(tmp, rel)): loi.append(f'public/{rel} thừa (build không sinh ra)')
            if not fn.endswith(('.html', '.css', '.js', '.svg')): continue
            s = open(os.path.join(dp, fn), encoding='utf-8').read(); t = s.lower()
            for w in HTML_CAM:
                if w in t: loi.append(f'public/{rel}: có chuỗi dẫn về nguồn "{w}"')
            if not fn.endswith('.html'): continue
            for h in re.findall(r'(?:href|src)="([^"]+)"', s):
                if re.match(r'^(https?:|mailto:|#|data:)', h): continue
                path = h.split('#')[0].split('?')[0]
                if not path: continue
                base = pub if path.startswith('/') else os.path.dirname(os.path.join(pub, rel))
                tgt = os.path.normpath(os.path.join(base, path.lstrip('/')))
                if path.endswith('/') or os.path.isdir(tgt): tgt = os.path.join(tgt, 'index.html')
                if not (os.path.exists(tgt) or os.path.exists(tgt + '.html')): loi.append(f'public/{rel}: link hỏng "{h}"')

if __name__ == '__main__':
    site = json.load(open(os.path.join(ROOT, 'content', 'site.json'), encoding='utf-8'))
    days = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(range(1, 16))
    for n in days: kiem_ngay(n, site)
    if len(days) == 15: kiem_html()
    for x in nhac: print('!', x)
    for x in loi: print('✗', x)
    print(f'{len(loi)} lỗi · {len(nhac)} cảnh báo · {len(days)} ngày')
    sys.exit(1 if loi else 0)
