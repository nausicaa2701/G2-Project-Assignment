# Đề xuất storyline: một câu hỏi, ba phần, một nhân vật

## Câu hỏi lớn (cả bài chỉ trả lời câu này)

> **"Giàu hơn có đồng nghĩa với phát triển hơn không?"**

**Câu trả lời (nói ngay từ đầu, theo Pyramid Principle):** *Phần lớn là có: thu nhập giải thích ~2/3 khác biệt. Nhưng phần còn lại mới là câu chuyện. Có những nước sống tốt hơn nhiều so với mức thu nhập, và Việt Nam là một ví dụ rõ nhất.*

**Nhân vật xuyên suốt:** Việt Nam, luôn tô **màu đỏ** (`#c0392b`, đúng màu notebook đang dùng) trên mọi biểu đồ. Khán giả nhìn vào hình nào cũng biết tìm điểm nào.

## Khung 3 phần: What → Why → So what

Ba phần tương ứng ba cấp phân tích dữ liệu: mô tả (descriptive), chẩn đoán (diagnostic), hàm ý (prescriptive). Mỗi phần kết thúc bằng một câu hỏi mà phần sau trả lời.

```
PHẦN 1 · WHAT                 PHẦN 2 · WHY                    PHẦN 3 · SO WHAT
"Thế giới tiến bộ,            "Thu nhập giải thích            "Nhìn bằng dữ liệu, không
 nhưng không đều"              phần lớn, phần dư mới           chỉ bằng thu nhập:
                               là câu chuyện"                  Việt Nam đứng ở đâu?"
Mô tả · so sánh theo thời gian Tương quan · hồi quy · residual  PCA · phân cụm · case study
        │                              │                              │
        └─► Nghịch lý: sức khỏe        └─► Nếu thu nhập không         └─► Trả lời câu hỏi lớn
            hội tụ, thu nhập thì           nói hết, xếp nhóm theo         + khuyến nghị + hạn chế
            không. Vậy thu nhập            thu nhập có đúng không?
            quan trọng đến mức nào?
```

---

## Phần 1 · WHAT: "Thế giới tiến bộ, nhưng không đều" (5 slide, ~7')

| # | Tiêu đề hành động (action title) | Hình | Con số neo |
|---|---|---|---|
| 1.1 | **Khoảng cách tuổi thọ giàu–nghèo giảm 1/3, nhưng khoảng cách thu nhập còn tăng** *(hook + câu hỏi lớn)* | 2 con số đặt cạnh nhau | 30,1 → 20,8 năm · p90/p10 77× → 81× |
| 1.2 | **55 năm, 214 nước, và biết rõ chỗ dữ liệu thiếu** *(độ tin cậy, chỉ 1 slide)* | `01_coverage_heatmap` | 45 % ô trống, phần lớn thiếu có cấu trúc; 5 quy tắc xử lý |
| 1.3 | **Sức khỏe, giáo dục, di động: gần như ai cũng tiến lên** | `06_trend_health` (+ 07, 09 nhỏ) | Nam Á +30 năm tuổi thọ; di động ~64/100 ở nước nghèo |
| 1.4 | **Trừ một ngoại lệ: Hạ Sahara chưa qua chuyển đổi dân số** | `10_trend_regions` | Sinh suất −28 % so với −60–67 % ở nơi khác |
| 1.5 | **Thu nhập không hội tụ, chỉ vài nước bứt phá (có Việt Nam)** | `14_convergence` | β r = −0,16; Trung Quốc 9,2 %/năm, Việt Nam 5,5 %/năm |

**Cầu nối →** *"Sức khỏe hội tụ trong khi thu nhập thì không. Vậy thu nhập thực sự quan trọng đến mức nào?"*

## Phần 2 · WHY: "Thu nhập giải thích phần lớn, phần dư mới là câu chuyện" (5 slide, ~7')

| # | Tiêu đề hành động | Hình | Con số neo |
|---|---|---|---|
| 2.1 | **Gần như mọi chỉ số đều đi cùng thu nhập** | `16_correlation` | ρ tuổi thọ 0,85 · ρ CO₂ 0,86 |
| 2.2 | **Giàu gấp 10 lần thì sống thêm ~10 năm** (đường Preston) | `17_preston_curve` | R² 0,65; cả đường cong dịch lên +5 năm từ 1990 |
| 2.3 | **Mô hình phức tạp hơn gần như không giúp gì, vì quan hệ vốn đơn giản** | `18_model_life_exp` + bảng 3 mô hình | log GDP: R² 0,64 → thêm 7 biến: 0,76 → RF: 0,76; ở 6 chủ đề Lasso chỉ kém ensemble 0,01–0,07 |
| 2.4 | **Phần dư: ai sống tốt hơn mức thu nhập cho phép?** *(slide quan trọng nhất)* | `17` phóng to phần residual | Việt Nam **+10,4 năm**; Nepal, Bangladesh; dầu mỏ & HIV: −15–20 năm |
| 2.5 | **Cái giá của tăng trưởng: CO₂ chưa giảm khi giàu lên** | `19_ekc` | Điểm ngoặt ~51.000 USD; chỉ 9/192 nước vượt |

**Cầu nối →** *"Thu nhập không nói hết câu chuyện. Vậy chia nhóm các nước theo thu nhập có còn đúng không?"*

## Phần 3 · SO WHAT: "Nhìn bằng dữ liệu, không chỉ bằng thu nhập" (5 slide, ~7')

| # | Tiêu đề hành động | Hình | Con số neo |
|---|---|---|---|
| 3.1 | **Phát triển chủ yếu là một trục liên tục, không phải các bậc tách biệt** | `21_pca_clusters` (trục PC1) | PC1 = 63 % phương sai; silhouette thấp → continuum |
| 3.2 | **4 cụm theo dữ liệu khớp nhóm thu nhập 74 %, chỗ lệch mới đáng nói** | `21_pca_clusters` + bảng cụm | Guinea Xích Đạo, Angola rơi vào cụm thấp; vùng Vịnh vào cụm "emerging" |
| 3.3 | **Việt Nam: thu nhập trung bình thấp, kết quả của nhóm "emerging"** | `15_vietnam_peers` | Tuổi thọ 75,8 = Trung Quốc, Thái Lan (giàu hơn 3,5×); sinh suất 1,74; internet 48 % |
| 3.4 | **Hai khoảng trống còn lại: thu nhập và tử vong trẻ em** | `15` (chỉ 2 chỉ số) | Tử vong dưới 5 tuổi 22‰ so với 7–13‰ ở các nước cùng nhóm |
| 3.5 | **Trả lời câu hỏi lớn + hàm ý + giới hạn** | 3 dòng chữ | Xem bên dưới |

**Slide 3.5, nội dung chốt:**
- *Trả lời:* Giàu hơn thì phần lớn phát triển hơn (~2/3), nhưng chính sách dịch được cả đường cong (+5 năm toàn cầu, +10 năm ở Việt Nam).
- *Hàm ý (dạng "gợi ý", vì đây là tương quan, không phải nhân quả):* nên đánh giá các nước theo kết quả xã hội, không chỉ theo GDP; với Việt Nam, ưu tiên là tử vong trẻ em và một lộ trình tăng trưởng ít CO₂ hơn những nước đi trước.
- *Giới hạn:* dữ liệu đến 2014; nước nghèo thiếu số liệu nhiều hơn; số liệu là tương quan; median không trọng số dân số.
- *Kết:* "Câu hỏi của bạn là gì?" → mở app (trang Compare/Clusters) để trả lời trực tiếp.

---

## Kỹ năng DA được áp dụng

| Kỹ năng | Áp dụng cụ thể |
|---|---|
| **Một câu hỏi trung tâm** | Mọi slide phải góp phần trả lời "giàu hơn = phát triển hơn?"; slide không góp phần thì đưa vào phụ lục |
| **Pyramid Principle / nói kết luận trước** | Câu trả lời xuất hiện ngay ở slide 1.1, ba phần sau là bằng chứng |
| **SCQA** | Situation (1.3) → Complication (1.5: thu nhập không hội tụ) → Question (cầu nối) → Answer (Phần 2–3) |
| **Action title** | Tiêu đề là một câu kết luận ("Giàu gấp 10 lần…"), không phải tên chủ đề ("Preston curve") |
| **Một hình, một thông điệp, một con số** | Mỗi slide có đúng một con số neo để khán giả nhớ |
| **Màu có chủ đích** | Xám cho mọi nước, đỏ cho Việt Nam, một màu nhấn cho nhóm được nhắc tới |
| **So sánh với benchmark** | Việt Nam luôn đặt cạnh một mốc so sánh (đường Preston, nhóm cụm, các nước láng giềng) thay vì đứng một mình |
| **Phân tích phần dư (residual)** | Insight hay nhất nằm ở chỗ mô hình đoán sai (2.4, 3.2), không phải ở R² |
| **Phương pháp là để tạo niềm tin, không phải để trình diễn** | ETL và dữ liệu thiếu gói trong 1 slide; 19 mô hình và grouped CV đưa vào phụ lục |
| **Trung thực về giới hạn** | Dùng "gắn liền với", "gợi ý", không dùng "gây ra"; giới hạn nằm ngay trong slide kết, không giấu |

## Những gì rút khỏi phần chính (đưa vào phụ lục / backup)

| Nội dung | Lý do | Dùng khi |
|---|---|---|
| `03_distributions`, `02_snapshot_coverage` | Kỹ thuật, không trả lời câu hỏi lớn | Bị hỏi vì sao dùng log |
| `04`, `05`, `08` trend riêng từng chủ đề | Lặp ý của 1.3–1.4 | Muốn kéo dài Phần 1 |
| `11`–`13` bảng xếp hạng | 1.4 đã nói ý "Hạ Sahara tụt hậu" | Bị hỏi top/bottom 10 |
| 19 mô hình, feature importance, panel vs snapshot | Kết luận giống hệt 2.3 | Hội đồng hỏi về độ chặt chẽ của mô hình |
| `20_cluster_k` (chọn k) | Chi tiết kỹ thuật | Bị hỏi vì sao chọn k = 4 |

## Cách mở rộng mà không phá mạch
Thêm slide ở phần nào cũng phải trả lời được câu: *"Slide này giúp trả lời câu hỏi lớn ở cấp nào: What, Why hay So what?"* Trả lời được thì chèn vào đúng phần đó, giữ tiêu đề dạng action title và một con số neo. Không trả lời được thì đưa vào phụ lục.
