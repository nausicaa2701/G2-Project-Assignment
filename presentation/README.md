# Kế hoạch thuyết trình: WDI 1960–2014

Bài trình bày chia **3 phần đều nhau**, mỗi phần do một người phụ trách và có thể mở rộng độc lập, không ảnh hưởng hai phần còn lại.

| Phần | Chủ đề | Câu hỏi trả lời | Nguồn trong repo | Slide core | Thời lượng |
|---|---|---|---|---|---|
| [1. Dữ liệu & Phương pháp](part1_data.md) | Bài toán, ETL, dữ liệu thiếu, EDA | *Dữ liệu là gì và có tin được không?* | Notebook §1–5, §8.1 · REPORT §1–2 | 6 | ~7' |
| [2. Xu hướng & So sánh](part2_trends.md) | 6 chủ đề, xếp hạng, bất bình đẳng, hội tụ, Việt Nam | *Thế giới đã thay đổi thế nào, ai đi nhanh ai đi chậm?* | Notebook §6–7 · REPORT finding 1–3, §4 | 6 | ~7' |
| [3. Mô hình, Phân cụm & Demo](part3_models.md) | Preston, EKC, 3 mô hình đại diện (Lasso · ExtraTrees · Voting), clustering, app, kết luận | *Cái gì giải thích được sự phát triển, và nhóm nước nào giống nhau?* | Notebook §8.2–9 · REPORT finding 4–7, §5 · `wdi/models.py`, `app.py` | 6 | ~7' |

Tổng: **18 slide core, ~21 phút** (+ title/Q&A). Mỗi phần có danh sách slide `[ext]` để thêm khi cần dài hơn.

## Mạch chuyện (để 3 phần nối nhau)

```
Phần 1: "Chúng tôi có dữ liệu sạch, biết rõ chỗ thiếu"
   └─ cầu nối → "Vậy dữ liệu nói gì về 55 năm phát triển?"
Phần 2: "Sức khỏe/giáo dục hội tụ, thu nhập thì không; Việt Nam vượt kỳ vọng"
   └─ cầu nối → "Có thể đo và dự đoán điều này một cách định lượng không?"
Phần 3: "Thu nhập giải thích phần lớn; phát triển gần như 1 chiều; demo + kết luận"
```

Mỗi phần **mở đầu bằng 1 câu hỏi** và **kết thúc bằng 1 câu cầu nối** (đã viết sẵn trong từng file). Giữ hai câu này cố định khi mở rộng thì mạch chuyện không bị gãy.

## Quy ước mở rộng

1. Mỗi slide là một block `### S<phần>.<số>`, gồm: **Thông điệp** (1 câu), **Hình**, **Ý chính**, **Nguồn**.
2. `[core]` là slide bắt buộc, nằm trong ngân sách ~7'. `[ext]` là slide tùy chọn, thêm được bất kỳ lúc nào.
3. Thêm slide mới: copy block mẫu ở cuối mỗi file, đánh số tiếp (ví dụ `S2.7`). **Không đổi số của slide core.**
4. Mỗi phần chỉ dùng hình/kết quả trong "vùng" của mình (bảng bên dưới) để tránh trùng lặp giữa các phần.
5. Khi rút ngắn: bỏ `[ext]` trước, sau đó gộp các slide core có đánh dấu *(gộp được)*.

## Phân vùng tài nguyên (tránh trùng)

| Tài nguyên | Phần 1 | Phần 2 | Phần 3 |
|---|---|---|---|
| `figures/` | 01, 02, 03, 16 | 04–15 | 17–21 |
| `results/` | — | `trends_income.csv`, `trends_region.csv` | `metrics_*`, `summary_*`, `importance_*` |
| `docs/screenshots/` | `overview_*` (tuỳ chọn) | `trends_light`, `compare_light` | `models_dark`, `clusters_dark` |
| App page (demo) | Overview | Trends, Compare | Models, Clusters |
