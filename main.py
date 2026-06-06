# import customtkinter as ctk
# import tkinter.messagebox as messagebox

# class Rule:
#     def __init__(self, rule_id, condition, action, how_text):
#         self.rule_id = rule_id
#         self.condition = condition  # A function checking if the rule should fire
#         self.action = action        # A function that updates working memory
#         self.how_text = how_text    # Text for the 'HOW did you reach this?' explanation
#         self.has_fired = False      # Keeps track so rules don't fire infinitely

# # --- DOMAIN KNOWLEDGE BASE ---

# # Rule 1: Diabetes Detection (Tiredness)
# def cond_r1(wm):
#     return "tiredness" in wm["symptoms"]

# def action_r1(wm):
#     wm["diabetes_score"] += 1

# rule1 = Rule(
#     rule_id="R1",
#     condition=cond_r1,
#     action=action_r1,
#     how_text="Because you reported 'tiredness', your Diabetes Risk Score increased by 1."
# )

# # Rule 5: Diabetes Status Confirmation
# def cond_r5(wm):
#     return wm["diabetes_score"] >= 3 and wm["diabetes_status"] is None

# def action_r5(wm):
#     wm["diabetes_status"] = True

# rule5 = Rule(
#     rule_id="R5",
#     condition=cond_r5,
#     action=action_r5,
#     how_text="Because your Diabetes Risk Score reached 3 or more, the system classified your Diabetes Status as TRUE."
# )

# # Put all your rules into a master list
# KNOWLEDGE_BASE = [rule1, rule5]

# # --- INFERENCE ENGINE ---
# def run_forward_chaining(working_memory, knowledge_base):
#     print("--- Starting Forward Chaining ---")
#     new_fact_derived = True
#     fired_rules_log = [] # This stores the history for your HOW explanation

#     while new_fact_derived:
#         new_fact_derived = False
#         for rule in knowledge_base:
#             # If the rule hasn't fired yet, and its conditions are met based on current memory
#             if not rule.has_fired and rule.condition(working_memory):
#                 print(f"Firing {rule.rule_id}...")
#                 rule.action(working_memory)       # Update the memory
#                 rule.has_fired = True             # Mark as fired
#                 fired_rules_log.append(rule.how_text) # Log for explanation
#                 new_fact_derived = True           # A new fact was learned, so loop again!

#     print("--- Inference Complete ---")
#     return fired_rules_log

# # --- 1. SETUP UI THEME (Clinical & Trustworthy) ---
# ctk.set_appearance_mode("Light")      # Clean white background
# ctk.set_default_color_theme("blue")   # Healthcare blue primary color

# class DietNutriESApp(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         # --- 2. WINDOW CONFIGURATION ---
#         self.title("DietNutriES - Clinical Nutrition Expert System")
#         self.geometry("750x550")
#         self.grid_columnconfigure(0, weight=1)

#         self.working_memory = {
#             "weight": None,
#             "symptoms": [],
#             "diabetes_score": 0,
#             "diabetes_status": None
#         }

#         self.setup_ui()

#     def setup_ui(self):
#         # Header Label
#         self.header = ctk.CTkLabel(
#             self, text="Step 1: Patient Profile & Symptoms", 
#             font=ctk.CTkFont(size=24, weight="bold")
#         )
#         self.header.grid(row=0, column=0, padx=20, pady=(20, 30))

#         # --- 3. QUESTION ROW: WEIGHT (With robust error handling) ---
#         self.weight_frame = ctk.CTkFrame(self, fg_color="transparent")
#         self.weight_frame.grid(row=1, column=0, padx=20, pady=10, sticky="w")

#         self.weight_label = ctk.CTkLabel(self.weight_frame, text="What is your current weight (kg)?", font=ctk.CTkFont(size=16))
#         self.weight_label.grid(row=0, column=0, padx=(0, 10))

#         self.weight_entry = ctk.CTkEntry(self.weight_frame, width=100, placeholder_text="e.g. 75.5")
#         self.weight_entry.grid(row=0, column=1, padx=10)

#         # --- 4. QUESTION ROW: SYMPTOMS (With the 'WHY' Explanation Facility) ---
#         self.symptom_frame = ctk.CTkFrame(self, fg_color="transparent")
#         self.symptom_frame.grid(row=2, column=0, padx=20, pady=20, sticky="w")

#         self.symptom_checkbox = ctk.CTkCheckBox(self.symptom_frame, text="Do you experience foamy urine?", font=ctk.CTkFont(size=16))
#         self.symptom_checkbox.grid(row=0, column=0, padx=(0, 10))

#         # The [?] WHY Button
#         self.why_btn = ctk.CTkButton(
#             self.symptom_frame, text="[?] WHY", width=60, 
#             fg_color="#17a2b8", hover_color="#138496", # Info blue
#             command=self.explain_why_foamy_urine
#         )
#         self.why_btn.grid(row=0, column=1)

#         # --- 5. FOOTER: NAVIGATION ---
#         self.next_btn = ctk.CTkButton(
#             self, text="Next Step →", font=ctk.CTkFont(size=16, weight="bold"),
#             command=self.process_inputs
#         )
#         self.next_btn.grid(row=3, column=0, pady=50)

#     # --- 6. EXPLANATION FACILITY LOGIC ---
#     def explain_why_foamy_urine(self):
#         """Displays the transparent reasoning for asking this specific question."""
#         why_text = (
#             "WHY AM I ASKING THIS?\n\n"
#             "Foamy urine is a primary indicator of excess protein in your urine (proteinuria). "
#             "Your answer helps the system calculate your Renal Risk Score (Rule 14) to "
#             "determine if you map to a Chronic Kidney Disease (CKD) stage."
#         )
#         messagebox.showinfo("Explanation (WHY)", why_text)

#     # --- 7. ERROR HANDLING & DATA COLLECTION ---
#     def process_inputs(self):
#         """Validates inputs before sending to the Inference Engine."""
#         raw_weight = self.weight_entry.get()
        
#         # Graceful Error Handling (Validating Data Types & Ranges)
#         try:
#             weight = float(raw_weight)
#             if weight <= 0 or weight > 300:
#                 messagebox.showerror("Validation Error", "Please enter a realistic weight between 1 and 300 kg.")
#                 return
#         except ValueError:
#             messagebox.showerror("Type Error", "Invalid input. Please enter numbers only for your weight (e.g., 75.5).")
#             return

#         # Save to working memory
#         self.working_memory["weight"] = weight
#         if self.symptom_checkbox.get() == 1:
#             self.working_memory["symptoms"].append("foamy_urine")

#         messagebox.showinfo("Success", f"Data saved successfully! \nWorking Memory State:\n{self.working_memory}\n\n(Forward-Chaining Engine would now evaluate this data...)")

# if __name__ == "__main__":
#     app = DietNutriESApp()
#     app.mainloop()
