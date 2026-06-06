"""
questions.py — Question map and user input configuration for the CKD Expert System UI.
"""

QUESTION_MAP: dict[str, str] = {
    # Section 1 — Diabetes symptoms
    "tiredness":           "Do you often feel tired or fatigued without a clear reason? (yes/no)",
    "frequent_urination":  "Do you urinate more frequently than usual, including at night? (yes/no)",
    "excessive_thirst":    "Do you feel excessively thirsty even after drinking water? (yes/no)",
    "constant_hunger":     "Do you feel constantly hungry even shortly after eating? (yes/no)",

    # Section 2 — Blood pressure symptoms
    "headaches":           "Do you experience frequent headaches, especially at the back of your head? (yes/no)",
    "dizziness":           "Do you feel dizzy or lightheaded regularly? (yes/no)",
    "blurred_vision_bp":   "Do you experience blurred vision at times? (yes/no)",
    "chest_discomfort":    "Do you feel chest discomfort or tightness? (yes/no)",

    # Section 3 — CKD Stage 2 symptoms
    "mild_swelling":       "Do you notice mild swelling in your ankles or feet? (yes/no)",
    "mild_fatigue":        "Do you feel mild but persistent fatigue throughout the day? (yes/no)",

    # Section 4 — CKD Stage 3 symptoms
    "persistent_fatigue":       "Is your fatigue persistent and worsening over time? (yes/no)",
    "swelling_extremities":     "Do you have noticeable swelling in your hands, legs, or feet? (yes/no)",
    "lower_back_pain":          "Do you experience lower back or flank pain regularly? (yes/no)",
    "itchy_skin":               "Do you have persistent itchy skin without a rash? (yes/no)",

    # Section 5 — CKD Stage 4 symptoms
    "nausea":                   "Do you frequently feel nauseous or want to vomit? (yes/no)",
    "loss_of_appetite":         "Have you noticed a significant loss of appetite recently? (yes/no)",
    "difficulty_concentrating": "Do you have difficulty concentrating or feel mentally foggy? (yes/no)",
    "muscle_cramps":            "Do you experience muscle cramps, especially in your legs? (yes/no)",
    "trouble_sleeping":         "Do you have trouble falling or staying asleep? (yes/no)",

    # Section 6 — Physical measurements
    "weight":              "Please enter your weight in kilograms (e.g. 70.5):",
    "height":              "Please enter your height in metres (e.g. 1.72):",
    "exercise_per_week":   "How many days per week do you exercise? (enter a number 0–7):",
}

# Ordered list of keys for sequential UI questioning
QUESTION_ORDER: list[str] = list(QUESTION_MAP.keys())

# Keys that expect float input
FLOAT_KEYS: set[str] = {"weight", "height"}

# Keys that expect integer input
INT_KEYS: set[str] = {"exercise_per_week"}

# Keys that expect yes/no input
YESNO_KEYS: set[str] = set(QUESTION_MAP.keys()) - FLOAT_KEYS - INT_KEYS
