# Phần 2: Xu hướng & So sánh (~7')

**Câu hỏi mở đầu:** *Trong 55 năm, thế giới tiến bộ ở đâu, và khoảng cách giữa các nước có thu hẹp không?*
**Câu cầu nối sang Phần 3:** *"Ta thấy thu nhập dường như kéo theo mọi thứ khác, và Việt Nam vượt kỳ vọng. Có thể đo điều này bằng mô hình không?"*

---

### S2.1: Tổng quan xu hướng theo 6 chủ đề `[core]` ~1.5'
- **Thông điệp:** Tiến bộ xã hội rộng khắp; kinh tế thì không đồng đều.
- **Hình:** lưới nhỏ `figures/04`–`09` (economy, demography, health, education, environment, technology)
- **Ý chính:** median theo nhóm thu nhập; giáo dục tiểu học gần phổ cập; di động ~64/100 người ngay cả ở nước thu nhập thấp
- **Nguồn:** Notebook §6.1–6.6, `results/trends_income.csv`

### S2.2: Sức khỏe dẫn đầu `[core]` ~1'
- **Thông điệp:** Tuổi thọ tăng ở mọi khu vực, khoảng cách giàu–nghèo giảm 30,1 → 20,8 năm.
- **Hình:** `figures/06_trend_health.png`
- **Ý chính:** Nam Á +30 năm (39 → 69)
- **Nguồn:** REPORT finding 1

### S2.3: Tốc độ theo khu vực & ngoại lệ châu Phi `[core]` ~1'
- **Thông điệp:** Hạ Sahara là ngoại lệ lớn của quá trình chuyển đổi nhân khẩu.
- **Hình:** `figures/10_trend_regions.png`, (phụ) `figures/05_trend_demography.png`
- **Ý chính:** sinh suất giảm 60–67 % ở Nam Á, MENA, Đông Á, Mỹ Latinh nhưng chỉ 28 % ở Hạ Sahara (6,7 → 4,8)
- **Nguồn:** Notebook §6.7, REPORT finding 3, `results/trends_region.csv`

### S2.4: Dẫn đầu & tụt hậu `[core]` ~1' *(gộp được với S2.5)*
- **Thông điệp:** 10 nước nghèo nhất và 10 nước tuổi thọ thấp nhất đều ở Hạ Sahara.
- **Hình:** `figures/11_rank_gdp.png`, `figures/12_rank_life.png`, `figures/13_rank_co2.png`
- **Nguồn:** Notebook §7.1

### S2.5: Thu nhập KHÔNG hội tụ `[core]` ~1.5'
- **Thông điệp:** Nước thu nhập trung bình tăng nhanh hơn, nhưng bất bình đẳng giữa các nước gần như không đổi.
- **Hình:** `figures/14_convergence.png`
- **Ý chính:** Gini 0,70 → 0,67; p90/p10 77× → 81×; β-convergence r = −0,16 (p = 0,05); bắt kịp đến từ một số nước cụ thể: Trung Quốc 9,2 %/năm, Việt Nam 5,5 %, Lào, Ấn Độ. Ngược lại, giáo dục, điện và di động *có* hội tụ.
- **Nguồn:** Notebook §7.2–7.3, REPORT finding 2

### S2.6: Case study: Việt Nam `[core]` ~1'
- **Thông điệp:** Việt Nam có tuổi thọ của nước giàu hơn 3,5 lần.
- **Hình:** `figures/15_vietnam_peers.png`
- **Ý chính:** GDP/người ×4,1 (1984–2014); tuổi thọ 75,8, bằng Trung Quốc và Thái Lan; sinh suất 1,74; internet 48/100; rừng 47 %. Khoảng cách còn lại: mức thu nhập và tử vong trẻ em (22‰ so với 7–13‰).
- **Nguồn:** Notebook §7.4, REPORT §4

---

## Slot mở rộng `[ext]`
- **S2.7: Từng chủ đề một slide** (tách S2.1 thành 6 slide với `figures/04`–`09`) để kéo dài thêm ~3'
- **S2.8: Môi trường & năng lượng**: rừng thế giới 31,8 % → 30,8 %; chỉ 26/56 nước thu nhập cao giảm CO₂/người (dẫn sang EKC ở Phần 3)
- **S2.9: Công nghệ**: tốc độ phổ cập di động/internet theo nhóm
- **S2.10: Demo app trang Trends & Compare** (`docs/screenshots/trends_light.png`, `compare_light.png`): bản đồ thế giới, scatter 2 chỉ số bất kỳ
- **S2.11: Việt Nam mở rộng**: so sánh thêm chỉ số với Indonesia, Philippines, Ấn Độ (+7–8 năm tuổi thọ)

## Block mẫu
```
### S2.x: <Tiêu đề> `[ext]` ~1'
- **Thông điệp:**
- **Hình:**
- **Ý chính:**
- **Nguồn:**
```
