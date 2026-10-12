"""M4: genuine RAGAS scores, explicit evaluation status and Diagnostic Tree."""

from __future__ import annotations

import copy
import json
import math
import os
from pathlib import Path
from dataclasses import asdict, dataclass

from config import TEST_SET_PATH

METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def _statement_sentences(segmenter, answer: str) -> str:
    """Preserve Markdown/list statements without changing the recorded answer.

    RAGAS 0.1.x filters out segments that do not end in a period, which can
    yield an empty statement prompt for valid Vietnamese Markdown answers.
    """
    sentences = [sentence.strip() for sentence in segmenter.segment(answer) if sentence.strip()]
    return "\n".join(f"{index}:{sentence}" for index, sentence in enumerate(sentences))


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def evaluate_ragas(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> dict:
    if len({len(questions), len(answers), len(contexts), len(ground_truths)}) != 1:
        raise ValueError("Evaluation inputs must have equal lengths")
    result = {name: 0.0 for name in METRICS}
    result["per_question"] = []
    try:
        from config import (
            EVAL_MODEL,
            EVAL_RPM,
            EVAL_SUPPORTS_N,
            EMBEDDING_MODEL,
            LLM_MODEL,
            OPENAI_API_KEY,
            OPENAI_BASE_URL,
        )

        if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-...":
            raise RuntimeError("OPENAI_API_KEY is missing; RAGAS was not measured")
        if not questions:
            result["evaluation"] = {"status": "empty", "engine": "ragas"}
            return result
        from datasets import Dataset
        import pandas as pd
        from langchain_core.embeddings import Embeddings
        from langchain_core.rate_limiters import InMemoryRateLimiter
        from langchain_openai import ChatOpenAI
        from ragas import evaluate
        from ragas.llms import LangchainLLMWrapper
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
        from ragas.metrics._faithfulness import Faithfulness
        from ragas.run_config import RunConfig

        from src.m2_search import get_dense_encoder
        from src.eval_checkpoint import MeasuredCells, digest, measured_score

        class LocalEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return (
                    get_dense_encoder()
                    .encode(texts, batch_size=8, normalize_embeddings=True)
                    .tolist()
                )

            def embed_query(self, text):
                return self.embed_documents([text])[0]

        class MarkdownFaithfulness(Faithfulness):
            def _create_statements_prompt(self, row):
                return self.statement_prompt.format(
                    question=row["question"], answer=row["answer"],
                    sentences=_statement_sentences(self.sentence_segmenter, row["answer"]),
                )

        # Keep the original RAGAS statement/NLI prompts and scoring formula;
        # only include segments omitted by its terminal-period heuristic.
        faithfulness = MarkdownFaithfulness()

        class SingleCompletionLLM(LangchainLLMWrapper):
            """Send n separate requests instead of one request with n>1."""

            def generate_text(self, prompt, n=1, temperature=None, stop=None, callbacks=None):
                results = [
                    super(SingleCompletionLLM, self).generate_text(
                        prompt, 1, temperature or self.get_temperature(n), stop, callbacks
                    )
                    for _ in range(n)
                ]
                results[0].generations = [[r.generations[0][0] for r in results]]
                return results[0]

            async def agenerate_text(self, prompt, n=1, temperature=None, stop=None, callbacks=None):
                results = [
                    await super(SingleCompletionLLM, self).agenerate_text(
                        prompt, 1, temperature or self.get_temperature(n), stop, callbacks
                    )
                    for _ in range(n)
                ]
                results[0].generations = [[r.generations[0][0] for r in results]]
                return results[0]

        def make_evaluator():
            # Each evaluate() creates a new event loop; give retries a fresh async client.
            llm = ChatOpenAI(
                model=EVAL_MODEL or LLM_MODEL,
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL or None,
                temperature=0,
                # Faithfulness/recall emit a JSON decision for every statement.
                # Leave enough output room rather than truncating valid evaluations.
                max_tokens=4096,
                timeout=180,
                max_retries=1,
                rate_limiter=InMemoryRateLimiter(
                    requests_per_second=EVAL_RPM / 60, max_bucket_size=1
                )
                if EVAL_RPM
                else None,
            )
            return llm if EVAL_SUPPORTS_N else SingleCompletionLLM(llm)

        rows = [dict(question=q, answer=a, contexts=c, ground_truth=g)
                for q, a, c, g in zip(questions, answers, contexts, ground_truths)]
        profile = {"engine": "ragas-0.1.22", "llm": EVAL_MODEL or LLM_MODEL,
                   "embedding": EMBEDDING_MODEL,
                   "adapter_sha256": digest(Path(__file__).read_text(encoding="utf-8")),
                   "checkpoint_sha256": digest(Path(__file__).with_name("eval_checkpoint.py").read_text(encoding="utf-8"))}
        checkpoint_path = Path(__file__).resolve().parents[1] / ".venv" / f"ragas_measured_{digest([profile, rows])[:16]}.json"
        checkpoint = MeasuredCells(checkpoint_path, rows, profile)
        frame = pd.DataFrame([{name: checkpoint.get(i, name) if checkpoint.get(i, name) is not None
                               else float("nan") for name in METRICS} for i in range(len(rows))])
        cached = sum(checkpoint.get(i, name) is not None for i in range(len(rows)) for name in METRICS)
        print(f"Measured cells resumed: {cached}/{len(rows)*4}", flush=True)
        metric_objects = dict(
            zip(
                METRICS,
                [faithfulness, answer_relevancy, context_precision, context_recall],
            )
        )
        def measure(indices, names):
            return evaluate(
                Dataset.from_list([rows[i] for i in indices]),
                metrics=[copy.deepcopy(metric_objects[name]) for name in names],
                llm=make_evaluator(), embeddings=LocalEmbeddings(), callbacks=[checkpoint],
                run_config=RunConfig(timeout=600, max_retries=5, max_wait=90, max_workers=4),
                raise_exceptions=False,
            ).to_pandas()

        if cached == 0:
            frame = measure(list(range(len(rows))), list(METRICS))
        else:
            for name in METRICS:
                missing = [i for i in range(len(rows)) if checkpoint.get(i, name) is None]
                if missing:
                    measured = measure(missing, [name])
                    for offset, index in enumerate(missing):
                        frame.at[index, name] = float(measured.iloc[offset][name])
        retried = []
        # Retry missing scores once; never replace a successfully measured score.
        for name in METRICS:
            missing = [
                int(i)
                for i in frame.index
                if not math.isfinite(float(frame.at[i, name]))
            ]
            if not missing:
                continue
            print(f"Retrying {len(missing)} missing {name} scores", flush=True)
            retry = measure(missing, [name])
            for offset, index in enumerate(missing):
                retried.append({"question_index": index, "metric": name})
                value = float(retry.iloc[offset][name])
                if math.isfinite(value):
                    frame.at[index, name] = value
        invalid = []
        for index, row in frame.iterrows():
            values = {}
            for name in METRICS:
                try:
                    value = measured_score(row[name])
                except (ValueError, TypeError):
                    value = float(row[name])
                    invalid.append({"question_index": int(index), "metric": name})
                values[name] = value
            result["per_question"].append(
                EvalResult(
                    questions[index],
                    answers[index],
                    contexts[index],
                    ground_truths[index],
                    **values,
                )
            )
        if invalid:
            raise ValueError(f"RAGAS has invalid measured scores after retry: {invalid}")
        result["metadata"] = {"evaluator_models": [EVAL_MODEL or LLM_MODEL, EMBEDDING_MODEL]}
        for name in METRICS:
            values = [getattr(item, name) for item in result["per_question"]]
            result[name] = sum(values) / len(values) if values else 0.0
        result["evaluation"] = {
            "status": "partial" if invalid else "ok",
            "engine": "ragas",
            "judge_model": EVAL_MODEL or LLM_MODEL,
            "embedding_model": EMBEDDING_MODEL,
            "invalid_scores": invalid,
            "retried_cells": retried,
            "resumed_cells": cached,
        }
    except Exception as error:  # noqa: BLE001 -- recover at external-service boundary
        raise RuntimeError("RAGAS evaluation failed; no synthetic scores will be exported") from error
    return result


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    tree = {
        "faithfulness": (
            "Unsupported claims in answer",
            "Require source evidence for every claim; reduce temperature.",
        ),
        "answer_relevancy": (
            "Answer does not directly address the question",
            "Answer all subquestions concisely; clarify ambiguous intent.",
        ),
        "context_precision": (
            "Irrelevant or redundant retrieved context",
            "Rerank more candidates; deduplicate parents and filter obsolete versions.",
        ),
        "context_recall": (
            "Relevant evidence missing from retrieved context",
            "Return parent text; increase candidate coverage; retrieve multiple documents.",
        ),
    }
    ordered = sorted(
        eval_results, key=lambda item: sum(getattr(item, m) for m in METRICS) / 4
    )
    failures = []
    for item in ordered[: max(0, bottom_n)]:
        worst = min(METRICS, key=lambda name: getattr(item, name))
        diagnosis, fix = tree[worst]
        failures.append(
            {
                "question": item.question,
                "answer": item.answer,
                "ground_truth": item.ground_truth,
                "contexts": item.contexts,
                "worst_metric": worst,
                "score": getattr(item, worst),
                "average_score": sum(getattr(item, name) for name in METRICS) / 4,
                "metrics": {name: getattr(item, name) for name in METRICS},
                "diagnosis": diagnosis,
                "suggested_fix": fix,
                "error_tree": (
                    "Output incorrect -> context sufficient -> prompt/generation"
                    if worst in ("faithfulness", "answer_relevancy")
                    else "Output incomplete -> context insufficient -> retrieval/chunking"
                ),
            }
        )
    return failures


def save_report(
    results: dict,
    failures: list[dict],
    path: str = "reports/ragas_report.json",
    extra: dict | None = None,
):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    report = {
        "aggregate": {name: results.get(name, 0.0) for name in METRICS},
        "num_questions": len(results.get("per_question", [])),
        "per_question": [asdict(item) for item in results.get("per_question", [])],
        "evaluation": results.get("evaluation", {}),
        "failures": failures,
        **(extra or {}),
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
    print(f"Report saved to {path}", flush=True)
