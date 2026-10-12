"""Shared configuration for K4 / Track 3B: Eval + Guardrail Stack."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")  # Optional: for HuggingFace models
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_RPM = float(os.getenv("LLM_RPM", "0"))
EVAL_MODEL = os.getenv("EVAL_MODEL", LLM_MODEL)
EVAL_RPM = float(os.getenv("EVAL_RPM", "0"))
EVAL_SUPPORTS_N = os.getenv("EVAL_SUPPORTS_N", "1") == "1"
ENRICHMENT_API_KEY = os.getenv("ENRICHMENT_API_KEY", OPENAI_API_KEY)
ENRICHMENT_BASE_URL = os.getenv("ENRICHMENT_BASE_URL", OPENAI_BASE_URL)
ENRICHMENT_MODEL = os.getenv("ENRICHMENT_MODEL", LLM_MODEL)
ENRICHMENT_RPM = float(os.getenv("ENRICHMENT_RPM", "0"))

# --- Qdrant (same as Day 18) ---
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "lab24_production"
NAIVE_COLLECTION = "lab24_naive"

# --- Embedding (same as Day 18) ---
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# --- Chunking (same as Day 18) ---
HIERARCHICAL_PARENT_SIZE = 2048
HIERARCHICAL_CHILD_SIZE = 256
SEMANTIC_THRESHOLD = 0.85

# --- Search (same as Day 18) ---
BM25_TOP_K = 20
DENSE_TOP_K = 20
HYBRID_TOP_K = 20
RERANK_TOP_K = 3

# --- Paths ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
FIXTURES_DIR = os.path.join(ROOT_DIR, "fixtures")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
TEST_SET_PATH = os.path.join(FIXTURES_DIR, "test_set_50q.json")
ANSWERS_PATH = os.path.join(ARTIFACTS_DIR, "answers_50q.json")
HUMAN_LABELS_PATH = os.path.join(FIXTURES_DIR, "human_labels_10q.json")
ADVERSARIAL_SET_PATH = os.path.join(FIXTURES_DIR, "adversarial_set_20.json")
CLEAN_SET_PATH = os.path.join(FIXTURES_DIR, "clean_set_8.json")
OUTPUT_SET_PATH = os.path.join(FIXTURES_DIR, "output_set_4.json")
GUARDRAILS_CONFIG_DIR = os.path.join(ROOT_DIR, "guardrails")
PAIR_QUESTION_IDS = (1, 5, 12, 21, 41)

# --- LLM Judge ---
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gpt-4o-mini")
GENERATION_MAX_TOKENS = int(os.getenv("GENERATION_MAX_TOKENS", "768"))
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-4o-mini")
JUDGE_RPM = float(os.getenv("JUDGE_RPM", "0"))

# --- Guardrail latency budget ---
LATENCY_BUDGET_P95_MS = 500  # Full guard target; Task 12 currently measures input guards only.
PRESIDIO_LANGUAGE = "en"    # Presidio base language; custom VN recognizers added via PatternRecognizer
