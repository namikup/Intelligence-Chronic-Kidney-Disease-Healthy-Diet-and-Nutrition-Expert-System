"""
test_engine.py — Integration tests for the InferenceEngine.

Tests verify that given a specific set of patient facts in WorkingMemory,
the forward-chaining engine correctly derives the expected conclusions.
"""

import sys
import os

# Ensure the ckd_expert_system package is importable from the tests folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine import create_expert_system, WorkingMemory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_with_facts(facts: dict):
    """Convenience: create a fresh engine, load facts, run, return (wm, fired)."""
    kb, engine, explainer = create_expert_system()
    wm = WorkingMemory(facts)
    fired = engine.run(wm)
    return wm, fired, explainer


# ---------------------------------------------------------------------------
# Test Suite 1 — Diabetes Detection
# ---------------------------------------------------------------------------

class TestDiabetesDetection:

    def test_three_diabetes_symptoms_set_status_true(self):
        """diabetes_status should be TRUE when 3+ diabetes symptoms are present."""
        wm, fired, _ = run_with_facts({
            "tiredness": "yes",
            "frequent_urination": "yes",
            "excessive_thirst": "yes",
        })
        assert wm.get("diabetes_status") is True, "Expected diabetes_status = True"

    def test_two_diabetes_symptoms_set_status_false(self):
        """diabetes_status should be FALSE when fewer than 3 diabetes symptoms are present."""
        wm, fired, _ = run_with_facts({
            "tiredness": "yes",
            "frequent_urination": "yes",
        })
        assert wm.get("diabetes_status") is False, "Expected diabetes_status = False"

    def test_all_four_diabetes_symptoms(self):
        """All 4 diabetes symptoms should yield diabetes_score of 4 and status True."""
        wm, fired, _ = run_with_facts({
            "tiredness": "yes",
            "frequent_urination": "yes",
            "excessive_thirst": "yes",
            "constant_hunger": "yes",
        })
        assert wm.get("diabetes_score") == 4
        assert wm.get("diabetes_status") is True


# ---------------------------------------------------------------------------
# Test Suite 2 — Blood Pressure Detection
# ---------------------------------------------------------------------------

class TestBloodPressureDetection:

    def test_three_bp_symptoms_set_status_true(self):
        """bp_status should be TRUE when 3+ BP symptoms are reported."""
        wm, fired, _ = run_with_facts({
            "headaches": "yes",
            "dizziness": "yes",
            "blurred_vision_bp": "yes",
        })
        assert wm.get("bp_status") is True, "Expected bp_status = True"

    def test_two_bp_symptoms_set_status_false(self):
        """bp_status should be FALSE when fewer than 3 BP symptoms are present."""
        wm, fired, _ = run_with_facts({
            "headaches": "yes",
            "dizziness": "yes",
        })
        assert wm.get("bp_status") is False, "Expected bp_status = False"


# ---------------------------------------------------------------------------
# Test Suite 3 — CKD Stage Classification
# ---------------------------------------------------------------------------

class TestCKDStageClassification:

    def test_stage1_from_dual_risk_factors(self):
        """CKD Stage 1 is set when both diabetes AND hypertension are confirmed."""
        wm, fired, _ = run_with_facts({
            # Diabetes (3 symptoms → status True)
            "tiredness": "yes",
            "frequent_urination": "yes",
            "excessive_thirst": "yes",
            # BP (3 symptoms → status True)
            "headaches": "yes",
            "dizziness": "yes",
            "blurred_vision_bp": "yes",
            # Physical
            "weight": 70.0,
            "height": 1.70,
            "exercise_per_week": 3,
        })
        assert wm.get("Stage_Determination") == 1, f"Expected Stage 1, got {wm.get('Stage_Determination')}"

    def test_stage2_from_mild_symptoms(self):
        """CKD Stage 2 is set when 2+ Stage-2 symptoms are reported."""
        wm, fired, _ = run_with_facts({
            "mild_swelling": "yes",
            "mild_fatigue": "yes",
            "weight": 65.0,
            "height": 1.65,
            "exercise_per_week": 2,
        })
        assert wm.get("Stage_Determination") == 2, f"Expected Stage 2, got {wm.get('Stage_Determination')}"

    def test_stage3_from_moderate_symptoms(self):
        """CKD Stage 3 is set when 3+ Stage-3 symptoms are reported."""
        wm, fired, _ = run_with_facts({
            "persistent_fatigue": "yes",
            "swelling_extremities": "yes",
            "lower_back_pain": "yes",
            "weight": 85.0,
            "height": 1.75,
            "exercise_per_week": 1,
        })
        assert wm.get("Stage_Determination") == 3, f"Expected Stage 3, got {wm.get('Stage_Determination')}"

    def test_stage4_from_severe_symptoms(self):
        """CKD Stage 4 is set when 4+ Stage-4 symptoms are reported."""
        wm, fired, _ = run_with_facts({
            "nausea": "yes",
            "loss_of_appetite": "yes",
            "difficulty_concentrating": "yes",
            "muscle_cramps": "yes",
            "trouble_sleeping": "yes",
            "weight": 55.0,
            "height": 1.60,
            "exercise_per_week": 0,
        })
        assert wm.get("Stage_Determination") == 4, f"Expected Stage 4, got {wm.get('Stage_Determination')}"

    def test_no_ckd_when_no_symptoms(self):
        """Stage_Determination should be 0 when no CKD symptoms are present."""
        wm, fired, _ = run_with_facts({
            "weight": 70.0,
            "height": 1.70,
            "exercise_per_week": 4,
        })
        assert wm.get("Stage_Determination") == 0, f"Expected Stage 0 (no CKD), got {wm.get('Stage_Determination')}"


# ---------------------------------------------------------------------------
# Test Suite 4 — BMI & Diet Type
# ---------------------------------------------------------------------------

class TestBMIAndDietType:

    def test_bmi_calculated_correctly(self):
        """BMI = weight / height^2, rounded to 2dp."""
        wm, _, _ = run_with_facts({"weight": 70.0, "height": 1.70, "exercise_per_week": 3})
        expected_bmi = round(70.0 / (1.70 ** 2), 2)
        assert wm.get("BMI") == expected_bmi

    def test_overweight_bmi_category(self):
        wm, _, _ = run_with_facts({"weight": 90.0, "height": 1.70, "exercise_per_week": 1})
        assert wm.get("BMI_Category") == "Overweight"

    def test_normal_bmi_category(self):
        wm, _, _ = run_with_facts({"weight": 65.0, "height": 1.75, "exercise_per_week": 3})
        assert wm.get("BMI_Category") == "Normal"

    def test_underweight_bmi_category(self):
        wm, _, _ = run_with_facts({"weight": 45.0, "height": 1.70, "exercise_per_week": 3})
        assert wm.get("BMI_Category") == "Underweight"

    def test_calorie_deficit_for_overweight_low_activity(self):
        wm, _, _ = run_with_facts({"weight": 90.0, "height": 1.70, "exercise_per_week": 1})
        assert wm.get("Final_Diet_Type") == "Calorie_Deficit"

    def test_calorie_maintenance_for_normal_bmi(self):
        wm, _, _ = run_with_facts({"weight": 65.0, "height": 1.75, "exercise_per_week": 3})
        assert wm.get("Final_Diet_Type") == "Calorie_Maintenance"


# ---------------------------------------------------------------------------
# Test Suite 5 — Final Recommendation End-to-End
# ---------------------------------------------------------------------------

class TestEndToEndRecommendation:

    def test_stage1_deficit_recommendation(self):
        """Full pipeline: Stage 1 patient, overweight, low activity → Calorie Deficit recommendation."""
        wm, fired, _ = run_with_facts({
            "tiredness": "yes",
            "frequent_urination": "yes",
            "excessive_thirst": "yes",
            "headaches": "yes",
            "dizziness": "yes",
            "blurred_vision_bp": "yes",
            "weight": 90.0,
            "height": 1.70,
            "exercise_per_week": 1,
        })
        assert wm.get("Medical_State") == "CKD Stage 1 Deficit"
        assert wm.get("Personalized_CKD_Recommendation") is not None

    def test_no_ckd_recommendation(self):
        """Full pipeline: healthy patient → Medical State 'No CKD'."""
        wm, fired, _ = run_with_facts({
            "weight": 65.0,
            "height": 1.75,
            "exercise_per_week": 5,
        })
        assert wm.get("Medical_State") == "No CKD"
        assert wm.get("Personalized_CKD_Recommendation") is not None

    def test_how_summary_contains_fired_rules(self):
        """ExplanationEngine.how_summary should mention at least one fired rule."""
        wm, fired, explainer = run_with_facts({
            "tiredness": "yes",
            "weight": 70.0,
            "height": 1.70,
            "exercise_per_week": 3,
        })
        summary = explainer.how_summary(fired, wm)
        assert "HOW" in summary
        assert len(fired) > 0
