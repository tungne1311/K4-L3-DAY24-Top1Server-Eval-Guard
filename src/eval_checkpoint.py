"""Persist genuine completed RAGAS cells so API interruptions can resume."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from threading import Lock

from langchain_core.callbacks import BaseCallbackHandler

METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
FIELDS = ("question", "answer", "contexts", "ground_truth")


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def measured_score(value) -> float:
    if isinstance(value, bool) or type(value).__name__ == "bool_":
        raise ValueError("Boolean is not a measured score")
    score = float(value)
    if not math.isfinite(score) or not -1e-12 <= score <= 1 + 1e-12:
        raise ValueError("Invalid measured score")
    # Cosine may exceed its mathematical bound by floating-point roundoff.
    # This never accepts NaN, infinity or a materially out-of-range result.
    return min(1.0, max(0.0, score))


class MeasuredCells(BaseCallbackHandler):
    run_inline = True

    def __init__(self, path: Path, rows: list[dict], profile: dict):
        self.path = path
        self.profile = profile
        self.row_keys = [digest({field: row[field] for field in FIELDS}) for row in rows]
        self.allowed = set(self.row_keys)
        self.cells = {}
        self.runs = {}
        self.lock = Lock()
        if path.exists():
            stored = json.loads(path.read_text(encoding="utf-8"))
            if stored.get("profile") != profile or stored.get("rows") != self.row_keys:
                raise ValueError("Checkpoint does not match evaluator and input rows")
            for key, metrics in stored["cells"].items():
                if key not in self.allowed or any(name not in METRICS for name in metrics):
                    raise ValueError("Invalid checkpoint cells")
                for cell in metrics.values():
                    measured_score(cell["score"])
            self.cells = stored["cells"]

    def get(self, index: int, metric: str):
        cell = self.cells.get(self.row_keys[index], {}).get(metric)
        return measured_score(cell["score"]) if cell is not None else None

    def on_chain_start(self, serialized, inputs, *, run_id, **kwargs):
        name = (serialized or {}).get("name")
        if name in METRICS and all(field in inputs for field in FIELDS):
            key = digest({field: inputs[field] for field in FIELDS})
            if key in self.allowed:
                with self.lock:
                    self.runs[run_id] = (key, name)

    def on_chain_end(self, outputs, *, run_id, **kwargs):
        with self.lock:
            tracked = self.runs.pop(run_id, None)
            if tracked is None:
                return
            try:
                score = measured_score(outputs["output"])
            except (KeyError, ValueError, TypeError):
                return
            key, metric = tracked
            self.cells.setdefault(key, {})[metric] = {
                "score": score, "raw_score": float(outputs["output"]),
                "measured_at": datetime.now(timezone.utc).isoformat(), "engine": "ragas",
            }
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps({
                "profile": self.profile, "rows": self.row_keys, "cells": self.cells,
            }, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
            temporary.replace(self.path)
            count = sum(len(cells) for cells in self.cells.values())
            if count % 10 == 0:
                print(f"Measured cells checkpoint: {count}/{len(self.row_keys)*4}", flush=True)

    def on_chain_error(self, error, *, run_id, **kwargs):
        with self.lock:
            self.runs.pop(run_id, None)
