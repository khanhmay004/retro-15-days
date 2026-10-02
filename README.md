# Retro 15 ngày

Trang tóm tắt 15 ngày Phase 1 chương trình AI Thực Chiến, gửi cho học viên: mỗi ngày có câu hỏi, mục tiêu, bài học, kiến thức và kỹ năng theo module, lab, câu tự soi. Gom theo 4 cột mốc; Ngày 15 thêm 3 track Phase 2 và 6 kỹ năng nền.

## Sửa nội dung

| Muốn sửa | Mở |
|---|---|
| Một ngày | `content/ngay-XX.json` |
| Cột mốc, track, kỹ năng nền, tên trang, domain | `content/site.json` |
| Giao diện | `assets/style.css`, `assets/app.js`; khung HTML trong `build.py` |

## Build, kiểm, xem thử

```bash
python3 build.py          # content + assets → public/
python3 check.py          # 0 lỗi mới được push/deploy
npx serve public          # xem ở http://localhost:3000
```

`check.py` kiểm schema, độ dài, từ cấm, link nội bộ, chuỗi dẫn về nguồn, và báo lỗi nếu `public/` cũ hơn nội dung.

## Deploy

Project Vercel `retro-15-days`, thư mục xuất `public/` (không có bước build trên Vercel).

```bash
npx vercel deploy --prod
```

Repo đã nối với project Vercel nên push lên `main` cũng tự deploy production; luôn chạy `build.py` và `check.py` trước khi push.
