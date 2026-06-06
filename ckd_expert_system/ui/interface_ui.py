"""
interface_ui.py — Fully implemented console UI for the CKD Expert System.
Loops through QUESTION_ORDER, validates input, runs the inference engine,
and displays results with a full HOW reasoning trace.
"""

from ckd_expert_system.engine import create_expert_system, WorkingMemory
from ckd_expert_system.ui.questions import QUESTION_MAP, QUESTION_ORDER, FLOAT_KEYS, INT_KEYS, YESNO_KEYS


class ConsoleUI:
    """Interactive command-line interface for the CKD Expert System.

    Flow
    ----
    1. collect_facts()  — Ask each question, validate, store in a dict
    2. engine.run(wm)   — Forward-chain across all 72 rules
    3. display_results()— Print Stage, Confidence, Risk, Recommendation + HOW trace
    """

    def __init__(self):
        self.kb, self.engine, self.explainer = create_expert_system()

    # ------------------------------------------------------------------
    # Input helpers
    # ------------------------------------------------------------------

    def _ask_yesno(self, key: str) -> str:
        """Prompt a yes/no question and validate the response."""
        question = QUESTION_MAP[key]
        while True:
            answer = input(f"\n  {question} ").strip().lower()
            if answer in ("yes", "no", "y", "n"):
                return "yes" if answer in ("yes", "y") else "no"
            print("  ⚠  Please answer 'yes' or 'no'.")

    def _ask_float(self, key: str) -> float:
        """Prompt a numeric (float) question and validate the response."""
        question = QUESTION_MAP[key]
        while True:
            try:
                value = float(input(f"\n  {question} ").strip())
                if value <= 0:
                    print("  ⚠  Please enter a positive number.")
                    continue
                return value
            except ValueError:
                print("  ⚠  Invalid input. Please enter a number (e.g. 70.5).")

    def _ask_int(self, key: str) -> int:
        """Prompt an integer question and validate the response."""
        question = QUESTION_MAP[key]
        while True:
            try:
                value = int(input(f"\n  {question} ").strip())
                if not (0 <= value <= 7):
                    print("  ⚠  Please enter a number between 0 and 7.")
                    continue
                return value
            except ValueError:
                print("  ⚠  Invalid input. Please enter a whole number (e.g. 3).")

    # ------------------------------------------------------------------
    # Task 2: Question Sequence — collect all user facts
    # ------------------------------------------------------------------

    def collect_facts(self) -> dict:
        """Loop through QUESTION_ORDER, collect and validate all patient inputs."""
        print("\n" + "=" * 60)
        print("   SECTION 1 OF 3 — Symptom Assessment (Diabetes & BP)")
        print("=" * 60)

        facts = {}
        current_section = None

        # Section headers for better UX
        sections = {
            "tiredness":              "  [Diabetes Risk Symptoms]",
            "headaches":              "\n" + "=" * 60 + "\n   SECTION 2 OF 3 — Symptom Assessment (CKD Stages)\n" + "=" * 60 + "\n  [Blood Pressure Symptoms]",
            "mild_swelling":          "  [CKD Stage 2 Symptoms]",
            "persistent_fatigue":     "  [CKD Stage 3 Symptoms]",
            "nausea":                 "  [CKD Stage 4 Symptoms]",
            "weight":                 "\n" + "=" * 60 + "\n   SECTION 3 OF 3 — Physical & Lifestyle Data\n" + "=" * 60,
        }

        for key in QUESTION_ORDER:
            # Print section header if applicable
            if key in sections:
                print(sections[key])

            if key in YESNO_KEYS:
                facts[key] = self._ask_yesno(key)
            elif key in FLOAT_KEYS:
                facts[key] = self._ask_float(key)
            elif key in INT_KEYS:
                facts[key] = self._ask_int(key)

        return facts

    # ------------------------------------------------------------------
    # Results display with HOW trace
    # ------------------------------------------------------------------

    def display_results(self, wm: WorkingMemory, fired_rules: list) -> None:
        """Print the complete clinical evaluation and HOW reasoning trace."""
        print("\n" + "=" * 60)
        print("   EXPERT SYSTEM EVALUATION RESULTS")
        print("=" * 60)

        stage       = wm.get("Stage_Determination")
        confidence  = wm.get("confidence")
        risk        = wm.get("risk")
        interp      = wm.get("final_interpretation")
        bmi         = wm.get("BMI")
        bmi_cat     = wm.get("Final_Bmi_Category")
        activity    = wm.get("Final_Activity")
        diet        = wm.get("Final_Diet_Type")
        med_state   = wm.get("Medical_State")
        rec         = wm.get("Personalized_CKD_Recommendation")

        print(f"\n  CKD Stage Detected  : {f'Stage {stage}' if stage else 'No CKD Detected'}")
        print(f"  Confidence          : {confidence}%")
        print(f"  Risk Level          : {risk}")
        print(f"  Clinical Finding    : {interp}")
        print(f"\n  BMI                 : {bmi} ({bmi_cat})")
        print(f"  Activity Level      : {activity}")
        print(f"  Diet Type           : {diet}")
        print(f"  Medical State       : {med_state}")
        print(f"\n{'=' * 60}")
        print("  PERSONALISED DIETARY RECOMMENDATION")
        print(f"{'=' * 60}")
        print(f"\n  {rec}\n")

        # HOW Explanation Trace
        print(f"{'=' * 60}")
        print("  HOW THE SYSTEM REACHED THIS CONCLUSION")
        print(f"{'=' * 60}")
        print(self.explainer.how_summary(fired_rules, wm))
        print("=" * 60)

    # ------------------------------------------------------------------
    # Main orchestration
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Orchestrate: collect facts → run engine → display results."""
        print("\n" + "=" * 60)
        print("   DietNutriES — CKD Expert System (Console Interface)")
        print("=" * 60)
        print("  This system evaluates your risk of Chronic Kidney Disease")
        print("  and provides a personalised dietary recommendation.")
        print("  Please answer all questions honestly.")

        # Step 1: Gather inputs (Task 2 — Question Sequence)
        facts = self.collect_facts()

        # Step 2: Populate Working Memory and run engine (Task 5)
        print("\n\n  [SYSTEM] Running 72-rule Forward-Chaining Inference Engine...")
        wm = WorkingMemory(facts)
        fired = self.engine.run(wm)
        print(f"  [SYSTEM] Complete. {len(fired)} rules fired.\n")

        # Step 3: Display results + HOW trace
        self.display_results(wm, fired)
