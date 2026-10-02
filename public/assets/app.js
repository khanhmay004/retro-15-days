(function () {
  var root = document.documentElement;

  // Sáng / tối: nhớ lựa chọn nếu trình duyệt cho phép
  var btn = document.getElementById('theme');
  if (btn) btn.addEventListener('click', function () {
    var dark = root.getAttribute('data-theme') === 'dark' ||
      (!root.getAttribute('data-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  // Đưa chấm ngày hiện tại vào giữa thanh trên (mobile)
  var dots = document.querySelector('.dots'), on = document.querySelector('.dot.on');
  if (dots && on && dots.scrollWidth > dots.clientWidth) {
    dots.scrollLeft = on.offsetLeft - dots.offsetLeft - dots.clientWidth / 2 + on.clientWidth / 2;
  }

  // Phím ← / → để chuyển ngày
  var prev = document.body.getAttribute('data-prev'), next = document.body.getAttribute('data-next');
  if (prev || next) document.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    var t = e.target && e.target.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT' || (e.target && e.target.isContentEditable)) return;
    if (e.key === 'ArrowLeft' && prev) location.href = prev;
    if (e.key === 'ArrowRight' && next) location.href = next;
  });

  // Nút in ở trang Cả khoá
  var p = document.querySelector('[data-print]');
  if (p) p.addEventListener('click', function () { window.print(); });
})();
