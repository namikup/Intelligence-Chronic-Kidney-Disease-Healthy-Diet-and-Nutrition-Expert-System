"""
models.py — Core data structures for the CKD Expert System.
Contains Rule dataclass and WorkingMemory class.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Rule data structure
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    """One production rule in the knowledge base.

    Attributes
    ----------
    rule_id    : unique label, e.g. "R1"
    condition  : callable (WorkingMemory) -> bool — evaluates the IF part
    conclusion : callable (WorkingMemory) -> None — fires the THEN part
    why        : text shown to the user when asked WHY a question is posed
    how        : text shown to the user when asked HOW a result was reached
    label      : short human-readable description of what the rule does
    """
    rule_id   : str
    condition : Callable[["WorkingMemory"], bool]
    conclusion: Callable[["WorkingMemory"], None]
    why       : str
    how       : str
    label     : str = ""


# ---------------------------------------------------------------------------
# Working Memory
# ---------------------------------------------------------------------------

class WorkingMemory:
    """Dict-backed fact store.

    Facts are key-value pairs.  Every write is appended to `history` so the
    explanation engine can reconstruct the reasoning chain later.
    """

    def __init__(self, initial_facts: Optional[Dict[str, Any]] = None):
        self._facts: Dict[str, Any] = {}
        self.history: List[Tuple[str, Any, str]] = []   # (key, value, rule_id)
        if initial_facts:
            for k, v in initial_facts.items():
                self.set(k, v, source="init")

    # ------------------------------------------------------------------
    def set(self, key: str, value: Any, source: str = "?") -> None:
        self._facts[key] = value
        self.history.append((key, value, source))

    def get(self, key: str, default: Any = None) -> Any:
        return self._facts.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self._facts

    def all_facts(self) -> Dict[str, Any]:
        return dict(self._facts)

    # convenience -------------------------------------------------------
    def increment(self, key: str, amount: int = 1, source: str = "?") -> None:
        self.set(key, self._facts.get(key, 0) + amount, source)