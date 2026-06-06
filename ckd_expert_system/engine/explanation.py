"""
explanation.py — ExplanationEngine class for WHY and HOW explanations.
"""

from typing import List, Dict
from .models import WorkingMemory
from .knowledge_base import KnowledgeBase


class ExplanationEngine:
    """Provides WHY and HOW explanations based on a KnowledgeBase.

    WHY explanations
    ----------------
    Returns the ``why`` text of the *first active rule* whose condition is
    currently True in the provided WorkingMemory — i.e. it answers "Why are
    you asking about X?".

    HOW explanations
    ----------------
    Given the list of fired rules and the WorkingMemory, returns a full
    reasoning trace of how the final diagnosis / recommendation was reached.
    """

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    # ------------------------------------------------------------------
    def why(self, rule_id: str) -> str:
        """Return the WHY explanation text for the given rule_id."""
        rule = self.kb.get_rule(rule_id)
        if rule is None:
            return f"No rule found with id '{rule_id}'."
        return rule.why

    def why_active(self, wm: WorkingMemory) -> List[Dict]:
        """Return WHY texts for all rules whose conditions are currently True.

        Returns list of dicts: {'rule_id', 'label', 'why'}
        """
        active = []
        for rule in self.kb.all_rules():
            try:
                if rule.condition(wm):
                    active.append({
                        "rule_id": rule.rule_id,
                        "label":   rule.label,
                        "why":     rule.why,
                    })
            except Exception:
                pass
        return active

    # ------------------------------------------------------------------
    def how(self, fired_rules: List[str], wm: WorkingMemory) -> List[Dict]:
        """Return a HOW trace for every rule that fired during the session.

        Returns ordered list of dicts: {'rule_id', 'label', 'how'}
        """
        trace = []
        for rid in fired_rules:
            rule = self.kb.get_rule(rid)
            if rule:
                trace.append({
                    "rule_id": rule.rule_id,
                    "label":   rule.label,
                    "how":     rule.how,
                })
        return trace

    def how_summary(self, fired_rules: List[str], wm: WorkingMemory) -> str:
        """Human-readable HOW trace as a single formatted string."""
        lines = ["=== HOW the system reached its conclusion ===\n"]
        for step in self.how(fired_rules, wm):
            lines.append(f"[{step['rule_id']}] {step['label']}")
            lines.append(f"    {step['how']}\n")
        facts = wm.all_facts()
        lines.append("=== Final Working Memory (selected facts) ===")
        key_facts = [
            "diabetes_status", "bp_status", "CKD_Stage", "Stage_Determination",
            "confidence", "risk", "final_interpretation",
            "BMI", "BMI_Category", "Activity_Level", "Diet_Type",
            "Medical_State", "Personalized_CKD_Recommendation",
        ]
        for k in key_facts:
            if k in facts:
                val = facts[k]
                if isinstance(val, str) and len(val) > 80:
                    val = val[:77] + "..."
                lines.append(f"  {k} = {val}")
        return "\n".join(lines)
