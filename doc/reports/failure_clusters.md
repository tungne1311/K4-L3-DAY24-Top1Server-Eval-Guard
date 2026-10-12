# Phân tích lỗi Phase A

Nhóm: Top1Server. Người phụ trách: Đỗ Thanh Tùng — 2A202602845 (người 1).

Nguồn: `artifacts/ragas_50q.json`; UTC run timestamp: `2026-10-12T14:35:46.690376+00:00`.

Models generation: `['gemini-3.5-flash-lite']`; evaluator: `['BAAI/bge-m3', 'gemini-3.5-flash-lite']`. M4 ghi model thực dùng, không lấy model judge làm evaluator.

50 answers có modes: {'llm': 50}. Chạy trên Python 3.11.9, Qdrant server v1.9.7, BGE-M3 và bge-reranker-v2-m3 từ cache. M1 đọc 25 Markdown và 1 PDF có text; hai PDF scan BCTC và Nghị định 13 không có lớp text được bỏ qua, chưa OCR. Giữ nguyên policy v2023/v2024 và mật khẩu v1/v2. M5 enrich thành công 106/106 chunks qua API, giữ đúng thứ tự; retrieval dùng BM25 + dense/RRF, rerank top 3 child chunks. Generation không nhận ground_truth.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
| --- | --- | --- | --- |
| faithfulness | 0.983333 | 0.722619 | 0.850000 |
| answer_relevancy | 0.906803 | 0.712103 | 0.752553 |
| context_precision | 0.866667 | 0.433333 | 0.683333 |
| context_recall | 0.783333 | 0.729167 | 0.690000 |
| avg_score | 0.885034 | 0.649305 | 0.743972 |

## Bottom 10 và giả thuyết chẩn đoán

| Rank | Id | Question | Distribution | Avg | Worst metric | Diagnosis | Suggested fix |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 33 | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | multi_hop | 0.2083 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 48 | Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không? | adversarial | 0.25 | faithfulness | LLM hallucinating; kiểm tra answer/context/reference về phiên bản, phủ định và điều kiện | Tighten system prompt, lower temperature; đối chiếu policy cũ/mới trước khi kết luận nguyên nhân |
| 3 | 30 | So sánh quyền lợi bảo hiểm giữa nhân viên thử việc và nhân viên chính thức. | multi_hop | 0.3393 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 4 | 39 | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | multi_hop | 0.4409 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 5 | 40 | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? | multi_hop | 0.4545 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 6 | 35 | Nhân viên Junior P1 có lương cơ bản 12 triệu vừa vào thử việc: nhận lương bao nhiêu và phụ cấp gì tháng đầu tiên? | multi_hop | 0.5418 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 7 | 49 | Theo chính sách nghỉ phép cũ (v2023), nhân viên được nghỉ bao nhiêu ngày? Còn chính sách nào đang có hiệu lực hiện tại? | adversarial | 0.5531 | context_precision | Too many irrelevant chunks; kiểm tra answer/context/reference về phiên bản, phủ định và điều kiện | Add reranking or metadata filter; đối chiếu policy cũ/mới trước khi kết luận nguyên nhân |
| 8 | 29 | Nhân viên tạm ứng 8 triệu, chưa thanh toán sau 30 ngày (quá hạn 15 ngày). Ai phê duyệt khoản này và phí phạt là bao nhiêu? | multi_hop | 0.5659 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 9 | 36 | Kết quả đánh giá hiệu suất tháng 6 và tháng 12 được dùng để làm gì khác nhau? | multi_hop | 0.5817 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 10 | 22 | Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT? | multi_hop | 0.5833 | answer_relevancy | Answer doesn't match question | Improve prompt template |

Diagnosis/fix ở bảng được giữ nguyên từ Task 3. Metric thấp chỉ gợi ý hướng điều tra; nguyên nhân được đối chiếu bằng answer, context và reference dưới đây.

## Matrix và nhóm yếu nhất

| Worst metric | factual | multi_hop | adversarial |
| --- | --- | --- | --- |
| faithfulness | 1 | 4 | 2 |
| answer_relevancy | 9 | 4 | 1 |
| context_precision | 4 | 11 | 4 |
| context_recall | 6 | 1 | 3 |

Nhóm yếu theo mean thấp nhất: **multi_hop**; mean=0.649305. Worst metric xuất hiện nhiều nhất: **context_precision** (19 câu). Tổng cột là 20/20/10 vì matrix đếm mọi câu, không có nghĩa mọi câu đều lỗi.

Nhóm multi_hop có mean thấp nhất (0.6493). context_precision là worst_metric nhiều nhất (19 câu). Matrix đếm mọi câu, không chứng minh mọi câu đều lỗi. Hướng kiểm chứng: Add reranking or metadata filter.

## Bằng chứng answer/context/reference

### Câu 33 — multi_hop

Question: Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu?

Answer: Không tìm thấy.

Reference: Phụ cấp tháng: ăn trưa 1.000.000 + điện thoại Manager 500.000 = 1.500.000 VNĐ. Phép năm v2024: 15 ngày cơ bản + 4 ngày thâm niên (12÷3=4) = 19 ngày phép.

Contexts thực: 1. Quy định về số ngày phép năm có lương cho nhân viên chính thức trong tài liệu nghi_phep_nam_v2024.md.

Mỗi nhân viên chính thức được hưởng **15 ngày phép năm** có lương, tăng từ 12 ngày so với chính sách năm 2023. Chính sách này thay thế hoàn toàn phiên bản 1.0 ban hành ngày 01/01/2023.

2. Đoạn văn nằm trong tài liệu nghi_phep_nam_v2023.md.

Mỗi nhân viên chính thức được hưởng **12 ngày phép năm** có lương. Số ngày phép được tính theo năm dương lịch từ 01/01 đến 31/12. Nhân viên vào công ty giữa năm sẽ được tính pro-rata theo số tháng làm việc thực tế.

3. Đoạn văn nằm trong phần thâm niên công tác của tài liệu nghi_phep_nam_v2024.md.

## Thâm niên công tác
Nhân viên có thâm niên từ **3 năm trở lên** được cộng thêm **1 ngày phép** cho mỗi 3 năm làm việc liên tục. Ví dụ: nhân viên 9 năm thâm niên được 18 ngày phép (15 + 3).

### Câu 48 — adversarial

Question: Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không?

Answer: Không tìm thấy.

Reference: KHÔNG. Nhân viên thử việc chưa được hưởng gói PVI. Chỉ được tham gia BHXH bắt buộc. Đây là negation trap — pipeline hay nhầm vì tài liệu PVI không đề cập rõ exclusion.

Contexts thực: 1. Đoạn văn nằm trong tài liệu thu_viec.md, phần đánh giá thử việc.

được hưởng gói bảo hiểm sức khỏe PVI.

## Đánh giá thử việc
Quản lý trực tiếp thực hiện đánh giá vào ngày thứ 30 (giữa kỳ) và ngày thứ 55 (cuối kỳ). Kết quả đánh giá quyết định việc ký hợp đồng chính thức.

2. Phần đầu của tài liệu chính sách bảo hiểm sức khỏe phiên bản 1.5 do phòng ban Nhân sự ban hành.

# Chính sách bảo hiểm sức khỏe
> Phiên bản: 1.5 | Ngày hiệu lực: 01/04/2024 | Phòng ban: Nhân sự

## Bảo hiểm cho nhân viên
Công ty cung cấp gói bảo hiểm sức khỏe toàn diện qua **PVI Insurance** cho tất cả nhân viên chính thức. Hạn mức bảo hiểm:

3. Đoạn văn mô tả mức đóng bảo hiểm và quy trình sử dụng bảo hiểm sức khỏe tại các cơ sở y tế.

viên đóng 50% qua khấu trừ lương hàng tháng.

## Quy trình sử dụng
Nhân viên xuất trình thẻ bảo hiểm PVI tại các bệnh viện/phòng khám trong danh sách liên kết. Trường hợp khám ngoài danh sách, nhân viên thanh toán trước và nộp hồ sơ bồi hoàn trong vòng 30

### Câu 30 — multi_hop

Question: So sánh quyền lợi bảo hiểm giữa nhân viên thử việc và nhân viên chính thức.

Answer: Dựa trên context được cung cấp:

* **Nhân viên thử việc:** Được tham gia bảo hiểm xã hội bắt buộc nhưng **chưa được hưởng** gói bảo hiểm sức khỏe PVI.
* **Nhân viên chính thức:** Context không đề cập cụ thể quyền lợi bảo hiểm của nhân viên chính thức (chỉ nêu thông tin về lương).

Vì vậy, chỉ có thể xác định quyền lợi bảo hiểm của nhân viên thử việc, không có đủ thông tin trong context để so sánh đầy đủ với nhân viên chính thức.

Reference: Nhân viên thử việc: chỉ được tham gia BHXH bắt buộc, KHÔNG được hưởng gói bảo hiểm sức khỏe PVI. Nhân viên chính thức: được hưởng BHXH + gói PVI hạn mức 200 triệu/năm (nội trú, ngoại trú, nha khoa).

Contexts thực: 1. Đoạn văn quy định về quyền lợi trong thời gian thử việc của nhân viên.

## Quyền lợi trong thử việc
Nhân viên thử việc **KHÔNG được nghỉ phép năm**. Trường hợp cần nghỉ việc riêng, nhân viên thử việc phải xin nghỉ không lương và được trưởng phòng phê duyệt. Nhân viên thử việc được tham gia bảo hiểm xã hội bắt buộc nhưng chưa

2. Đoạn văn nằm trong tài liệu thu_viec.md, phần đánh giá thử việc.

được hưởng gói bảo hiểm sức khỏe PVI.

## Đánh giá thử việc
Quản lý trực tiếp thực hiện đánh giá vào ngày thứ 30 (giữa kỳ) và ngày thứ 55 (cuối kỳ). Kết quả đánh giá quyết định việc ký hợp đồng chính thức.

3. Đoạn văn quy định về mức lương thử việc và việc điều chỉnh lương khi ký hợp đồng chính thức trong tài liệu bang_luong_2024.md.

## Lương thử việc
Nhân viên trong thời gian thử việc được nhận **85% lương** của cấp bậc tương ứng. Sau khi hoàn thành thử việc, lương được điều chỉnh lên 100% kể từ ngày ký hợp đồng chính thức.

### Câu 39 — multi_hop

Question: So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA.

Answer: Dựa trên context được cung cấp:

* **Độ dài tối thiểu:**
  * Phiên bản 2.0 yêu cầu mật khẩu có tối thiểu **12 ký tự** (Context không cung cấp thông tin về độ dài tối thiểu của phiên bản 1.0).
* **Thời hạn đổi:**
  * Không tìm thấy.
* **MFA (Xác thực đa yếu tố):**
  * Tất cả nhân viên **bắt buộc** kích hoạt MFA cho tài khoản email, VPN và các hệ thống nội bộ. Các phương thức MFA được chấp nhận gồm: ứng dụng Authenticator (ưu tiên), SMS OTP, hoặc YubiKey. (Context không đề cập đến MFA trong phiên bản 1.0).

Reference: v1.0 (đã hết hiệu lực): tối thiểu 8 ký tự, đổi mỗi 90 ngày, không yêu cầu MFA. v2.0 (hiện hành): tối thiểu 12 ký tự, đổi mỗi 120 ngày, MFA bắt buộc cho tất cả: email, VPN và hệ thống nội bộ.

Contexts thực: 1. Đoạn văn mở đầu tài liệu về chính sách mật khẩu phiên bản cũ (v1.0).

# Chính sách mật khẩu (Phiên bản cũ)
> Phiên bản: 1.0 | Ngày hiệu lực: 01/01/2022 | Phòng ban: CNTT | Trạng thái: ĐÃ THAY THẾ bởi v2.0

2. Đoạn văn nằm trong tài liệu mat_khau_v2.md, phần Xác thực đa yếu tố (MFA).

khích sử dụng passphrase dài hơn 16 ký tự.

## Xác thực đa yếu tố (MFA)
Tất cả nhân viên **bắt buộc** kích hoạt MFA cho tài khoản email, VPN và các hệ thống nội bộ. Phương thức MFA được chấp nhận: ứng dụng Authenticator (ưu tiên), SMS OTP, hoặc YubiKey.

3. Đoạn văn nằm trong phần yêu cầu mật khẩu của chính sách mật khẩu phiên bản 2.0.

# Chính sách mật khẩu (Phiên bản hiện hành)
> Phiên bản: 2.0 | Ngày hiệu lực: 01/07/2024 | Phòng ban: CNTT

## Yêu cầu mật khẩu
Mật khẩu phải có tối thiểu **12 ký tự**, bao gồm ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt (!@#$%^&*). Khuyến

### Câu 40 — multi_hop

Question: Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách?

Answer: Dựa trên context:

**Nên làm:**
* Báo cáo trong vòng 1 giờ qua email **helpdesk@cty.vn** hoặc hotline CNTT nội bộ (ext. 9999) khi phát hiện hoặc nghi ngờ sự cố bảo mật.

**Không nên làm:**
* Tuyệt đối không tự ý xử lý malware hoặc tìm cách khắc phục mà không có sự hướng dẫn của đội CNTT.

Reference: NÊN: báo cáo ngay trong vòng 1 giờ qua helpdesk@cty.vn hoặc hotline CNTT (ext. 9999). KHÔNG được: tự xử lý malware, xóa dấu vết, hoặc chia sẻ thông tin sự cố rộng rãi. Không báo cáo hoặc tự xử lý = vi phạm nghiêm trọng, có thể bị kỷ luật.

Contexts thực: 1. Quy định xử lý khi phát hiện sự cố bảo mật trong tài liệu bao_mat_su_co.md.

Khi phát hiện hoặc nghi ngờ sự cố bảo mật, nhân viên **phải báo cáo trong vòng 1 giờ** qua email **helpdesk@cty.vn** hoặc hotline CNTT nội bộ (ext. 9999). Tuyệt đối **không tự ý xử lý malware** hoặc tìm cách khắc phục mà không có sự hướng dẫn của đội CNTT.

2. Đoạn văn nằm trong tài liệu phان_loai_du_lieu.md, mục phân loại dữ liệu tối mật và chế tài vi phạm.

- **Tối mật**: mã hóa end-to-end, truy cập cần phê duyệt Giám đốc CNTT, log tất cả truy cập

## Vi phạm
Vi phạm chính sách phân loại dữ liệu sẽ bị xử lý kỷ luật theo Quy chế kỷ luật công ty, mức cao nhất là sa thải và chịu trách nhiệm pháp lý.

3. Phần đầu của tài liệu chính sách thử việc quy định về thời gian thử việc.

# Chính sách thử việc
> Phiên bản: 1.2 | Ngày hiệu lực: 01/01/2024 | Phòng ban: Nhân sự

## Thời gian thử việc
Thời gian thử việc tiêu chuẩn là **60 ngày** kể từ ngày bắt đầu làm việc. Đối với vị trí quản lý cấp cao (Manager trở lên), thời gian thử việc có

### Câu 35 — multi_hop

Question: Nhân viên Junior P1 có lương cơ bản 12 triệu vừa vào thử việc: nhận lương bao nhiêu và phụ cấp gì tháng đầu tiên?

Answer: Dựa trên context, nhân viên thử việc được nhận **85% mức lương** của cấp bậc tương ứng và **phụ cấp ăn trưa được áp dụng đầy đủ từ ngày đầu tiên**.

Với mức lương gross của Junior (P1-P2) là 12.000.000 - 20.000.000 VNĐ/tháng, nhân viên Junior P1 có lương cơ bản 12 triệu sẽ nhận được lương thử việc là 85% của 12.000.000 VNĐ (tương ứng 10.200.000 VNĐ) và phụ cấp ăn trưa trong tháng đầu tiên.

Reference: Lương thử việc: 85% × 12.000.000 = 10.200.000 VNĐ. Phụ cấp ăn trưa áp dụng từ ngày đầu tiên: 1.000.000 VNĐ. Không có phụ cấp điện thoại (cấp Junior). Tổng nhận: 11.200.000 VNĐ.

Contexts thực: 1. Đoạn văn quy định về thời gian, mức lương và phụ cấp trong giai đoạn thử việc.

thể kéo dài đến 90 ngày.

## Lương thử việc
Nhân viên thử việc được nhận **85% mức lương** của cấp bậc tương ứng theo bảng lương công ty. Phụ cấp ăn trưa được áp dụng đầy đủ từ ngày đầu tiên.

2. Đoạn văn quy định về mức lương thử việc và việc điều chỉnh lương khi ký hợp đồng chính thức trong tài liệu bang_luong_2024.md.

## Lương thử việc
Nhân viên trong thời gian thử việc được nhận **85% lương** của cấp bậc tương ứng. Sau khi hoàn thành thử việc, lương được điều chỉnh lên 100% kể từ ngày ký hợp đồng chính thức.

3. Phần khung lương theo cấp bậc Junior trong tài liệu bảng lương năm 2024.

# Bảng lương năm 2024
> Phiên bản: 3.0 | Ngày hiệu lực: 01/01/2024 | Phòng ban: Nhân sự & Tài chính

## Khung lương theo cấp bậc
| Cấp bậc | Lương gross (VNĐ/tháng) |
|----------|--------------------------|
| Junior (P1-P2) | 12.000.000 - 20.000.000 |

### Câu 49 — adversarial

Question: Theo chính sách nghỉ phép cũ (v2023), nhân viên được nghỉ bao nhiêu ngày? Còn chính sách nào đang có hiệu lực hiện tại?

Answer: Theo chính sách nghỉ phép cũ (v2023), nhân viên được hưởng 12 ngày phép năm có lương.

Chính sách đang có hiệu lực hiện tại là chính sách theo tài liệu `nghi_phep_nam_v2024.md` (mỗi nhân viên chính thức được hưởng 15 ngày phép năm có lương, thay thế hoàn toàn phiên bản 1.0 ban hành ngày 01/01/2023).

Reference: Chính sách cũ v2023 (ĐÃ HẾT HIỆU LỰC): 12 ngày phép, thêm 1 ngày/5 năm thâm niên. Chính sách HIỆN HÀNH v2024: 15 ngày cơ bản, thêm 1 ngày/3 năm thâm niên. Pipeline tốt phải nhận ra v2024 là bản hiệu lực.

Contexts thực: 1. Đoạn văn nằm trong tài liệu nghi_phep_nam_v2023.md.

Mỗi nhân viên chính thức được hưởng **12 ngày phép năm** có lương. Số ngày phép được tính theo năm dương lịch từ 01/01 đến 31/12. Nhân viên vào công ty giữa năm sẽ được tính pro-rata theo số tháng làm việc thực tế.

2. Quy định về số ngày phép năm có lương cho nhân viên chính thức trong tài liệu nghi_phep_nam_v2024.md.

Mỗi nhân viên chính thức được hưởng **15 ngày phép năm** có lương, tăng từ 12 ngày so với chính sách năm 2023. Chính sách này thay thế hoàn toàn phiên bản 1.0 ban hành ngày 01/01/2023.

3. Đoạn văn nằm trong tài liệu nghi_phep_nam_v2023.md thuộc phần Quy định sử dụng.

## Quy định sử dụng
Phép năm phải được đăng ký trước ít nhất 3 ngày làm việc qua hệ thống HR Portal. Nghỉ phép từ 3 ngày trở lên cần được trưởng phòng phê duyệt. Phép năm không sử dụng hết có thể chuyển tối đa 5 ngày sang năm sau, hết hạn vào 31/03 năm kế

### Câu 29 — multi_hop

Question: Nhân viên tạm ứng 8 triệu, chưa thanh toán sau 30 ngày (quá hạn 15 ngày). Ai phê duyệt khoản này và phí phạt là bao nhiêu?

Answer: Dựa trên context:

* **Ai phê duyệt:** Khoản tạm ứng từ 5.000.000 VNĐ trở lên cần thêm phê duyệt của **Kế toán trưởng** (và trưởng phòng).
* **Phí phạt:** **2%/tháng** trên số tiền chưa hoàn ứng.

Reference: Phê duyệt: 8 triệu (≥5 triệu) cần Trưởng phòng + Kế toán trưởng. Phí phạt quá hạn 15 ngày: 2%/tháng × 8.000.000 × (15/30) = 80.000 VNĐ. Không được tạm ứng mới cho đến khi hoàn ứng.

Contexts thực: 1. Phần phạt quá hạn trong tài liệu tam_ung.md.

## Phạt quá hạn
Khoản tạm ứng chưa thanh toán sau 15 ngày sẽ bị tính phí **2%/tháng** trên số tiền chưa hoàn ứng. Phí này được khấu trừ vào lương tháng kế tiếp. Nhân viên có khoản tạm ứng chưa thanh toán sẽ không được phê duyệt tạm ứng mới.

2. Phần phê duyệt trong tài liệu tam_ung.md

## Phê duyệt
Tạm ứng dưới 5.000.000 VNĐ: trưởng phòng phê duyệt. Từ 5.000.000 VNĐ trở lên: cần thêm phê duyệt Kế toán trưởng.

3. Đoạn văn nằm trong tài liệu tam_ung.md, phần thời hạn thanh toán.

phí dự án.

## Thời hạn thanh toán
Khoản tạm ứng phải được thanh toán (nộp chứng từ hoàn ứng) trong vòng **15 ngày** kể từ ngày nhận tiền. Trường hợp công tác dài ngày, thời hạn tính từ ngày kết thúc chuyến công tác.

### Câu 36 — multi_hop

Question: Kết quả đánh giá hiệu suất tháng 6 và tháng 12 được dùng để làm gì khác nhau?

Answer: Dựa trên context:
- Kết quả đánh giá giữa năm (tháng 6) dùng để điều chỉnh mục tiêu.
- Kết quả cuối năm (tháng 12) dùng để xét tăng lương và thưởng.

Reference: Tháng 6 (giữa năm): dùng để điều chỉnh mục tiêu cho nửa năm còn lại. Tháng 12 (cuối năm): dùng để xét tăng lương và tính thưởng Tết. Cả hai đều dựa trên KPI 70% + Peer review 30%.

Contexts thực: 1. Phần Chu kỳ đánh giá thuộc tài liệu Quy trình đánh giá hiệu suất phiên bản 2.0.

# Quy trình đánh giá hiệu suất
> Phiên bản: 2.0 | Ngày hiệu lực: 01/06/2024 | Phòng ban: Nhân sự

## Chu kỳ đánh giá
Đánh giá hiệu suất được thực hiện **2 lần/năm** vào tháng 6 và tháng 12. Kết quả đánh giá giữa năm (tháng 6) dùng để điều chỉnh mục tiêu,

2. Đoạn văn nằm trong phần cơ cấu đánh giá của tài liệu danh_gia_hieu_suat.md.

kết quả cuối năm (tháng 12) dùng để xét tăng lương và thưởng.

## Cơ cấu đánh giá
- **KPI cá nhân**: chiếm **70%** tổng điểm, do quản lý trực tiếp đánh giá dựa trên mục tiêu đã thống nhất đầu kỳ

3. Đoạn văn nằm trong phần tiêu chí tính thưởng Tết của tài liệu thuong_tet.md.

6 tháng được hưởng pro-rata theo số tháng làm việc thực tế.

## Tiêu chí tính thưởng
Mức thưởng Tết được tính dựa trên hai yếu tố chính:
- **Kết quả đánh giá hiệu suất cá nhân** (trọng số 60%): dựa trên kết quả đánh giá cuối năm

### Câu 22 — multi_hop

Question: Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT?

Answer: Dựa trên context, không tìm thấy thông tin cụ thể về người phê duyệt đối với đơn hàng mua laptop 30 triệu (vì bảng thẩm quyền phê duyệt chỉ đề cập đơn hàng dưới 5.000.000 VNĐ là Trưởng phòng, và không có thông tin về nhân viên mới).

Tuy nhiên, về yêu cầu từ phòng CNTT: Mua sắm thiết bị CNTT (laptop, server, phần mềm) **cần có xác nhận của phòng CNTT về cấu hình kỹ thuật trước khi đề xuất**.

Reference: Laptop 30 triệu nằm trong khoảng 5-50 triệu nên cần Giám đốc phòng ban (Director) phê duyệt. Cần đính kèm ít nhất 3 báo giá (trên 10 triệu). Mua sắm thiết bị CNTT cần xác nhận cấu hình kỹ thuật từ phòng CNTT trước khi đề xuất.

Contexts thực: 1. Phần lưu ý đặc biệt trong tài liệu mua_sam.md

## Lưu ý đặc biệt
Mua sắm thiết bị CNTT (laptop, server, phần mềm) cần có xác nhận của phòng CNTT về cấu hình kỹ thuật trước khi đề xuất. Đơn hàng khẩn cấp có thể bỏ qua yêu cầu 3 báo giá nhưng phải có giải trình bằng văn bản.

2. Đoạn văn nằm trong phần thẩm quyền phê duyệt của quy trình mua sắm.

# Quy trình mua sắm
> Phiên bản: 2.2 | Ngày hiệu lực: 01/04/2024 | Phòng ban: Hành chính & Tài chính

## Thẩm quyền phê duyệt
| Giá trị đơn hàng | Người phê duyệt |
|-------------------|-----------------|
| Dưới **5.000.000 VNĐ** | Trưởng phòng (Manager) |

3. Đoạn văn nằm trong tài liệu hoan_chi_dao_tao.md nói về quy định chi trả chi phí đào tạo bên ngoài cho nhân viên.

Công ty chi trả chi phí đào tạo bên ngoài (chứng chỉ, khóa học dài hạn, hội thảo) cho nhân viên có **thâm niên từ 1 năm trở lên**. Chi phí được tài trợ tối đa **30.000.000 VNĐ/khóa** và cần phê duyệt của Giám đốc phòng ban.

## Phân tích nguyên nhân và hướng sửa

- **Coverage multi-hop:** câu 21 chỉ retrieve ba chunks nghỉ phép, không có bảng lương Senior. Answer tính đúng 18 ngày nhưng không trả lời được 20–35 triệu. Câu 33 cũng retrieve nghỉ phép, thiếu phụ cấp, rồi từ chối toàn bộ dù context đủ tính 19 ngày. Cần tách subqueries theo ý, kết hợp chứng cứ giữa các tài liệu và trả lời phần đã có evidence.
- **Chunking bảng và phủ định:** câu 22 lấy đầu bảng mua sắm chỉ có dòng dưới 5 triệu; thiếu dòng Director cho 5–50 triệu và yêu cầu ba báo giá. Câu 48 lấy fragment “được hưởng gói bảo hiểm sức khỏe PVI.” nhưng nguồn `data/thu_viec.md:11` thực tế viết “chưa được hưởng”. Answer abstain, không trả lời phủ định mà reference yêu cầu. Cần giữ nguyên hàng bảng/câu phủ định, retrieve parent theo parent_id và thử lại cùng fixtures; không xóa policy cũ.
- **Generation và quy ước tính toán:** câu 24 và 29 contexts có thời hạn 15 ngày, phí 2%/tháng và quy trình phê duyệt. Answers chỉ nhắc mức phí, chưa tính số tiền 50.000/80.000 VNĐ. Reference dùng pro-rata với tháng 30 ngày; công thức chia 30 không được nêu rõ trong chunks. Đây vừa là thiếu thực hiện tính toán vừa là giả định của reference cần xác minh, không thể kết luận hoàn toàn do retrieval. Cần tool tính toán với quy ước tài chính được nêu rõ.
- **Version conflict:** câu 41 trả cả 12 và 15 ngày, câu 42 trả cả mốc 5 và 3 năm nhưng không chốt hiện hành; đây là lỗi ưu tiên hiệu lực ở generation khi contexts chứa cả hai bản. Câu 43 trả 12 ký tự theo v2; câu 44 chọn 120 ngày và nhận ra v1 đã thay thế; câu 45 yêu cầu MFA; câu 49 nhận diện v2024 đang hiệu lực nhưng không nêu chu kỳ thâm niên. Nên truyền version/effective_date/status từ metadata, yêu cầu câu trả lời chốt bản đang hiệu lực, đồng thời cho phép truy vấn lịch sử như câu 49.
- **Phủ định/điều kiện:** câu 46 trả “Không”, câu 47 không tự xử lý malware, câu 50 không dùng VPN cá nhân: đúng hướng chính của reference. Câu 48 là trường hợp thiếu evidence phủ định đầy đủ ở ranh giới chunk. Câu 30 retrieve được quyền lợi thử việc nhưng thiếu PVI nhân viên chính thức nên so sánh chưa hoàn chỉnh. Không đánh đồng tất cả adversarial với cùng một nguyên nhân.
- **Cách đọc metric:** faithfulness kiểm tra hỗ trợ từ contexts, answer_relevancy dựa trên câu hỏi sinh ngược và cosine BGE-M3; hai metric không thay accuracy/reference compliance. Context precision/recall đánh giá chứng cứ truy xuất, không trực tiếp đo tính đầy đủ của answer. Default diagnosis ở Task 3 là giả thuyết; ví dụ abstention không tự chứng minh hallucination. Các nhận xét trên đối chiếu answer/context/reference và nguồn corpus, không dùng score thấp để suy nguyên nhân.

## Đối chiếu riêng 10 câu yếu

| Id | Quan sát từ answer/contexts/reference | Hướng sửa cần kiểm chứng |
| --- | --- | --- |
| 33 | Answer abstain toàn bộ; contexts chỉ nghỉ phép, có thể tính 19 ngày nhưng thiếu phụ cấp. Faithfulness/relevancy=0 không tự chứng minh hallucination. | Tách phụ cấp và nghỉ phép thành hai truy vấn; trả lời phần có evidence. |
| 48 | Fragment PVI mất “chưa”, answer abstain; nguồn thử việc nêu phủ định rõ. | Chunk theo câu/đoạn và retrieve parent giữ trọn phủ định. |
| 30 | Có quyền lợi thử việc nhưng thiếu PVI nhân viên chính thức; answer trả lời một phần rồi noncommittal, answer_relevancy=0. | Retrieve cả thử việc và bảo hiểm nhân viên chính thức, kiểm chứng từng vế so sánh. |
| 39 | Context v1 chỉ tiêu đề; v2 có độ dài/MFA nhưng không chu kỳ đổi. Answer thiếu các thông số v1 và 90/120 ngày. | Retrieve toàn bộ mục yêu cầu mật khẩu ở cả hai phiên bản cho truy vấn lịch sử. |
| 40 | Answer nêu báo cáo một giờ và không tự xử lý, được context 1 hỗ trợ; thiếu cấm xóa dấu vết/chia sẻ rộng. Faithfulness=0.4 cần audit NLI vì chưa thấy bằng chứng cho mọi kết luận “hallucinating” từ default diagnosis. | Bổ sung chứng cứ hành động cấm, xem lại phân rã statement/NLI và human review. |
| 35 | Tính đúng 10,2 triệu; contexts thiếu mức phụ cấp 1 triệu và quy định không phụ cấp điện thoại Junior. | Retrieve policy phụ cấp, trả tổng 11,2 triệu chỉ khi đủ chứng cứ cho từng khoản. |
| 49 | Nhận diện v2024 đang hiệu lực và đúng 12/15 ngày; contexts/answer thiếu chu kỳ thâm niên 5/3 năm trong reference. | Retrieve thêm mục thâm niên; giữ truy vấn lịch sử và current policy rõ ràng. |
| 29 | Context_recall=1 nhưng context_precision=0; contexts có phê duyệt/2%/thời hạn. Answer thiếu số phạt 80.000 và điều kiện không tạm ứng mới. | Thêm tính toán, xác minh quy ước pro-rata; audit classifier precision, không kết luận toàn bộ contexts vô ích. |
| 36 | Answer đúng mục đích đánh giá tháng 6/tháng 12 theo contexts 1–2; thiếu Peer review 30% so với reference. Precision=0 chưa phản ánh đủ chứng cứ ý chính đang có. | Ưu tiên chứng cứ trực tiếp, bổ sung cơ cấu đánh giá nếu cần; human review metric/reference compliance. |
| 22 | Context_recall=1/3; answer nêu đúng xác nhận CNTT nhưng thiếu Director và ba báo giá vì bảng bị cắt. Precision gần 1 là average precision của những context được judge coi hữu ích, không có nghĩa cả ba chunks đều liên quan hoặc evidence đã đầy đủ. | Giữ bảng/mục mua sắm thành parent, retrieve đủ các điều kiện cho đơn 30 triệu. |

Các score context_precision bằng 0 ở 29, 36, 40, 49 cần được đọc cùng nội dung: vẫn có evidence trực tiếp cho một phần câu hỏi. RAGAS dùng LLM classifier trên từng context và reference rồi tính average precision; judgment có thể khắt khe với evidence từng phần hoặc thiếu ổn định. Không đổi điểm đã đo, không loại câu làm metric xấu. Cần lưu/audit các statement/verdict traces và chấm thêm tập độc lập để kiểm tra giả thuyết này; lượt này chưa có bằng chứng xác định chính xác vì sao từng verdict sai lệch.

## Bẫy adversarial và giới hạn

Adversarial mean=0.743972; factual mean=0.885034. So sánh mean không tự chứng minh pipeline nhận ra version conflict hoặc phủ định. Một lượt 50 câu, model evaluator tự động và metric phân rã có dao động. Không đổi answers, ground_truth hoặc bộ fixture để tăng điểm. Các PDF scan chưa OCR và việc chỉ lấy top 3 child chunks giới hạn coverage. Cải tiến cần đánh giá lại cùng dữ liệu và báo cáo cả thay đổi chất lượng lẫn chi phí.

RAGAS mean toàn bộ 50 câu (trung bình đều bốn metric): **0.762530**. RAGAS 0.1.22 chạy bốn workers dùng chung rate limiter 12 requests/phút; max output 4096 tokens. Adapter faithfulness giữ cả câu không kết thúc bằng dấu chấm (6 answers gặp trường hợp này), dùng nguyên prompt phân rã/NLI và công thức RAGAS. Answers đã lưu không bị sửa; missing/NaN không được thay bằng số giả.
