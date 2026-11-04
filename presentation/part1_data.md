# Phần 1: Dữ liệu & Phương pháp (~7')

**Câu hỏi mở đầu:** *Làm sao biến 5,66 triệu dòng số liệu thô thành thứ có thể so sánh giữa các nước?*
**Câu cầu nối sang Phần 2:** *"Dữ liệu đã sạch và chúng tôi biết rõ chỗ nào thiếu. Vậy 55 năm số liệu này nói gì về thế giới?"*

---

### S1.1: Bài toán & mục tiêu `[core]` ~1'
- **Thông điệp:** Các nước đã phát triển ra sao trên 6 chủ đề, và nhóm thu nhập của World Bank có phản ánh đúng không?
- **Hình:** sơ đồ 6 chủ đề (Economy, Demography, Health, Education, Environment, Technology)
- **Ý chính:** 3 câu hỏi: so sánh hiện tại / chỉ số nào đi cùng nhau / nhóm theo dữ liệu có khớp nhóm thu nhập không
- **Nguồn:** REPORT §1

### S1.2: Bộ dữ liệu `[core]` ~1'
- **Thông điệp:** WDI là bộ dữ liệu lớn, rộng nhưng thưa.
- **Ý chính:** 5,66 M quan sát · 247 nền kinh tế/aggregate · 1.344 chỉ số · 1960–2015 · chỉ dùng `Country.csv`, `Series.csv`, `Indicators.csv`
- **Nguồn:** REPORT header, README "Reproduce"

### S1.3: Pipeline ETL `[core]` ~1.5'
- **Thông điệp:** Lọc sớm để xử lý file 574 MB trong ~35 MB RAM.
- **Hình:** sơ đồ Extract → Transform → Reshape
- **Ý chính:**
  - Extract: đọc theo chunk, chọn 32 chỉ số, còn 247k dòng
  - Transform: tách 214 nước khỏi 33 aggregate; kiểm tra trùng, giá trị vô hạn, miền giá trị; gắn cờ 29 năm siêu lạm phát (giữ lại)
  - Reshape: long → wide panel (nước × năm) + snapshot (giá trị mới nhất 2005–2014)
- **Nguồn:** Notebook §2–3, §4.1

### S1.4: Dữ liệu thiếu `[core]` ~1.5'
- **Thông điệp:** 45 % ô trống, phần lớn là thiếu *có cấu trúc*, nên xử lý theo từng mục đích.
- **Hình:** `figures/01_coverage_heatmap.png`, `figures/02_snapshot_coverage.png`
- **Ý chính:** nội suy khoảng trống ≤ 3 năm (không ngoại suy) · snapshot lấy giá trị gần nhất trong 10 năm · median theo nhóm thu nhập chỉ dùng cho model · bỏ chỉ số coverage < 60 % · chỉ vẽ trend khi ≥ 30 % nước có số liệu
- **Nguồn:** Notebook §4.2, REPORT §2

### S1.5: EDA: phân phối `[core]` ~1' *(gộp được với S1.6)*
- **Thông điệp:** Nhiều chỉ số lệch phải mạnh nên dùng log (GDP, CO₂).
- **Hình:** `figures/03_distributions.png`
- **Nguồn:** Notebook §5

### S1.6: EDA: tương quan `[core]` ~1'
- **Thông điệp:** Hầu hết chỉ số tương quan mạnh với thu nhập, gợi ý "phát triển là một chiều" (Phần 3 sẽ kiểm chứng).
- **Hình:** `figures/16_correlation.png`
- **Ý chính:** Spearman; CO₂ ~ thu nhập (ρ = 0,86) chặt ngang tuổi thọ ~ thu nhập (ρ = 0,85)
- **Nguồn:** Notebook §8.1

---

## Slot mở rộng `[ext]`
- **S1.7: Tiêu chí chọn 32 chỉ số** (Notebook §2.1): vì sao chọn, coverage từng chỉ số
- **S1.8: Kiểm tra chất lượng chi tiết**: ví dụ cụ thể về các năm siêu lạm phát bị gắn cờ
- **S1.9: Hạn chế của dữ liệu** (REPORT §5): dữ liệu chỉ đến 2014, thiếu không ngẫu nhiên, median không trọng số dân số. *(Có thể chuyển sang Phần 3 nếu Phần 3 cần ngắn bớt.)*
- **S1.10: Cấu trúc repo & khả năng tái lập**: notebook → `run_models.py` → `app.py`, lệnh trong README
- **S1.11: Demo trang Overview của app** (`docs/screenshots/overview_*.png`)

## Block mẫu
```
### S1.x: <Tiêu đề> `[ext]` ~1'
- **Thông điệp:**
- **Hình:**
- **Ý chính:**
- **Nguồn:**
```
