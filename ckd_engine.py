# """
# ckd_engine.py
# =============
# CKD Expert System — Backend Logic (Knowledge Engineer Role)
# ============================================================
# Contains:
#   - Rule          : data-class for one production rule
#   - KnowledgeBase : stores all 72 rules; supports lookup by id / conclusion
#   - WorkingMemory : dict-backed fact store with full history
#   - InferenceEngine: forward-chaining engine (agenda-driven)
#   - ExplanationEngine: WHY / HOW traces

# NO print statements, NO input() calls — pure logic for UI integration.
# """

# from __future__ import annotations
# from dataclasses import dataclass, field
# from typing import Any, Callable, Dict, List, Optional, Tuple


# # ---------------------------------------------------------------------------
# # Rule data structure
# # ---------------------------------------------------------------------------

# @dataclass
# class Rule:
#     """One production rule in the knowledge base.

#     Attributes
#     ----------
#     rule_id    : unique label, e.g. "R1"
#     condition  : callable (WorkingMemory) -> bool — evaluates the IF part
#     conclusion : callable (WorkingMemory) -> None — fires the THEN part
#     why        : text shown to the user when asked WHY a question is posed
#     how        : text shown to the user when asked HOW a result was reached
#     label      : short human-readable description of what the rule does
#     """
#     rule_id   : str
#     condition : Callable[["WorkingMemory"], bool]
#     conclusion: Callable[["WorkingMemory"], None]
#     why       : str
#     how       : str
#     label     : str = ""


# # ---------------------------------------------------------------------------
# # Working Memory
# # ---------------------------------------------------------------------------

# class WorkingMemory:
#     """Dict-backed fact store.

#     Facts are key-value pairs.  Every write is appended to `history` so the
#     explanation engine can reconstruct the reasoning chain later.
#     """

#     def __init__(self, initial_facts: Optional[Dict[str, Any]] = None):
#         self._facts: Dict[str, Any] = {}
#         self.history: List[Tuple[str, Any, str]] = []   # (key, value, rule_id)
#         if initial_facts:
#             for k, v in initial_facts.items():
#                 self.set(k, v, source="init")

#     # ------------------------------------------------------------------
#     def set(self, key: str, value: Any, source: str = "?") -> None:
#         self._facts[key] = value
#         self.history.append((key, value, source))

#     def get(self, key: str, default: Any = None) -> Any:
#         return self._facts.get(key, default)

#     def __contains__(self, key: str) -> bool:
#         return key in self._facts

#     def all_facts(self) -> Dict[str, Any]:
#         return dict(self._facts)

#     # convenience -------------------------------------------------------
#     def increment(self, key: str, amount: int = 1, source: str = "?") -> None:
#         self.set(key, self._facts.get(key, 0) + amount, source)


# # ---------------------------------------------------------------------------
# # Knowledge Base — 72 rules
# # ---------------------------------------------------------------------------

# class KnowledgeBase:
#     """Stores all 72 CKD production rules and provides lookup helpers."""

#     def __init__(self):
#         self._rules: List[Rule] = []
#         self._build_rules()

#     # ------------------------------------------------------------------
#     # Public API
#     # ------------------------------------------------------------------

#     def all_rules(self) -> List[Rule]:
#         return list(self._rules)

#     def get_rule(self, rule_id: str) -> Optional[Rule]:
#         for r in self._rules:
#             if r.rule_id == rule_id:
#                 return r
#         return None

#     def rules_by_label(self, label_fragment: str) -> List[Rule]:
#         return [r for r in self._rules if label_fragment.lower() in r.label.lower()]

#     def __len__(self):
#         return len(self._rules)

#     # ------------------------------------------------------------------
#     # Rule builder — all 72 rules
#     # ------------------------------------------------------------------

#     def _add(self, rule_id, condition, conclusion, why, how, label=""):
#         self._rules.append(Rule(rule_id, condition, conclusion, why, how, label))

#     def _build_rules(self):

#         # ── SECTION 1 : DIABETES DETECTION (R1–R6) ────────────────────

#         self._add(
#             "R1",
#             condition  = lambda wm: wm.get("tiredness") == "yes",
#             conclusion = lambda wm: wm.increment("diabetes_score", 1, "R1"),
#             why = (
#                 "Tiredness / fatigue is a classic early symptom of uncontrolled blood "
#                 "glucose, because cells cannot absorb sugar efficiently. "
#                 "We ask this to contribute to the diabetes symptom score."
#             ),
#             how = (
#                 "R1 fired because tiredness = yes. "
#                 "diabetes_score was incremented by 1."
#             ),
#             label = "Diabetes: tiredness symptom"
#         )

#         self._add(
#             "R2",
#             condition  = lambda wm: wm.get("frequent_urination") == "yes",
#             conclusion = lambda wm: wm.increment("diabetes_score", 1, "R2"),
#             why = (
#                 "Frequent urination (polyuria) occurs when excess glucose forces the "
#                 "kidneys to filter more fluid. It is one of the cardinal signs of "
#                 "diabetes and contributes to the diabetes symptom score."
#             ),
#             how = (
#                 "R2 fired because frequent_urination = yes. "
#                 "diabetes_score was incremented by 1."
#             ),
#             label = "Diabetes: frequent urination symptom"
#         )

#         self._add(
#             "R3",
#             condition  = lambda wm: wm.get("excessive_thirst") == "yes",
#             conclusion = lambda wm: wm.increment("diabetes_score", 1, "R3"),
#             why = (
#                 "Excessive thirst (polydipsia) accompanies polyuria — the body tries to "
#                 "compensate for fluid lost through frequent urination. It is a strong "
#                 "indicator of elevated blood sugar."
#             ),
#             how = (
#                 "R3 fired because excessive_thirst = yes. "
#                 "diabetes_score was incremented by 1."
#             ),
#             label = "Diabetes: excessive thirst symptom"
#         )

#         self._add(
#             "R4",
#             condition  = lambda wm: wm.get("constant_hunger") == "yes",
#             conclusion = lambda wm: wm.increment("diabetes_score", 1, "R4"),
#             why = (
#                 "Constant hunger (polyphagia) happens when cells are deprived of glucose "
#                 "despite high blood sugar levels, triggering persistent hunger signals."
#             ),
#             how = (
#                 "R4 fired because constant_hunger = yes. "
#                 "diabetes_score was incremented by 1."
#             ),
#             label = "Diabetes: constant hunger symptom"
#         )

#         self._add(
#             "R5",
#             condition  = lambda wm: wm.get("diabetes_score", 0) >= 3,
#             conclusion = lambda wm: wm.set("diabetes_status", True, "R5"),
#             why = (
#                 "A diabetes_score of 3 or more means at least three classic diabetes "
#                 "symptoms are present, which is the threshold used by this system to "
#                 "flag a likely diabetic condition."
#             ),
#             how = (
#                 "R5 fired because diabetes_score >= 3. "
#                 "diabetes_status has been set to TRUE, indicating likely diabetes."
#             ),
#             label = "Diabetes: positive status (score >= 3)"
#         )

#         self._add(
#             "R6",
#             condition  = lambda wm: wm.get("diabetes_score", 0) < 3,
#             conclusion = lambda wm: wm.set("diabetes_status", False, "R6"),
#             why = (
#                 "Fewer than 3 diabetes symptoms are present. The system does not flag "
#                 "diabetes at this threshold, though the user should still consult a doctor."
#             ),
#             how = (
#                 "R6 fired because diabetes_score < 3. "
#                 "diabetes_status has been set to FALSE."
#             ),
#             label = "Diabetes: negative status (score < 3)"
#         )

#         # ── SECTION 2 : BLOOD PRESSURE DETECTION (R7–R12) ─────────────

#         self._add(
#             "R7",
#             condition  = lambda wm: wm.get("headaches") == "yes",
#             conclusion = lambda wm: wm.increment("bp_score", 1, "R7"),
#             why = (
#                 "Persistent headaches — especially at the back of the head — are a "
#                 "recognised symptom of high blood pressure (hypertension)."
#             ),
#             how = (
#                 "R7 fired because headaches = yes. "
#                 "bp_score was incremented by 1."
#             ),
#             label = "BP: headaches symptom"
#         )

#         self._add(
#             "R8",
#             condition  = lambda wm: wm.get("dizziness") == "yes",
#             conclusion = lambda wm: wm.increment("bp_score", 1, "R8"),
#             why = (
#                 "Dizziness can result from elevated blood pressure affecting circulation "
#                 "to the brain, and is therefore included in the hypertension symptom score."
#             ),
#             how = (
#                 "R8 fired because dizziness = yes. "
#                 "bp_score was incremented by 1."
#             ),
#             label = "BP: dizziness symptom"
#         )

#         self._add(
#             "R9",
#             condition  = lambda wm: wm.get("blurred_vision_bp") == "yes",
#             conclusion = lambda wm: wm.increment("bp_score", 1, "R9"),
#             why = (
#                 "High blood pressure can damage the small blood vessels in the retina, "
#                 "causing blurred vision. This symptom contributes to the BP score."
#             ),
#             how = (
#                 "R9 fired because blurred_vision_bp = yes. "
#                 "bp_score was incremented by 1."
#             ),
#             label = "BP: blurred vision symptom"
#         )

#         self._add(
#             "R10",
#             condition  = lambda wm: wm.get("chest_discomfort") == "yes",
#             conclusion = lambda wm: wm.increment("bp_score", 1, "R10"),
#             why = (
#                 "Chest discomfort or tightness can indicate elevated blood pressure "
#                 "putting strain on the heart. It is included as a serious BP symptom."
#             ),
#             how = (
#                 "R10 fired because chest_discomfort = yes. "
#                 "bp_score was incremented by 1."
#             ),
#             label = "BP: chest discomfort symptom"
#         )

#         self._add(
#             "R11",
#             condition  = lambda wm: wm.get("bp_score", 0) >= 3,
#             conclusion = lambda wm: wm.set("bp_status", True, "R11"),
#             why = (
#                 "Three or more blood pressure symptoms meet the system's threshold to "
#                 "flag likely hypertension, which is a major risk factor for CKD."
#             ),
#             how = (
#                 "R11 fired because bp_score >= 3. "
#                 "bp_status has been set to TRUE, indicating likely high blood pressure."
#             ),
#             label = "BP: positive status (score >= 3)"
#         )

#         self._add(
#             "R12",
#             condition  = lambda wm: wm.get("bp_score", 0) < 3,
#             conclusion = lambda wm: wm.set("bp_status", False, "R12"),
#             why = (
#                 "Fewer than 3 blood pressure symptoms are present. "
#                 "The system does not flag hypertension at this threshold."
#             ),
#             how = (
#                 "R12 fired because bp_score < 3. "
#                 "bp_status has been set to FALSE."
#             ),
#             label = "BP: negative status (score < 3)"
#         )

#         # ── SECTION 3 : CKD STAGE 1 (R13–R14) ─────────────────────────

#         self._add(
#             "R13",
#             condition  = lambda wm: (
#                 wm.get("diabetes_status") is True and
#                 wm.get("bp_status") is True
#             ),
#             conclusion = lambda wm: wm.set("stage1_score", 1, "R13"),
#             why = (
#                 "CKD Stage 1 is characterised by near-normal kidney function but with "
#                 "underlying risk factors. Both diabetes AND hypertension together are "
#                 "the primary dual risk factors for early CKD."
#             ),
#             how = (
#                 "R13 fired because diabetes_status = TRUE AND bp_status = TRUE. "
#                 "stage1_score has been set to 1, indicating Stage 1 risk criteria are met."
#             ),
#             label = "CKD Stage 1: dual risk factor score"
#         )

#         self._add(
#             "R14",
#             condition  = lambda wm: wm.get("stage1_score") == 1,
#             conclusion = lambda wm: wm.set("CKD_Stage", 1, "R14"),
#             why = (
#                 "We are confirming whether the Stage 1 criteria (stage1_score = 1) "
#                 "are sufficient to classify the condition as CKD Stage 1."
#             ),
#             how = (
#                 "R14 fired because stage1_score = 1. "
#                 "CKD_Stage has been set to 1."
#             ),
#             label = "CKD Stage 1: confirm stage"
#         )

#         # ── SECTION 4 : CKD STAGE 2 (R15–R17) ─────────────────────────

#         self._add(
#             "R15",
#             condition  = lambda wm: wm.get("mild_swelling") == "yes",
#             conclusion = lambda wm: wm.increment("stage2_score", 1, "R15"),
#             why = (
#                 "Mild swelling (oedema), particularly in the ankles or feet, can signal "
#                 "the kidneys are beginning to retain more fluid — a Stage 2 CKD indicator."
#             ),
#             how = (
#                 "R15 fired because mild_swelling = yes. "
#                 "stage2_score was incremented by 1."
#             ),
#             label = "CKD Stage 2: mild swelling symptom"
#         )

#         self._add(
#             "R16",
#             condition  = lambda wm: wm.get("mild_fatigue") == "yes",
#             conclusion = lambda wm: wm.increment("stage2_score", 1, "R16"),
#             why = (
#                 "Mild but persistent fatigue at Stage 2 often results from the kidneys' "
#                 "reduced ability to filter waste, leading to a slight build-up of toxins."
#             ),
#             how = (
#                 "R16 fired because mild_fatigue = yes. "
#                 "stage2_score was incremented by 1."
#             ),
#             label = "CKD Stage 2: mild fatigue symptom"
#         )

#         self._add(
#             "R17",
#             condition  = lambda wm: wm.get("stage2_score", 0) >= 2,
#             conclusion = lambda wm: wm.set("CKD_Stage", 2, "R17"),
#             why = (
#                 "Two Stage 2 symptoms are enough for the system to classify the condition "
#                 "as CKD Stage 2, where kidney damage is mild but confirmed."
#             ),
#             how = (
#                 "R17 fired because stage2_score >= 2. "
#                 "CKD_Stage has been set to 2."
#             ),
#             label = "CKD Stage 2: confirm stage (score >= 2)"
#         )

#         # ── SECTION 5 : CKD STAGE 3 (R18–R22) ─────────────────────────

#         self._add(
#             "R18",
#             condition  = lambda wm: wm.get("persistent_fatigue") == "yes",
#             conclusion = lambda wm: wm.increment("stage3_score", 1, "R18"),
#             why = (
#                 "Persistent and worsening fatigue at Stage 3 is caused by anaemia — the "
#                 "damaged kidneys produce less erythropoietin, reducing red blood cell count."
#             ),
#             how = (
#                 "R18 fired because persistent_fatigue = yes. "
#                 "stage3_score was incremented by 1."
#             ),
#             label = "CKD Stage 3: persistent fatigue symptom"
#         )

#         self._add(
#             "R19",
#             condition  = lambda wm: wm.get("swelling_extremities") == "yes",
#             conclusion = lambda wm: wm.increment("stage3_score", 1, "R19"),
#             why = (
#                 "Swelling in the hands, feet, and legs (oedema) becomes more pronounced "
#                 "at Stage 3 as the kidneys struggle to regulate fluid and sodium balance."
#             ),
#             how = (
#                 "R19 fired because swelling_extremities = yes. "
#                 "stage3_score was incremented by 1."
#             ),
#             label = "CKD Stage 3: swelling extremities symptom"
#         )

#         self._add(
#             "R20",
#             condition  = lambda wm: wm.get("lower_back_pain") == "yes",
#             conclusion = lambda wm: wm.increment("stage3_score", 1, "R20"),
#             why = (
#                 "Lower back or flank pain in CKD can indicate kidney inflammation or "
#                 "the increased strain placed on the kidneys as function declines."
#             ),
#             how = (
#                 "R20 fired because lower_back_pain = yes. "
#                 "stage3_score was incremented by 1."
#             ),
#             label = "CKD Stage 3: lower back pain symptom"
#         )

#         self._add(
#             "R21",
#             condition  = lambda wm: wm.get("itchy_skin") == "yes",
#             conclusion = lambda wm: wm.increment("stage3_score", 1, "R21"),
#             why = (
#                 "Itchy skin (pruritus) at Stage 3 CKD results from phosphorus build-up "
#                 "in the blood when kidneys can no longer adequately filter minerals."
#             ),
#             how = (
#                 "R21 fired because itchy_skin = yes. "
#                 "stage3_score was incremented by 1."
#             ),
#             label = "CKD Stage 3: itchy skin symptom"
#         )

#         self._add(
#             "R22",
#             condition  = lambda wm: wm.get("stage3_score", 0) >= 3,
#             conclusion = lambda wm: wm.set("CKD_Stage", 3, "R22"),
#             why = (
#                 "Three or more Stage 3 symptoms indicate moderate-to-severe kidney "
#                 "damage (GFR 30–59 mL/min), which the system classifies as CKD Stage 3."
#             ),
#             how = (
#                 "R22 fired because stage3_score >= 3. "
#                 "CKD_Stage has been set to 3."
#             ),
#             label = "CKD Stage 3: confirm stage (score >= 3)"
#         )

#         # ── SECTION 6 : CKD STAGE 4 (R23–R28) ─────────────────────────

#         self._add(
#             "R23",
#             condition  = lambda wm: wm.get("nausea") == "yes",
#             conclusion = lambda wm: wm.increment("stage4_score", 1, "R23"),
#             why = (
#                 "Nausea at Stage 4 CKD is caused by a high build-up of urea and waste "
#                 "products (uraemia) that the severely damaged kidneys cannot excrete."
#             ),
#             how = (
#                 "R23 fired because nausea = yes. "
#                 "stage4_score was incremented by 1."
#             ),
#             label = "CKD Stage 4: nausea symptom"
#         )

#         self._add(
#             "R24",
#             condition  = lambda wm: wm.get("loss_of_appetite") == "yes",
#             conclusion = lambda wm: wm.increment("stage4_score", 1, "R24"),
#             why = (
#                 "Loss of appetite (anorexia) at advanced CKD is linked to uraemia and "
#                 "nausea, and is a serious sign of deteriorating kidney function."
#             ),
#             how = (
#                 "R24 fired because loss_of_appetite = yes. "
#                 "stage4_score was incremented by 1."
#             ),
#             label = "CKD Stage 4: loss of appetite symptom"
#         )

#         self._add(
#             "R25",
#             condition  = lambda wm: wm.get("difficulty_concentrating") == "yes",
#             conclusion = lambda wm: wm.increment("stage4_score", 1, "R25"),
#             why = (
#                 "Difficulty concentrating (cognitive impairment) at Stage 4 is due to "
#                 "toxic waste products crossing the blood-brain barrier when kidneys fail."
#             ),
#             how = (
#                 "R25 fired because difficulty_concentrating = yes. "
#                 "stage4_score was incremented by 1."
#             ),
#             label = "CKD Stage 4: difficulty concentrating symptom"
#         )

#         self._add(
#             "R26",
#             condition  = lambda wm: wm.get("muscle_cramps") == "yes",
#             conclusion = lambda wm: wm.increment("stage4_score", 1, "R26"),
#             why = (
#                 "Muscle cramps at Stage 4 CKD occur due to electrolyte imbalances "
#                 "(low calcium, high phosphorus) as the kidneys lose mineral-regulation ability."
#             ),
#             how = (
#                 "R26 fired because muscle_cramps = yes. "
#                 "stage4_score was incremented by 1."
#             ),
#             label = "CKD Stage 4: muscle cramps symptom"
#         )

#         self._add(
#             "R27",
#             condition  = lambda wm: wm.get("trouble_sleeping") == "yes",
#             conclusion = lambda wm: wm.increment("stage4_score", 1, "R27"),
#             why = (
#                 "Trouble sleeping (insomnia/restless leg syndrome) at Stage 4 CKD is "
#                 "linked to toxin accumulation and is a commonly reported symptom."
#             ),
#             how = (
#                 "R27 fired because trouble_sleeping = yes. "
#                 "stage4_score was incremented by 1."
#             ),
#             label = "CKD Stage 4: trouble sleeping symptom"
#         )

#         self._add(
#             "R28",
#             condition  = lambda wm: wm.get("stage4_score", 0) >= 4,
#             conclusion = lambda wm: wm.set("CKD_Stage", 4, "R28"),
#             why = (
#                 "Four or more Stage 4 symptoms indicate severely reduced kidney function "
#                 "(GFR 15–29 mL/min). The system classifies this as CKD Stage 4."
#             ),
#             how = (
#                 "R28 fired because stage4_score >= 4. "
#                 "CKD_Stage has been set to 4."
#             ),
#             label = "CKD Stage 4: confirm stage (score >= 4)"
#         )

#         # ── SECTION 7 : STAGE PRIORITY (R29–R30) ───────────────────────

#         def _r29_condition(wm):
#             return wm.get("CKD_Stage") not in (1, 2, 3, 4)

#         def _r29_conclusion(wm):
#             wm.set("Stage_Determination", 0, "R29")

#         self._add(
#             "R29",
#             condition  = _r29_condition,
#             conclusion = _r29_conclusion,
#             why = (
#                 "If none of the CKD stage rules have fired, the system defaults to "
#                 "Stage_Determination = 0, meaning no CKD stage was detected."
#             ),
#             how = (
#                 "R29 fired because no CKD_Stage value (1-4) was set. "
#                 "Stage_Determination has been set to 0 (no CKD detected)."
#             ),
#             label = "Stage priority: no CKD detected"
#         )

#         self._add(
#             "R30",
#             condition  = lambda wm: wm.get("CKD_Stage") in (1, 2, 3, 4),
#             conclusion = lambda wm: wm.set("Stage_Determination", wm.get("CKD_Stage"), "R30"),
#             why = (
#                 "This rule propagates the detected CKD stage to Stage_Determination, "
#                 "which is the authoritative stage fact used by all downstream rules."
#             ),
#             how = (
#                 "R30 fired because CKD_Stage is set to a valid stage (1–4). "
#                 "Stage_Determination has been set equal to CKD_Stage."
#             ),
#             label = "Stage priority: propagate CKD stage"
#         )

#         # ── SECTION 8 : CONFIDENCE CALCULATION (R31–R34) ───────────────

#         def _confidence_r31(wm):
#             wm.set("confidence", round((wm.get("stage1_score", 0) / 1) * 100, 1), "R31")

#         def _confidence_r32(wm):
#             wm.set("confidence", round((wm.get("stage2_score", 0) / 2) * 100, 1), "R32")

#         def _confidence_r33(wm):
#             wm.set("confidence", round((wm.get("stage3_score", 0) / 4) * 100, 1), "R33")

#         def _confidence_r34(wm):
#             wm.set("confidence", round((wm.get("stage4_score", 0) / 5) * 100, 1), "R34")

#         self._add(
#             "R31",
#             condition  = lambda wm: wm.get("Stage_Determination") == 1,
#             conclusion = _confidence_r31,
#             why = (
#                 "For Stage 1, confidence is calculated as (stage1_score / 1) * 100. "
#                 "The maximum score is 1 (both risk factors present), so 100% = fully confirmed."
#             ),
#             how = (
#                 "R31 fired because Stage_Determination = 1. "
#                 "confidence = (stage1_score / 1) × 100."
#             ),
#             label = "Confidence: Stage 1 calculation"
#         )

#         self._add(
#             "R32",
#             condition  = lambda wm: wm.get("Stage_Determination") == 2,
#             conclusion = _confidence_r32,
#             why = (
#                 "For Stage 2, confidence is (stage2_score / 2) * 100, where 2 is the "
#                 "maximum number of Stage 2 symptoms tracked."
#             ),
#             how = (
#                 "R32 fired because Stage_Determination = 2. "
#                 "confidence = (stage2_score / 2) × 100."
#             ),
#             label = "Confidence: Stage 2 calculation"
#         )

#         self._add(
#             "R33",
#             condition  = lambda wm: wm.get("Stage_Determination") == 3,
#             conclusion = _confidence_r33,
#             why = (
#                 "For Stage 3, confidence is (stage3_score / 4) * 100, where 4 is the "
#                 "maximum number of Stage 3 symptoms tracked."
#             ),
#             how = (
#                 "R33 fired because Stage_Determination = 3. "
#                 "confidence = (stage3_score / 4) × 100."
#             ),
#             label = "Confidence: Stage 3 calculation"
#         )

#         self._add(
#             "R34",
#             condition  = lambda wm: wm.get("Stage_Determination") == 4,
#             conclusion = _confidence_r34,
#             why = (
#                 "For Stage 4, confidence is (stage4_score / 5) * 100, where 5 is the "
#                 "maximum number of Stage 4 symptoms tracked."
#             ),
#             how = (
#                 "R34 fired because Stage_Determination = 4. "
#                 "confidence = (stage4_score / 5) × 100."
#             ),
#             label = "Confidence: Stage 4 calculation"
#         )

#         # ── SECTION 9 : RISK LEVEL (R35–R37) ───────────────────────────

#         self._add(
#             "R35",
#             condition  = lambda wm: wm.get("confidence", 0) >= 75,
#             conclusion = lambda wm: wm.set("risk", "HIGH", "R35"),
#             why = (
#                 "A confidence of 75% or above indicates strong symptom alignment with "
#                 "the detected CKD stage, warranting a HIGH risk classification."
#             ),
#             how = (
#                 "R35 fired because confidence >= 75. "
#                 "risk has been set to HIGH."
#             ),
#             label = "Risk level: HIGH (confidence >= 75)"
#         )

#         self._add(
#             "R36",
#             condition  = lambda wm: 50 <= wm.get("confidence", 0) < 75,
#             conclusion = lambda wm: wm.set("risk", "MODERATE", "R36"),
#             why = (
#                 "A confidence between 50% and 74% shows moderate symptom alignment, "
#                 "suggesting the user should be monitored for potential CKD progression."
#             ),
#             how = (
#                 "R36 fired because 50 <= confidence < 75. "
#                 "risk has been set to MODERATE."
#             ),
#             label = "Risk level: MODERATE (50 <= confidence < 75)"
#         )

#         self._add(
#             "R37",
#             condition  = lambda wm: wm.get("confidence", 0) < 50,
#             conclusion = lambda wm: wm.set("risk", "LOW", "R37"),
#             why = (
#                 "A confidence below 50% means fewer than half the expected symptoms for "
#                 "the detected stage are present, indicating a LOW risk classification."
#             ),
#             how = (
#                 "R37 fired because confidence < 50. "
#                 "risk has been set to LOW."
#             ),
#             label = "Risk level: LOW (confidence < 50)"
#         )

#         # ── SECTION 10 : INTERPRETATION (R38–R41) ──────────────────────

#         self._add(
#             "R38",
#             condition  = lambda wm: wm.get("risk") == "HIGH",
#             conclusion = lambda wm: wm.set(
#                 "interpretation", "High likelihood of CKD condition", "R38"),
#             why = (
#                 "HIGH risk means most symptoms for the detected CKD stage are present. "
#                 "The interpretation is set to reflect a high CKD likelihood."
#             ),
#             how = (
#                 "R38 fired because risk = HIGH. "
#                 "interpretation = 'High likelihood of CKD condition'."
#             ),
#             label = "Interpretation: high likelihood"
#         )

#         self._add(
#             "R39",
#             condition  = lambda wm: wm.get("risk") == "MODERATE",
#             conclusion = lambda wm: wm.set(
#                 "interpretation", "Moderate likelihood, monitoring required", "R39"),
#             why = (
#                 "MODERATE risk means roughly half the expected symptoms are present. "
#                 "The system recommends monitoring and follow-up clinical assessment."
#             ),
#             how = (
#                 "R39 fired because risk = MODERATE. "
#                 "interpretation = 'Moderate likelihood, monitoring required'."
#             ),
#             label = "Interpretation: moderate likelihood"
#         )

#         self._add(
#             "R40",
#             condition  = lambda wm: wm.get("risk") == "LOW",
#             conclusion = lambda wm: wm.set(
#                 "interpretation", "Low likelihood, weak symptom match", "R40"),
#             why = (
#                 "LOW risk means fewer than half the expected symptoms for the detected "
#                 "stage are present. The system flags this as a weak symptom match."
#             ),
#             how = (
#                 "R40 fired because risk = LOW. "
#                 "interpretation = 'Low likelihood, weak symptom match'."
#             ),
#             label = "Interpretation: low likelihood"
#         )

#         self._add(
#             "R41",
#             condition  = lambda wm: wm.get("interpretation") in (
#                 "Low likelihood, weak symptom match",
#                 "Moderate likelihood, monitoring required",
#                 "High likelihood of CKD condition",
#             ),
#             conclusion = lambda wm: wm.set(
#                 "final_interpretation", wm.get("interpretation"), "R41"),
#             why = (
#                 "This rule finalises the interpretation by copying it to "
#                 "final_interpretation, which is the fact consumed by the output layer."
#             ),
#             how = (
#                 "R41 fired because interpretation is set to a valid value. "
#                 "final_interpretation = interpretation."
#             ),
#             label = "Interpretation: finalise"
#         )

#         # ── SECTION 11 : BMI CALCULATION (R42–R46) ─────────────────────

#         def _r42_condition(wm):
#             return (wm.get("weight") is not None and
#                     wm.get("height") is not None and
#                     wm.get("height", 0) > 0)

#         def _r42_conclusion(wm):
#             h = wm.get("height")
#             w = wm.get("weight")
#             bmi = round(w / (h * h), 2)
#             wm.set("BMI", bmi, "R42")

#         self._add(
#             "R42",
#             condition  = _r42_condition,
#             conclusion = _r42_conclusion,
#             why = (
#                 "BMI (Body Mass Index) = weight (kg) ÷ height² (m²). "
#                 "It is required to classify the user's weight category, which in turn "
#                 "determines the appropriate diet type."
#             ),
#             how = (
#                 "R42 fired because weight and height are provided. "
#                 "BMI = weight / (height × height)."
#             ),
#             label = "BMI: calculate value"
#         )

#         self._add(
#             "R43",
#             condition  = lambda wm: wm.get("BMI", 0) >= 25,
#             conclusion = lambda wm: wm.set("BMI_Category", "Overweight", "R43"),
#             why = (
#                 "A BMI of 25 or above is classified as Overweight according to WHO "
#                 "standards. Overweight status is a known risk factor for CKD progression."
#             ),
#             how = (
#                 "R43 fired because BMI >= 25. "
#                 "BMI_Category has been set to Overweight."
#             ),
#             label = "BMI: Overweight (>= 25)"
#         )

#         self._add(
#             "R44",
#             condition  = lambda wm: 18.5 <= wm.get("BMI", 0) <= 24.9,
#             conclusion = lambda wm: wm.set("BMI_Category", "Normal", "R44"),
#             why = (
#                 "A BMI between 18.5 and 24.9 falls within the Normal range per WHO "
#                 "guidelines, indicating a healthy body weight."
#             ),
#             how = (
#                 "R44 fired because 18.5 <= BMI <= 24.9. "
#                 "BMI_Category has been set to Normal."
#             ),
#             label = "BMI: Normal (18.5 – 24.9)"
#         )

#         self._add(
#             "R45",
#             condition  = lambda wm: wm.get("BMI", 99) < 18.5,
#             conclusion = lambda wm: wm.set("BMI_Category", "Underweight", "R45"),
#             why = (
#                 "A BMI below 18.5 is classified as Underweight. This may indicate "
#                 "malnutrition, which requires a special dietary approach for CKD patients."
#             ),
#             how = (
#                 "R45 fired because BMI < 18.5. "
#                 "BMI_Category has been set to Underweight."
#             ),
#             label = "BMI: Underweight (< 18.5)"
#         )

#         self._add(
#             "R46",
#             condition  = lambda wm: wm.get("BMI_Category") in (
#                 "Overweight", "Normal", "Underweight"),
#             conclusion = lambda wm: wm.set(
#                 "Final_Bmi_Category", wm.get("BMI_Category"), "R46"),
#             why = (
#                 "This rule finalises BMI classification by copying BMI_Category to "
#                 "Final_Bmi_Category, consumed by the diet-type rules downstream."
#             ),
#             how = (
#                 "R46 fired because BMI_Category is set to a valid category. "
#                 "Final_Bmi_Category = BMI_Category."
#             ),
#             label = "BMI: finalise category"
#         )

#         # ── SECTION 12 : ACTIVITY LEVEL (R47–R50) ──────────────────────

#         self._add(
#             "R47",
#             condition  = lambda wm: wm.get("exercise_per_week", 99) <= 1,
#             conclusion = lambda wm: wm.set("Activity_Level", "Low", "R47"),
#             why = (
#                 "Exercising once a week or less is classified as a Low activity level, "
#                 "which influences the calorie requirement and recommended diet type."
#             ),
#             how = (
#                 "R47 fired because exercise_per_week <= 1. "
#                 "Activity_Level has been set to Low."
#             ),
#             label = "Activity: Low (<= 1 day/week)"
#         )

#         self._add(
#             "R48",
#             condition  = lambda wm: 2 <= wm.get("exercise_per_week", 0) <= 4,
#             conclusion = lambda wm: wm.set("Activity_Level", "Moderate", "R48"),
#             why = (
#                 "Exercising 2–4 days per week is a Moderate activity level. "
#                 "This helps determine whether a maintenance or deficit diet is appropriate."
#             ),
#             how = (
#                 "R48 fired because 2 <= exercise_per_week <= 4. "
#                 "Activity_Level has been set to Moderate."
#             ),
#             label = "Activity: Moderate (2–4 days/week)"
#         )

#         self._add(
#             "R49",
#             condition  = lambda wm: wm.get("exercise_per_week", 0) >= 5,
#             conclusion = lambda wm: wm.set("Activity_Level", "High", "R49"),
#             why = (
#                 "Exercising 5 or more days per week is classified as a High activity "
#                 "level. High activity increases caloric needs and shapes the diet type."
#             ),
#             how = (
#                 "R49 fired because exercise_per_week >= 5. "
#                 "Activity_Level has been set to High."
#             ),
#             label = "Activity: High (>= 5 days/week)"
#         )

#         self._add(
#             "R50",
#             condition  = lambda wm: wm.get("Activity_Level") in ("Low", "Moderate", "High"),
#             conclusion = lambda wm: wm.set(
#                 "Final_Activity", wm.get("Activity_Level"), "R50"),
#             why = (
#                 "This rule finalises the activity classification by copying "
#                 "Activity_Level to Final_Activity, used by the diet-type rules."
#             ),
#             how = (
#                 "R50 fired because Activity_Level is set to a valid level. "
#                 "Final_Activity = Activity_Level."
#             ),
#             label = "Activity: finalise level"
#         )

#         # ── SECTION 13 : DIET TYPE (R51–R53) ───────────────────────────

#         self._add(
#             "R51",
#             condition  = lambda wm: (
#                 wm.get("Final_Bmi_Category") == "Overweight" and
#                 wm.get("Final_Activity") == "Low"
#             ),
#             conclusion = lambda wm: wm.set("Diet_Type", "Calorie_Deficit", "R51"),
#             why = (
#                 "An Overweight user with a Low activity level needs to reduce caloric "
#                 "intake to achieve a healthy weight, which also reduces strain on the kidneys."
#             ),
#             how = (
#                 "R51 fired because Final_Bmi_Category = Overweight AND Final_Activity = Low. "
#                 "Diet_Type has been set to Calorie_Deficit."
#             ),
#             label = "Diet type: Calorie Deficit (Overweight + Low activity)"
#         )

#         self._add(
#             "R52",
#             condition  = lambda wm: (
#                 wm.get("Final_Bmi_Category") == "Normal" and
#                 wm.get("Final_Activity") in ("Low", "Moderate", "High")
#             ),
#             conclusion = lambda wm: wm.set("Diet_Type", "Calorie_Maintenance", "R52"),
#             why = (
#                 "A Normal BMI user at any activity level should maintain their current "
#                 "caloric intake to preserve body weight while managing CKD."
#             ),
#             how = (
#                 "R52 fired because Final_Bmi_Category = Normal and Final_Activity is valid. "
#                 "Diet_Type has been set to Calorie_Maintenance."
#             ),
#             label = "Diet type: Calorie Maintenance (Normal BMI)"
#         )

#         self._add(
#             "R53",
#             condition  = lambda wm: wm.get("Diet_Type") in (
#                 "Calorie_Maintenance", "Calorie_Deficit"),
#             conclusion = lambda wm: wm.set(
#                 "Final_Diet_Type", wm.get("Diet_Type"), "R53"),
#             why = (
#                 "This rule finalises the diet type by propagating Diet_Type to "
#                 "Final_Diet_Type, which is consumed by the medical state rules."
#             ),
#             how = (
#                 "R53 fired because Diet_Type is set to a valid value. "
#                 "Final_Diet_Type = Diet_Type."
#             ),
#             label = "Diet type: finalise"
#         )

#         # ── SECTION 14 : MEDICAL STATE (R54–R62) ───────────────────────

#         medical_state_rules = [
#             ("R54", 0,  None,               "No CKD"),
#             ("R55", 1,  "Calorie_Deficit",  "CKD Stage 1 Deficit"),
#             ("R56", 1,  "Calorie_Maintenance","CKD Stage 1 Maintenance"),
#             ("R57", 2,  "Calorie_Deficit",  "CKD Stage 2 Deficit"),
#             ("R58", 2,  "Calorie_Maintenance","CKD Stage 2 Maintenance"),
#             ("R59", 3,  "Calorie_Deficit",  "CKD Stage 3 Deficit"),
#             ("R60", 3,  "Calorie_Maintenance","CKD Stage 3 Maintenance"),
#             ("R61", 4,  "Calorie_Deficit",  "CKD Stage 4 Deficit"),
#             ("R62", 4,  "Calorie_Maintenance","CKD Stage 4 Maintenance"),
#         ]

#         for rid, stage, diet, state in medical_state_rules:
#             _rid   = rid
#             _stage = stage
#             _diet  = diet
#             _state = state

#             if stage == 0:
#                 def _cond(wm, s=_stage): return wm.get("Stage_Determination") == s
#             else:
#                 def _cond(wm, s=_stage, d=_diet):
#                     return (wm.get("Stage_Determination") == s and
#                             wm.get("Final_Diet_Type") == d)

#             def _concl(wm, st=_state, r=_rid): wm.set("Medical_State", st, r)

#             self._add(
#                 _rid,
#                 condition  = _cond,
#                 conclusion = _concl,
#                 why = (
#                     f"We are determining the specific medical state for a patient with "
#                     f"Stage_Determination={_stage} and Final_Diet_Type={_diet}."
#                 ),
#                 how = (
#                     f"{_rid} fired because Stage_Determination = {_stage}"
#                     + (f" AND Final_Diet_Type = {_diet}." if _diet else ".")
#                     + f" Medical_State has been set to '{_state}'."
#                 ),
#                 label = f"Medical state: {_state}"
#             )

#         # ── SECTION 15 : DIET RECOMMENDATIONS (R63–R72) ────────────────

#         recommendations = {
#             "CKD Stage 1 Deficit": (
#                 "Calorie deficit kidney-friendly diet: grilled skinless chicken, quinoa, "
#                 "mixed vegetables, and fresh fruits in controlled portions. Reduce calorie "
#                 "intake for weight control. Limit sodium to less than 2300 mg/day and "
#                 "maintain moderate protein consumption to reduce kidney strain."
#             ),
#             "CKD Stage 1 Maintenance": (
#                 "Calorie maintenance kidney-friendly diet: balanced meals with grilled "
#                 "chicken, quinoa, vegetables, fruits, and whole grains. Maintain stable "
#                 "calorie intake, balanced protein consumption, and sodium below 2300 mg/day."
#             ),
#             "CKD Stage 2 Deficit": (
#                 "Calorie deficit kidney-support diet: grilled lean protein, steamed "
#                 "vegetables, quinoa, and low-sodium foods in controlled portions. Reduce "
#                 "processed food and maintain sodium between 2000–2300 mg/day for kidney "
#                 "protection and weight reduction."
#             ),
#             "CKD Stage 2 Maintenance": (
#                 "Calorie maintenance kidney-support diet: balanced intake of lean protein, "
#                 "whole grains, vegetables, and healthy carbohydrates. Maintain stable calorie "
#                 "intake while controlling sodium and monitoring protein consumption."
#             ),
#             "CKD Stage 3 Deficit": (
#                 "Calorie deficit strict kidney-friendly diet: controlled portions of lean "
#                 "chicken or fish, low-potassium vegetables, and limited quinoa intake. Reduce "
#                 "overall calorie intake for weight management, maintain sodium below "
#                 "2000 mg/day, and avoid processed food."
#             ),
#             "CKD Stage 3 Maintenance": (
#                 "Calorie maintenance kidney-friendly diet: low sodium meals with moderate "
#                 "protein restriction, controlled portions of grains and vegetables, and stable "
#                 "calorie intake to maintain body weight. Regular kidney monitoring is recommended."
#             ),
#             "CKD Stage 4 Deficit": (
#                 "Calorie deficit advanced kidney-friendly diet: low protein, low potassium, "
#                 "and low phosphorus foods with carefully controlled portions. Maintain reduced "
#                 "calorie intake, restrict sodium below 2000 mg/day, control fluids, and prepare "
#                 "for dialysis planning."
#             ),
#             "CKD Stage 4 Maintenance": (
#                 "Calorie maintenance advanced kidney-friendly diet: strict protein restriction, "
#                 "careful fluid management, and balanced low sodium, low potassium, and low "
#                 "phosphorus meals. Maintain stable calorie intake under medical supervision."
#             ),
#             "No CKD": (
#                 "Healthy balanced diet for prevention: vegetables, fruits, lean proteins, whole "
#                 "grains, and adequate hydration. Maintain healthy calorie intake, limit sodium "
#                 "below 2300 mg/day, and perform regular exercise for at least 30 minutes per "
#                 "day, 5 days per week."
#             ),
#         }

#         rule_ids = [f"R{i}" for i in range(63, 73)]   # R63–R72
#         states    = list(recommendations.keys())       # 9 states
#         # R63–R71 → one state each; R72 → finalise

#         for i, (ms, rec) in enumerate(recommendations.items()):
#             _rid = rule_ids[i]
#             _ms  = ms
#             _rec = rec

#             def _cond(wm, s=_ms): return wm.get("Medical_State") == s
#             def _concl(wm, r=_rec, ri=_rid): wm.set("Recommendation", r, ri)

#             self._add(
#                 _rid,
#                 condition  = _cond,
#                 conclusion = _concl,
#                 why = (
#                     f"We are retrieving the personalised diet recommendation "
#                     f"for Medical_State = '{_ms}'."
#                 ),
#                 how = (
#                     f"{_rid} fired because Medical_State = '{_ms}'. "
#                     f"Recommendation has been set with the appropriate kidney-friendly diet."
#                 ),
#                 label = f"Recommendation: {_ms}"
#             )

#         # R72 — finalise recommendation
#         self._add(
#             "R72",
#             condition  = lambda wm: wm.get("Recommendation") is not None,
#             conclusion = lambda wm: wm.set(
#                 "Personalized_CKD_Recommendation", wm.get("Recommendation"), "R72"),
#             why = (
#                 "This final rule seals the system output by copying Recommendation to "
#                 "Personalized_CKD_Recommendation — the fact consumed by the output UI."
#             ),
#             how = (
#                 "R72 fired because Recommendation is set. "
#                 "Personalized_CKD_Recommendation has been finalised."
#             ),
#             label = "Finalise: Personalized_CKD_Recommendation"
#         )


# # ---------------------------------------------------------------------------
# # Inference Engine — forward chaining
# # ---------------------------------------------------------------------------

# class InferenceEngine:
#     """Agenda-driven forward chaining engine.

#     Algorithm
#     ---------
#     1. Load all rules onto a ``pending`` agenda.
#     2. In each cycle, scan every pending rule whose condition is True.
#     3. Fire matching rules (execute conclusion), record which rules fired
#        in ``fired_rules``, remove them from pending.
#     4. Repeat until no new rules fire (fixed point).

#     Returns
#     -------
#     fired_rules : list[str]   — rule IDs in the order they fired
#     """

#     def __init__(self, kb: KnowledgeBase):
#         self.kb = kb

#     # ------------------------------------------------------------------
#     def run(self, wm: WorkingMemory) -> List[str]:
#         """Run the inference loop.  Returns ordered list of fired rule IDs."""
#         fired_rules: List[str] = []
#         pending: List[Rule]    = list(self.kb.all_rules())

#         changed = True
#         while changed:
#             changed    = False
#             still_pending: List[Rule] = []
#             for rule in pending:
#                 try:
#                     fires = rule.condition(wm)
#                 except Exception:
#                     fires = False

#                 if fires:
#                     try:
#                         rule.conclusion(wm)
#                     except Exception:
#                         pass
#                     fired_rules.append(rule.rule_id)
#                     changed = True
#                 else:
#                     still_pending.append(rule)

#             pending = still_pending

#         return fired_rules


# # ---------------------------------------------------------------------------
# # Explanation Engine
# # ---------------------------------------------------------------------------

# class ExplanationEngine:
#     """Provides WHY and HOW explanations based on a KnowledgeBase.

#     WHY explanations
#     ----------------
#     Returns the ``why`` text of the *first active rule* whose condition is
#     currently True in the provided WorkingMemory — i.e. it answers "Why are
#     you asking about X?".

#     HOW explanations
#     ----------------
#     Given the list of fired rules and the WorkingMemory, returns a full
#     reasoning trace of how the final diagnosis / recommendation was reached.
#     """

#     def __init__(self, kb: KnowledgeBase):
#         self.kb = kb

#     # ------------------------------------------------------------------
#     def why(self, rule_id: str) -> str:
#         """Return the WHY explanation text for the given rule_id."""
#         rule = self.kb.get_rule(rule_id)
#         if rule is None:
#             return f"No rule found with id '{rule_id}'."
#         return rule.why

#     def why_active(self, wm: WorkingMemory) -> List[dict]:
#         """Return WHY texts for all rules whose conditions are currently True.

#         Returns list of dicts: {'rule_id', 'label', 'why'}
#         """
#         active = []
#         for rule in self.kb.all_rules():
#             try:
#                 if rule.condition(wm):
#                     active.append({
#                         "rule_id": rule.rule_id,
#                         "label":   rule.label,
#                         "why":     rule.why,
#                     })
#             except Exception:
#                 pass
#         return active

#     # ------------------------------------------------------------------
#     def how(self, fired_rules: List[str], wm: WorkingMemory) -> List[dict]:
#         """Return a HOW trace for every rule that fired during the session.

#         Returns ordered list of dicts: {'rule_id', 'label', 'how'}
#         """
#         trace = []
#         for rid in fired_rules:
#             rule = self.kb.get_rule(rid)
#             if rule:
#                 trace.append({
#                     "rule_id": rule.rule_id,
#                     "label":   rule.label,
#                     "how":     rule.how,
#                 })
#         return trace

#     def how_summary(self, fired_rules: List[str], wm: WorkingMemory) -> str:
#         """Human-readable HOW trace as a single formatted string."""
#         lines = ["=== HOW the system reached its conclusion ===\n"]
#         for step in self.how(fired_rules, wm):
#             lines.append(f"[{step['rule_id']}] {step['label']}")
#             lines.append(f"    {step['how']}\n")
#         facts = wm.all_facts()
#         lines.append("=== Final Working Memory (selected facts) ===")
#         key_facts = [
#             "diabetes_status", "bp_status", "CKD_Stage", "Stage_Determination",
#             "confidence", "risk", "final_interpretation",
#             "BMI", "BMI_Category", "Activity_Level", "Diet_Type",
#             "Medical_State", "Personalized_CKD_Recommendation",
#         ]
#         for k in key_facts:
#             if k in facts:
#                 val = facts[k]
#                 if isinstance(val, str) and len(val) > 80:
#                     val = val[:77] + "..."
#                 lines.append(f"  {k} = {val}")
#         return "\n".join(lines)


# # ---------------------------------------------------------------------------
# # Convenience factory
# # ---------------------------------------------------------------------------

# def create_expert_system() -> Tuple[KnowledgeBase, InferenceEngine, ExplanationEngine]:
#     """Instantiate and wire together all three components.

#     Usage
#     -----
#     kb, engine, explainer = create_expert_system()
#     wm = WorkingMemory(initial_facts={...})
#     fired = engine.run(wm)
#     print(explainer.how_summary(fired, wm))
#     result = wm.get("Personalized_CKD_Recommendation")
#     """
#     kb       = KnowledgeBase()
#     engine   = InferenceEngine(kb)
#     explainer= ExplanationEngine(kb)
#     return kb, engine, explainer
