"""
interface_ui.py — Premium CustomTkinter GUI for the CKD Expert System.

Redesign of the original wizard into a SaaS-style shell: dark navigation rail,
slide page-transitions, hover-elevation result cards, an eased button set, a real
spinner during inference, and a slide-in WHY/HOW explanation drawer that replaces
the old messagebox popups. Engine wiring and result keys are unchanged.

Requires (next to this file in ckd_expert_system/ui/):  theme.py, components.py
"""

import threading

import customtkinter as ctk

from ckd_expert_system.engine import create_expert_system, WorkingMemory
from ckd_expert_system.ui.questions import WIZARD_STEPS, WHY_EXPLANATIONS

try:                                   # in-package or standalone
    from .theme import theme, SP, R
    from .components import (Card, Button, Spinner, Drawer, toast,
                             slide_swap, NavItem)
except ImportError:
    from theme import theme, SP, R
    from components import (Card, Button, Spinner, Drawer, toast,
                            slide_swap, NavItem)


# Section metadata for the nav rail (derived from WIZARD_STEPS titles).
SECTION_ICONS = {
    "Welcome": "◴", "Physical Information": "⚖", "Diabetes Screening": "✚",
    "Hypertension Screening": "♥", "CKD Assessment": "◉",
    "Review Answers": "▤", "Processing": "⟳", "Results": "✓",
}

REVIEW_SECTIONS = {
    "Physical Information": ["weight", "height", "exercise_per_week"],
    "Diabetes Symptoms": ["tiredness", "excessive_thirst", "constant_hunger",
                          "frequent_urination"],
    "Hypertension Symptoms": ["headaches", "dizziness", "blurred_vision_bp",
                             "chest_discomfort"],
    "CKD Symptoms": ["mild_swelling", "mild_fatigue", "persistent_fatigue",
                     "swelling_extremities", "lower_back_pain", "itchy_skin",
                     "nausea", "loss_of_appetite", "difficulty_concentrating",
                     "muscle_cramps", "trouble_sleeping"],
}


class DietNutriESApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Renal IQ — CKD Clinical Nutrition Expert System")
        self.geometry("1280x800")
        self.minsize(1080, 700)

        self.current_step_index = 0
        self.answers = {}
        self.inference_results = None
        self.rules_fired = []
        self._infer_done = False
        self._infer_error = None

        # ordered unique section titles + the first step index of each
        self._sections = []
        for i, s in enumerate(WIZARD_STEPS):
            if s["title"] not in [t for t, _ in self._sections]:
                self._sections.append((s["title"], i))

        self.configure(fg_color=theme.c("bg"))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.drawer = Drawer(self)          # global, floats above everything
        self._build_shell()
        self._set_step(0, animate=False)

    # ======================================================================
    # SHELL
    # ======================================================================
    def _build_shell(self):
        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=272, corner_radius=0,
                                    fg_color=theme.c("sidebar"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # brand
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=SP[5], pady=(SP[6], SP[6]))
        logo = ctk.CTkFrame(brand, width=42, height=42, corner_radius=R["md"],
                            fg_color=theme.c("accent"))
        logo.pack(side="left"); logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="◉", font=theme.font("h2"),
                     text_color=theme.c("text_on_accent")).pack(expand=True)
        txt = ctk.CTkFrame(brand, fg_color="transparent"); txt.pack(side="left",
                     padx=SP[3])
        ctk.CTkLabel(txt, text="Renal IQ", font=theme.font("h3"),
                     text_color=theme.c("text_on_dark")).pack(anchor="w")
        ctk.CTkLabel(txt, text="Clinical Nutrition AI", font=theme.font("micro"),
                     text_color=theme.c("text_on_dark_muted")).pack(anchor="w")

        ctk.CTkLabel(self.sidebar, text="ASSESSMENT", font=theme.font("micro"),
                     text_color=theme.c("text_on_dark_muted")).pack(
                     anchor="w", padx=SP[6], pady=(SP[2], SP[2]))

        self.nav_holder = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_holder.pack(fill="x", padx=SP[3])

        # footer: progress + theme toggle
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=SP[5], pady=SP[5])
        self.side_progress = ctk.CTkProgressBar(footer, progress_color=theme.c("accent"),
                                                fg_color="#1d2c3a", height=6,
                                                corner_radius=R["pill"])
        self.side_progress.pack(fill="x", pady=(0, SP[2]))
        self.side_step_lbl = ctk.CTkLabel(footer, text="", font=theme.font("micro"),
                                          text_color=theme.c("text_on_dark_muted"))
        self.side_step_lbl.pack(anchor="w")
        Button(footer, text="◑  Toggle theme", variant="secondary", height=38,
               command=self._toggle_theme).pack(fill="x", pady=(SP[4], 0))

    def _build_main(self):
        self.main = ctk.CTkFrame(self, fg_color=theme.c("bg"), corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # top bar
        self.topbar = ctk.CTkFrame(self.main, fg_color=theme.c("bg"), height=78,
                                   corner_radius=0)
        self.topbar.grid(row=0, column=0, sticky="ew", padx=SP[8], pady=(SP[6], SP[2]))
        self.topbar.grid_propagate(False)
        tcol = ctk.CTkFrame(self.topbar, fg_color="transparent"); tcol.pack(side="left")
        self.page_title = ctk.CTkLabel(tcol, text="", font=theme.font("h1"),
                                       text_color=theme.c("text"))
        self.page_title.pack(anchor="w")
        self.page_sub = ctk.CTkLabel(tcol, text="", font=theme.font("caption"),
                                     text_color=theme.c("text_muted"))
        self.page_sub.pack(anchor="w")

        # swappable page region (transitions happen here)
        self.page = ctk.CTkFrame(self.main, fg_color="transparent")
        self.page.grid(row=1, column=0, sticky="nsew", padx=SP[8], pady=SP[2])

        # footer nav
        nav = ctk.CTkFrame(self.main, fg_color=theme.c("bg"))
        nav.grid(row=2, column=0, sticky="ew", padx=SP[8], pady=(SP[2], SP[6]))
        nav.grid_columnconfigure(1, weight=1)
        self.back_btn = Button(nav, text="←  Back", variant="secondary",
                               command=self._prev_step, width=120)
        self.back_btn.grid(row=0, column=0, sticky="w")
        self.step_label = ctk.CTkLabel(nav, text="", font=theme.font("caption"),
                                       text_color=theme.c("text_muted"))
        self.step_label.grid(row=0, column=1)
        self.next_btn = Button(nav, text="Next  →", variant="primary",
                               command=self._next_step, width=160)
        self.next_btn.grid(row=0, column=2, sticky="e")

    # ======================================================================
    # STEP DRIVER
    # ======================================================================
    def _set_step(self, index, animate=True):
        if index < 0 or index >= len(WIZARD_STEPS):
            return
        direction = "left" if index >= self.current_step_index else "right"
        self.current_step_index = index
        step = WIZARD_STEPS[index]

        # chrome
        self._render_nav()
        prog = (index + 1) / len(WIZARD_STEPS)
        self.side_progress.set(prog)
        self.side_step_lbl.configure(text=f"Step {index + 1} of {len(WIZARD_STEPS)}")
        self.step_label.configure(text=f"Step {index + 1} of {len(WIZARD_STEPS)}")
        self.page_title.configure(text=self._title_for(step))
        self.page_sub.configure(text=self._subtitle_for(step))
        self._refresh_nav_buttons(step)

        # body
        if animate and self.page.winfo_children():
            slide_swap(self.page, self._build_screen, direction)
        else:
            for w in self.page.winfo_children():
                w.destroy()
            holder = ctk.CTkFrame(self.page, fg_color="transparent")
            holder.pack(fill="both", expand=True)
            self._build_screen(holder)

    def _title_for(self, step):
        return {"welcome": "Welcome", "review": "Review your answers",
                "processing": "Analyzing", "results": "Assessment results"
                }.get(step["type"], step["title"])

    def _subtitle_for(self, step):
        t = step["type"]
        if t == "results":
            return "72-rule forward-chaining inference"
        if t in ("symptom_input", "physical_input", "exercise_input", "category_intro"):
            return step["title"]
        return "Clinical nutrition assessment"

    def _refresh_nav_buttons(self, step):
        t = step["type"]
        self.back_btn.configure(state="normal" if self.current_step_index > 0 else "disabled")
        self.next_btn.configure(state="normal", command=self._next_step)

        if t == "welcome":
            self.next_btn.configure(text="Start assessment  →")
        elif t == "review":
            self.next_btn.configure(text="Run assessment  →")
        elif t == "processing":
            self.back_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled", text="Analyzing…")
        elif t == "results":
            self.back_btn.configure(state="disabled")
            self.next_btn.configure(text="Start over", command=self._restart)
        elif t == "symptom_input":
            # answered via Yes/No buttons
            self.next_btn.configure(state="disabled", text="Choose Yes or No")
        else:
            self.next_btn.configure(text="Next  →")

    # ----------------------------------------------------------------- nav rail
    def _render_nav(self):
        for w in self.nav_holder.winfo_children():
            w.destroy()
        cur_section = WIZARD_STEPS[self.current_step_index]["title"]
        for title, first_idx in self._sections:
            # last step index belonging to this section
            last_idx = max(i for i, s in enumerate(WIZARD_STEPS) if s["title"] == title)
            active = (title == cur_section)
            done = (last_idx < self.current_step_index)
            # allow clicking only to go back to an earlier (answered) section
            cmd = None
            if first_idx < self.current_step_index and not active:
                cmd = lambda idx=first_idx: self._set_step(idx)
            NavItem(self.nav_holder, SECTION_ICONS.get(title, "•"), title,
                    active=active, done=done, command=cmd).pack(fill="x", pady=2)

    # ======================================================================
    # SCREEN BUILDERS  (each builds into `parent`)
    # ======================================================================
    def _build_screen(self, parent):
        step = WIZARD_STEPS[self.current_step_index]
        t = step["type"]
        builder = {
            "welcome": self._screen_welcome,
            "physical_input": self._screen_physical,
            "exercise_input": self._screen_exercise,
            "category_intro": self._screen_category,
            "symptom_input": self._screen_symptom,
            "review": self._screen_review,
            "processing": self._screen_processing,
            "results": self._screen_results,
        }.get(t)
        if builder:
            builder(parent, step)

    # ---- welcome ----------------------------------------------------------
    def _screen_welcome(self, parent, step):
        card = Card(parent, accent=theme.c("accent"), padding=SP[8])
        card.pack(fill="both", expand=True)
        b = card.body
        ctk.CTkLabel(b, text="Clinical nutrition, decided by rules you can read",
                     font=theme.font("display"), text_color=theme.c("text"),
                     wraplength=720, justify="left").pack(anchor="w")
        ctk.CTkLabel(b, justify="left", wraplength=720,
                     text="A guided clinical interview evaluates your nutritional needs "
                          "across CKD progression. A 72-rule expert system analyzes your "
                          "responses and explains every step of its reasoning.",
                     font=theme.font("body"),
                     text_color=theme.c("text_muted")).pack(anchor="w", pady=(SP[4], SP[6]))

        chips = ctk.CTkFrame(b, fg_color="transparent"); chips.pack(anchor="w")
        for txt in ("72 production rules", "~5–10 minutes", "WHY / HOW explainable"):
            chip = ctk.CTkFrame(chips, fg_color=theme.c("accent_soft"),
                                corner_radius=R["pill"])
            chip.pack(side="left", padx=(0, SP[2]))
            ctk.CTkLabel(chip, text=f"  {txt}  ", font=theme.font("label"),
                         text_color=theme.c("accent")).pack(padx=SP[2], pady=SP[1])

    # ---- physical (weight / height) --------------------------------------
    def _screen_physical(self, parent, step):
        card = Card(parent, padding=SP[8]); card.pack(fill="both", expand=True)
        b = card.body
        ctk.CTkLabel(b, text=step["question"], font=theme.font("h2"),
                     text_color=theme.c("text")).pack(anchor="w", pady=(0, SP[5]))

        entry = ctk.CTkEntry(
            b,
            placeholder_text=step.get("placeholder", ""),
            font=theme.font("body"),
            height=52,
            width=360,
            corner_radius=R["md"],
            border_color=theme.c("border"),
            fg_color=theme.c("surface_alt"),
            text_color=theme.c("text"),   # ✅ FIX HERE
        )
        entry.pack(anchor="w")
        if step["key"] in self.answers:
            entry.insert(0, str(self.answers[step["key"]]))
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=theme.c("focus_ring")))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=theme.c("border")))
        entry.bind("<Return>", lambda e: self._next_step())

        self._error_lbl = ctk.CTkLabel(b, text="", font=theme.font("caption"),
                                       text_color=theme.c("danger"))
        self._error_lbl.pack(anchor="w", pady=(SP[2], 0))

        Button(b, text="?  Why we ask this", variant="ghost", height=38,
               command=lambda: self._why(step["key"])).pack(anchor="w", pady=(SP[6], 0))

        self._current_input = entry
        self._current_step_key = step["key"]
        entry.focus()

    # ---- exercise (segmented) --------------------------------------------
    def _screen_exercise(self, parent, step):
        card = Card(parent, padding=SP[8]); card.pack(fill="both", expand=True)
        b = card.body
        ctk.CTkLabel(b, text=step["question"], font=theme.font("h2"),
                     text_color=theme.c("text")).pack(anchor="w", pady=(0, SP[5]))

        options = ["0 days", "1–2 days", "3–4 days", "5–7 days"]
        values = [0, 1, 3, 5]
        seg = ctk.CTkSegmentedButton(
            b, values=options, font=theme.font("body_md"), height=46,
            corner_radius=R["md"], selected_color=theme.c("accent"),
            selected_hover_color=theme.c("accent_hover"),
            fg_color=theme.c("surface_alt"), unselected_color=theme.c("surface_alt"),
            text_color=theme.c("text"),
            command=lambda v: self.answers.__setitem__("exercise_per_week",
                                                        values[options.index(v)]))
        seg.pack(anchor="w")
        # preselect if revisiting
        if "exercise_per_week" in self.answers and self.answers["exercise_per_week"] in values:
            seg.set(options[values.index(self.answers["exercise_per_week"])])

        Button(b, text="?  Why we ask this", variant="ghost", height=38,
               command=lambda: self._why("exercise_per_week")).pack(anchor="w",
               pady=(SP[6], 0))
        self._current_input = None
        self._current_step_key = "exercise_per_week"

    # ---- category intro ---------------------------------------------------
    def _screen_category(self, parent, step):
        category = step["category"]
        descriptions = {
            "Diabetes": "Common signs of diabetes, a leading driver of kidney damage.",
            "Hypertension": "High blood pressure is a major risk factor for CKD.",
            "Chronic Kidney Disease Symptoms": "Symptoms related to declining kidney function.",
        }
        card = Card(parent, accent=theme.c("accent"), padding=SP[8])
        card.pack(fill="both", expand=True)
        b = card.body
        badge = ctk.CTkFrame(b, width=64, height=64, corner_radius=R["lg"],
                             fg_color=theme.c("accent_soft"))
        badge.pack(anchor="w"); badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=SECTION_ICONS.get(step["title"], "◉"),
                     font=theme.font("display"),
                     text_color=theme.c("accent")).pack(expand=True)
        ctk.CTkLabel(b, text=f"{category}", font=theme.font("h1"),
                     text_color=theme.c("text")).pack(anchor="w", pady=(SP[5], SP[2]))
        ctk.CTkLabel(b, text=descriptions.get(category, ""), font=theme.font("body"),
                     text_color=theme.c("text_muted"), wraplength=620,
                     justify="left").pack(anchor="w")
        self._current_input = None

    # ---- symptom (Yes / No, auto-advance) --------------------------------
    def _screen_symptom(self, parent, step):
        card = Card(parent, padding=SP[8]); card.pack(fill="both", expand=True)
        b = card.body
        ctk.CTkLabel(b, text=step["question"], font=theme.font("h2"),
                     text_color=theme.c("text"), wraplength=680,
                     justify="left").pack(anchor="w", pady=(0, SP[8]))

        row = ctk.CTkFrame(b, fg_color="transparent"); row.pack(anchor="w")
        current = self.answers.get(step["key"])

        def choose(val):
            self.answers[step["key"]] = val
            self._set_step(self.current_step_index + 1)

        yes = Button(row, text="✓  Yes", variant="primary", width=160, height=56,
                     command=lambda: choose("yes"))
        yes.grid(row=0, column=0, padx=(0, SP[3]))
        no = Button(row, text="✕  No", variant="secondary", width=160, height=56,
                    command=lambda: choose("no"))
        no.grid(row=0, column=1)
        # subtle indicator if previously answered
        if current in ("yes", "no"):
            ctk.CTkLabel(b, text=f"Previously answered: {current.upper()}",
                         font=theme.font("caption"),
                         text_color=theme.c("text_faint")).pack(anchor="w",
                         pady=(SP[4], 0))

        Button(b, text="?  Why we ask this", variant="ghost", height=38,
               command=lambda: self._why(step["key"])).pack(anchor="w", pady=(SP[8], 0))
        self._current_input = None

    # ---- review -----------------------------------------------------------
    def _screen_review(self, parent, step):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for section_title, keys in REVIEW_SECTIONS.items():
            present = [k for k in keys if k in self.answers]
            if not present:
                continue
            card = Card(scroll); card.pack(fill="x", pady=SP[2])
            ctk.CTkLabel(card.body, text=section_title.upper(), font=theme.font("label"),
                         text_color=theme.c("text_muted")).pack(anchor="w",
                         pady=(0, SP[3]))
            for k in present:
                v = self.answers[k]
                disp = (f"{v:.2f}" if isinstance(v, float)
                        else str(v) if isinstance(v, int) else str(v).upper())
                rowf = ctk.CTkFrame(card.body, fg_color=theme.c("surface_alt"),
                                    corner_radius=R["sm"])
                rowf.pack(fill="x", pady=2)
                rowf.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(rowf, text=k.replace("_", " ").title(),
                             font=theme.font("body"), text_color=theme.c("text_muted")
                             ).grid(row=0, column=0, sticky="w", padx=SP[3], pady=SP[2])
                ctk.CTkLabel(rowf, text=disp, font=theme.font("body_md"),
                             text_color=theme.c("text")
                             ).grid(row=0, column=1, sticky="e", padx=SP[3], pady=SP[2])

        hint = ctk.CTkFrame(scroll, fg_color=theme.c("accent_soft"),
                            corner_radius=R["md"])
        hint.pack(fill="x", pady=SP[3])
        ctk.CTkLabel(hint, text="Review your answers, then run the 72-rule analysis.",
                     font=theme.font("body"), text_color=theme.c("accent")).pack(
                     anchor="w", padx=SP[4], pady=SP[3])

    # ---- processing -------------------------------------------------------
    def _screen_processing(self, parent, step):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.place(relx=0.5, rely=0.42, anchor="center")
        sp = Spinner(wrap, size=58, bg=theme.c("bg")); sp.pack(pady=(0, SP[5]))
        sp.start()
        ctk.CTkLabel(wrap, text="Running expert system analysis",
                     font=theme.font("h2"), text_color=theme.c("text")).pack()
        self._proc_status = ctk.CTkLabel(wrap, text="Loading knowledge base…",
                                         font=theme.font("caption"),
                                         text_color=theme.c("text_muted"))
        self._proc_status.pack(pady=(SP[2], 0))

        self._infer_done = False
        self._infer_error = None
        threading.Thread(target=self._run_inference, daemon=True).start()
        self._poll_inference(0)

    def _run_inference(self):
        try:
            facts = dict(self.answers)
            _, engine, explainer = create_expert_system()
            wm = WorkingMemory(facts)
            self.rules_fired = engine.run(wm)
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
                "wm": wm, "explainer": explainer,
            }
            self._infer_done = True
        except Exception as e:           # surfaced on the main thread by the poller
            self._infer_error = str(e)

    def _poll_inference(self, tick):
        if self._infer_error is not None:
            toast(self, f"Inference failed: {self._infer_error}", "danger", ms=4000)
            self._set_step(self.current_step_index - 1)
            return
        if self._infer_done:
            self.after(500, lambda: self._set_step(self.current_step_index + 1))
            return
        msgs = ["Loading knowledge base…", "Evaluating production rules…",
                "Scoring diabetes & hypertension…", "Determining CKD stage…",
                "Matching dietary recommendation…"]
        if hasattr(self, "_proc_status") and self._proc_status.winfo_exists():
            self._proc_status.configure(text=msgs[tick % len(msgs)])
        self.after(450, lambda: self._poll_inference(tick + 1))

    # ---- results ----------------------------------------------------------
    def _screen_results(self, parent, step):
        if not self.inference_results:
            ctk.CTkLabel(parent, text="No results available.",
                         font=theme.font("h3"),
                         text_color=theme.c("danger")).pack(pady=SP[8])
            return
        res = self.inference_results
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure((0, 1, 2), weight=1, uniform="cards")

        risk_tone = {"HIGH": "danger", "MODERATE": "warning",
                     "LOW": "success"}.get(str(res["risk"]).upper(), "info")
        stage_txt = f"Stage {res['stage']}" if res["stage"] else "No CKD"

        cards = [
            ("CKD STAGE", stage_txt, "Forward-chaining result", "accent"),
            ("CONFIDENCE", f"{(res['confidence'] or 0):.1f}%",
             f"{len(self.rules_fired)} rules fired", "warning"),
            ("RISK LEVEL", str(res["risk"]), "Clinical risk band", risk_tone),
            ("BMI", f"{(res['bmi'] or 0):.1f}", str(res["bmi_category"]), "info"),
            ("ACTIVITY", str(res["activity_level"]), "From exercise frequency", "success"),
            ("DIET TYPE", str(res["diet_type"]).replace("_", " "),
             "Selected for your profile", "accent"),
        ]
        for i, (label, value, sub, tone) in enumerate(cards):
            self._metric_card(scroll, i // 3, i % 3, label, value, sub, tone)

        # recommendation
        rec = Card(scroll, accent=theme.c("accent"))
        rec.grid(row=2, column=0, columnspan=3, sticky="ew", pady=SP[3])
        head = ctk.CTkFrame(rec.body, fg_color="transparent"); head.pack(fill="x")
        ctk.CTkLabel(head, text="PERSONALIZED RECOMMENDATION", font=theme.font("label"),
                     text_color=theme.c("text_muted")).pack(side="left")
        Button(head, text="?  How was this calculated", variant="ghost", height=36,
               command=self._how).pack(side="right")
        ctk.CTkLabel(rec.body,
                     text=f"Stage {res['stage']} · {str(res['diet_type']).replace('_',' ')}",
                     font=theme.font("h3"), text_color=theme.c("text")).pack(
                     anchor="w", pady=(SP[2], SP[2]))
        rec_box = ctk.CTkTextbox(rec.body, font=theme.font("body"), height=160,
                                 corner_radius=R["md"], fg_color=theme.c("surface_alt"),
                                 border_width=0, text_color=theme.c("text"),
                                 wrap="word")
        rec_box.pack(fill="x")
        rec_box.insert("1.0", str(res["recommendation"] or "No recommendation produced."))
        rec_box.configure(state="disabled")

        # diet mapping key
        mapping = Card(scroll); mapping.grid(row=3, column=0, columnspan=3,
                                             sticky="ew", pady=SP[3])
        ctk.CTkLabel(mapping.body, text="DIET SELECTION KEY", font=theme.font("label"),
                     text_color=theme.c("text_muted")).pack(anchor="w")
        ctk.CTkLabel(mapping.body,
                     text=f"Stage {res['stage']} + "
                          f"{str(res['diet_type']).replace('_',' ')}  →  "
                          f"'{res['medical_state']}'",
                     font=theme.font("body_md"), text_color=theme.c("accent")).pack(
                     anchor="w", pady=(SP[1], 0))

    def _metric_card(self, parent, r, c, label, value, sub, tone):
        card = Card(parent, interactive=True, accent=theme.c(tone),
                    on_click=lambda: toast(self, f"{label}: {value}", "info"))
        card.grid(row=r, column=c, sticky="nsew", padx=SP[2], pady=SP[2])
        ctk.CTkFrame(card.body, fg_color=theme.c(tone), height=3, width=36,
                     corner_radius=R["pill"]).pack(anchor="w", pady=(0, SP[3]))
        ctk.CTkLabel(card.body, text=label, font=theme.font("label"),
                     text_color=theme.c("text_muted")).pack(anchor="w")
        ctk.CTkLabel(card.body, text=value, font=theme.font("display"),
                     text_color=theme.c("text")).pack(anchor="w", pady=(SP[1], 0))
        ctk.CTkLabel(card.body, text=sub, font=theme.font("caption"),
                     text_color=theme.c("text_faint")).pack(anchor="w")

    # ======================================================================
    # NAVIGATION + VALIDATION
    # ======================================================================
    def _next_step(self):
        step = WIZARD_STEPS[self.current_step_index]

        if step["type"] == "physical_input":
            raw = self._current_input.get().strip()
            try:
                value = float(raw)
            except ValueError:
                self._show_error("Enter a valid number.")
                return
            key = step["key"]
            if key == "weight" and not (5 < value < 400):
                self._show_error("Weight must be between 5 and 400 kg.")
                return
            if key == "height" and not (0.5 < value < 3.0):
                self._show_error("Height must be between 0.5 and 3.0 m.")
                return
            self.answers[key] = value

        if step["type"] == "exercise_input" and "exercise_per_week" not in self.answers:
            toast(self, "Select how often you exercise.", "warning")
            return

        self._set_step(self.current_step_index + 1)

    def _prev_step(self):
        self._set_step(self.current_step_index - 1)

    def _restart(self):
        self.current_step_index = 0
        self.answers = {}
        self.inference_results = None
        self.rules_fired = []
        self._set_step(0, animate=False)

    def _show_error(self, msg):
        if hasattr(self, "_error_lbl") and self._error_lbl.winfo_exists():
            self._error_lbl.configure(text=msg)
        toast(self, msg, "danger")

    # ======================================================================
    # EXPLANATION FACILITY  (drawer — replaces messagebox)
    # ======================================================================
    def _why(self, key):
        text = WHY_EXPLANATIONS.get(
            key, "This information helps the expert system refine its assessment.")

        def body(f):
            ctk.CTkLabel(f, text=text, font=theme.font("body"),
                         text_color=theme.c("text_muted"), justify="left",
                         wraplength=360).pack(anchor="w", pady=(0, SP[4]))
            ctk.CTkLabel(f, text="WHY EXPLANATION", font=theme.font("label"),
                         text_color=theme.c("text_faint")).pack(anchor="w")
        self.drawer.open("Why we ask this", body)

    def _how(self):
        if not self.inference_results:
            return
        res = self.inference_results
        wm = res["wm"]
        rows = [
            ("BMI calculation", f"{(res['bmi'] or 0):.2f} from weight ÷ height² "
                                f"→ {res['bmi_category']}"),
            ("Activity level", f"{self.answers.get('exercise_per_week', 0)} days/week "
                               f"→ {res['activity_level']}"),
            ("Diabetes score", f"{wm.get('diabetes_score', 0)} "
                               f"({'threshold met' if wm.get('diabetes_status') else 'below threshold'})"),
            ("Hypertension score", f"{wm.get('bp_score', 0)} "
                                   f"({'threshold met' if wm.get('bp_status') else 'below threshold'})"),
            ("Stage determination",
             "No thresholds met" if not res["stage"]
             else f"Pattern matched criteria for Stage {res['stage']}"),
            ("Diet type", f"BMI {res['bmi_category']} + {res['activity_level']} "
                          f"→ {str(res['diet_type']).replace('_',' ')}"),
            ("Recommendation key", f"Stage {res['stage']} + "
                                   f"{str(res['diet_type']).replace('_',' ')} "
                                   f"→ '{res['medical_state']}'"),
            ("Confidence", f"{(res['confidence'] or 0):.1f}% · "
                           f"{len(self.rules_fired)} rules fired · risk {res['risk']}"),
        ]

        # full engine trace (if available)
        trace = ""
        try:
            trace = res["explainer"].how_summary(self.rules_fired, wm)
        except Exception:
            pass

        def body(f):
            for i, (k, v) in enumerate(rows, 1):
                rowf = ctk.CTkFrame(f, fg_color=theme.c("surface_alt"),
                                    corner_radius=R["sm"])
                rowf.pack(fill="x", pady=2)
                ctk.CTkLabel(rowf, text=str(i), width=26, font=theme.font("label"),
                             text_color=theme.c("accent")).pack(side="left",
                             padx=(SP[3], 0), pady=SP[3])
                col = ctk.CTkFrame(rowf, fg_color="transparent")
                col.pack(side="left", fill="x", expand=True, padx=SP[3])
                ctk.CTkLabel(col, text=k, font=theme.font("body_md"),
                             text_color=theme.c("text"), anchor="w").pack(anchor="w")
                ctk.CTkLabel(col, text=v, font=theme.font("caption"),
                             text_color=theme.c("text_muted"), anchor="w",
                             wraplength=300, justify="left").pack(anchor="w")
            if trace:
                ctk.CTkLabel(f, text="FULL INFERENCE TRACE", font=theme.font("label"),
                             text_color=theme.c("text_faint")).pack(anchor="w",
                             pady=(SP[5], SP[2]))
                box = ctk.CTkTextbox(f, font=theme.mono(10), height=220,
                                     corner_radius=R["md"], wrap="word",
                                     fg_color=theme.c("surface_alt"), border_width=0,
                                     text_color=theme.c("text_muted"))
                box.pack(fill="x")
                box.insert("1.0", trace)
                box.configure(state="disabled")
        self.drawer.open("How we reached this", body)

    # ======================================================================
    # THEME TOGGLE
    # ======================================================================
    def _toggle_theme(self):
        theme.toggle()
        self.configure(fg_color=theme.c("bg"))
        for w in (self.sidebar, self.main):
            w.destroy()
        self.drawer = Drawer(self)
        self._build_shell()
        self._set_step(self.current_step_index, animate=False)
        toast(self, f"{theme.mode.title()} mode", "info", ms=1500)


def main():
    app = DietNutriESApp()
    app.mainloop()


if __name__ == "__main__":
    main()
