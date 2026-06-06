"""
inference.py — InferenceEngine class for forward-chaining inference.
"""

from typing import List
from .models import Rule, WorkingMemory
from .knowledge_base import KnowledgeBase


class InferenceEngine:
    """Agenda-driven forward chaining engine.

    Algorithm
    ---------
    1. Load all rules onto a ``pending`` agenda.
    2. In each cycle, scan every pending rule whose condition is True.
    3. Fire matching rules (execute conclusion), record which rules fired
       in ``fired_rules``, remove them from pending.
    4. Repeat until no new rules fire (fixed point).

    Returns
    -------
    fired_rules : list[str]   — rule IDs in the order they fired
    """

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    # ------------------------------------------------------------------
    def run(self, wm: WorkingMemory) -> List[str]:
        """Run the inference loop.  Returns ordered list of fired rule IDs."""
        fired_rules: List[str] = []
        pending: List[Rule]    = list(self.kb.all_rules())

        changed = True
        while changed:
            changed    = False
            still_pending: List[Rule] = []
            for rule in pending:
                try:
                    fires = rule.condition(wm)
                except Exception:
                    fires = False

                if fires:
                    try:
                        rule.conclusion(wm)
                    except Exception:
                        pass
                    fired_rules.append(rule.rule_id)
                    changed = True
                else:
                    still_pending.append(rule)

            pending = still_pending

        return fired_rules
