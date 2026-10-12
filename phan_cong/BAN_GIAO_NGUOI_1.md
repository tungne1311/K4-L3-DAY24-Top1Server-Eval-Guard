# Bàn giao Người 1 — hoàn thành CP0, Phase A/B

Đã đọc yêu cầu lab và phân công, thực hiện lần lượt CP0 rồi Tasks 1–8. Nguồn m1–m5: repo Day 18 `E:/K4-Track3B-DAY18-DoThanhTung-2A202602845-ProductionRAG/src`. Corpus và fixtures giữ nguyên. Chưa push/nộp link; phần tích hợp cuối thuộc Người 2.

Commit code, artifacts và báo cáo: `e540cb20e992d72c847bb14dc4699d106f66cfbc`.

## Kết quả cho Người 2

| Bằng chứng | Kết quả |
| --- | --- |
| answers_50q.json | 50 LLM answers; 20 factual / 20 multi_hop / 10 adversarial; 3 contexts/câu |
| ragas_50q.json | 50 × 4 metrics hữu hạn [0,1]; mean=0.762530; nhóm yếu=multi_hop |
| judge_results.json | 5 cặp cố định/10 lượt swap; 10 binary labels; Cohen κ=1.000000 |
| Báo cáo | failure_clusters.md và bias_report.md đã điền theo JSON thực |
| Code/checks | Tasks 1–8 hoàn thành; 99 tests offline pass; checker Người 1 xác minh hash/schema |

Models thực: Gemini `gemini-3.5-flash-lite` cho enrichment/generation/evaluator/judge; `BAAI/bge-m3` cho embeddings; `BAAI/bge-reranker-v2-m3` cho rerank. RAGAS mean là mean đều bốn metrics trên 50 câu, không phải accuracy. Đọc `per_distribution`, `failure_clusters` và `calibration` trong hai JSON để điền blueprint. Bias chỉ là tín hiệu trên mẫu nhỏ.

## Môi trường và cách tái chạy

Python 3.11.9; RAGAS 0.1.22; langchain 0.2.17/core 0.2.43/openai adapter 0.1.25; OpenAI SDK 1.109.1; NumPy 1.26.4; PyArrow 20.0.0. `pip check` không có broken requirements. Qdrant server v1.9.7 chạy Docker tại localhost:6333, client 1.9.2. Models đã cache và inference thật.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements/requirements-person1.txt -c requirements/constraints-core.txt
docker compose -f infra/docker-compose.yml up -d
$env:PYTHONIOENCODING='utf-8'
$env:OMP_NUM_THREADS='4'
$env:MKL_NUM_THREADS='4'
.\.venv\Scripts\python.exe scripts/setup_answers.py --live
.\.venv\Scripts\python.exe scripts/run_experiments.py --phase a --live
.\.venv\Scripts\python.exe scripts/run_experiments.py --phase b --live
.\.venv\Scripts\python.exe scripts/check_person1.py
```

Lượt này dùng key Gemini cũ từ `.env` của Day19 theo yêu cầu; chỉ lưu trong `.env` Day24 bị Git ignore. [OpenAI compatibility chính thức](https://ai.google.dev/gemini-api/docs/openai) là nguồn đối chiếu endpoint. Không đưa key vào Git/chat. Khi tái chạy, cấu hình trong `.env`: `OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`, `OPENAI_API_KEY` chứa Gemini key; `LLM_MODEL`, `GENERATION_MODEL`, `ENRICHMENT_MODEL`, `EVAL_MODEL`, `JUDGE_MODEL` đều là model trên; `EVAL_SUPPORTS_N=0`; các caps `LLM_RPM`, `ENRICHMENT_RPM`, `EVAL_RPM`, `JUDGE_RPM`=12; `GENERATION_MAX_TOKENS`=768. Base URL/provider và model của guardrail YAML phải được Người 2 kiểm tra riêng.

```powershell
$env:LLM_RPM='0'; $env:ENRICHMENT_RPM='0'; $env:EVAL_RPM='0'; $env:JUDGE_RPM='0'
.\.venv\Scripts\python.exe -m pytest tests/test_phase_a.py tests/test_phase_b.py tests/test_person1_validation.py tests/test_support.py tests/test_report_contracts.py --basetemp .venv/pytest-person1 -q
```

Các biến 0 chỉ dùng khi kiểm thử mock trong shell này; xóa/đặt lại trước chạy API. Unit tests không thay số đo live. Script checker không gọi API.

Phase A tự tiếp tục các điểm hợp lệ ở `.venv/ragas_measured_*.json` khi inputs/model/code khớp. Đây là cache điểm đã đo thật, không phải lượt gọi API mới; metadata `created_at` là thời điểm tạo artifact. Muốn đo một lượt hoàn toàn mới với cùng inputs/model/code, lưu lại rồi bỏ checkpoint tương ứng trước khi chạy A. Lượt A cuối trong artifacts hiện tại bắt đầu với 0 cached cells và đo đủ 200 cells qua RAGAS.

## Phần Người 2 còn phải hoàn thiện

- Quota: l??t A ??u b?ng key Day19 ch?m 500 requests/ng?y; tr??c khi ch?y C c?n ki?m tra quota/provider hi?n t?i. A/B d?ng key Day10, c?c model roles ?ang ???c c?u h?nh ri?ng.
- Full NeMo/Presidio runtime: cài full requirements từng thất bại ở Annoy 1.17.3 vì thiếu Microsoft C++ Build Tools (MSVC 14+). Bộ Người 1 không bao gồm NeMo; không khai full stack đã chạy.
- Implement Phase C, chạy suite/clean controls/output/latency thật, điền blueprint; hoàn thiện thông tin nhóm/thành viên/deadline/commit chung trong TEAM, chạy checker toàn lab, rồi push/nộp.
- Hai PDF scan BCTC/Nghị định 13 chưa OCR. M1 đọc 25 Markdown và một PDF có text, tạo 106 child chunks. Báo cáo A ghi rõ giới hạn coverage và mất phủ định/hàng bảng.

Các file `src/phase_c_guard.py`, `guardrails/`, `doc/reports/blueprint.md` giữ nguyên trong phần Người 1. Bằng chứng chi tiết nằm trong [failure_clusters](../doc/reports/failure_clusters.md), [bias_report](../doc/reports/bias_report.md) và mục INDIVIDUAL của TEAM.

Kiểm tra cuối: `scripts/check_person1.py` pass CP0/A/B, hashes và hai báo cáo; quét secret và `git diff --check` pass. `scripts/check_lab.py` pass toàn bộ phần Người 1, còn đúng 4 failed checks: placeholder chung trong TEAM, blueprint chưa điền, Phase C còn TODO và chưa có `guard_results.json`. Đây không phải điểm rubric.
