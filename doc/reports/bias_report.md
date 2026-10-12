# Đánh giá LLM Judge Phase B

Nhóm: Top1Server. Người phụ trách: Đỗ Thanh Tùng — 2A202602845 (người 1).

Nguồn: `artifacts/judge_results.json`; UTC run timestamp: `2026-10-12T14:37:51.167239+00:00`.

Models generation: `['gemini-3.5-flash-lite']`; judge: `['gemini-3.5-flash-lite']`.

## Năm cặp A/B và hai lượt

Nguồn cố định: A=`artifacts/answers_50q.json:answer`; B=`fixtures/human_labels_10q.json:model_answer`; reference=`fixtures/test_set_50q.json:ground_truth`. Ids 1, 5, 12, 21, 41. Hai lượt nhận cùng question/reference, lượt hai đảo candidates; winner và scores đã quy về A/B gốc. Final chỉ chọn winner khi hai lượt đồng thuận; bất đồng là tie.

| Id | Candidate A | Candidate B | Pass 1 | Pass 2 (đã quy đổi) | Final | Consistent |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Nhân viên được nghỉ 3 ngày làm việc khi kết hôn. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | B | B | B | True |
| 5 | Tổng Giám đốc (CEO) | Cần Giám đốc phòng ban phê duyệt. | A | A | A | True |
| 12 | 1 tháng lương | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | tie | tie | tie | True |
| 21 | Một nhân viên có 9 năm thâm niên được **18 ngày phép** (15 + 3). <br><br>Không tìm thấy thông tin về mức lương. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | B | B | B | True |
| 41 | Dựa trên context:<br>- Nhân viên chính thức theo tài liệu năm 2023 được hưởng **12 ngày phép năm**.<br>- Nhân viên chính thức theo tài liệu năm 2024 được hưởng **15 ngày phép năm**. | Nhân viên được nghỉ 12 ngày phép năm. | B | A | tie | False |

| Id | Reasoning pass 1 | Scores pass 1 | Reasoning pass 2 (nhãn nguyên lượt swap) | Scores pass 2 (quy đổi) |
| --- | --- | --- | --- | --- |
| 1 | Cả hai câu trả lời đều thiếu ý 'không trừ vào phép năm' so với reference, tuy nhiên câu B cung cấp ý 'có lương' quan trọng hơn câu A. | {'A': 0.6, 'B': 0.8} | Câu A nêu đúng thông tin 'có lương' theo reference, trong khi câu B thiếu ý quan trọng này. | {'A': 0.5, 'B': 1.0} |
| 5 | Reference quy định đơn hàng trên 50 triệu cần Tổng Giám đốc (CEO) phê duyệt. Thiết bị trị giá 55 triệu thuộc trường hợp này, nên câu trả lời của A là chính xác, còn B sai. | {'A': 1.0, 'B': 0.0} | Reference quy định đơn hàng trên 50 triệu cần Tổng Giám đốc (CEO) phê duyệt, thiết bị 55 triệu thuộc trường hợp này. Câu trả lời B chính xác theo reference, trong khi câu trả lời A sai. | {'A': 1.0, 'B': 0.0} |
| 12 | Cả hai câu trả lời đều cung cấp chính xác thông tin "1 tháng lương" theo đúng reference, đáp ứng đủ ý thiết yếu và không bịa đặt thêm thông tin sai lệch. | {'A': 1.0, 'B': 1.0} | Cả hai câu trả lời đều cung cấp chính xác thông tin về mức thưởng Tết tối thiểu là 1 tháng lương dựa trên reference. Cả hai đều ngắn gọn và đúng trọng tâm. | {'A': 1.0, 'B': 1.0} |
| 21 | Câu trả lời B trả lời đầy đủ cả hai ý theo reference (số ngày phép và mức lương), trong khi câu A bỏ sót thông tin về mức lương. | {'A': 0.5, 'B': 1.0} | A trả lời đúng và đầy đủ cả hai ý theo reference (18 ngày phép và mức lương 20-35 triệu). B bỏ sót thông tin về mức lương. | {'A': 0.5, 'B': 1.0} |
| 41 | Reference yêu cầu ưu tiên chính sách v2024 HIỆN HÀNH (15 ngày cơ bản) và coi v2023 là đã bị thay thế. Cả hai câu trả lời đều chưa hoàn hảo vì thiếu phần thâm niên, nhưng B đưa ra con số 12 ngày (không đúng với phiên bản hiện hành được yêu cầu ưu tiên), trong khi A đưa ra cả hai và nhầm lẫn coi chính sách 2023 vẫn áp dụng. Tuy nhiên, nếu xét theo yêu cầu ưu tiên v2024, A có nhắc đến 15 ngày nhưng lại liệt kê cả 2 chính sách cũ. Đợi chút, theo chuẩn RAG, A trả lời lan man đưa cả chính sách cũ đã bị thay thế vào làm nhiễu. B chỉ nêu 12 ngày là sai phiên bản hiện hành (2024). Cả hai đều chưa tốt, nhưng A cung cấp đúng con số 15 ngày của bản v2024 (dù kèm bản cũ). Do prompt yêu cầu ưu tiên v2024, A có nhắc tới 15 ngày. B sai hoàn toàn theo v2024. Do đó A tốt hơn một chút dù trình bày dài dòng. | {'A': 0.5, 'B': 0.0} | Reference yêu cầu ưu tiên chính sách v2024 (15 ngày cơ bản) và loại bỏ chính sách v2023 đã bị thay thế. Answer A trả lời theo chính sách cũ v2023 (12 ngày) nên sai. Answer B có đề cập đến cả 2 năm nhưng nêu đúng số ngày của chính sách v2024 theo yêu cầu. | {'A': 0.8, 'B': 0.0} |

Position inconsistency count/rate: **1/5 = 0.200000**. Verbosity win rate: **0.333333**; details: `{'a_wins_a_longer': 0, 'b_wins_b_longer': 1, 'total_decisive': 3}`. Độ dài tính bằng ký tự; tie không vào mẫu số verbosity, độ dài bằng nhau không tính longer winner.

Không nhất quán khi đảo vị trí: 1/5; winner dài hơn: 1/3 case decisive (độ dài tính bằng ký tự). Không nhất quán có thể do dao động model; winner dài hơn có thể vì đủ ý hơn. Cần đọc reasoning/reference trước kết luận bias. Mẫu nhỏ, chưa đủ suy rộng.

## Đối chiếu nội dung và bias

- **Cặp 1:** B thắng cả hai lượt vì có ý “có lương”, A chỉ nói ba ngày nghỉ. B dài hơn nhưng chứa thông tin có ý nghĩa; chưa thể quy winner về độ dài. Cả hai vẫn thiếu “không trừ vào phép năm”. Scores của cùng candidate thay đổi giữa hai lượt, dù winner đồng thuận.
- **Cặp 5:** A ngắn hơn vẫn thắng 2/2 nhờ chọn đúng CEO cho thiết bị 55 triệu; B chọn Director sai ngưỡng. Đây là ví dụ judge ưu tiên tính đúng thay vì độ dài.
- **Cặp 12:** tie 2/2; cả hai trả đúng một tháng lương. B diễn đạt thành câu dài hơn nhưng không được thưởng thắng chỉ vì dài hơn.
- **Cặp 21:** B thắng 2/2 vì đủ cả 18 ngày phép và lương 20–35 triệu; A thiếu lương. B còn ngắn hơn A vì A có thêm câu “không tìm thấy”, nên sufficient coverage quan trọng hơn số ký tự.
- **Cặp 41 — lỗi nhất quán JSON:** pass 1 ghi winner=B nhưng reasoning kết luận A tốt hơn và scores A=0.5, B=0.0. Pass 2 sau quy đổi chọn A, scores A=0.8, B=0.0. Final=tie đúng quy tắc bất đồng. Cần phân biệt lỗi winner/reasoning/scores này với bằng chứng ưu tiên vị trí; con số 1/5 chỉ đo inconsistency. Validator hiện kiểm tra schema, domain và range, chưa kiểm tra sự phù hợp giữa winner với nội dung reasoning/scores. Hướng cải tiến tương lai là phát hiện contradiction và retry, không sửa tay winner của lượt đã lưu.
- **Verbosity:** ba case decisive là 1, 5, 21; chỉ B ở case 1 vừa thắng vừa dài hơn. Tỷ lệ 1/3 không cho thấy ưu tiên độ dài mạnh trên mẫu này; hai winner ngắn hơn thắng do đúng/đủ hơn. Hai ties không nằm trong mẫu số.
- **Binary calibration:** các lỗi ngưỡng phê duyệt (5), thiếu ý/tính toán (29), bản policy cũ (41), VPN cá nhân (50) đều được chấm 0; sáu câu còn lại được chấm 1. Nhãn ở câu 41 đúng dù pairwise pass 1 sai winner, chứng minh hai phép chấm không thể suy ra nhau. Reasoning binary 29 có cụm “sau 30 ngày đầu” thiếu chính xác: thực tế nhận tiền 30 ngày, hạn 15 ngày, quá hạn 15 ngày; label=0 vẫn có căn cứ từ thiếu Kế toán trưởng và chưa tính pro-rata. κ chỉ kiểm tra agreement của labels, không xác nhận mọi reasoning đều đúng.
- **κ trên mẫu được cấp:** p_o=10/10=1; p_e=(4×4+6×6)/100=0.52; κ=(1−0.52)/(1−0.52)=1. Đây là kết quả trên đúng mười model_answer gốc, không phải accuracy trên 50 answers pipeline hay trên toàn corpus. Prompt không chỉnh theo nhãn người sau khi đọc kết quả.
- **Model chung:** generation A và judge đều dùng Gemini 3.5 Flash Lite. Chưa kiểm tra xu hướng model thích câu trả lời do chính nó sinh; cần judge/model và tập calibration độc lập để đánh giá trước khi triển khai gate tự động.

## Calibration đúng model_answer

Helper chấm đúng question/model_answer gốc, dùng ground_truth của cùng question_id làm reference. Prompt không chứa human_label, human_note hay phân bố nhãn. Nhãn người chỉ được đọc để đối chiếu sau khi đã tạo đủ 10 binary judgments. Nhãn 0/1 không được suy từ winner A/B.

| Id | Model answer gốc | Judge label | Reasoning | Human label | Agree |
| --- | --- | --- | --- | --- | --- |
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | Answer trả lời đúng và đủ ý chính theo reference, không bỏ sót điều kiện quan trọng. | 1 | True |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | Câu hỏi hỏi về thiết bị 55 triệu (trên 50 triệu), theo reference cần Tổng Giám đốc (CEO) phê duyệt nhưng answer lại trả lời là Giám đốc phòng ban phê duyệt, dẫn đến sai sót về cấp phê duyệt. | 0 | True |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | Answer trả lời chính xác và đầy đủ ý thiết yếu theo reference, đúng mức thưởng Tết tối thiểu 1 tháng lương cho nhân viên chính thức từ 6 tháng trở lên. | 1 | True |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | Câu trả lời đáp ứng chính xác số ngày phép (18 ngày) và khoảng lương (20-35 triệu) theo đúng chính sách trong reference. | 1 | True |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | Answer trả lời chính xác, đủ ý (hoàn trả 25 triệu), đúng điều kiện và không bỏ sót thông tin so với reference. | 1 | True |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | Thiếu thẩm quyền phê duyệt của Kế toán trưởng và tính sai phí phạt (trong reference phạt cho 15 ngày quá hạn sau 30 ngày đầu, không phải phạt nguyên tháng trên 8 triệu). | 0 | True |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | Answer trả lời đúng và đủ số ngày phép (19 ngày) và tổng phụ cấp hàng tháng (1.500.000 VNĐ) theo đúng reference. | 1 | True |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | Câu trả lời sử dụng thông tin từ phiên bản cũ (v2023 là 12 ngày) thay vì phiên bản hiện hành v2024 (15 ngày) theo yêu cầu của reference. | 0 | True |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | Câu trả lời hoàn toàn chính xác theo reference, bao gồm cả ý nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương. | 1 | True |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | Reference cấm sử dụng VPN cá nhân, nhưng answer lại trả lời là được phép, vi phạm trực tiếp quy định trong chính sách. | 0 | True |

Observed agreement p_o=1.000000 (10/10). Judge counts 0/1=4/6; human counts 0/1=4/6. Chance p_e=(4×4+6×6)/10²=0.520000. Cohen κ=(p_o−p_e)/(1−p_e)=**1.000000**.

## Giới hạn và cách dùng judge

Pairwise prompt ưu tiên chính xác theo reference, đủ ý, phiên bản/phủ định/điều kiện rồi mới súc tích; temperature=0 và JSON response_format. Binary dùng prompt starter, chưa tinh chỉnh theo nhãn người. Năm cặp và mười nhãn là mẫu nhỏ; cùng reference có thể bỏ sót vấn đề reference hoặc diễn giải khác. κ không thay tỷ lệ chính xác trên toàn corpus. Inconsistency không tự chứng minh position bias, winner dài hơn có thể đủ ý hơn. Cần human review các trường hợp bất đồng và kiểm tra tập mới độc lập trước khi dùng judge làm quality gate. Chưa đánh giá độ ổn định qua nhiều seed/model/lượt chạy.
