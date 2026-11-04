# Phần 3: Mô hình, Phân cụm & Demo (~7')

**Câu hỏi mở đầu:** *Thu nhập giải thích được bao nhiêu phần của sự phát triển, và dữ liệu tự chia các nước thành những nhóm nào?*
**Kết thúc:** 3 takeaway + hạn chế + hướng phát triển, sau đó Q&A.

---

### S3.1: Đường Preston: thu nhập & tuổi thọ `[core]` ~1.5'
- **Thông điệp:** Thu nhập tăng 10× thì tuổi thọ tăng ~10 năm (R² = 0,65), nhưng không phải tất cả.
- **Hình:** `figures/17_preston_curve.png`
- **Ý chính:** đường cong dịch lên ~5 năm kể từ 1990; vượt kỳ vọng: Việt Nam (+10,4), Nepal, Nicaragua, Bangladesh; dưới kỳ vọng: Nam Phi (HIV), Guinea Xích Đạo, Angola (−15–20 năm)
- **Nguồn:** Notebook §8.2, REPORT finding 4

### S3.2: Dự đoán tuổi thọ: linear vs random forest `[core]` ~1'
- **Thông điệp:** Mô hình tuyến tính đơn giản là đủ, và dễ giải thích hơn.
- **Hình:** `figures/18_model_life_exp.png`
- **Ý chính:** chỉ log GDP: R² 0,64 (MAE 3,6 năm); thêm 7 biến: R² 0,76 (MAE 2,9); RF: R² 0,76 (MAE 2,8), không tốt hơn
- **Nguồn:** Notebook §8.3, REPORT finding 5

### S3.3: Mô hình phức tạp có đáng không? `[core]` ~1.5'
- **Thông điệp:** Mô hình phức tạp chỉ hơn mô hình tuyến tính +0,01–0,07 R², nên quan hệ chủ yếu là tuyến tính và mô hình đơn giản là đủ để giải thích.
- **Chỉ trình bày 3 mô hình đại diện** (mỗi cái trả lời một câu hỏi):
  - **Lasso**: baseline tuyến tính, đọc được hệ số. *"Quan hệ đơn giản giải thích được bao nhiêu?"*
  - **ExtraTrees**: cây, bắt được phi tuyến/tương tác. *"Có quan hệ phi tuyến bị bỏ sót không?"*
  - **Voting**: trung bình nhiều mô hình. *"Gộp lại có tốt hơn hẳn không?"*
- **Bảng (R² trung bình, grouped CV theo nước, 5 seed):**

  | Chủ đề (target) | Lasso | ExtraTrees | Voting | Chênh lệch |
  |---|---|---|---|---|
  | Economy (log GDP/người) | 0,81 | 0,88 | 0,87 | +0,07 |
  | Environment (log CO₂/người) | 0,85 | 0,86 | 0,87 | +0,01 |
  | Technology (internet) | 0,79 | 0,85 | 0,84 | +0,06 |
  | Demography (sinh suất) | 0,77 | 0,80 | 0,82 | +0,05 |
  | Health (tuổi thọ) | 0,79 | 0,80 | 0,81 | +0,02 |
  | Education (nhập học THCS) | 0,73 | 0,77 | 0,77 | +0,04 |

- **Câu nói khi bị hỏi "sao không dùng nhiều mô hình hơn?":** "Chúng tôi đã thử 19 mô hình (`wdi/models.py`); kết quả cả nhóm nằm trong khoảng hẹp, nên chỉ trình bày 3 đại diện."
- **Lưu ý phương pháp (1 câu):** chia train/test theo nước, nên một nước không nằm ở cả hai phía; loại các biến gần như định nghĩa target (ví dụ tử vong trẻ em khi đoán tuổi thọ).
- **Nguồn:** `results/summary_snapshot.csv`, `wdi/models.py`

### S3.4: Đường cong Kuznets môi trường `[core]` ~1' *(gộp được với S3.1)*
- **Thông điệp:** Tăng trưởng vẫn đồng nghĩa với nhiều CO₂ hơn.
- **Hình:** `figures/19_ekc.png`
- **Ý chính:** điểm ngoặt ~51.000 USD/người; chỉ 9/192 nước vượt mức này
- **Nguồn:** Notebook §8.4, REPORT finding 6

### S3.5: Phân cụm: phát triển gần như một chiều `[core]` ~1'
- **Thông điệp:** PC1 giải thích 63 % phương sai; 4 cụm khớp nhóm thu nhập ở 74 % số nước, và chỗ lệch mới là điều thú vị.
- **Hình:** `figures/21_pca_clusters.png` (phụ: `figures/20_cluster_k.png`)
- **Ý chính:** low development / transition / emerging / advanced; Guinea Xích Đạo, Angola rơi vào cụm thấp; Việt Nam (lower-middle) cùng cụm "emerging" với Trung Quốc, Thái Lan, Malaysia
- **Nguồn:** Notebook §8.5, REPORT finding 7

### S3.6: Kết luận, hạn chế, hướng tiếp `[core]` ~1'
- **3 takeaway:** (1) sức khỏe và giáo dục hội tụ, thu nhập thì không · (2) thu nhập giải thích phần lớn, phần còn lại là chính sách (Việt Nam) · (3) tăng trưởng vẫn đi kèm CO₂
- **Hạn chế:** dữ liệu đến 2014; thiếu không ngẫu nhiên; tương quan không phải nhân quả; median không trọng số dân số; CO₂ theo lãnh thổ
- **Hướng tiếp:** WDI API cho 2020s, fixed-effects panel, CO₂ theo tiêu dùng
- **Nguồn:** Notebook §9, REPORT §5

---

## Slot mở rộng `[ext]`
- **S3.7: Live demo app**, trang Models (chạy thử nghiệm trực tiếp) và Clusters (chọn k, seed; K-means/GMM/Ward). Khoảng 2–3'. Nên có video dự phòng.
- **S3.7b: Toàn bộ 19 mô hình (backup / phụ lục)**, chia 5 họ: tuyến tính (6), cây (3), boosting (5), ensemble (2), khác (KNN, SVR, MLP). Thông điệp: Decision Tree đơn lẻ kém nhất (R² 0,60–0,77); các họ còn lại sát nhau. Chỉ mở khi có người hỏi.
- **S3.8: Feature importance** từ `results/importance_snapshot.csv`: biến nào quan trọng nhất cho mỗi chủ đề
- **S3.9: Snapshot vs Panel**: so sánh `summary_snapshot.csv` và `summary_panel.csv` (1990–2014, nhiều dòng hơn; ảnh hưởng của biến Year)
- **S3.10: Độ ổn định theo seed**: R² ± std, vì sao cần nhiều seed
- **S3.11: Chọn k cho clustering**: silhouette (`figures/20_cluster_k.png`)
- **S3.12: Kiến trúc kỹ thuật & deploy**: Streamlit Community Cloud, `app_data/` nén 1,5 MB

## Block mẫu
```
### S3.x: <Tiêu đề> `[ext]` ~1'
- **Thông điệp:**
- **Hình:**
- **Ý chính:**
- **Nguồn:**
```
