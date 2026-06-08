import customtkinter as ctk
from tkinter import messagebox
import threading
import time

from ckd_expert_system.engine import create_expert_system, WorkingMemory

# ==========================================
# CUSTOMTKINTER CONFIGURATION
# ==========================================
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

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
# WIZARD STEP DEFINITIONS
# ==========================================
WIZARD_STEPS = [
    {"id": "welcome", "title": "Welcome", "type": "welcome"},
    {"id": "weight", "title": "Physical Information", "type": "physical_input", "question": "What is your weight (kg)?", "key": "weight", "placeholder": "e.g., 75.5"},
    {"id": "height", "title": "Physical Information", "type": "physical_input", "question": "What is your height (m)?", "key": "height", "placeholder": "e.g., 1.70"},
    {"id": "exercise", "title": "Physical Information", "type": "exercise_input", "question": "How many days per week do you exercise?", "key": "exercise_per_week"},
    {"id": "diabetes_intro", "title": "Diabetes Screening", "type": "category_intro", "category": "Diabetes"},
    {"id": "tiredness", "title": "Diabetes Screening", "type": "symptom_input", "question": "Do you experience persistent tiredness or fatigue?", "key": "tiredness"},
    {"id": "excessive_thirst", "title": "Diabetes Screening", "type": "symptom_input", "question": "Do you experience excessive thirst?", "key": "excessive_thirst"},
    {"id": "constant_hunger", "title": "Diabetes Screening", "type": "symptom_input", "question": "Do you experience constant hunger?", "key": "constant_hunger"},
    {"id": "frequent_urination", "title": "Diabetes Screening", "type": "symptom_input", "question": "Do you experience frequent urination, especially at night?", "key": "frequent_urination"},
    {"id": "hypertension_intro", "title": "Hypertension Screening", "type": "category_intro", "category": "Hypertension"},
    {"id": "headaches", "title": "Hypertension Screening", "type": "symptom_input", "question": "Do you experience frequent headaches (especially at the back of your head)?", "key": "headaches"},
    {"id": "dizziness", "title": "Hypertension Screening", "type": "symptom_input", "question": "Do you experience dizziness or lightheadedness?", "key": "dizziness"},
    {"id": "blurred_vision_bp", "title": "Hypertension Screening", "type": "symptom_input", "question": "Do you experience blurred vision?", "key": "blurred_vision_bp"},
    {"id": "chest_discomfort", "title": "Hypertension Screening", "type": "symptom_input", "question": "Do you experience chest discomfort or tightness?", "key": "chest_discomfort"},
    {"id": "ckd_intro", "title": "CKD Assessment", "type": "category_intro", "category": "Chronic Kidney Disease Symptoms"},
    {"id": "mild_swelling", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience mild swelling in your ankles or feet?", "key": "mild_swelling"},
    {"id": "mild_fatigue", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience mild, persistent fatigue?", "key": "mild_fatigue"},
    {"id": "persistent_fatigue", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience persistent or worsening fatigue?", "key": "persistent_fatigue"},
    {"id": "swelling_extremities", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience swelling in your hands, legs, or feet?", "key": "swelling_extremities"},
    {"id": "lower_back_pain", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience lower back or flank pain?", "key": "lower_back_pain"},
    {"id": "itchy_skin", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience itchy skin without a rash?", "key": "itchy_skin"},
    {"id": "nausea", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience frequent nausea or urge to vomit?", "key": "nausea"},
    {"id": "loss_of_appetite", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience significant loss of appetite?", "key": "loss_of_appetite"},
    {"id": "difficulty_concentrating", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience difficulty concentrating or brain fog?", "key": "difficulty_concentrating"},
    {"id": "muscle_cramps", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience muscle cramps, especially in your legs?", "key": "muscle_cramps"},
    {"id": "trouble_sleeping", "title": "CKD Assessment", "type": "symptom_input", "question": "Do you experience trouble falling or staying asleep?", "key": "trouble_sleeping"},
    {"id": "review", "title": "Review Answers", "type": "review"},
    {"id": "processing", "title": "Processing", "type": "processing"},
    {"id": "results", "title": "Results", "type": "results"},
]

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
        # Collect unique categories
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

        # Icon/status
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

        # Title
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

        # Reset Next Button (Crucial for Start Over logic)
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

    def _render_welcome(self):
        """Render the welcome screen."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=60, pady=40)

        # Title
        ctk.CTkLabel(
            container,
            text="CKD Clinical Nutrition Expert System",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 10))

        # Subtitle
        ctk.CTkLabel(
            container,
            text="Intelligent Clinical Assessment Powered by AI",
            font=ctk.CTkFont(size=18),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 40))

        # Description
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

        # Estimated time
        time_frame = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=8)
        time_frame.pack(pady=(0, 40), fill="x")

        ctk.CTkLabel(
            time_frame,
            text="⏱  Estimated completion time: 5-10 minutes",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["primary_blue"]
        ).pack(padx=20, pady=15)

    def _render_physical_input(self, step):
        """Render a physical information input screen (one question at a time)."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=80, pady=60)

        # Question title
        ctk.CTkLabel(
            container,
            text=step["question"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 40))

        # Input field
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

        # Store reference for validation
        self._current_input = entry
        self._current_step_key = step["key"]
        self._current_step_type = "float"

        # Focus on entry
        entry.focus()

    def _render_exercise_input(self, step):
        """Render the exercise frequency input with segmented buttons."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=80, pady=60)

        # Question title
        ctk.CTkLabel(
            container,
            text=step["question"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 40))

        # Segmented button for exercise frequency
        options = ["0 days", "1-2 days", "3-4 days", "5-7 days"]
        values = [0, 1, 3, 5]  # Approximate values

        selected_var = ctk.StringVar(value="")

        def on_select(value):
            idx = options.index(value)
            self.answers["exercise_per_week"] = values[idx]
            self._current_input = None  # Mark as filled

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

        # Store reference
        self._current_input = seg_button
        self._current_step_key = "exercise_per_week"
        self._current_step_type = "segmented"

    def _render_category_intro(self, step):
        """Render a category introduction screen."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=80, pady=60)

        category = step["category"]

        # Icon/emoji based on category
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

        # Description
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

        self._current_input = None  # Mark as auto-completed

    def _render_symptom_input(self, step):
        """Render a symptom question with Yes/No buttons."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=80, pady=60)

        # Question title
        ctk.CTkLabel(
            container,
            text=step["question"],
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"],
            justify="center"
        ).pack(pady=(0, 60))

        # Yes/No buttons
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

        self._current_input = None  # Symptom questions auto-advance

    def _render_review(self):
        """Render the review/summary screen."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=20)

        # Title
        ctk.CTkLabel(
            container,
            text="Review Your Answers",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 20))

        # Content frame (removed nested scrollable frame)
        review_content = ctk.CTkFrame(
            container,
            fg_color=COLORS["card_bg"],
            corner_radius=8
        )
        review_content.pack(fill="x", padx=10, pady=10)

        # Display all answers
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
            # Section header
            ctk.CTkLabel(
                review_content,
                text=section_title,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(anchor="w", padx=15, pady=(15, 5))

            # Section content
            for key in keys:
                if key in self.answers:
                    value = self.answers[key]
                    if isinstance(value, float):
                        display_value = f"{value:.2f}"
                    elif isinstance(value, int):
                        display_value = str(value)
                    else:
                        display_value = value.upper()

                    # Convert key to display name
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

        # Info message
        info_frame = ctk.CTkFrame(container, fg_color=COLORS["border"], corner_radius=6)
        info_frame.pack(fill="x", padx=10, pady=20)

        info_buttons = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_buttons.pack(padx=15, pady=12)

        ctk.CTkLabel(
            info_buttons,
            text="💡 Review your answers above. Click 'Run Assessment' to analyze your data with our 72-rule expert system.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_primary"],
            justify="left"
        ).pack(side="left")

    def _render_processing(self):
        """Render the processing screen with animation."""
        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=60, pady=60)

        # Title
        ctk.CTkLabel(
            container,
            text="Running Expert System Analysis",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 40))

        # Progress bar
        progress_bar = ctk.CTkProgressBar(
            container,
            progress_color=COLORS["primary_blue"],
            fg_color=COLORS["border"],
            height=10
        )
        progress_bar.pack(fill="x", padx=40, pady=20)
        progress_bar.set(0)

        # Rule counter label
        counter_label = ctk.CTkLabel(
            container,
            text="Rules Evaluated: 0 / 72",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        counter_label.pack(pady=10)

        # Status label
        status_label = ctk.CTkLabel(
            container,
            text="Evaluating inference engine...",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        status_label.pack(pady=(0, 40))

        # Run inference in a separate thread
        def run_inference_thread():
            try:
                # Build facts from answers
                facts = {}
                for key, value in self.answers.items():
                    if isinstance(value, str) and value in ["yes", "no"]:
                        facts[key] = value
                    else:
                        facts[key] = value

                # Initialize engine
                _, engine, explainer = create_expert_system()
                wm = WorkingMemory(facts)

                # Simulate animation during inference
                for i in range(0, 73):
                    counter_label.configure(text=f"Rules Evaluated: {i} / 72")
                    progress_bar.set(i / 72)
                    self.update()
                    time.sleep(0.02)  # Smooth animation

                # Run actual inference
                self.rules_fired = engine.run(wm)

                # Final update
                counter_label.configure(text=f"Rules Evaluated: 72 / 72")
                progress_bar.set(1.0)
                status_label.configure(text="Analysis complete! Moving to results...")

                # Store results
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

                # Move to results after a brief delay
                self.after(500, lambda: self._show_step(self.current_step_index + 1))

            except Exception as e:
                messagebox.showerror("Error", f"Failed to run inference engine:\n{str(e)}")
                self.after(500, lambda: self._show_step(self.current_step_index - 1))

        # Start thread
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

        # Title
        ctk.CTkLabel(
            container,
            text="Your Clinical Assessment Results",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 10))

        # HOW button
        ctk.CTkButton(
            container,
            text="[?] HOW was this result calculated?",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self._explain_how
        ).pack(pady=(0, 20))

        # ===== CARDS LAYOUT (NO INNER SCROLLFRAME) =====

        # Row 1: Stage, Confidence, Risk
        row1_frame = ctk.CTkFrame(container, fg_color="transparent")
        row1_frame.pack(fill="x", pady=10)
        row1_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # CKD Stage Card
        self._make_result_card(
            row1_frame, 0, 0,
            "CKD Stage",
            f"Stage {res['stage']}" if res['stage'] else "No CKD",
            COLORS["primary_blue"]
        )

        # Confidence Card
        self._make_result_card(
            row1_frame, 0, 1,
            "Confidence",
            f"{res['confidence']:.1f}%",
            COLORS["warning_amber"]
        )

        # Risk Level Card
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

        self._make_result_card(
            row2_frame, 0, 2,
            "Diet Type",
            res['diet_type'].replace("_", " "),
            COLORS["text_primary"]
        )

        # Medical State
        state_card = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=10)
        state_card.pack(fill="x", padx=10, pady=10)
        state_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            state_card,
            text="Medical State",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            state_card,
            text=res['medical_state'],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
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
            height=180
        )
        rec_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        rec_textbox.insert("1.0", res['recommendation'])
        rec_textbox.configure(state="disabled")

        # Inference Trace (Rules Fired)
        trace_card = ctk.CTkFrame(container, fg_color=COLORS["card_bg"], corner_radius=10)
        trace_card.pack(fill="x", padx=10, pady=10)
        trace_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            trace_card,
            text=f"Inference Trace ({len(self.rules_fired)} Rules Fired)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        # Build trace text
        trace_text = f"Total Rules in Knowledge Base: 72\nRules Fired: {len(self.rules_fired)}\n\nFired Rules:\n"
        for i, rule_id in enumerate(self.rules_fired, 1):
            trace_text += f"{i}. {rule_id}\n"

        # Try to get HOW summary from explainer
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

        # Accent bar at top
        accent_bar = ctk.CTkFrame(card, fg_color=accent_color, height=4, corner_radius=10)
        accent_bar.pack(fill="x")

        # Title
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(padx=15, pady=(12, 4), anchor="w")

        # Value
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(padx=15, pady=(4, 12), anchor="w")

    def _next_step(self):
        """Move to the next step with validation."""
        step = WIZARD_STEPS[self.current_step_index]

        # Validate current step
        if step["type"] == "physical_input":
            try:
                value = float(self._current_input.get())
                key = self._current_step_key

                # Validate ranges
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

        # Move to next step
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

    # ==========================================
    # EXPLANATION FACILITY (WHY / HOW)
    # ==========================================

    def _explain_why(self, key):
        """Explain WHY a specific question is being asked."""
        explanations = {
            "weight": "Weight is used to calculate your Body Mass Index (BMI). BMI is a critical factor in determining your risk for metabolic syndrome, which often coexists with kidney disease.",
            "height": "Height is required to calculate your BMI accurately. This helps the expert system determine if you are underweight, normal, overweight, or obese, which affects nutritional recommendations.",
            "exercise_per_week": "Exercise frequency determines your activity level. This is used by the expert system to decide between calorie deficit or maintenance diets based on your BMI and kidney stage.",
            "tiredness": "Tiredness can be an early sign of diabetes or a symptom of waste build-up (uremia) in kidney disease. Rules R1 and R16 monitor this.",
            "excessive_thirst": "Polydipsia (excessive thirst) is a primary indicator of high blood sugar/diabetes. Rule R3 uses this to assess metabolic health.",
            "constant_hunger": "Polyphagia (constant hunger) combined with other symptoms points toward diabetes, a leading cause of kidney damage. Rule R4 tracks this.",
            "frequent_urination": "Polyuria (frequent urination) suggests the kidneys are working overtime to filter excess sugar or that they are losing the ability to concentrate urine. Rule R2 evaluates this.",
            "headaches": "Frequent headaches at the back of the head are a common symptom of high blood pressure (hypertension), which can damage kidney vessels. Rules R7 and R10 monitor this.",
            "dizziness": "Dizziness is often associated with blood pressure fluctuations or early signs of anemia related to kidney function decline. Rule R8 tracks this.",
            "blurred_vision_bp": "High blood pressure can affect the blood vessels in your eyes. This symptom is used by rules R9 and R10 to assess hypertension severity.",
            "chest_discomfort": "Chest discomfort can indicate cardiovascular strain related to hypertension, which is a major complication of Chronic Kidney Disease.",
            "mild_swelling": "Mild swelling in extremities is an early sign (Stage 2) that the kidneys are beginning to struggle with fluid and sodium balance. Rule R15 monitors this.",
            "mild_fatigue": "Mild fatigue is often the first sign that toxins are not being filtered efficiently. Rule R16 uses this to detect early-stage CKD.",
            "persistent_fatigue": "Persistent or worsening fatigue (Stage 3) often indicates anemia, as failing kidneys produce less erythropoietin. Rules R18 and R21 evaluate this.",
            "swelling_extremities": "Significant swelling (edema) in hands and feet is a hallmark of Stage 3 kidney disease. Rules R19 and R21 monitor fluid retention.",
            "lower_back_pain": "Flank or lower back pain can indicate kidney inflammation, stones, or structural issues affecting function. Rule R20 tracks this.",
            "itchy_skin": "Pruritus (itchy skin) is caused by the build-up of phosphorus and other waste products in the blood. Rule R21 monitors this in Stage 3.",
            "nausea": "Frequent nausea is a sign of uremia (Stage 4), where urea build-up in the blood becomes toxic to the digestive system. Rules R23 and R27 monitor this.",
            "loss_of_appetite": "Anorexia or loss of appetite is a common metabolic symptom of advanced kidney disease (Stage 4). Rules R24 and R27 track this.",
            "difficulty_concentrating": "Cognitive fog or difficulty concentrating is caused by the effect of toxins on the nervous system in advanced stages. Rules R25 and R27 monitor this.",
            "muscle_cramps": "Muscle cramps result from electrolyte imbalances (calcium, potassium) caused by failing kidney regulation. Rule R26 evaluates this.",
            "trouble_sleeping": "Sleep disturbances are common in Stage 4 due to restless legs, itching, or metabolic imbalances. Rule R27 monitors this.",
        }

        message = explanations.get(key, "This information helps the expert system refine its assessment of your clinical state.")
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

        # Explain Score Logic
        how_text += "\n3. SYMPTOM SCORING:\n"
        if wm.get("diabetes_status"):
            how_text += "• Diabetes markers were positive (Score ≥ 3).\n"
        if wm.get("bp_status"):
            how_text += "• Hypertension markers were positive (Score ≥ 3).\n"

        stage = res['stage']
        if stage == 0:
            how_text += "\n4. STAGE DETERMINATION: No significant CKD symptoms were matched across the 72-rule knowledge base.\n"
        else:
            how_text += f"\n4. STAGE DETERMINATION: The forward-chaining engine matched your symptom pattern to clinical criteria for Stage {stage}.\n"

        how_text += f"\n5. DIET LOGIC: A '{res['diet_type'].replace('_', ' ')}' was selected based on your BMI category ({res['bmi_category']}) and CKD stage.\n"

        how_text += f"\n6. CONFIDENCE: The {res['confidence']:.1f}% confidence level reflects the density of symptomatic matches found during inference."

        messagebox.showinfo("HOW — Explanation Facility", how_text)


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    app = DietNutriESApp()
    app.mainloop()
