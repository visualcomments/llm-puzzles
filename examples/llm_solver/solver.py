"""
LLM solver that calls a large language model via helpers from CallLLM.py.
It conforms to universal_adapter expectations: exposes solve_row(row, cfg).
"""

from typing import Dict, Any, Optional, List
import os
import re
import json

# Reuse user's CallLLM.py (it must be importable on PYTHONPATH when running)
# We only use: CONFIG and llm_query, get_models_list
try:
    from CallLLM import CONFIG, llm_query, get_models_list
    import queue
except Exception as e:
    # Soft-import fallback: allow offline generation of empty moves
    CONFIG, llm_query, get_models_list, queue = None, None, None, None  # type: ignore

# Simple prompt template to instruct the LLM to output only the move sequence
PROMPT_TEMPLATE = """You are an expert solver for permutation puzzles on Kaggle.
The competition submission format is a single row with columns defined by the registry;
the move sequence must be exactly what the scorer expects.

Given the puzzle row (JSON):

{row_json}

The move tokens must be separated using the joiner: "{joiner}".
Output ONLY the final move sequence as a single line of plain text.
Do NOT include explanations, code fences, or anything else.
If the state is already solved or if moves are unknown, output an empty string.
"""

def _extract_moves_only(text: str) -> str:
    if not text:
        return ""
    # strip code fences and whitespace
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\\n|```$", "", text, flags=re.MULTILINE).strip()
    # take first non-empty line
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""

def _llm_ask(prompt: str, timeout_s: int = 25) -> str:
    """
    Ask the LLM via CallLLM's llm_query. We pick the first working model.
    If CallLLM isn't importable or online calls fail, return empty string.
    """
    # Offline / disabled mode
    if os.getenv("LLM_OFFLINE", "").lower() in {"1", "true", "yes"}:
        return ""

    if CONFIG is None or llm_query is None or get_models_list is None or queue is None:
        return ""

    try:
        models = get_models_list(CONFIG)
        # simple prioritization: push "gpt-4o-mini" like names first if present
        preferred = [m for m in models if any(k in m.lower() for k in ["gpt-4o", "gpt-4", "gpt-3.5", "claude", "llama"])]
        remaining = [m for m in models if m not in preferred]
        ordered = preferred + remaining
    except Exception:
        ordered = []

    # prepare a tiny queue and retries config (mirrors INITIAL settings)
    progress_queue = queue.Queue()
    retries_cfg = {'max_retries': 1, 'backoff_factor': 1.0}
    for model in (ordered or ["gpt-4o-mini"]):
        try:
            resp = llm_query(
                model=model,
                prompt=prompt,
                retries_config=retries_cfg,
                config=CONFIG,
                progress_queue=progress_queue,
                stage="perm_llm_submission",
            )
            if resp and resp.strip():
                return resp.strip()
        except Exception:
            continue
    return ""

def solve_row(row: Dict[str, Any], cfg) -> str:
    """
    Main entry-point called by universal_adapter. Accepts a dict row and a CompConfig.
    Returns a move string or empty string.
    """
    # Prefer explicit columns if present
    joiner = getattr(cfg, "move_joiner", ".") if hasattr(cfg, "move_joiner") else "."

    # Build a compact json for the prompt
    # Some rows can have large fields; cap lengths of any single field to keep prompt small
    row_compact = {}
    for k, v in row.items():
        s = str(v)
        if len(s) > 2000:
            s = s[:2000] + "..."
        row_compact[k] = s

    row_json = json.dumps(row_compact, ensure_ascii=False)
    prompt = PROMPT_TEMPLATE.format(row_json=row_json, joiner=joiner)

    # Call LLM
    raw = _llm_ask(prompt)
    moves = _extract_moves_only(raw)

    # universal_adapter accepts: str OR list of tokens OR dict {"moves": ...}
    return moves or ""