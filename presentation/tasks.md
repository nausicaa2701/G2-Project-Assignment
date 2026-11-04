# Phân công task: 3 người · 3 phần · trình bày bằng Streamlit

Mỗi người sở hữu **một phần của câu chuyện** ([storyline.md](storyline.md)), từ tiền xử lý → thực nghiệm ([experiments.md](experiments.md)) → **một trang Streamlit** dùng để trình bày trực tiếp, thay cho slide.

| | **Người A · Phần 1 WHAT** | **Người B · Phần 2 WHY** | **Người C · Phần 3 SO WHAT** |
|---|---|---|---|
| Thông điệp | Thế giới tiến bộ, nhưng không đều | Thu nhập giải thích phần lớn, phần dư mới là câu chuyện | Nhìn bằng dữ liệu, không chỉ bằng thu nhập |
| Hạ tầng chung phụ trách | **Setup + pipeline ETL + deploy** | **Tiền xử lý cho mô hình + chạy lại kết quả** | **Gắn nav + helper nhỏ + review `app.py`** |
| Tiền xử lý riêng | Làm sạch, dữ liệu thiếu, reshape, panel cân bằng | Log transform, loại biến rò rỉ, lọc coverage, impute, chia fold theo nước | Chọn 15 chỉ số, chuẩn hóa, PCA, không gian khoảng cách bỏ GDP |
| Thực nghiệm | E1.1 σ-convergence · E1.2 β-convergence · E1.3 độ vững dữ liệu | E2.1 R² 3 lớp · E2.2 bảng điểm phần dư Việt Nam · E2.3 fixed effects | E3.1 độ vững phân cụm · E3.2 song sinh phát triển · E3.3 khoảng trống Việt Nam |
| Trang Streamlit | `page_part1`, dùng lại Overview + Trends | `page_part2`, dùng lại Compare (scatter) + Models | `page_part3`, dùng lại Clusters |

Mỗi người có khối lượng tương đương: **1 phần hạ tầng + 1 phần tiền xử lý + 3 thực nghiệm + 1 trang app (~7')**.

---

## Tận dụng app có sẵn (không xây lại)

`app.py` đã có design system (light/dark, `style`, `hero`, `section`, `tiles`, `table`, `LABELS`, `load_data`, `group_trend`) và 5 trang. Phần lớn nội dung câu chuyện **đã có sẵn**, mỗi người chỉ cần lấy lại phần đó và *bổ sung* thực nghiệm mới:

| Phần | Đã có trong `app.py` (dùng lại) | Cần thêm |
|---|---|---|
| **A · WHAT** | `page_overview` (tuổi thọ theo nhóm thu nhập, 4 insight), `page_trends` (trend theo theme/region, so sánh nước), `group_trend()` | Heatmap coverage, E1.1 đường CV, E1.2 β, câu cầu nối |
| **B · WHY** | `page_compare` → "Relationship explorer" (scatter 2 chỉ số bất kỳ, dùng cho Preston/EKC), `page_models` (R² 19 mô hình, importance, live experiment) | E2.1 R² 3 lớp, E2.2 bảng điểm phần dư Việt Nam, tô đỏ Việt Nam |
| **C · SO WHAT** | `page_clusters` (K-means/GMM/Ward, PCA, bản đồ, profile cụm, % khớp nhóm thu nhập) | E3.1 độ vững, E3.2 song sinh, E3.3 khoảng trống, phần kết luận |

**Cách làm:** mỗi người viết **một hàm trang mới** `page_part1()` / `page_part2()` / `page_part3()`, gọi lại helper và đoạn biểu đồ có sẵn, rồi thêm một dòng `st.Page(...)` vào `st.navigation`. Các trang cũ giữ nguyên để làm mục "Khám phá" trong Q&A.

```
app.py                         chung  # mỗi người chỉ thêm hàm page_partN của mình + 1 dòng nav
wdi/story/part1.py             A   # logic thực nghiệm tách khỏi app.py để test được
wdi/story/part2.py             B
wdi/story/part3.py             C
wdi/etl.py                     A   # tách cell 4–18 của notebook thành script chạy được
wdi/models.py                  B   # đã có; chỉ thêm, không sửa hành vi cũ
wdi/story/part1.py             A   # E1.1–E1.3, mỗi hàm trả về DataFrame
wdi/story/part2.py             B   # E2.1–E2.3
wdi/story/part3.py             C   # E3.1–E3.3 + tiền xử lý phân cụm (tách từ page_clusters)
run_story.py                   B   # CLI: python run_story.py --part 2 --seeds 0 1 2 3 4 → results/story/
results/story/E*.csv           mỗi người ghi file của mình
tests/test_part{1,2,3}.py      mỗi người một file
SETUP.md                       A
```

**Quy tắc tránh xung đột:** trong `app.py`, mỗi người chỉ thêm hàm của mình vào một vùng riêng, đánh dấu `# ---- part N (owner X)`, và không sửa helper hay trang cũ. Như vậy git merge tự động được vì các thay đổi nằm ở những đoạn khác nhau. Cần sửa helper chung hoặc `requirements.txt` thì mở PR riêng cho C review. Mỗi người làm trên nhánh riêng: `part1/...`, `part2/...`, `part3/...`.
*Tùy chọn, chỉ làm nếu `app.py` quá dài:* tách helper ra `ui/common.py`. Không bắt buộc cho buổi trình bày.

---

## Giai đoạn 0 · Setup (mọi người, chặn các bước sau)

| ID | Việc | Ai | Xong khi |
|---|---|---|---|
| S0.1 | Clone repo, tạo venv, `pip install -r requirements.txt` | A, B, C | `streamlit run app.py` chạy được trên máy mỗi người |
| S0.2 | Kaggle token, tải dữ liệu thô vào `data/raw/` | A, B, C | Có `Country.csv`, `Series.csv`, `Indicators.csv` (có thể xóa `database.sqlite`) |
| S0.3 | Viết `SETUP.md`: lệnh cho cả macOS/Linux và Windows, lỗi thường gặp | **A** | Một người khác làm theo từ máy trắng mà không cần hỏi thêm |
| S0.4 | **Gắn 3 trang vào nav:** `st.navigation` chia 2 nhóm "Câu chuyện" (`page_part1..3`, tạm thời rỗng) và "Khám phá" (5 trang cũ giữ nguyên) | **C** | App chạy như cũ, có thêm 3 mục trong nhóm Câu chuyện. Khoảng 15 dòng code |
| S0.5 | **Hợp đồng dữ liệu:** liệt kê tên cột, đơn vị, kiểu dữ liệu của `panel`/`snapshot`, đặt trong `wdi/etl.py` dưới dạng hằng số `SCHEMA` | **A** | B và C import `SCHEMA` được, không phải đoán tên cột |
| S0.6 | **Thêm 3 helper nhỏ** vào phần design system có sẵn: `VN_COLOR`, `takeaway()`, `bridge()`, `method_box()` (có thể dựa trên `hero`/`section`/`.insight` CSS sẵn có) | **C** | A và B gọi được ngay trong hàm trang |

> S0.4–S0.6 chỉ là vài chục dòng; merge vào `main` trong ngày đầu, rồi chia nhánh làm phần riêng.

---

## Người A · Phần 1 WHAT: Setup, ETL, "Thế giới thay đổi thế nào"

### A1. Pipeline tiền xử lý (`wdi/etl.py`)
| ID | Việc | Nguồn | Xong khi |
|---|---|---|---|
| A1.1 | Extract: đọc chunk `Indicators.csv`, lọc 32 chỉ số | Notebook cell 6–7 | Chạy `python -m wdi.etl` ra cùng 247k dòng |
| A1.2 | Transform: tách 214 nước khỏi 33 aggregate; gộp nhóm High income; kiểm tra trùng, giá trị vô hạn, miền giá trị; gắn cờ siêu lạm phát | Cell 10–12 | Log in ra: số dòng bị loại, 29 năm gắn cờ |
| A1.3 | Reshape: long → wide; nội suy ≤ 3 năm, không ngoại suy; snapshot 2005–2014 | Cell 17–18 | File ra **khớp** `app_data/*.csv.gz` hiện tại (viết test so sánh) |
| A1.4 | Xuất thêm `coverage.csv` (chỉ số × thập kỷ) và `balanced_panel` (chỉ các nước có đủ số liệu) | Cell 15 + mới | Trang Phần 1 đọc được hai file này |
| A1.5 | Ghi ra `data/processed/` và `app_data/*.gz` | | Notebook và app đều dùng chung kết quả |

### A2. Thực nghiệm (`wdi/story/part1.py`)
| ID | Việc | Xong khi |
|---|---|---|
| A2.1 | **E1.1** `sigma_convergence(vars, min_n=100)` → CV theo năm | Ra đúng số pilot: tuổi thọ 0,23 → 0,12; GDP 1,47 → 1,46 |
| A2.2 | **E1.2** `beta_convergence(var, start=1990, end=2014)` → β, CI 95 %, R² cho 4 chỉ số | Kết quả cho GDP trùng notebook (r = −0,16) |
| A2.3 | **E1.3** chạy E1.1 trên panel cân bằng và với trọng số dân số | Có bảng "chiều xu hướng giữ / đổi" |

### A3. Trang Streamlit `page_part1()` (dùng lại `page_overview`, `page_trends`, `group_trend`)
1. **Hero:** câu hỏi lớn + nghịch lý (tuổi thọ 30 → 21 năm và thu nhập 77× → 81×)
2. **Dữ liệu có tin được không?** Heatmap coverage + 5 quy tắc xử lý dữ liệu thiếu + kết quả E1.3 (trong `method_box`, mở ra khi cần)
3. **Cái gì hội tụ:** đường CV của E1.1, có nút chọn chỉ số
4. **Ngoại lệ Hạ Sahara:** xu hướng sinh suất theo khu vực
5. **Thu nhập không hội tụ:** 4 ô β của E1.2, Việt Nam màu đỏ
6. `bridge("Sức khỏe hội tụ trong khi thu nhập thì không. Vậy thu nhập quan trọng đến mức nào?")`

### A4. Deploy
Đẩy app lên Streamlit Community Cloud và kiểm tra app chạy chỉ với `app_data/` + `results/`. Làm thêm một bản video quay màn hình để dự phòng khi mất mạng.

---

## Người B · Phần 2 WHY: Mô hình, "Vai trò của thu nhập"

### B1. Tiền xử lý cho mô hình (mở rộng `wdi/models.py`, không phá code cũ)
| ID | Việc | Xong khi |
|---|---|---|
| B1.1 | Viết tài liệu cho `dataset()` hiện có: log transform (`LOG_FEATURES`), loại biến rò rỉ (`leak`), lọc coverage < 60 %, impute | Có docstring + một bảng trong `method_box` của trang |
| B1.2 | Thêm `feature_set="income_only" \| "all"` vào `Config` | `tests/test_models.py` cũ vẫn pass |
| B1.3 | Hàm `oof_predictions(theme, cfg)` trả về dự đoán ngoài mẫu và phần dư theo nước, trung bình qua 5 seed | Phần dư tuổi thọ của Việt Nam ≈ +10 năm |
| B1.4 | Chạy lại `run_models.py` (snapshot, 5 seed) để xác nhận `results/` hiện tại | Không lệch quá 0,01 R² |

### B2. Thực nghiệm (`wdi/story/part2.py` + `run_story.py`)
| ID | Việc | Xong khi |
|---|---|---|
| B2.1 | **E2.1** R² 3 lớp × 6 chủ đề (chỉ thu nhập / tất cả biến / mô hình tốt nhất) | `results/story/E2_1.csv`, mean ± std |
| B2.2 | **E2.2** bảng điểm phần dư: đơn vị gốc + phân vị + hạng, cho Việt Nam và 4 nước so sánh | Ra lại số pilot: tuổi thọ hạng 1/192, CO₂ ≈ 3× |
| B2.3 | **E2.3** fixed effects (khử trung bình theo nước và năm, viết bằng numpy, **không thêm thư viện**) | Hệ số trong-nước so với giữa-các-nước, kèm khoảng tin cậy |
| B2.4 | `run_story.py --part N` dùng chung cho cả 3 người, ghi ra `results/story/` | A và C chạy được phần của họ qua CLI |

### B3. Trang Streamlit `page_part2()` (dùng lại scatter của `page_compare` và biểu đồ R² của `page_models`)
1. **Hero:** "Giàu gấp 10 lần thì sống thêm ~10 năm, nhưng chưa phải tất cả"
2. **Mọi thứ đi cùng thu nhập:** heatmap tương quan, nút chọn cho phép xếp các chỉ số theo ρ với GDP
3. **Đường Preston:** scatter tương tác, có ô chọn nước để tô sáng (mặc định Việt Nam)
4. **R² 3 lớp (E2.1):** cột chồng; `method_box` ghi grouped CV, 5 seed, danh sách 19 mô hình
5. **Bảng điểm phần dư Việt Nam (E2.2):** dot plot, có ô chọn nước để khán giả hỏi "còn nước X thì sao?"
6. **Cái giá CO₂:** đường cong Kuznets + điểm Việt Nam ≈ 3×; E2.3 đặt trong expander "Giàu hơn khác giàu lên"
7. `bridge("Thu nhập không nói hết. Vậy xếp nhóm theo thu nhập có còn đúng không?")`

---

## Người C · Phần 3 SO WHAT: Khung app, phân cụm, "Việt Nam đứng ở đâu"

### C1. Hạ tầng app (nhẹ, vì app đã có)
S0.4 và S0.6 ở trên, cộng thêm:
- `VN_COLOR = "#c0392b"` và `highlight(fig, codes)` để Việt Nam đỏ thống nhất trên mọi trang
- `takeaway(text)`: khung tiêu đề dạng câu kết luận; `bridge(text)`: câu cầu nối ở cuối trang; `method_box(md)`: expander "Phương pháp & tiền xử lý"
- Chế độ **"Trình bày"** (toggle): ẩn sidebar và widget phụ, chữ to hơn, để dùng khi đứng thuyết trình

### C2. Tiền xử lý cho phân cụm (`wdi/story/part3.py`)
| ID | Việc | Xong khi |
|---|---|---|
| C2.1 | Tách phần tiền xử lý đang viết thẳng trong `page_clusters` thành `cluster_matrix(snap, vars, log_vars, min_cov=.7)`: log, impute median theo nhóm thu nhập, chuẩn hóa | Trang Clusters cũ gọi hàm mới và ra kết quả giống hệt |
| C2.2 | `fit_clusters(Z, algo, k, seed)` + sắp tên cụm theo GDP | Khớp 74 % với k = 4, K-means |
| C2.3 | `social_space(snap)`: các chỉ số xã hội, **bỏ GDP**, chuẩn hóa (dùng cho E3.2) | Có ma trận không chứa biến thu nhập |

### C3. Thực nghiệm
| ID | Việc | Xong khi |
|---|---|---|
| C3.1 | **E3.1** 3 thuật toán × 20 seed: ARI, % lần Việt Nam ở cụm "emerging", % khớp nhóm thu nhập | Có `results/story/E3_1.csv` + kết luận "vững / ranh giới" |
| C3.2 | **E3.2** 5 nước gần nhất theo GDP so với 5 nước gần nhất theo chỉ số xã hội | Bảng 2 cột tên nước |
| C3.3 | **E3.3** khoảng cách của Việt Nam tới median cụm "emerging"/"advanced", đơn vị độ lệch chuẩn, xếp hạng | Khoảng trống lớn nhất có tử vong trẻ em và thu nhập |

### C4. Trang Streamlit `page_part3()` (dùng lại toàn bộ pipeline của `page_clusters`)
1. **Hero:** "Nhìn bằng dữ liệu, không chỉ bằng thu nhập"
2. **Một trục phát triển:** PCA, PC1 = 63 %
3. **Cụm và nhóm thu nhập:** bản đồ + ma trận lệch (74 %) + độ vững từ E3.1
4. **Song sinh của Việt Nam (E3.2):** 2 cột tên nước + radar chart so sánh
5. **Khoảng trống (E3.3):** biểu đồ cột ngang, có ô chọn nhóm so sánh (emerging/advanced)
6. **Kết luận:** trả lời câu hỏi lớn, hàm ý (dạng gợi ý), giới hạn
7. **"Câu hỏi của bạn là gì?"**: dẫn sang mục Khám phá để demo trực tiếp trong Q&A

---

## Giai đoạn cuối · Tích hợp (cả nhóm)

| ID | Việc | Ai |
|---|---|---|
| I.1 | **Kiểm tra số liệu chéo:** mọi con số trên 3 trang trùng với `results/` và REPORT | A kiểm trang của B, B kiểm của C, C kiểm của A |
| I.2 | Cập nhật REPORT.md/README theo câu chuyện mới | Mỗi người viết mục của mình |
| I.3 | Tập dượt: mỗi trang ≤ 7 phút, chuyển trang bằng câu `bridge` | Cả nhóm |
| I.4 | Phương án dự phòng: video + ảnh chụp mỗi trang trong `docs/screenshots/` | A |
| I.5 | Chuẩn bị Q&A: mỗi người 3 câu hỏi khó cho phần của mình, kèm `method_box` để mở ra trả lời | Từng người |

## Thứ tự & phụ thuộc

```
Giai đoạn 0 (S0.1–S0.6) ─┬─► A1 ETL ──► A2 ──► A3 ─┐
                         ├─► B1 ──────► B2 ──► B3 ─┼─► Tích hợp (I.1–I.5) ──► A4 Deploy
                         └─► C2 ──────► C3 ──► C4 ─┘
```
- Sau Giai đoạn 0, B và C **không cần chờ** A1, vì họ dùng `app_data/` có sẵn. A1.3 chỉ cần đảm bảo file mới khớp file cũ.
- Thứ tự ưu tiên khi thiếu thời gian: A2.1, B2.1, B2.2, C3.2, C3.3 → trang app → A2.3, C3.1 → A2.2, B2.3.

## Định nghĩa "xong" cho mỗi trang
- [ ] Mỗi section mở đầu bằng `takeaway` là **một câu kết luận** có một con số neo
- [ ] Việt Nam màu `VN_COLOR` trên mọi biểu đồ
- [ ] Phần tiền xử lý và phương pháp nằm trong `method_box`, không chiếm màn hình chính
- [ ] Trang tải trong < 3 giây (đọc `results/story/`, không train lúc trình bày)
- [ ] Chạy đúng ở cả light và dark mode, và trên màn hình máy chiếu
- [ ] `tests/test_partN.py` pass
- [ ] Kết thúc trang bằng `bridge` (trang 3 kết thúc bằng phần kết luận)
