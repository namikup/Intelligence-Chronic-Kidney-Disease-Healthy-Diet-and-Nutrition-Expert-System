import customtkinter as ctk
import tkinter.messagebox as messagebox

# Import from the full package path — no sys.path tricks needed.
# ckd_expert_system/__init__.py makes it a proper package importable from the project root.
from ckd_expert_system.engine import create_expert_system, WorkingMemory

# ==========================================
# CUSTOMTKINTER UI — WIRED TO FULL 72-RULE ENGINE
# ==========================================

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class DietNutriESApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DietNutriES — CKD Clinical Nutrition Expert System")
        self.geometry("800x640")
        self.grid_columnconfigure(0, weight=1)
        self.setup_ui()

    # ------------------------------------------------------------------
    # UI Layout
    # ------------------------------------------------------------------

    def setup_ui(self):
        # Header
        ctk.CTkLabel(
            self, text="Patient Profile & Clinical Symptom Assessment",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 5))

        ctk.CTkLabel(
            self, text="Powered by a 72-Rule Forward-Chaining Inference Engine",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).grid(row=1, column=0, padx=20, pady=(0, 20))

        # --- SECTION 1: Physical Data ---
        physical_frame = ctk.CTkFrame(self, fg_color="transparent")
        physical_frame.grid(row=2, column=0, padx=30, pady=5, sticky="w")

        ctk.CTkLabel(physical_frame, text="Physical Data", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        ctk.CTkLabel(physical_frame, text="Weight (kg):", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=(0, 8))
        self.weight_entry = ctk.CTkEntry(physical_frame, width=100, placeholder_text="e.g. 75.5")
        self.weight_entry.grid(row=1, column=1, padx=(0, 30))

        ctk.CTkLabel(physical_frame, text="Height (m):", font=ctk.CTkFont(size=14)).grid(row=1, column=2, padx=(0, 8))
        self.height_entry = ctk.CTkEntry(physical_frame, width=100, placeholder_text="e.g. 1.70")
        self.height_entry.grid(row=1, column=3)

        ctk.CTkLabel(physical_frame, text="Exercise (days/week):", font=ctk.CTkFont(size=14)).grid(row=2, column=0, padx=(0, 8), pady=(10, 0))
        self.exercise_entry = ctk.CTkEntry(physical_frame, width=100, placeholder_text="0 – 7")
        self.exercise_entry.grid(row=2, column=1, pady=(10, 0))

        # --- SECTION 2: Symptoms ---
        symptom_frame = ctk.CTkFrame(self, fg_color="transparent")
        symptom_frame.grid(row=3, column=0, padx=30, pady=15, sticky="w")

        ctk.CTkLabel(symptom_frame, text="Symptom Assessment — check all that apply", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Symptom checkboxes mapped to their working memory key names
        self.symptom_vars = {}
        symptoms = [
            # (label, wm_key)
            ("Persistent tiredness / fatigue",          "tiredness"),
            ("Frequent urination (especially at night)", "frequent_urination"),
            ("Excessive thirst",                         "excessive_thirst"),
            ("Constant hunger",                          "constant_hunger"),
            ("Frequent headaches (back of head)",        "headaches"),
            ("Dizziness or lightheadedness",             "dizziness"),
            ("Blurred vision",                           "blurred_vision_bp"),
            ("Chest discomfort or tightness",            "chest_discomfort"),
            ("Mild swelling in ankles/feet",             "mild_swelling"),
            ("Mild persistent fatigue",                  "mild_fatigue"),
            ("Persistent & worsening fatigue",           "persistent_fatigue"),
            ("Swelling in hands, legs, or feet",         "swelling_extremities"),
            ("Lower back or flank pain",                 "lower_back_pain"),
            ("Itchy skin without a rash",                "itchy_skin"),
            ("Frequent nausea / urge to vomit",          "nausea"),
            ("Significant loss of appetite",             "loss_of_appetite"),
            ("Difficulty concentrating / brain fog",     "difficulty_concentrating"),
            ("Muscle cramps (especially in legs)",       "muscle_cramps"),
            ("Trouble falling or staying asleep",        "trouble_sleeping"),
        ]

        for i, (label, key) in enumerate(symptoms):
            col = i % 2          # 2 columns
            row = (i // 2) + 1
            cb = ctk.CTkCheckBox(symptom_frame, text=label, font=ctk.CTkFont(size=13))
            cb.grid(row=row, column=col, sticky="w", padx=(0, 40), pady=3)
            self.symptom_vars[key] = cb

        # [?] WHY Button
        why_row = (len(symptoms) // 2) + 2
        ctk.CTkButton(
            symptom_frame, text="[?] WHY are we asking about symptoms?",
            fg_color="#17a2b8", hover_color="#138496",
            command=self.explain_why
        ).grid(row=why_row, column=0, columnspan=2, pady=15, sticky="w")

        # Run Engine Button
        ctk.CTkButton(
            self, text="▶  Run Inference Engine (72 Rules)",
            font=ctk.CTkFont(size=17, weight="bold"), height=44,
            command=self.process_inputs
        ).grid(row=4, column=0, pady=(5, 25))

    # ------------------------------------------------------------------
    # Explanation Facility
    # ------------------------------------------------------------------

    def explain_why(self):
        messagebox.showinfo(
            "WHY — Explanation Facility",
            "WHY ARE WE ASKING THESE QUESTIONS?\n\n"
            "Each symptom is mapped to a specific IF-THEN production rule in the Knowledge Base:\n\n"
            "• Diabetes symptoms (R1–R4): Tiredness, thirst, hunger, frequent urination\n"
            "• Blood Pressure symptoms (R7–R10): Headaches, dizziness, blurred vision\n"
            "• CKD Stage 2 (R15–R16): Mild swelling, mild fatigue\n"
            "• CKD Stage 3 (R18–R21): Persistent fatigue, swelling, back pain, itchy skin\n"
            "• CKD Stage 4 (R23–R27): Nausea, appetite loss, concentration issues\n\n"
            "The Forward-Chaining Engine evaluates your answers to infer your CKD Stage, "
            "Confidence %, Risk Level, and generates a personalised dietary recommendation."
        )

    # ------------------------------------------------------------------
    # Data Collection, Engine Execution & Results Display
    # ------------------------------------------------------------------

    def process_inputs(self):
        # 1. Validate physical inputs
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            exercise = int(self.exercise_entry.get())
            if not (5 < weight < 400):
                raise ValueError("weight out of range")
            if not (0.5 < height < 3.0):
                raise ValueError("height out of range")
            if not (0 <= exercise <= 7):
                raise ValueError("exercise out of range")
        except ValueError:
            messagebox.showerror(
                "Validation Error",
                "Please enter valid values:\n"
                "• Weight: a number between 5 and 400 kg\n"
                "• Height: a number between 0.5 and 3.0 m\n"
                "• Exercise: a whole number between 0 and 7"
            )
            return

        # 2. Build initial facts for Working Memory
        facts = {
            "weight": weight,
            "height": height,
            "exercise_per_week": exercise,
        }
        # Map each checkbox to its yes/no working memory key
        for key, cb in self.symptom_vars.items():
            facts[key] = "yes" if cb.get() == 1 else "no"

        # 3. Instantiate engine and run forward chaining
        kb, engine, explainer = create_expert_system()
        wm = WorkingMemory(facts)
        fired = engine.run(wm)

        # 4. Extract results
        stage       = wm.get("Stage_Determination")
        confidence  = wm.get("confidence")
        risk        = wm.get("risk")
        interp      = wm.get("final_interpretation")
        bmi         = wm.get("BMI")
        bmi_cat     = wm.get("Final_Bmi_Category")
        diet        = wm.get("Final_Diet_Type")
        med_state   = wm.get("Medical_State")
        rec         = wm.get("Personalized_CKD_Recommendation")
        how_trace   = explainer.how_summary(fired, wm)

        # 5. Display results in a messagebox
        result_text = (
            f"{'='*50}\n"
            f" EXPERT SYSTEM EVALUATION\n"
            f"{'='*50}\n\n"
            f"CKD Stage Detected : {'Stage ' + str(stage) if stage else 'No CKD Detected'}\n"
            f"Confidence         : {confidence}%\n"
            f"Risk Level         : {risk}\n"
            f"Clinical Finding   : {interp}\n\n"
            f"BMI                : {bmi} ({bmi_cat})\n"
            f"Diet Type          : {diet}\n"
            f"Medical State      : {med_state}\n\n"
            f"{'='*50}\n"
            f"PERSONALISED RECOMMENDATION:\n"
            f"{'='*50}\n"
            f"{rec}\n\n"
            f"[{len(fired)} rules fired from 72-rule Knowledge Base]"
        )
        messagebox.showinfo("Inference Complete ✓", result_text)

        # 6. Also print HOW trace to terminal for academic reference
        print("\n" + how_trace)


if __name__ == "__main__":
    app = DietNutriESApp()
    app.mainloop()
