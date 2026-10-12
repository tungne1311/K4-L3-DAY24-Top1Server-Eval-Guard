# Nhóm thực hiện K4 Track 3B

Tên nhóm: {{Tên nhóm}}

Repo chung: {{Link repo}}

Trưởng nhóm/người nộp: {{Họ tên và MSSV}}

Ngày lab/deadline áp dụng: {{Ngày giờ theo thông báo lớp}} — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 2 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 3 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: {{Phiên bản thực tế}}.
Virtualenv/dependencies/imports: {{Lệnh và kết quả}}.
Models/Qdrant/50 answers đã chuẩn bị: {{Bằng chứng và giới hạn/fallback}}.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### DoThanhTung-2A202602845

- Phần được giao và đã làm: người 1 — CP0, Tasks 1–4 Phase A, Tasks 5–8 Phase B. Port m1–m5 từ Day 18, ghép config/provider, sửa Qdrant 1.9.x; m4 ghi evaluator thật, không xuất sentinel 0/NaN; xử lý câu Markdown không dấu chấm. Implement group, RAGAS adapter, bottom 10, cluster mean; JSON judge/reference, swap cả winner/scores, Cohen κ và bias.
- Bằng chứng live: 106 chunks enrich qua API; `artifacts/answers_50q.json` có 50 answers LLM, 20/20/10 và 3 contexts/câu; `ragas_50q.json` có 50 × 4 metrics; `judge_results.json` có 5 cặp/10 lượt và 10 binary judgments đúng nguồn. Hai báo cáo đã điền và phân tích contexts/reference. Mean RAGAS=0.762530, nhóm yếu=multi_hop; Cohen κ=1.000000. Đối chiếu commit đóng góp qua git log và các paths này.
- Kiểm tra: Python 3.11.9; 99 tests offline trên test_phase_a, test_phase_b, test_person1_validation, test_support, test_report_contracts. Tests dùng mock/chặn mạng; ba artifacts trên là bằng chứng API thật riêng. `python scripts/check_person1.py` kiểm tra schemas, model provenance, source hashes và báo cáo; `pip check` không có broken requirements. Qdrant server v1.9.7, client 1.9.2; BGE-M3/reranker đã inference thật.
- Điều cần giải thích: worst-metric matrix đếm mọi câu; nhóm yếu chọn theo mean; faithfulness không bảo đảm đúng phiên bản; retrieval child có thể làm mất phủ định/hàng bảng. Swap cần đổi cả winner/scores; pairwise A/B khác quality binary 0/1; κ trừ agreement ngẫu nhiên. Inconsistency/longer-winner rate chưa chứng minh nguyên nhân bias.
- Môi trường/giới hạn: dùng key Gemini cũ từ lab trước trong `.env` bị Git ignore, model thực `gemini-3.5-flash-lite` cho enrichment/generation/evaluator/judge. OpenRouter cũ hết credit nên batch fallback ban đầu đã được thay bằng batch LLM thật. Full requirements chưa cài được Annoy do thiếu MSVC 14+; người 1 dùng requirements-person1.txt và constraints-core.txt, PyArrow 20.0.0 với NumPy 1.26.4. Hai PDF scan chưa OCR. Phase C, guardrails, blueprint và phần chung TEAM thuộc người 2, chưa hoàn thiện trong phần này.
- Nguồn/AI hỗ trợ: m1–m5 từ E:/K4-Track3B-DAY18-DoThanhTung-2A202602845-ProductionRAG/src. Codex hỗ trợ đọc yêu cầu, port/implement, kiểm thử, chạy API và viết báo cáo; kiểm chứng bằng unit tests, runtime thật và schema/source hashes. Thành viên cần tự đọc, giải thích mã và báo cáo trước khi nộp.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
