"""
test_rules.py — Unit tests verifying the integrity of the KnowledgeBase.

Tests verify:
  - The exact number of rules is 72
  - All expected rule IDs (R1–R72) are present
  - Every rule has a non-empty why, how, and label
  - The KnowledgeBase lookup helpers work correctly
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine import KnowledgeBase


# ---------------------------------------------------------------------------
# Fixtures (class-level setup)
# ---------------------------------------------------------------------------

class TestKnowledgeBaseIntegrity:

    def setup_method(self):
        """Instantiate a fresh KnowledgeBase before each test."""
        self.kb = KnowledgeBase()

    # -----------------------------------------------------------------------
    # 1. Rule count
    # -----------------------------------------------------------------------

    def test_total_rule_count_is_72(self):
        """The KnowledgeBase must contain exactly 72 rules."""
        assert len(self.kb) == 72, f"Expected 72 rules, found {len(self.kb)}"

    # -----------------------------------------------------------------------
    # 2. All expected rule IDs are present
    # -----------------------------------------------------------------------

    def test_all_rule_ids_r1_to_r72_present(self):
        """Every rule ID from R1 to R72 must exist in the KnowledgeBase."""
        all_ids = {r.rule_id for r in self.kb.all_rules()}
        missing = []
        for i in range(1, 73):
            rid = f"R{i}"
            if rid not in all_ids:
                missing.append(rid)
        assert not missing, f"Missing rule IDs: {missing}"

    def test_no_duplicate_rule_ids(self):
        """No two rules should share the same rule_id."""
        ids = [r.rule_id for r in self.kb.all_rules()]
        duplicates = [rid for rid in ids if ids.count(rid) > 1]
        assert not duplicates, f"Duplicate rule IDs found: {set(duplicates)}"

    # -----------------------------------------------------------------------
    # 3. Rule documentation completeness
    # -----------------------------------------------------------------------

    def test_all_rules_have_non_empty_why(self):
        """Every rule must have a non-empty 'why' explanation."""
        empty_why = [r.rule_id for r in self.kb.all_rules() if not r.why.strip()]
        assert not empty_why, f"Rules with empty 'why': {empty_why}"

    def test_all_rules_have_non_empty_how(self):
        """Every rule must have a non-empty 'how' explanation."""
        empty_how = [r.rule_id for r in self.kb.all_rules() if not r.how.strip()]
        assert not empty_how, f"Rules with empty 'how': {empty_how}"

    def test_all_rules_have_non_empty_label(self):
        """Every rule must have a non-empty label."""
        empty_label = [r.rule_id for r in self.kb.all_rules() if not r.label.strip()]
        assert not empty_label, f"Rules with empty 'label': {empty_label}"

    # -----------------------------------------------------------------------
    # 4. Rule callables are callable
    # -----------------------------------------------------------------------

    def test_all_rule_conditions_are_callable(self):
        """Every rule's condition must be callable."""
        non_callable = [r.rule_id for r in self.kb.all_rules() if not callable(r.condition)]
        assert not non_callable, f"Rules with non-callable condition: {non_callable}"

    def test_all_rule_conclusions_are_callable(self):
        """Every rule's conclusion must be callable."""
        non_callable = [r.rule_id for r in self.kb.all_rules() if not callable(r.conclusion)]
        assert not non_callable, f"Rules with non-callable conclusion: {non_callable}"

    # -----------------------------------------------------------------------
    # 5. Lookup helpers
    # -----------------------------------------------------------------------

    def test_get_rule_by_id_returns_correct_rule(self):
        """get_rule('R1') must return the rule with rule_id='R1'."""
        rule = self.kb.get_rule("R1")
        assert rule is not None, "R1 not found"
        assert rule.rule_id == "R1"

    def test_get_rule_returns_none_for_invalid_id(self):
        """get_rule with a non-existent ID must return None."""
        assert self.kb.get_rule("R999") is None

    def test_rules_by_label_fragment(self):
        """rules_by_label('Diabetes') should return at least 6 rules (R1–R6 section)."""
        diabetes_rules = self.kb.rules_by_label("Diabetes")
        assert len(diabetes_rules) >= 6, f"Expected >= 6 diabetes rules, got {len(diabetes_rules)}"

    # -----------------------------------------------------------------------
    # 6. Section-specific rule ID ranges
    # -----------------------------------------------------------------------

    def _assert_rules_exist(self, start: int, end: int, section_name: str):
        all_ids = {r.rule_id for r in self.kb.all_rules()}
        for i in range(start, end + 1):
            assert f"R{i}" in all_ids, f"Section '{section_name}': R{i} is missing"

    def test_diabetes_rules_r1_to_r6(self):
        self._assert_rules_exist(1, 6, "Diabetes Detection")

    def test_bp_rules_r7_to_r12(self):
        self._assert_rules_exist(7, 12, "Blood Pressure Detection")

    def test_ckd_stage1_rules_r13_to_r14(self):
        self._assert_rules_exist(13, 14, "CKD Stage 1")

    def test_ckd_stage2_rules_r15_to_r17(self):
        self._assert_rules_exist(15, 17, "CKD Stage 2")

    def test_ckd_stage3_rules_r18_to_r22(self):
        self._assert_rules_exist(18, 22, "CKD Stage 3")

    def test_ckd_stage4_rules_r23_to_r28(self):
        self._assert_rules_exist(23, 28, "CKD Stage 4")

    def test_stage_priority_rules_r29_to_r30(self):
        self._assert_rules_exist(29, 30, "Stage Priority")

    def test_confidence_rules_r31_to_r34(self):
        self._assert_rules_exist(31, 34, "Confidence Calculation")

    def test_risk_level_rules_r35_to_r37(self):
        self._assert_rules_exist(35, 37, "Risk Level")

    def test_interpretation_rules_r38_to_r41(self):
        self._assert_rules_exist(38, 41, "Interpretation")

    def test_bmi_rules_r42_to_r46(self):
        self._assert_rules_exist(42, 46, "BMI Calculation")

    def test_activity_rules_r47_to_r50(self):
        self._assert_rules_exist(47, 50, "Activity Level")

    def test_diet_type_rules_r51_to_r53(self):
        self._assert_rules_exist(51, 53, "Diet Type")

    def test_medical_state_rules_r54_to_r62(self):
        self._assert_rules_exist(54, 62, "Medical State")

    def test_recommendation_rules_r63_to_r72(self):
        self._assert_rules_exist(63, 72, "Diet Recommendations")
