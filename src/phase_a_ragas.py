from __future__ import annotations

"""Phase A: RAGAS Production Evaluation — 50q, 3 distributions, cluster analysis."""

import json
import math
from collections.abc import Mapping
import os
import sys
from dataclasses import asdict, dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, ANSWERS_PATH, ARTIFACTS_DIR
from src.experiment_support import write_json

Distribution = str  # "factual" | "multi_hop" | "adversarial"

DIAGNOSTIC_TREE = {
    "faithfulness":      ("LLM hallucinating", "Tighten system prompt, lower temperature"),
    "context_recall":    ("Missing relevant chunks", "Improve chunking or add BM25"),
    "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
    "answer_relevancy":  ("Answer doesn't match question", "Improve prompt template"),
}


@dataclass
class RagasResult:
    question_id: int
    distribution: Distribution
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    @property
    def avg_score(self) -> float:
        return (self.faithfulness + self.answer_relevancy +
                self.context_precision + self.context_recall) / 4

    @property
    def worst_metric(self) -> str:
        scores = {
            "faithfulness":      self.faithfulness,
            "answer_relevancy":  self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall":    self.context_recall,
        }
        return min(scores, key=scores.get)


# ─── Đã implement sẵn ────────────────────────────────────────────────────────

@dataclass
class RagasEvaluation:
    """Task 2 output: measured rows plus model identifiers reported by m4."""
    results: list[RagasResult]
    evaluator_models: list[str]

def load_test_set_50q(path: str = TEST_SET_PATH) -> list[dict]:
    """Load 50q test set với 3 distributions."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_answers(path: str = ANSWERS_PATH) -> list[dict]:
    """Load pre-generated answers từ setup_answers.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"answers_50q.json không tìm thấy tại {path}\n"
            "→ Chạy trước: python scripts/setup_answers.py --live"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict]) -> dict:
    """Provided exporter: preserve the student-produced Task 3 rows verbatim."""
    per_dist: dict[str, dict] = {}
    for dist in ["factual", "multi_hop", "adversarial"]:
        subset = [r for r in results if r.distribution == dist]
        if subset:
            per_dist[dist] = {
                "count": len(subset),
                "faithfulness":      sum(r.faithfulness for r in subset) / len(subset),
                "answer_relevancy":  sum(r.answer_relevancy for r in subset) / len(subset),
                "context_precision": sum(r.context_precision for r in subset) / len(subset),
                "context_recall":    sum(r.context_recall for r in subset) / len(subset),
                "avg_score":         sum(r.avg_score for r in subset) / len(subset),
            }

    report = {
        "total_questions": len(results),
        "per_question": [asdict(r) for r in results],
        "per_distribution": per_dist,
        "failure_clusters": clusters,
        "bottom_10": bottom,
    }
    return report


def save_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict],
                        path: str = os.path.join(ARTIFACTS_DIR, "ragas_50q.json")) -> None:
    write_json(path, build_phase_a_report(results, clusters, bottom))



# ─── Tasks 1-4: Sinh viên implement ──────────────────────────────────────────

DISTRIBUTIONS = ("factual", "multi_hop", "adversarial")
METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def group_by_distribution(test_set: list[dict]) -> dict[str, list[dict]]:
    """Task 1: Preserve every source row in its declared distribution."""
    groups = {distribution: [] for distribution in DISTRIBUTIONS}
    for row in test_set:
        if row["distribution"] not in groups:
            raise ValueError(f"Unknown distribution: {row['distribution']}")
        groups[row["distribution"]].append(row)
    return groups


def run_ragas_50q(answers: list[dict]) -> RagasEvaluation:
    """Task 2: Adapt measured m4 rows without losing alignment or provenance."""
    from src.m4_eval import evaluate_ragas

    if not answers or len({row["id"] for row in answers}) != len(answers):
        raise ValueError("Evaluation requires nonempty answers with unique ids")
    group_by_distribution(answers)
    raw = evaluate_ragas(
        [row["question"] for row in answers], [row["answer"] for row in answers],
        [row["contexts"] for row in answers], [row["ground_truth"] for row in answers],
    )
    measured = raw.get("per_question", [])
    if len(measured) != len(answers):
        raise ValueError("m4 per_question count does not match answers")
    models = raw.get("metadata", {}).get("evaluator_models")
    if not isinstance(models, list) or not models or any(
        not isinstance(model, str) or not model.strip() or model != model.strip()
        for model in models
    ):
        raise ValueError("m4 must report actual evaluator_models")
    if raw.get("evaluation", {}).get("status", "ok") != "ok":
        raise ValueError("m4 evaluation is incomplete or failed")
    results = []
    for answer, record in zip(answers, measured):
        def read(key, default=None):
            return record.get(key, default) if isinstance(record, Mapping) else getattr(record, key, default)
        for key, source in (("question", "question"), ("answer", "answer"),
                            ("contexts", "contexts"), ("ground_truth", "ground_truth"),
                            ("question_id", "id")):
            value = read(key)
            if value is not None and value != answer[source]:
                raise ValueError(f"m4 row alignment mismatch: id={answer['id']}, {key}")
        metrics = {}
        for metric in METRICS:
            raw_value = read(metric)
            if isinstance(raw_value, bool) or type(raw_value).__name__ == "bool_":
                raise ValueError(f"Invalid boolean {metric} for id={answer['id']}")
            value = float(raw_value)
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"Invalid {metric} for id={answer['id']}: {value}")
            metrics[metric] = value
        results.append(RagasResult(
            question_id=answer["id"], distribution=answer["distribution"],
            question=answer["question"], answer=answer["answer"],
            contexts=answer["contexts"], ground_truth=answer["ground_truth"], **metrics,
        ))
    return RagasEvaluation(results, list(models))


def bottom_10(results: list[RagasResult]) -> list[dict]:
    """Task 3: Rank measured rows; diagnoses are hypotheses for manual review."""
    rows = []
    for rank, result in enumerate(sorted(results, key=lambda row: row.avg_score)[:10], 1):
        diagnosis, fix = DIAGNOSTIC_TREE[result.worst_metric]
        if result.distribution == "adversarial":
            diagnosis += "; kiểm tra answer/context/reference về phiên bản, phủ định và điều kiện"
            fix += "; đối chiếu policy cũ/mới trước khi kết luận nguyên nhân"
        rows.append({
            "rank": rank, "question_id": result.question_id,
            "question": result.question, "distribution": result.distribution,
            "avg_score": round(result.avg_score, 4), "worst_metric": result.worst_metric,
            "diagnosis": diagnosis, "suggested_fix": fix,
        })
    return rows


def cluster_analysis(results: list[RagasResult]) -> dict:
    """Task 4: Count all worst metrics; select quality by mean, not group size."""
    matrix = {metric: {distribution: 0 for distribution in DISTRIBUTIONS} for metric in METRICS}
    for result in results:
        matrix[result.worst_metric][result.distribution] += 1
    means = {}
    for distribution in DISTRIBUTIONS:
        subset = [row.avg_score for row in results if row.distribution == distribution]
        if subset:
            means[distribution] = sum(subset) / len(subset)
    weakest = min(means, key=means.get) if means else None
    dominant = max(matrix, key=lambda metric: sum(matrix[metric].values())) if results else None
    insight = (
        f"Nhóm {weakest} có mean thấp nhất ({means[weakest]:.4f}). "
        f"{dominant} là worst_metric nhiều nhất ({sum(matrix[dominant].values())} câu). "
        "Matrix đếm mọi câu, không chứng minh mọi câu đều lỗi. "
        f"Hướng kiểm chứng: {DIAGNOSTIC_TREE[dominant][1]}."
        if results else "Không có kết quả để xác định nhóm yếu; nhóm rỗng không được gán điểm 0."
    )
    return {"matrix": matrix, "distribution_avg_scores": means,
            "dominant_failure_distribution": weakest, "dominant_failure_metric": dominant,
            "insight": insight}


if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "a", *sys.argv[1:]]))
