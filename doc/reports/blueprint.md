# Blueprint CI/CD cho RAG và guardrails

Nhóm: Chưa được cung cấp trong file phân công cá nhân.

Người phụ trách: Phạm Đức Anh — 2A202602994.

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả dự kiến: `artifacts/ragas_50q.json`, `artifacts/judge_results.json`, `artifacts/guard_results.json`.
Run timestamp: `2026-10-13T06:41:58.657703+00:00`; Phase C live artifact: `artifacts/guard_results.json`.
Guard model: `openai/gpt-4o-mini` via OpenRouter (key read only from `.env`). Models generation/evaluator/judge from A/B are not available in this checkout.

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

Đề xuất: kiểm tra PII bằng Presidio trước khi gọi NeMo input rail; nếu input bị chặn thì dừng trước RAG và trả thông báo an toàn. Nếu được phép, chạy RAG rồi kiểm tra câu trả lời bằng output rail trước khi trả cho người dùng. Redact PII trước khi lưu/ghi log; log tối thiểu mã request, kết quả/loại rail và latency, không ghi raw prompt, PII hay API key. Giữ secrets trong biến môi trường/secret store, không đưa vào Git. Nếu guard service lỗi hoặc timeout, không mặc định cho nội dung không kiểm tra đi qua; cần nhóm quyết định chính sách fail-closed/fallback phù hợp trước khi triển khai. Đây là thiết kế đề xuất, chưa được triển khai hay xác nhận bằng live run.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Timed samples: 20; warm-up: 2; method: linear interpolation over raw samples.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 13.238 | 27.282 | 28.697 | live Phase C |
| NeMo input | 1437.267 | 1946.993 | 1971.479 | live Phase C; dominant latency |
| Input guard sequential | 1449.794 | 1954.874 | 1981.826 | live Phase C; exceeds 500ms input-layer target |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; actual P95 is 1954.874ms, so `latency_budget_ok=false`. The bottleneck is the remote NeMo/OpenRouter input call (P95 1946.993ms), not Presidio. This does not claim full-guard latency because RAG and output rails were not included in this measurement.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.

Đề xuất job: cài dependencies theo constraints, chạy `python scripts/check_lab.py --with-tests`, và chạy live experiments trong job riêng có credentials bảo mật. Job kiểm tra chất lượng nên trả non-zero khi kết quả thấp hơn ngưỡng đã thống nhất; `MIN_*` chỉ là cấu hình đề xuất, không phải gate đang hoạt động. Workflow CI chưa được triển khai/xác minh trong checkout này.

## Monitoring và cải tiến

Đề xuất theo dõi tỷ lệ input bị chặn, false positives trên clean controls, output bị redact, lỗi/timeouts của rail và P50/P95/P99 từng lớp. Báo động khi clean false positives tăng hoặc guard lỗi/latency vượt ngưỡng đã thống nhất; lấy mẫu đã loại bỏ PII, có thời hạn lưu và người phụ trách phản hồi. Đánh giá drift định kỳ bằng bộ test versioned; bộ 20 attacks/8 clean/4 outputs nhỏ, không đại diện toàn bộ traffic. Chưa có số đo thật hoặc người trực vận hành được cung cấp.

RAGAS mean/worst distribution: chưa có `artifacts/ragas_50q.json`.
Cohen’s κ: chưa có `artifacts/judge_results.json`.
Phase C live evidence: attacks passed 20/20; clean controls allowed 8/8 (false-positive rate 0.0); output controls passed 4/4.

Cải tiến có thể kiểm tra sau khi có live evidence:
1. Phân loại từng attack lọt theo PII hay NeMo rail, rồi cập nhật prompt/recognizer và chạy lại cùng bộ fixture bất biến.
2. Chạy clean controls sau mỗi thay đổi để đảm bảo không tăng false positives.
3. Theo dõi P95 của Presidio và NeMo input riêng; chỉ tuyên bố full-guard budget sau phép đo end-to-end.
4. Kiểm tra log/export để bảo đảm không chứa raw PII hoặc credentials.

The Phase C statements above are verified against the live artifact. Phase A/B claims remain pending because their artifacts are not present in this checkout.
