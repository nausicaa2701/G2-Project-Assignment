# Thiết kế thực nghiệm theo storyline

Storyline ([storyline.md](storyline.md)) đặt ra một câu hỏi: **"Giàu hơn có đồng nghĩa với phát triển hơn không?"** Mỗi phần cần thực nghiệm để *chứng minh* thông điệp của nó, không chỉ minh họa. Mỗi phần có 3 thực nghiệm, mỗi thực nghiệm sinh ra **một hình chính cho một slide**.

## Nguyên tắc chung

1. **Giả thuyết viết trước, kết quả đến sau.** Mỗi thực nghiệm ghi rõ: giả thuyết, cách đo, ngưỡng để chấp nhận, và *câu chuyện sẽ đổi thế nào nếu kết quả ngược lại*.
2. **Dùng lại pipeline có sẵn.** Hàm `THEMES`, `data_path`, danh sách biến rò rỉ (`leak`) và grouped CV theo nước đều lấy từ `wdi/models.py`. Báo cáo mean ± std trên 5 seed, giống `run_models.py`.
3. **Mỗi kết luận có ít nhất một kiểm tra độ vững** (robustness): dữ liệu khác, phương pháp khác, hoặc trọng số khác.
4. **Đo bằng ngôn ngữ của khán giả.** Dùng "năm tuổi thọ", "gấp mấy lần CO₂", "hạng mấy / 192 nước" thay vì chỉ báo R².

> **Trạng thái:** ✅ đã có trong repo · 🧪 đã chạy thử nghiệm sơ bộ (pilot) trong phiên này · 🔨 cần xây.
> Số liệu pilot dùng Ridge, impute median, 5-fold grouped CV, 1 lần chạy, nên phải chạy lại theo protocol đầy đủ trước khi đưa lên slide.

---

## Phần 1 · WHAT: "Thế giới tiến bộ, nhưng không đều"

### E1.1 σ-convergence: cái gì hội tụ, cái gì không 🧪 → hình cho slide 1.1 (hook)
- **Giả thuyết:** chênh lệch giữa các nước về chỉ số xã hội giảm mạnh, còn về thu nhập thì không.
- **Cách đo:** hệ số biến thiên (CV = std/mean) giữa các nước theo từng năm, chỉ tính năm có > 100 nước báo cáo.
- **Pilot:**

  | Chỉ số | Năm đầu | Năm cuối | Kết luận |
  |---|---|---|---|
  | Tuổi thọ | 0,23 (1960) | 0,12 (2013) | giảm một nửa, hội tụ |
  | Nhập học tiểu học | 0,40 (1971) | 0,13 (2013) | hội tụ mạnh |
  | GDP/người | 1,47 (1967) | 1,46 (2014) | **đứng yên** |
  | Sinh suất | 0,31 (1960) | 0,50 (2013) | **phân kỳ**, vì Hạ Sahara đứng lại |

- **Hình:** đường CV của mỗi chỉ số, chuẩn hóa về 1 ở năm đầu. Thu nhập nằm ngang trong khi các đường xã hội đi xuống. Một hình này thay được hai con số ở slide 1.1.
- **Nếu ngược lại:** nếu thu nhập cũng hội tụ thì nghịch lý mở bài không tồn tại, và phải đổi câu hook.

### E1.2 β-convergence cho cả chỉ số xã hội 🔨 → slide 1.5
- **Giả thuyết:** nước xuất phát thấp tăng tuổi thọ và nhập học nhanh hơn (hệ số β âm rõ), còn với thu nhập thì β yếu (đã có: r = −0,16, p = 0,05 ✅).
- **Cách đo:** hồi quy (mức thay đổi hằng năm 1990–2014) theo (mức năm 1990), cho 4 chỉ số. Báo hệ số β, khoảng tin cậy 95 % và R².
- **Hình:** 4 ô scatter nhỏ đặt cạnh nhau, Việt Nam tô đỏ ở cả 4 ô.

### E1.3 Kiểm tra độ vững của dữ liệu: kết luận có do dữ liệu thiếu tạo ra không? 🔨 → slide 1.2
- **Lo ngại:** nước nghèo báo cáo thiếu nhiều hơn, nên hội tụ có thể chỉ là ảo giác do thay đổi tập nước theo thời gian.
- **Cách đo:** chạy lại E1.1 trên (a) **panel cân bằng**, chỉ gồm các nước có đủ số liệu cả kỳ, và (b) **trọng số theo dân số** thay vì median.
- **Chấp nhận nếu:** chiều xu hướng không đổi trong cả (a) và (b). Khi đó slide 1.2 có câu: "kết luận không đổi khi chỉ dùng nước có đủ số liệu."

---

## Phần 2 · WHY: "Thu nhập giải thích phần lớn, phần dư mới là câu chuyện"

### E2.1 Thu nhập giải thích bao nhiêu? Tách R² thành 3 lớp 🧪 → slide 2.3 (thay slide 19 mô hình)
- **Giả thuyết:** chỉ riêng log GDP/người giải thích khoảng 2/3 ở hầu hết các chủ đề. Thêm biến khác giúp vừa phải, thêm mô hình phi tuyến giúp rất ít.
- **Cách đo:** với mỗi chủ đề, chạy 3 cấu hình cùng một cách chia fold:
  ① Ridge chỉ với log GDP → ② Ridge với tất cả biến → ③ mô hình tốt nhất (đã có trong `results/summary_snapshot.csv` ✅)
- **Pilot (① → ②):**

  | Chủ đề | ① chỉ thu nhập | ② tất cả biến | ③ tốt nhất (đã có) |
  |---|---|---|---|
  | Health (tuổi thọ) | 0,65 | 0,81 | 0,81 |
  | Environment (CO₂) | 0,72 | 0,86 | 0,87 |
  | Technology (internet) | 0,81 | 0,81 | 0,85 |
  | Education (THCS) | 0,60 | 0,75 | 0,77 |
  | Demography (sinh suất) | 0,55 | 0,77 | 0,82 |
  | *trung bình* | *0,67* | | |

- **Hình:** cột chồng cho mỗi chủ đề gồm ba lớp: phần của thu nhập, phần thêm từ biến khác, phần thêm từ mô hình phức tạp. Lớp đầu chiếm phần lớn, lớp cuối rất mỏng.
- **Kết quả này cho phép nói "~2/3" có bằng chứng ở cả 5 chủ đề**, không chỉ ở chủ đề sức khỏe.

### E2.2 Bảng điểm phần dư của Việt Nam 🧪 → slide 2.4 (slide quan trọng nhất)
- **Giả thuyết:** Việt Nam vượt kỳ vọng so với thu nhập ở các chỉ số xã hội.
- **Cách đo:** lấy phần dư ngoài mẫu (out-of-fold) của mô hình ①, đổi sang đơn vị dễ hiểu, rồi xếp hạng Việt Nam trong số các nước.
- **Pilot:**

  | Chỉ số | Thực tế so với mức thu nhập dự đoán | Hạng |
  |---|---|---|
  | Tuổi thọ | **+10,0 năm** | **1 / 192** |
  | Internet | +25 điểm % | 3 / 195 |
  | Sinh suất | −1,9 con/phụ nữ (thấp hơn nhiều) | 190 / 192 |
  | **CO₂/người** | **≈ 3× mức dự đoán** | 22 / 192 |

- **Phát hiện mới, rất đắt giá cho Phần 3:** Việt Nam vượt kỳ vọng về mặt xã hội, nhưng **phát thải gấp ~3 lần mức thu nhập dự đoán**. Phần "cái giá của tăng trưởng" (slide 2.5) vì vậy có một ví dụ cụ thể ngay trong nước.
- **Hình:** dot plot gồm các chủ đề × phân vị phần dư; Việt Nam tô đỏ, các nước cùng nhóm (Trung Quốc, Thái Lan, Indonesia, Philippines) tô xám.

### E2.3 "Giàu hơn" khác "giàu lên": thêm góc nhìn trong từng nước 🔨 → slide 2.2 (hoặc backup)
- **Lo ngại:** đường Preston là tương quan *giữa các nước*. Hội đồng có thể hỏi: khi một nước giàu lên thì tuổi thọ có tăng tương ứng không?
- **Cách đo:** panel 1990–2014, hồi quy fixed effects (theo nước và theo năm): `life_exp ~ log_gdp + FE_country + FE_year`. So hệ số trong-nước với hệ số giữa-các-nước (~10 năm cho mỗi 10× thu nhập).
- **Diễn giải:** nếu hệ số trong-nước nhỏ hơn nhiều thì thu nhập là một phần của câu chuyện, còn yếu tố chung theo thời gian (công nghệ y tế, vaccine) mới là động lực lớn. Điều này giải thích vì sao đường cong dịch lên 5 năm, và củng cố ý "chính sách dịch được cả đường cong".
- Đây là bước tiếp theo đã ghi sẵn trong REPORT ("fixed-effects panel models"). Làm thực nghiệm này là trả lời luôn mục giới hạn đó.

---

## Phần 3 · SO WHAT: "Nhìn bằng dữ liệu, không chỉ bằng thu nhập"

### E3.1 Phân cụm có vững không? 🔨 (công cụ đã có trong app) → slide 3.2
- **Lo ngại:** silhouette thấp (0,19 ở k = 4), nên vị trí của một nước có thể chỉ do seed hoặc thuật toán.
- **Cách đo:** chạy K-means, GMM và Ward với 20 seed (app đã hỗ trợ cả ba). Đo (a) ARI giữa các lần chạy, (b) **tỉ lệ số lần Việt Nam rơi vào cụm "emerging"**, (c) tỉ lệ khớp với nhóm thu nhập (hiện 74 % ✅).
- **Chấp nhận nếu:** Việt Nam ở cụm "emerging" ≥ 80 % số lần chạy. Nếu không, slide 3.2 phải nói "Việt Nam nằm ở ranh giới giữa hai cụm". Câu này vẫn là một insight, chỉ khác cách nói.

### E3.2 "Song sinh phát triển" của Việt Nam 🔨 → slide 3.3
- **Câu hỏi:** Việt Nam *giống* nước nào nhất nếu bỏ qua thu nhập?
- **Cách đo:** chuẩn hóa các chỉ số xã hội, **không** đưa GDP vào, rồi lấy 5 nước gần nhất theo khoảng cách Euclid. So với 5 nước gần nhất *chỉ theo GDP*.
- **Hình:** hai cột tên nước đặt cạnh nhau: "Cùng mức thu nhập" và "Cùng kết quả phát triển". Dự kiến cột phải gồm các nước giàu hơn hẳn, đây là cách trực quan nhất để nói "Việt Nam vượt mức thu nhập".

### E3.3 Phân tích khoảng trống: ưu tiên tiếp theo của Việt Nam 🔨 → slide 3.4
- **Cách đo:** với từng chỉ số, tính khoảng cách giữa Việt Nam và median cụm "emerging" (và cụm "advanced"), đổi sang đơn vị độ lệch chuẩn, rồi xếp hạng.
- **Dự kiến:** khoảng trống lớn nhất là thu nhập, tử vong trẻ em (22‰ so với 7–13‰) và CO₂ theo thu nhập (từ E2.2).
- **Hình:** biểu đồ cột ngang (bar chart dạng "gap"), sắp từ khoảng trống lớn nhất. Đây chính là phần "Now what" của bài, và mỗi gợi ý đều có số đi kèm.

---

## Liên kết thực nghiệm → slide

| Slide | Trước (hình có sẵn) | Sau (hình từ thực nghiệm) |
|---|---|---|
| 1.1 hook | 2 con số | **E1.1** đường CV: xã hội hội tụ, thu nhập đứng yên |
| 1.2 dữ liệu | heatmap coverage | heatmap + 1 câu kết quả từ **E1.3** |
| 1.5 thu nhập không hội tụ | `14_convergence` | **E1.2** β cho 4 chỉ số |
| 2.3 mô hình | bảng 3 mô hình | **E2.1** R² 3 lớp |
| 2.4 phần dư | `17` phóng to | **E2.2** bảng điểm Việt Nam |
| 2.5 CO₂ | `19_ekc` | `19` + điểm Việt Nam ≈ 3× (từ E2.2) |
| 3.2 cụm | `21_pca_clusters` | `21` + độ vững từ **E3.1** |
| 3.3 Việt Nam | `15_vietnam_peers` | **E3.2** song sinh phát triển |
| 3.4 khoảng trống | `15` | **E3.3** biểu đồ khoảng trống |

## Cách tổ chức code (đề xuất)

```
wdi/story.py              # hàm cho E1.1–E3.3, dùng lại THEMES/data_path/grouped CV của wdi/models.py
run_story.py              # CLI: python run_story.py --exp E2.2 --seeds 0 1 2 3 4
results/story/E*.csv      # số liệu cho mỗi thực nghiệm
figures/story/E*.png      # một hình mỗi thực nghiệm, Việt Nam màu #c0392b
tests/test_story.py       # smoke test, giống tests/test_models.py
```
Mỗi thực nghiệm là một hàm độc lập trả về `(bảng, hình)`, nên ba người có thể làm song song theo phần mà không đụng file của nhau. Nếu muốn, có thể thêm trang "Story" vào `app.py` để demo cuối bài.

## Thứ tự ưu tiên (nếu thiếu thời gian)
1. **E2.2, E2.1, E1.1**: đã có pilot và là xương sống của câu chuyện.
2. **E3.2, E3.3**: biến Phần 3 từ mô tả thành khuyến nghị.
3. **E1.3, E3.1**: kiểm tra độ vững, để trả lời câu hỏi của hội đồng.
4. **E1.2, E2.3**: làm sâu thêm. E2.3 có thể để ở backup.
