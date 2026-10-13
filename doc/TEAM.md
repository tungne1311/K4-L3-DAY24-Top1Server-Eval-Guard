# Nhóm thực hiện K4 Track 3B

Tên nhóm: **Top1Server**.

Repo chung: [K4-L3-DAY24-Top1Server-Eval-Guard](https://github.com/tungne1311/K4-L3-DAY24-Top1Server-Eval-Guard).

Trưởng nhóm/người nộp: **Đỗ Thanh Tùng — 2A202602845** (đã xác nhận ngày 13/10/2026).

Ngày lab/deadline áp dụng: chưa được cung cấp thông báo lớp để xác nhận ngày cụ thể. Quy định repo: 23:59 ngày diễn ra lab, Asia/Ho_Chi_Minh (UTC+07:00), áp dụng điều chỉnh của coach. Ngày tạo artifacts và ngày push không được dùng thay ngày lab/deadline.

Commit dùng để chấm (bản hoàn thiện mã/artifacts/báo cáo): [`27d6310ccaeb62b1412054a4860ee30c1c26235b`](https://github.com/tungne1311/K4-L3-DAY24-Top1Server-Eval-Guard/commit/27d6310ccaeb62b1412054a4860ee30c1c26235b). Bản này kế thừa mã/artifacts A/B/C ở `5214e84759afd5e98e956cfa83119f1a94325dfa` và bổ sung TEAM/blueprint hoàn chỉnh. Commit ghi nhận SHA này chỉ cập nhật thông tin bàn giao trong TEAM; code, artifacts và số đo giữ nguyên.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Đỗ Thanh Tùng | 2A202602845 | CP0, m1–m5, Tasks 1–8 Phase A/B; tích hợp và hoàn thiện tài liệu chung | `e540cb20e992d72c847bb14dc4699d106f66cfbc`, `8e70f37`, `20b6359`; artifacts answers/RAGAS/judge; failure_clusters và bias_report |
| 2 | Phạm Đức Anh | 2A202602994 | Tasks 9a–12 Phase C, cấu hình NeMo/PII, guard artifact và bản đầu Task 13 blueprint | `5214e84759afd5e98e956cfa83119f1a94325dfa`; guard_results; src/phase_c_guard.py; guardrails/ |

Người tích hợp/chạy batch/nộp link: Tùng chạy CP0/A/B và tích hợp bản chung; Đức Anh chạy C trong môi trường riêng. Tùng phụ trách gửi link repo và SHA qua kênh coach công bố. Chưa có bằng chứng đã gửi bài cho coach.

## Môi trường và kiểm chứng

- Người 1: Windows, Python 3.11.9, `.venv` với `requirements/requirements-person1.txt` và `constraints-core.txt`; RAGAS 0.1.22, LangChain 0.2.17/core 0.2.43, langchain-openai 0.1.25, OpenAI SDK 1.109.1, NumPy 1.26.4, PyArrow 20.0.0. `pip check` không có broken requirements. Môi trường này không có NeMo/Presidio/spaCy; unit tests offline không chứng minh full guard runtime đã cài trên máy Tùng.
- Người 2: theo ghi nhận của Đức Anh ở commit `5214e84`, Windows NT 10.0.26300, Python 3.11.9, MSVC 14.51 x64; Annoy 1.17.3 build thành công, full requirements/constraints, NeMo/Presidio/spaCy và `en_core_web_lg` đã cài, `pip check` đạt. Bằng chứng batch C là `artifacts/guard_results.json` với `run_kind=live`. Đây là ghi nhận môi trường chạy C riêng; lần tích hợp này kiểm tra artifact/schema/hash và tests offline, không chạy lại API hay xác minh lại compiler trên máy Đức Anh.
- Qdrant của CP0: server 1.9.7 qua Docker ở localhost:6333, client 1.9.2. BGE-M3 và BGE-reranker-v2-m3 đã inference thật. Corpus 25 Markdown và một PDF có text tạo 106 child chunks; hai PDF scan BCTC/Nghị định 13 chưa OCR.
- A/B: enrichment/generation/evaluator/judge dùng Gemini `gemini-3.5-flash-lite` qua endpoint OpenAI-compatible của Gemini; embedding evaluator `BAAI/bge-m3`. C: NeMo dùng `openai/gpt-4o-mini` qua OpenRouter. Keys chỉ giữ trong `.env`/biến môi trường, bị Git ignore.
- Khi tái chạy: A/B dùng provider/key/model theo `phan_cong/BAN_GIAO_NGUOI_1.md`; C dùng OpenRouter key và endpoint tương ứng (`OPENAI_BASE_URL` và `OPENAI_API_BASE` là `https://openrouter.ai/api/v1`) trong một tiến trình riêng. Một cấu hình key Gemini không dùng để gọi guard model OpenRouter. Không commit hay đưa giá trị key vào log.
- Kiểm tra bản tích hợp ngày 13/10/2026: `python scripts/check_lab.py --with-tests` → **113 passed, 3 deselected; 0 failed checks**. Checker kiểm schema, nguồn/hash, số lượng/nhãn/percentiles, báo cáo và tests offline. Ba tests integration được loại khỏi kiểm tra offline; không lặp batch API khi artifacts đã có. `git diff --check` đạt; quét secret trước khi push.

## INDIVIDUAL

### DoThanhTung-2A202602845

- Phần được giao và đã làm: người 1 — CP0, Tasks 1–4 Phase A, Tasks 5–8 Phase B. Port m1–m5 từ Day 18, ghép config/provider, sửa Qdrant 1.9.x; m4 ghi evaluator thật, không xuất sentinel 0/NaN; xử lý câu Markdown không dấu chấm. Implement group, RAGAS adapter, bottom 10, cluster mean; JSON judge/reference, swap cả winner/scores, Cohen κ và bias.
- Bằng chứng live: 106 chunks enrich qua API; `artifacts/answers_50q.json` có 50 answers LLM, 20/20/10 và 3 contexts/câu; `ragas_50q.json` có 50 × 4 metrics; `judge_results.json` có 5 cặp/10 lượt và 10 binary judgments đúng nguồn. Hai báo cáo đã điền và phân tích contexts/reference. Mean RAGAS=0.762530, nhóm yếu=multi_hop; Cohen κ=1.000000. Commit code, artifacts và báo cáo: `e540cb20e992d72c847bb14dc4699d106f66cfbc`.
- Kiểm tra: Python 3.11.9; 99 tests offline trên test_phase_a, test_phase_b, test_person1_validation, test_support, test_report_contracts. Tests dùng mock/chặn mạng; ba artifacts trên là bằng chứng API thật riêng. `python scripts/check_person1.py` kiểm tra schemas, model provenance, source hashes và báo cáo; `pip check` không có broken requirements. Qdrant server v1.9.7, client 1.9.2; BGE-M3/reranker đã inference thật.
- Điều cần giải thích: worst-metric matrix đếm mọi câu; nhóm yếu chọn theo mean; faithfulness không bảo đảm đúng phiên bản; retrieval child có thể làm mất phủ định/hàng bảng. Swap cần đổi cả winner/scores; pairwise A/B khác quality binary 0/1; κ trừ agreement ngẫu nhiên. Inconsistency/longer-winner rate chưa chứng minh nguyên nhân bias.
- Môi trường/giới hạn: dùng key Gemini cũ từ lab trước trong `.env` bị Git ignore, model thực `gemini-3.5-flash-lite` cho enrichment/generation/evaluator/judge. OpenRouter cũ hết credit nên batch fallback ban đầu đã được thay bằng batch LLM thật. Tại thời điểm chạy Người 1, full requirements chưa cài được Annoy do thiếu MSVC 14+; người 1 dùng requirements-person1.txt và constraints-core.txt, PyArrow 20.0.0 với NumPy 1.26.4. Hai PDF scan chưa OCR. Phase C/guardrails do Người 2 hoàn thành riêng ở commit `5214e84759afd5e98e956cfa83119f1a94325dfa`; lượt này Tùng tích hợp TEAM và đồng bộ blueprint từ artifacts A/B/C.
- Nguồn/AI hỗ trợ: m1–m5 từ E:/K4-Track3B-DAY18-DoThanhTung-2A202602845-ProductionRAG/src. Codex hỗ trợ đọc yêu cầu, port/implement, kiểm thử, chạy API và viết báo cáo; kiểm chứng bằng unit tests, runtime thật và schema/source hashes. Thành viên cần tự đọc, giải thích mã và báo cáo trước khi nộp.
- Tích hợp cuối ngày 13/10/2026: cập nhật `main` với commit Người 2, hoàn thiện TEAM, đồng bộ blueprint với models/metrics A/B/C và kiểm tra bản chung. Codex hỗ trợ sửa tài liệu, kiểm tra offline và Git; không tạo lại hay sửa số đo artifacts.

### PhamDucAnh-2A202602994

- Phần được giao và đã làm: Phase C guardrails — Presidio PII, NeMo input/output rails, adversarial suite và latency; Task 13 blueprint ban đầu. Code/cấu hình/batch C nằm trong commit `5214e84759afd5e98e956cfa83119f1a94325dfa`.
- Bằng chứng: `artifacts/guard_results.json`, timestamp UTC `2026-10-13T06:41:58.657703+00:00`, OpenRouter `openai/gpt-4o-mini`; attacks 20/20, clean 8/8 (false-positive rate 0), output 4/4. Có 20 timed samples và hai warm-up bị loại.
- Cách kiểm tra theo bàn giao: `python -m pytest tests/test_phase_c.py -q` → 14 passed; `python scripts/run_experiments.py --phase c --live --latency-samples 20` tạo artifact. Presidio runtime kiểm tra câu sạch và CCCD giả. Lần tích hợp đối chiếu artifact với fixtures bất biến và chạy toàn bộ tests offline.
- Điều cần giải thích: PII được detect/anonymize; quyết định chặn lấy từ activated rail log, không đoán bằng câu từ chối; expected chỉ dùng đối chiếu actual. Input-layer latency chạy đủ Presidio rồi NeMo, khác request short-circuit và full RAG/output.
- Giới hạn: input-layer P95 1954.874405 ms vượt mục tiêu 500 ms; NeMo input P95 1946.993305 ms chiếm phần lớn. RAG, NeMo output và full request chưa đo. Bộ 20 attacks/8 clean/4 outputs nhỏ, chưa đại diện traffic thực. Artifacts A/B đã có trong bản chung; RAGAS mean 0.762530, nhóm yếu multi_hop, Cohen κ 1.000000; các kết quả này thuộc lượt chạy Người 1.
- Nguồn/AI hỗ trợ theo bàn giao: ChatGPT hỗ trợ rà soát yêu cầu, triển khai và kiểm tra offline. Tests mock và artifact live là hai loại bằng chứng khác nhau; không dùng unit tests để khẳng định runtime. Tùng/Codex đồng bộ blueprint và tài liệu chung sau tích hợp, không quy công việc A/B cho Đức Anh.

## Phiên bản và thông tin nộp

Ngày 13/10/2026: tích hợp code/artifacts A/B/C, sửa TEAM và cập nhật blueprint từ kết quả đã lưu. Các lần tạo artifacts có timestamp UTC riêng, không phải một batch mới ngày tích hợp. Chưa có thông báo ngày lab/deadline hay bằng chứng gửi bài; không kết luận đã nộp đúng hạn hoặc sửa sau hạn. Người nộp đối chiếu lịch lớp và gửi đúng SHA bản bàn giao; cập nhật sau deadline cần ghi thời điểm/lý do và theo quyết định coach.
