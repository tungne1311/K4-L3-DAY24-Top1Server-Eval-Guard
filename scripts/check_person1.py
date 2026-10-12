"""Offline handoff check for CP0 and Phase A/B, without requiring Phase C."""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ANSWERS_PATH, ARTIFACTS_DIR, HUMAN_LABELS_PATH, ROOT_DIR, TEST_SET_PATH
from src import phase_a_ragas, phase_b_judge
from src.experiment_support import read_json, require_completed
from src.report_contracts import (
    validate_answers, validate_markdown, validate_metadata, validate_phase_a, validate_phase_b,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cp0-only', action='store_true', help='Validate saved answers while A/B are pending.')
    args = parser.parse_args()
    require_completed(phase_a_ragas)
    require_completed(phase_b_judge)
    answers, questions, humans = map(read_json, (ANSWERS_PATH, TEST_SET_PATH, HUMAN_LABELS_PATH))
    validate_answers(answers, questions)
    if args.cp0_only:
        print('CP0: 50 source ids, distributions, contexts and generation provenance validated offline.')
        return
    report_a = read_json(Path(ARTIFACTS_DIR) / 'ragas_50q.json')
    report_b = read_json(Path(ARTIFACTS_DIR) / 'judge_results.json')
    validate_phase_a(report_a, answers)
    validate_metadata(report_a, [ANSWERS_PATH, TEST_SET_PATH])
    validate_phase_b(report_b, answers, questions, humans)
    validate_metadata(report_b, [ANSWERS_PATH, TEST_SET_PATH, HUMAN_LABELS_PATH])
    for filename in ('failure_clusters.md', 'bias_report.md'):
        validate_markdown(Path(ROOT_DIR) / 'doc' / 'reports' / filename)
    print('Person 1: CP0, Phase A/B, source hashes and reports validated offline.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, FileNotFoundError, KeyError, TypeError) as error:
        raise SystemExit(f'Person 1 check failed: {error}')
