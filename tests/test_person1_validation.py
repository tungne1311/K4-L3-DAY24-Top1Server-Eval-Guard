"""Failure boundaries for Person 1; all evaluators are offline doubles."""
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src import phase_a_ragas as phase_a
from src import phase_b_judge as phase_b

pytestmark = pytest.mark.student


def test_unknown_distribution_is_not_silently_dropped():
    with pytest.raises(ValueError, match="distribution"):
        phase_a.group_by_distribution([{"distribution": "unknown"}])


@pytest.mark.parametrize("mutation", ["short", "nan", "range", "bool", "missing_models", "misaligned", "failed"])
def test_ragas_rejects_invalid_or_unmeasured_rows(monkeypatch, mutation):
    answers = [{"id": 1, "distribution": "factual", "question": "Q", "answer": "A",
                "contexts": ["C"], "ground_truth": "GT"}]
    record = dict(faithfulness=.9, answer_relevancy=.8, context_precision=.7, context_recall=.6)
    raw = {"per_question": [record], "metadata": {"evaluator_models": ["actual-evaluator"]}}
    if mutation == "short":
        raw["per_question"] = []
    elif mutation == "nan":
        record["faithfulness"] = float("nan")
    elif mutation == "range":
        record["context_recall"] = 1.1
    elif mutation == "bool":
        record["faithfulness"] = True
    elif mutation == "missing_models":
        raw["metadata"] = {}
    elif mutation == "misaligned":
        record["question"] = "Other question"
    else:
        raw["evaluation"] = {"status": "failed"}
    monkeypatch.setitem(sys.modules, "src.m4_eval", SimpleNamespace(evaluate_ragas=Mock(return_value=raw)))
    with pytest.raises(ValueError):
        phase_a.run_ragas_50q(answers)


def test_empty_clusters_do_not_assign_zero_quality():
    result = phase_a.cluster_analysis([])
    assert result["distribution_avg_scores"] == {}
    assert result["dominant_failure_distribution"] is None


@pytest.mark.parametrize("bad", [
    {"winner": "C", "reasoning": "R", "scores": {"A": .9, "B": .2}},
    {"winner": "A", "reasoning": "", "scores": {"A": .9, "B": .2}},
    {"winner": "A", "reasoning": "R", "scores": {"A": True, "B": .2}},
    {"winner": "A", "reasoning": "R", "scores": {"A": float("nan"), "B": .2}},
    {"winner": "A", "reasoning": "R", "scores": {"A": 1.1, "B": .2}},
])
def test_pairwise_rejects_invalid_sdk_output(openai_client, bad):
    import json
    openai_client.chat.completions.create.return_value.choices[0].message.content = json.dumps(bad)
    with pytest.raises(ValueError):
        phase_b.pairwise_judge("Q", "A", "B", "GT")


@pytest.mark.parametrize("judge,human", [([], []), ([1], [1, 0]), ([True], [1]), ([2], [1])])
def test_kappa_rejects_invalid_labels(judge, human):
    with pytest.raises(ValueError):
        phase_b.cohen_kappa(judge, human)


def test_constant_agreement_kappa_convention():
    assert phase_b.cohen_kappa([1, 1], [1, 1]) == 0.0


def test_m4_missing_api_key_raises_instead_of_exporting_zero_scores(monkeypatch):
    import config
    from src.m4_eval import evaluate_ragas
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    with pytest.raises(RuntimeError, match="no synthetic scores"):
        evaluate_ragas(["Q"], ["A"], [["C"]], ["GT"])


def test_m4_rejects_input_length_mismatch():
    from src.m4_eval import evaluate_ragas
    with pytest.raises(ValueError, match="equal lengths"):
        evaluate_ragas(["Q"], [], [["C"]], ["GT"])


@pytest.mark.parametrize("answer", ["Tổng Giám đốc (CEO)", "- **12 ngày**\n- **15 ngày**"])
def test_faithfulness_keeps_unpunctuated_answers(answer):
    from pysbd import Segmenter
    from src.m4_eval import _statement_sentences
    prompt_sentences = _statement_sentences(Segmenter(language="en", clean=False), answer)
    assert prompt_sentences.startswith("0:")
    for line in answer.splitlines():
        assert line in prompt_sentences


def test_measured_cells_persist_only_valid_completed_metrics(tmp_path):
    from src.eval_checkpoint import MeasuredCells
    row = {"question": "Q", "answer": "A", "contexts": ["C"], "ground_truth": "GT"}
    path = tmp_path / "measured.json"
    handler = MeasuredCells(path, [row], {"model": "real-model"})
    handler.on_chain_start({"name": "faithfulness"}, row, run_id="ok")
    handler.on_chain_end({"output": .75}, run_id="ok")
    handler.on_chain_start({"name": "context_recall"}, row, run_id="bad")
    handler.on_chain_end({"output": float("nan")}, run_id="bad")
    resumed = MeasuredCells(path, [row], {"model": "real-model"})
    assert resumed.get(0, "faithfulness") == .75
    assert resumed.get(0, "context_recall") is None
    with pytest.raises(ValueError, match="match"):
        MeasuredCells(path, [row], {"model": "different-model"})


def test_measured_score_accepts_only_floating_point_roundoff():
    from src.eval_checkpoint import measured_score
    assert measured_score(1 + 2e-16) == 1
    for value in (float("nan"), float("inf"), True, -0.1, 1.001):
        with pytest.raises(ValueError):
            measured_score(value)
