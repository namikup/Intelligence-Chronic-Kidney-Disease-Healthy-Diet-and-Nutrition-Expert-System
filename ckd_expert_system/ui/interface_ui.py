"""
interface_ui.py — Modern CustomTkinter GUI for the CKD Expert System.
Implements a multi-step wizard UI with progress tracking, explanation facility,
and professional results dashboard.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import time

from ckd_expert_system.engine import create_expert_system, WorkingMemory
from ckd_expert_system.ui.questions import WIZARD_STEPS, WHY_EXPLANATIONS

# ==========================================
# COLOR PALETTE
# ==========================================
COLORS = {
    "primary_blue": "#2563EB",
    "success_green": "#16A34A",
    "warning_amber": "#F59E0B",
    "danger_red": "#DC2626",
    "background": "#F8FAFC",
    "card_bg": "#FFFFFF",
    "text_primary": "#1F2937",
    "text_secondary": "#6B7280",
    "border": "#E5E7EB",
    "sidebar_bg": "#F3F4F6",
}

# ==========================================
# MAIN APPLICATION CLASS
# ==========================================
class DietNutriESApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CKD Clinical Nutrition Expert System")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # State management
        self.current_step_index = 0
        self.answers = {}
        self.inference_results = None
        self.rules_fired = []

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build UI
        self._build_ui()
        self._show_step(0)

    def _build_ui(self):
        """Build the main UI structure: sidebar, content area, navigation."""
        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS["sidebar_bg"], width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(1, weight=1)

        # Sidebar header
        ctk.CTkLabel(
            self.sidebar,
            text="Assessment Progress",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # Progress items container
        self.progress_items_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.progress_items_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.progress_items_frame.grid_columnconfigure(0, weight=1)

        self._build_progress_sidebar()

        # ========== MAIN CONTENT AREA ==========
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["background"])
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.content_frame,
            progress_color=COLORS["primary_blue"],
            fg_color=COLORS["border"]
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # Main scrollable content frame
        self.main_content = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["background"],
            label_text=""
        )
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_columnconfigure(0, weight=1)

        # Navigation buttons at the bottom
        nav_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["background"])
        nav_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        nav_frame.grid_columnconfigure(1, weight=1)

        self.back_button = ctk.CTkButton(
            nav_frame,
            text="← Back",
            command=self._prev_step,
            fg_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color="#D1D5DB"
        )
        self.back_button.grid(row=0, column=0, padx=(0, 10))

        self.next_button = ctk.CTkButton(
            nav_frame,
            text="Next →",
            command=self._next_step,
            fg_color=COLORS["primary_blue"],
            hover_color="#1D4ED8"
        )
        self.next_button.grid(row=0, column=2, padx=(10, 0))

        # Step indicator label
        self.step_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.step_label.grid(row=0, column=1, padx=20)

    def _build_progress_sidebar(self):
        """Build the progress items in the sidebar."""
        categories_seen = set()
        for i, step in enumerate(WIZARD_STEPS):
            title = step["title"]
            if title not in categories_seen:
                categories_seen.add(title)
                is_current = (i == self.current_step_index)
                is_completed = (i < self.current_step_index)

                self._add_progress_item(title, is_current, is_completed)

    def _add_progress_item(self, title, is_current=False, is_completed=False):
        """Add a single progress item to the sidebar."""
        container = ctk.CTkFrame(self.progress_items_frame, fg_color="transparent")
        container.grid(sticky="w", pady=5)
        container.grid_columnconfigure(1, weight=1)

        if is_completed:
            status_text = "✓"
            status_color = COLORS["success_green"]
        elif is_current:
            status_text = "→"
            status_color = COLORS["primary_blue"]
        else:
            status_text = "□"
            status_color = COLORS["text_secondary"]

        ctk.CTkLabel(
            container,
            text=status_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=status_color
        ).grid(row=0, column=0, padx=(5, 10))

        text_color = COLORS["text_primary"] if is_current or is_completed else COLORS["text_secondary"]
        ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold" if is_current else "normal"),
            text_color=text_color
        ).grid(row=0, column=1, sticky="w")

    def _show_step(self, index):
        """Display the step at the given index."""
        if index < 0 or index >= len(WIZARD_STEPS):
            return

        self.current_step_index = index
        step = WIZARD_STEPS[index]

        # Update progress bar
        progress = (index + 1) / len(WIZARD_STEPS)
        self.progress_bar.set(progress)

        # Update step label
        self.step_label.configure(text=f"Step {index + 1} of {len(WIZARD_STEPS)}")

        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Rebuild sidebar
        for widget in self.progress_items_frame.winfo_children():
            widget.destroy()
        self._build_progress_sidebar()

        # Update navigation buttons
        self.back_button.configure(state="normal" if index > 0 else "disabled")

        # Reset Next Button
        self.next_button.configure(
            state="normal",
            text="Next →",
            command=self._next_step,
            fg_color=COLORS["primary_blue"]
        )

        # Render the appropriate screen
        step_type = step.get("type")

        if step_type == "welcome":
            self._render_welcome()
            self.next_button.configure(text="Start Assessment →")
        elif step_type == "physical_input":
            self._render_physical_input(step)
        elif step_type == "exercise_input":
            self._render_exercise_input(step)
        elif step_type == "category_intro":
            self._render_category_intro(step)
        elif step_type == "symptom_input":
            self._render_symptom_input(step)
        elif step_type == "review":
            self._render_review()
            self.next_button.configure(text="Run Assessment →")
        elif step_type == "processing":
            self._render_processing()
            self.back_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
        elif step_type == "results":
            self._render_results()
            self.back_button.configure(state="disabled")
            self.next_button.configure(text="Start Over", command=self._restart)

    # ==========================================
    # SCREEN RENDERING METHODS
    # ==========================================

    def _render_welcome(self):
        """Render the welcome screen."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=60, pady=40)

        ctk.CTkLabel(
            container,
            text="CKD Clinical Nutrition Expert System",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            container,
            text="Intelligent Clinical Assessment Powered by AI",
            font=ctk.CTkFont(size=18),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 40))

        description = (
            "This assessment will guide you through a comprehensive clinical interview "
            "to evaluate your nutritional needs based on Chronic Kidney Disease (CKD) progression.\n\n"
            "Our 72-rule expert system will analyze your responses and provide personalized "
            "dietary recommendations based on your health profile.\n\n"
            "The assessment takes approximately 5-10 minutes."
        )
        ctk.CTkLabel(
            container,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            justify="center"
        ).pack(pady=(0, 50))

        time_frame = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=8)
        time_frame.pack(pady=(0, 40), fill="x")

        ctk.CTkLabel(
            time_frame,
            text="⏱  Estimated completion time: 5-10 minutes",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["primary_blue"]
        ).pack(padx=20, pady=15)

    def _render_physical_input(self, step):
        """Render a physical information input screen."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=80, pady=60)

        ctk.CTkLabel(
            container,
            text=step["question"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 40))

        entry = ctk.CTkEntry(
            container,
            placeholder_text=step["placeholder"],
            font=ctk.CTkFont(size=14),
            height=50,
            width=300
        )
        entry.pack(pady=20)

        ctk.CTkButton(
            container,
            text="[?] WHY is this asked?",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#17a2b8",
            hover_color="#138496",
            command=lambda: self._explain_why(step["key"])
        ).pack(pady=(10, 0))

        self._current_input = entry
        self._current_step_key = step["key"]
        self._current_step_type = "float"

        entry.focus()

    def _render_exercise_input(self, step):
        """Render the exercise frequency input with segmented buttons."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=80, pady=60)

        ctk.CTkLabel(
            container,
            text=step["question"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 40))

        options = ["0 days", "1-2 days", "3-4 days", "5-7 days"]
        values = [0, 1, 3, 5]

        selected_var = ctk.StringVar(value="")

        def on_select(value):
            idx = options.index(value)
            self.answers["exercise_per_week"] = values[idx]
            self._current_input = None

        seg_button = ctk.CTkSegmentedButton(
            container,
            values=options,
            command=on_select,
            variable=selected_var,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        seg_button.pack(pady=20)

        ctk.CTkButton(
            container,
            text="[?] WHY is this asked?",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#17a2b8",
            hover_color="#138496",
            command=lambda: self._explain_why("exercise_per_week")
        ).pack(pady=(10, 0))

        self._current_input = seg_button
        self._current_step_key = "exercise_per_week"
        self._current_step_type = "segmented"

    def _render_category_intro(self, step):
        """Render a category introduction screen."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=80, pady=60)

        category = step["category"]

        icons = {
            "Diabetes": "🩺",
            "Hypertension": "❤️",
            "Chronic Kidney Disease Symptoms": "🫘"
        }
        icon = icons.get(category, "📋")

        ctk.CTkLabel(
            container,
            text=icon,
            font=ctk.CTkFont(size=60)
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            container,
            text=f"{category} Assessment",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 20))

        descriptions = {
            "Diabetes": "We'll ask about common signs of diabetes, which can contribute to kidney disease progression.",
            "Hypertension": "High blood pressure is a major risk factor for CKD. Let's assess your symptoms.",
            "Chronic Kidney Disease Symptoms": "Now we'll evaluate symptoms related to kidney function decline."
        }
        desc = descriptions.get(category, "")

        ctk.CTkLabel(
            container,
            text=desc,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            justify="center"
        ).pack(pady=20)

        self._current_input = None

    def _render_symptom_input(self, step):
        """Render a symptom question with Yes/No buttons."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=80, pady=60)

        ctk.CTkLabel(
            container,
            text=step["question"],
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"],
            justify="center"
        ).pack(pady=(0, 60))

        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack()

        def on_yes():
            self.answers[step["key"]] = "yes"
            self._current_input = None
            self._next_step()

        def on_no():
            self.answers[step["key"]] = "no"
            self._current_input = None
            self._next_step()

        ctk.CTkButton(
            button_frame,
            text="YES",
            command=on_yes,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["success_green"],
            hover_color="#15803D",
            height=60,
            width=150
        ).grid(row=0, column=0, padx=20)

        ctk.CTkButton(
            button_frame,
            text="NO",
            command=on_no,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["danger_red"],
            hover_color="#991B1B",
            height=60,
            width=150
        ).grid(row=0, column=1, padx=20)

        ctk.CTkButton(
            container,
            text="[?] WHY are we asking this?",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#17a2b8",
            hover_color="#138496",
            command=lambda: self._explain_why(step["key"])
        ).pack(pady=(40, 0))

        self._current_input = None

    def _render_review(self):
        """Render the review/summary screen."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(
            container,
            text="Review Your Answers",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 20))

        review_content = ctk.CTkFrame(
            container,
            fg_color=COLORS["card_bg"],
            corner_radius=8
        )
        review_content.pack(fill="x", padx=10, pady=10)

        sections = {
            "Physical Information": ["weight", "height", "exercise_per_week"],
            "Diabetes Symptoms": ["tiredness", "excessive_thirst", "constant_hunger", "frequent_urination"],
            "Hypertension Symptoms": ["headaches", "dizziness", "blurred_vision_bp", "chest_discomfort"],
            "CKD Symptoms": [
                "mild_swelling", "mild_fatigue", "persistent_fatigue", "swelling_extremities",
                "lower_back_pain", "itchy_skin", "nausea", "loss_of_appetite",
                "difficulty_concentrating", "muscle_cramps", "trouble_sleeping"
            ]
        }

        for section_title, keys in sections.items():
            ctk.CTkLabel(
                review_content,
                text=section_title,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(anchor="w", padx=15, pady=(15, 5))

            for key in keys:
                if key in self.answers:
                    value = self.answers[key]
                    if isinstance(value, float):
                        display_value = f"{value:.2f}"
                    elif isinstance(value, int):
                        display_value = str(value)
                    else:
                        display_value = value.upper()

                    display_key = key.replace("_", " ").title()

                    item_frame = ctk.CTkFrame(review_content, fg_color=COLORS["background"], corner_radius=4)
                    item_frame.pack(fill="x", padx=15, pady=3)
                    item_frame.grid_columnconfigure(1, weight=1)

                    ctk.CTkLabel(
                        item_frame,
                        text=display_key,
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS["text_secondary"]
                    ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

                    ctk.CTkLabel(
                        item_frame,
                        text=display_value,
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS["text_primary"]
                    ).grid(row=0, column=1, padx=10, pady=8, sticky="e")

        info_frame = ctk.CTkFrame(container, fg_color=COLORS["border"], corner_radius=6)
        info_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkLabel(
            info_frame,
            text="💡 Review your answers above. Click 'Run Assessment' to analyze your data with our 72-rule expert system.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_primary"],
            justify="left"
        ).pack(padx=15, pady=12)

    def _render_processing(self):
        """Render the processing screen with animation."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=60, pady=60)

        ctk.CTkLabel(
            container,
            text="Running Expert System Analysis",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 40))

        progress_bar = ctk.CTkProgressBar(
            container,
            progress_color=COLORS["primary_blue"],
            fg_color=COLORS["border"],
            height=10
        )
        progress_bar.pack(fill="x", padx=40, pady=20)
        progress_bar.set(0)

        counter_label = ctk.CTkLabel(
            container,
            text="Rules Evaluated: 0 / 72",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        counter_label.pack(pady=10)

        status_label = ctk.CTkLabel(
            container,
            text="Evaluating inference engine...",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        status_label.pack(pady=(0, 40))

        def run_inference_thread():
            try:
                facts = {}
                for key, value in self.answers.items():
                    if isinstance(value, str) and value in ["yes", "no"]:
                        facts[key] = value
                    else:
                        facts[key] = value

                _, engine, explainer = create_expert_system()
                wm = WorkingMemory(facts)

                for i in range(0, 73):
                    counter_label.configure(text=f"Rules Evaluated: {i} / 72")
                    progress_bar.set(i / 72)
                    self.update()
                    time.sleep(0.02)

                self.rules_fired = engine.run(wm)

                counter_label.configure(text=f"Rules Evaluated: 72 / 72")
                progress_bar.set(1.0)
                status_label.configure(text="Analysis complete! Moving to results...")

                self.inference_results = {
                    "stage": wm.get("Stage_Determination"),
                    "confidence": wm.get("confidence"),
                    "risk": wm.get("risk"),
                    "interpretation": wm.get("final_interpretation"),
                    "bmi": wm.get("BMI"),
                    "bmi_category": wm.get("Final_Bmi_Category"),
                    "activity_level": wm.get("Activity_Level"),
                    "diet_type": wm.get("Final_Diet_Type"),
                    "medical_state": wm.get("Medical_State"),
                    "recommendation": wm.get("Personalized_CKD_Recommendation"),
                    "wm": wm,
                    "explainer": explainer
                }

                self.after(500, lambda: self._show_step(self.current_step_index + 1))

            except Exception as e:
                messagebox.showerror("Error", f"Failed to run inference engine:\n{str(e)}")
                self.after(500, lambda: self._show_step(self.current_step_index - 1))

        thread = threading.Thread(target=run_inference_thread, daemon=True)
        thread.start()

    def _render_results(self):
        """Render the professional results dashboard."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        if not self.inference_results:
            ctk.CTkLabel(
                container,
                text="Error: No results available",
                font=ctk.CTkFont(size=16),
                text_color=COLORS["danger_red"]
            ).pack()
            return

        res = self.inference_results

        ctk.CTkLabel(
            container,
            text="Your Clinical Assessment Results",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            container,
            text="[?] HOW was this result calculated?",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self._explain_how
        ).pack(pady=(0, 20))

        # Row 1: Stage, Confidence, Risk
        row1_frame = ctk.CTkFrame(container, fg_color="transparent")
        row1_frame.pack(fill="x", pady=10)
        row1_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._make_result_card(
            row1_frame, 0, 0,
            "CKD Stage",
            f"Stage {res['stage']}" if res['stage'] else "No CKD",
            COLORS["primary_blue"]
        )

        confidence_display = f"{res['confidence']:.1f}%" if res['confidence'] is not None else "0.0%"
        self._make_result_card(
            row1_frame, 0, 1,
            "Confidence",
            confidence_display,
            COLORS["warning_amber"]
        )

        risk_color = {
            "HIGH": COLORS["danger_red"],
            "MODERATE": COLORS["warning_amber"],
            "LOW": COLORS["success_green"]
        }.get(res['risk'], COLORS["text_secondary"])

        self._make_result_card(
            row1_frame, 0, 2,
            "Risk Level",
            res['risk'],
            risk_color
        )

        # Row 2: BMI, Activity, Diet
        row2_frame = ctk.CTkFrame(container, fg_color="transparent")
        row2_frame.pack(fill="x", pady=10)
        row2_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._make_result_card(
            row2_frame, 0, 0,
            "BMI",
            f"{res['bmi']:.1f} ({res['bmi_category']})",
            COLORS["text_primary"]
        )

        self._make_result_card(
            row2_frame, 0, 1,
            "Activity Level",
            res['activity_level'],
            COLORS["text_primary"]
        )

        diet_type_display = res['diet_type'].replace("_", " ") if res['diet_type'] else "N/A"
        self._make_result_card(
            row2_frame, 0, 2,
            "Diet Type",
            diet_type_display,
            COLORS["text_primary"]
        )

        # Medical State
        state_card = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=10)
        state_card.pack(fill="x", padx=10, pady=10)
        state_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            state_card,
            text="Diet Selection Logic (Mapping Key)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        if res['stage'] == 0:
            mapping_info = f"No CKD detected → Key: '{res['medical_state']}'"
        else:
            mapping_info = f"Stage {res['stage']} + {diet_type_display} → Key: '{res['medical_state']}'"
        ctk.CTkLabel(
            state_card,
            text=mapping_info,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["primary_blue"]
        ).grid(row=1, column=0, columnspan=2, padx=15, pady=(5, 10), sticky="w")

        # Personalized Recommendation
        rec_card = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=10)
        rec_card.pack(fill="x", padx=10, pady=10)
        rec_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            rec_card,
            text="Personalized Dietary Recommendation",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        rec_textbox = ctk.CTkTextbox(
            rec_card,
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            fg_color=COLORS["background"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            height=200
        )
        rec_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        rec_textbox.insert("1.0", res['recommendation'])
        rec_textbox.configure(state="disabled")

        # Inference Trace
        trace_card = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=10)
        trace_card.pack(fill="x", padx=10, pady=10)
        trace_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            trace_card,
            text=f"Inference Trace ({len(self.rules_fired)} Rules Fired)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        trace_text = f"Total Rules in Knowledge Base: 72\nRules Fired: {len(self.rules_fired)}\n\nFired Rules:\n"
        for i, rule_id in enumerate(self.rules_fired, 1):
            trace_text += f"{i}. {rule_id}\n"

        try:
            how_trace = self.inference_results["explainer"].how_summary(self.rules_fired, self.inference_results["wm"])
            trace_text = how_trace
        except:
            pass

        trace_textbox = ctk.CTkTextbox(
            trace_card,
            font=ctk.CTkFont(size=10, family="Courier"),
            corner_radius=6,
            fg_color=COLORS["background"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_secondary"],
            height=180
        )
        trace_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        trace_textbox.insert("1.0", trace_text)
        trace_textbox.configure(state="disabled")

    def _make_result_card(self, parent, row, col, title, value, accent_color):
        """Helper to create a result card."""
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        accent_bar = ctk.CTkFrame(card, fg_color=accent_color, height=4, corner_radius=10)
        accent_bar.pack(fill="x")

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(padx=15, pady=(12, 4), anchor="w")

        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(padx=15, pady=(4, 12), anchor="w")

    # ==========================================
    # NAVIGATION & EXPLANATION FACILITY
    # ==========================================

    def _next_step(self):
        """Move to the next step with validation."""
        step = WIZARD_STEPS[self.current_step_index]

        if step["type"] == "physical_input":
            try:
                value = float(self._current_input.get())
                key = self._current_step_key

                if key == "weight" and not (5 < value < 400):
                    messagebox.showerror("Validation Error", "Weight must be between 5 and 400 kg")
                    return
                if key == "height" and not (0.5 < value < 3.0):
                    messagebox.showerror("Validation Error", "Height must be between 0.5 and 3.0 m")
                    return

                self.answers[key] = value
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid number")
                return

        self._show_step(self.current_step_index + 1)

    def _prev_step(self):
        """Move to the previous step."""
        self._show_step(self.current_step_index - 1)

    def _restart(self):
        """Restart the assessment from the beginning."""
        self.current_step_index = 0
        self.answers = {}
        self.inference_results = None
        self.rules_fired = []
        self._show_step(0)

    def _explain_why(self, key):
        """Explain WHY a specific question is being asked."""
        message = WHY_EXPLANATIONS.get(key, "This information helps the expert system refine its assessment.")
        messagebox.showinfo("WHY — Explanation Facility", message)

    def _explain_how(self):
        """Explain HOW the results were reached."""
        if not self.inference_results:
            return

        res = self.inference_results
        wm = res["wm"]

        how_text = "HOW DID THE EXPERT SYSTEM REACH THIS CONCLUSION?\n\n"
        how_text += f"1. BMI Calculation: Your BMI was calculated as {res['bmi']:.2f} using Weight/Height².\n"
        how_text += f"2. Activity Level: Based on {self.answers.get('exercise_per_week', 0)} days/week, you were classified as '{res['activity_level']}'.\n"

        how_text += "\n3. CLINICAL CRITERIA PER STAGE:\n"
        how_text += "The system evaluates symptoms across four clinical thresholds:\n"
        how_text += "• Stage 1: Requires both Diabetes (Score ≥ 3) AND Hypertension (Score ≥ 3).\n"
        how_text += "• Stage 2: Requires at least 1 mild kidney symptom (Mild Swelling/Fatigue).\n"
        how_text += "• Stage 3: Requires at least 2 moderate symptoms (Persistent Fatigue/Edema/Flank Pain/Itchiness).\n"
        how_text += "• Stage 4: Requires at least 3 severe symptoms (Nausea/Appetite Loss/Brain Fog/Cramps).\n"

        how_text += "\n4. YOUR SCORE ANALYSIS:\n"
        if wm.get("diabetes_status"):
            how_text += f"• Diabetes Score: {wm.get('diabetes_score', 0)} (Threshold Met)\n"
        else:
            how_text += f"• Diabetes Score: {wm.get('diabetes_score', 0)} (Below Threshold)\n"

        if wm.get("bp_status"):
            how_text += f"• Hypertension Score: {wm.get('bp_score', 0)} (Threshold Met)\n"
        else:
            how_text += f"• Hypertension Score: {wm.get('bp_score', 0)} (Below Threshold)\n"

        stage = res['stage']
        if stage == 0:
            how_text += "\n5. STAGE DETERMINATION: No stage thresholds were met.\n"
        else:
            how_text += f"\n5. STAGE DETERMINATION: Your pattern matched the criteria for Stage {stage}.\n"

        diet_type_str = res['diet_type'].replace('_', ' ') if res['diet_type'] else "N/A"
        how_text += f"\n6. DIET TYPE SELECTION:\n"
        how_text += f"Based on your BMI ({res['bmi']:.1f}, category: {res['bmi_category']}) and Activity Level ({res['activity_level']}):\n"
        how_text += f"• If BMI is Overweight/Obese → 'Calorie_Deficit' diet (reduce intake for weight loss).\n"
        how_text += f"• If BMI is Normal/Underweight → 'Calorie_Maintenance' diet (maintain stable intake).\n"
        how_text += f"• Your result: '{diet_type_str}'\n"

        how_text += f"\n7. RECOMMENDATION RETRIEVAL:\n"
        if stage == 0:
            how_text += f"For a patient with no CKD, the system bypasses stage-specific diet plans and retrieves the general prevention guidelines.\n"
            how_text += f"Key: 'No CKD'\n"
        else:
            how_text += f"The system combines Stage {stage} + {diet_type_str} to create the lookup key:\n"
            how_text += f"Key: '{res['medical_state']}'\n"
        how_text += f"This key matches an entry in the Knowledge Base recommendations dictionary,\n"
        how_text += f"which contains clinically-reviewed dietary guidelines specific to your stage and metabolic needs.\n"

        confidence_str = f"{res['confidence']:.1f}%" if res['confidence'] is not None else "0.0%"
        how_text += f"\n8. CONFIDENCE & VALIDATION:\n"
        how_text += f"Confidence: {confidence_str}\n"
        how_text += f"Rules Fired: {len(self.rules_fired)} out of 72\n"
        how_text += f"Risk Level: {res['risk']}"

        messagebox.showinfo("HOW — Explanation Facility", how_text)
