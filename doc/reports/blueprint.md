# Blueprint CI/CD cho RAG và guardrails

Nhóm: **Top1Server**. Phụ trách Phase C/blueprint ban đầu: **Phạm Đức Anh — 2A202602994**. Tích hợp A/B/C và hoàn thiện tài liệu: **Đỗ Thanh Tùng — 2A202602845**, ngày 13/10/2026.

Đây là **đề xuất CI/CD và vận hành**, chưa có workflow triển khai hay hệ thống monitoring production đã chạy. Bằng chứng thực nghiệm là các artifacts đã lưu; không tạo thêm batch API trong lần sửa tài liệu này.

## Nguồn kết quả và models thực

| Phase / nguồn | Timestamp UTC tạo artifact | Models theo vai trò |
|---|---|---|
| A — [ragas_50q.json](../../artifacts/ragas_50q.json) | 2026-10-12T14:35:46.690376+00:00 | generation: gemini-3.5-flash-lite; evaluator: gemini-3.5-flash-lite và BAAI/bge-m3 |
| B — [judge_results.json](../../artifacts/judge_results.json) | 2026-10-12T14:37:51.167239+00:00 | generation: gemini-3.5-flash-lite; judge: gemini-3.5-flash-lite |
| C — [guard_results.json](../../artifacts/guard_results.json) | 2026-10-13T06:41:58.657703+00:00 | guard: openai/gpt-4o-mini qua OpenRouter |

CP0 có 50 LLM answers, 20 factual/20 multi_hop/10 adversarial và ba contexts/câu. Enrichment dùng Gemini; retrieval embedding BAAI/bge-m3, reranker BAAI/bge-reranker-v2-m3. A/B dùng endpoint Gemini OpenAI-compatible, C dùng OpenRouter với credential/cấu hình riêng; không suy guard model từ generation/judge model. Source hashes của A/B/C được đối chiếu với fixtures/answers bởi checker.

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.

Đề xuất luồng request: Presidio detect CCCD/CMND, VN phone và email; phát hiện PII thì dừng trước RAG, trả yêu cầu bỏ thông tin nhạy cảm. Nếu không có PII, NeMo input kiểm chủ đề HR/IT, jailbreak, giả quyền và yêu cầu bí mật. Đọc quyết định activated rail; khi chặn thì trả câu từ chối an toàn. Input hợp lệ mới chạy RAG, rồi output rail kiểm answer có sẵn. Output bị chặn được thay bằng thông báo an toàn, output sạch giữ nguyên.

Nếu Presidio/NeMo lỗi hoặc timeout, đề xuất dừng request và trả lỗi dịch vụ/thông báo cố định; không gửi raw answer chưa kiểm qua một model dự phòng. RAG thiếu context hoặc xung đột phiên bản thì yêu cầu abstain/nêu giới hạn theo policy, không tự bịa. Fallback chỉ bật sau khi engine dự phòng đã qua cùng bộ regression và giữ thứ tự guard; chưa triển khai cơ chế fallback production.

Secrets nằm trong `.env` bị Git ignore hoặc secret store của CI; không ghi giá trị key vào YAML/Git/log. Đề xuất log request ID, model ID, version/config, loại rail, status/error và latency, tránh raw question/answer, context hay entity text. Redact trước khi xuất log; chỉ lưu samples đã ẩn danh với quyền truy cập hạn chế và retention bảy ngày (đề xuất). Chuỗi PII trong fixtures/artifact C là dữ liệu mẫu của lab, không phải thông tin nhân viên thật. Không dùng corpus HR thật để tạo evidence mới.

Request thực có short-circuit khi bị chặn; phép đo Task 12 luôn chạy đủ hai tầng input, kể cả khi Presidio phát hiện PII. Các batch A/B/C độc lập chưa chứng minh một dịch vụ end-to-end production đã triển khai.

## Phạm vi và số đo latency

Scope bắt buộc: `input_layers_sequential`. Engines tạo trước đo; hai lượt warm-up thật bị loại; 20 samples timed xoay vòng tám câu sạch. Đo bằng perf_counter; percentile nội suy tuyến tính tại (n−1)×q; `input_guard_ms` là tổng hai lớp của từng sample, không phải tổng hai P95.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 13.237650 | 27.282455 | 28.696891 | Đo trong batch C |
| NeMo input | 1437.267300 | 1946.993305 | 1971.479061 | Đo trong batch C; phần lớn latency |
| Input guard sequential | 1449.793500 | 1954.874405 | 1981.825601 | Đo tổng từng sample; vượt 500 ms |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi Task 12 |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi Task 12 |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer target 500 ms; P95 thực 1954.874405 ms, `latency_budget_ok=false`. NeMo input P95 1946.993305 ms là phần lớn; số đo này bao gồm overhead NeMo/provider, chưa tách network/model/token time. Vượt target vẫn giữ số thật; lab không yêu cầu sửa metric cho đạt.

Kế hoạch đo phần còn lại: tạo các engines trước đo, hai warm-up full request, ít nhất 50 timed requests cho mỗi nhóm sạch/bị chặn; giữ timestamps perf_counter cho Presidio, NeMo input, retrieval/rerank/generation, output rail và toàn request. Tách cache nóng/lạnh, short-circuit và allowed; giữ raw samples, model/config và tính percentile theo từng scope. Chỉ đánh giá full-request P95 <500 ms sau khi đã có phép đo đó.

## CI gates đề xuất

Job offline có thể dùng ngay: `python scripts/check_lab.py --with-tests`. Checker kiểm schema/hash/counts/labels/percentiles, báo cáo, TODO và unit tests; không gọi API và không tự thực hiện tất cả ngưỡng chất lượng sau đây.

| Gate đề xuất | Kết quả artifact hiện tại | Cách áp dụng |
|---|---|---|
| Faithfulness mean ≥0.75 trên 50 câu | 0.852381 | Job chất lượng cần tính từ 50 per_question; trả nonzero nếu thấp |
| RAGAS avg_score mean ≥0.65 trên 50 câu | 0.762530 | Mean đều bốn metrics/câu, rồi mean 50 câu; không lấy mean đều ba nhóm |
| Attacks ≥18/20; clean allowed 8/8; outputs 4/4 | 20/20, 8/8, 4/4 | Gate CI/bonus đề xuất; checker lab dùng ngưỡng bắt buộc attacks ≥15/20 |
| Full-request P95 <500 ms | chưa đo | Chỉ bật gate sau phép đo đúng scope; input-layer P95 hiện vượt mục tiêu |

Chưa có script quality gate hoặc workflow CI mới được triển khai. Nếu thêm biến `MIN_*`, job phải thực sự đọc và so sánh, không coi việc khai biến là gate đã hoạt động. Job live riêng chỉ chạy khi đổi model/prompt/retrieval hoặc theo lịch đánh giá đã thống nhất, dùng secrets và budget/quota; không lặp API sau mỗi sửa Markdown. Giữ artifacts/version/hashes, không thay fixtures/reference/labels sau khi xem kết quả để vượt gate. CI failures giữ bản candidate và yêu cầu review trước release; không gửi model chưa kiểm vào production.

## Monitoring và cải tiến có thể kiểm tra

Baseline A: RAGAS mean **0.762530**; factual **0.885034**, multi_hop **0.649305**, adversarial **0.743972**. Nhóm yếu nhất **multi_hop**; context_precision là worst metric của 19/50 câu, riêng multi_hop mean context_precision **0.433333**. Matrix đếm mọi câu, không tự chứng minh mọi context vô ích.

Baseline B: Cohen κ **1.000000** trên đúng 10 model_answer được cấp; observed=1, chance=0.52. Inconsistency khi swap 1/5; longer-winner rate 1/3 case decisive. Cặp 41 có winner pass 1 mâu thuẫn scores/reasoning; κ=1 không xác nhận mọi reasoning đều đúng. Xem [bias_report](bias_report.md).

Baseline C: attacks **20/20**, clean allowed **8/8**, false-positive rate **0.0**, output **4/4**; 20 latency samples. Đây là bộ 50/20/8/4 nhỏ; chưa có traffic production hay validation set độc lập để suy rộng.

Đề xuất theo dõi blocked/allowed theo loại rail, clean false positives, output bị thay, error/timeout/provider quota, P50/P95/P99 từng scope và metrics RAGAS theo distribution. Cảnh báo ngay khi bất kỳ clean control bị chặn, unsafe output lọt hoặc rail lỗi; cảnh báo khi rolling input P95 >500 ms trên ít nhất 20 mẫu hoặc quality score thấp hơn gate. Tùng xử lý retrieval/evaluator/judge; Đức Anh xử lý PII/input/output/prompt guard; Tùng tổng hợp/release. Vai trò vận hành này là đề xuất, chưa có dashboard/on-call đã chạy. Samples phải redact, review false positives và đánh giá drift theo model/corpus/config mới, dùng tập bổ sung độc lập.

1. Multi_hop precision 0.433333 và câu 21/33 thiếu context lương/phụ cấp: thử tách sub-query và ghép parent chunks; so sánh precision/recall, đủ ý và phiên bản trên tập bất biến. Không chỉ tăng top-k vì có thể thêm nhiễu.
2. Câu 48 mất phủ định “chưa”, câu 22 bị cắt hàng bảng: giữ câu phủ định và header/hàng bảng khi chunk; kiểm lại answer/context/reference cho bottom 10. Hai PDF scan chưa OCR cần bước OCR được kiểm chất lượng trước khi thay corpus.
3. Câu 41/42 lẫn policy cũ/mới: bổ sung metadata phiên bản/ngày hiệu lực, chọn nguồn hiện hành và regression version/negation. Giữ bản cũ trong corpus làm bẫy có chủ ý; không xóa để làm eval dễ hơn.
4. Pairwise 41 mâu thuẫn winner/scores: đề xuất semantic validation và retry có giới hạn, audit raw response; giữ nguyên kết quả đã lưu. Bổ sung calibration độc lập và judge khác generation để kiểm độ ổn định, không tinh chỉnh theo human_label đã thấy.
5. Guard P95 1954.874405 ms: tách network/model/NeMo overhead và thử engine/provider gần hơn trên cùng policy; chỉ nhận cải thiện khi attacks, clean/output và raw latency đều được đo lại. Thay đổi prompt phải kiểm cả tám clean controls để tránh chặn nhầm câu hỏi password/VPN hợp lệ.

Các nhận xét A/B đã đối chiếu với [failure_clusters](failure_clusters.md), [bias_report](bias_report.md) và JSON nguồn. Blueprint tích hợp đủ A/B/C; số đo ngoài phạm vi giữ trạng thái chưa đo cùng kế hoạch cụ thể.
