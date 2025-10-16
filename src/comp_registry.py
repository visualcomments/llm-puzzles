from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

@dataclass
class CompConfig:
    slug: str
    # Expected submission CSV headers in order
    submission_headers: List[str] = None
    # Which key in our produced dict maps to each header (usually same names)
    header_keys: List[str] = None
    # Column name in puzzles.csv that is the identifier
    puzzles_id_field: str = "id"
    # The key name we expect from solver output for move string; if solver returns a string,
    # we put it to this field.
    moves_key: str = "moves"
    # Joiner for tokens if solver returns a list of tokens instead of string
    move_joiner: str = "."

    def __post_init__(self):
        if self.submission_headers is None:
            self.submission_headers = ["id", "moves"]
        if self.header_keys is None:
            self.header_keys = ["id", "moves"]

# Defaults: many CayleyPy comps accept id,moves
DEFAULT = CompConfig(slug="generic-id-moves")

# Known competitions registry (customize if any comp deviates)
REGISTRY: Dict[str, CompConfig] = {
    # CayleyPy series (can be overridden later if needed)
    "cayley-py-professor-tetraminx-solve-optimally": CompConfig(slug="cayley-py-professor-tetraminx-solve-optimally"),
    "cayleypy-christophers-jewel": CompConfig(slug="cayleypy-christophers-jewel"),
    "cayleypy-glushkov": CompConfig(slug="cayleypy-glushkov"),
    "cayleypy-rapapport-m2": CompConfig(slug="cayleypy-rapapport-m2"),
    "cayley-py-megaminx": CompConfig(slug="cayley-py-megaminx"),
    "CayleyPy-pancake": CompConfig(slug="CayleyPy-pancake"),
    "cayleypy-reversals": CompConfig(slug="cayleypy-reversals"),
    "cayley-py-444-cube": CompConfig(slug="cayley-py-444-cube"),
    "cayleypy-transposons": CompConfig(slug="cayleypy-transposons"),
    "cayleypy-ihes-cube": CompConfig(slug="cayleypy-ihes-cube"),
    # Santa as fallback example
    "santa-2023": CompConfig(slug="santa-2023"),
}

def get_config(slug: str) -> CompConfig:
    # Return specific config or DEFAULT if unknown
    return REGISTRY.get(slug, DEFAULT)


# ---- Added: common format profiles for quick reuse ----
# You can use these directly as --competition slugs if your contest matches the format,
# or copy them as a base for a new entry.
FORMAT_PROFILES = {
    # Classic "id,moves" with dot-joiner "U.R2.D'"
    "format/moves-dot": CompConfig(
        slug="format/moves-dot",
        submission_headers=["id", "moves"],
        id_col="id",
        move_col="moves",
        move_joiner=".",
        # Optional: a regex hint for acceptable tokens (used only for prompt examples/logging)
        move_token_hint=r"[URDLFBxyz][2']?|\-?[urdlfbxyz]\d+",
    ),
    # "id,moves" with space joiner "U R2 D'"
    "format/moves-space": CompConfig(
        slug="format/moves-space",
        submission_headers=["id", "moves"],
        id_col="id",
        move_col="moves",
        move_joiner=" ",
        move_token_hint=r"[A-Za-z][0-9']*",
    ),
    # "id,solution" with space joiner, some contests use 'solution' column
    "format/solution-space": CompConfig(
        slug="format/solution-space",
        submission_headers=["id", "solution"],
        id_col="id",
        move_col="solution",
        move_joiner=" ",
        move_token_hint=r"[A-Za-z][0-9']*",
    ),
    # "id,moves" with comma joiner "U,R2,D'"
    "format/moves-comma": CompConfig(
        slug="format/moves-comma",
        submission_headers=["id", "moves"],
        id_col="id",
        move_col="moves",
        move_joiner=",",
        move_token_hint=r"[A-Za-z][0-9']*",
    ),
    # Example with an extra numeric column produced by solver: "cost".
    # If your solver returns {"moves": "...", "cost": 123}, it will be written.
    "format/moves-plus-cost": CompConfig(
        slug="format/moves-plus-cost",
        submission_headers=["id", "moves", "cost"],
        id_col="id",
        move_col="moves",
        move_joiner=".",
        extra_cols=["cost"],
        move_token_hint=r"[A-Za-z][0-9']*",
    ),
}

# Merge into REGISTRY if not already present
for k, v in FORMAT_PROFILES.items():
    if k not in REGISTRY:
        REGISTRY[k] = v
