"""
questions.py — Question definitions and metadata for the modern CKD Wizard UI.
"""

# ==========================================
# WIZARD STEP DEFINITIONS
# ==========================================
# This structure defines the flow, types, and clinical mapping for the UI.
WIZARD_STEPS = [
    {"id": "welcome", "title": "Welcome", "type": "welcome"},

    # Physical Section
    {"id": "weight", "title": "Physical Information", "type": "physical_input",
     "question": "What is your weight (kg)?", "key": "weight", "placeholder": "e.g., 75.5"},
    {"id": "height", "title": "Physical Information", "type": "physical_input",
     "question": "What is your height (m)?", "key": "height", "placeholder": "e.g., 1.70"},
    {"id": "exercise", "title": "Physical Information", "type": "exercise_input",
     "question": "How many days per week do you exercise?", "key": "exercise_per_week"},

    # Category Intros & Symptoms
    {"id": "diabetes_intro", "title": "Diabetes Screening", "type": "category_intro", "category": "Diabetes"},
    {"id": "tiredness", "title": "Diabetes Screening", "type": "symptom_input",
     "question": "Do you experience persistent tiredness or fatigue?", "key": "tiredness"},
    {"id": "excessive_thirst", "title": "Diabetes Screening", "type": "symptom_input",
     "question": "Do you experience excessive thirst?", "key": "excessive_thirst"},
    {"id": "constant_hunger", "title": "Diabetes Screening", "type": "symptom_input",
     "question": "Do you experience constant hunger?", "key": "constant_hunger"},
    {"id": "frequent_urination", "title": "Diabetes Screening", "type": "symptom_input",
     "question": "Do you experience frequent urination, especially at night?", "key": "frequent_urination"},

    {"id": "hypertension_intro", "title": "Hypertension Screening", "type": "category_intro", "category": "Hypertension"},
    {"id": "headaches", "title": "Hypertension Screening", "type": "symptom_input",
     "question": "Do you experience frequent headaches (especially at the back of your head)?", "key": "headaches"},
    {"id": "dizziness", "title": "Hypertension Screening", "type": "symptom_input",
     "question": "Do you experience dizziness or lightheadedness?", "key": "dizziness"},
    {"id": "blurred_vision_bp", "title": "Hypertension Screening", "type": "symptom_input",
     "question": "Do you experience blurred vision?", "key": "blurred_vision_bp"},
    {"id": "chest_discomfort", "title": "Hypertension Screening", "type": "symptom_input",
     "question": "Do you experience chest discomfort or tightness?", "key": "chest_discomfort"},

    {"id": "ckd_intro", "title": "CKD Assessment", "type": "category_intro", "category": "Chronic Kidney Disease Symptoms"},
    {"id": "mild_swelling", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience mild swelling in your ankles or feet?", "key": "mild_swelling"},
    {"id": "mild_fatigue", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience mild, persistent fatigue?", "key": "mild_fatigue"},
    {"id": "persistent_fatigue", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience persistent or worsening fatigue?", "key": "persistent_fatigue"},
    {"id": "swelling_extremities", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience swelling in your hands, legs, or feet?", "key": "swelling_extremities"},
    {"id": "lower_back_pain", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience lower back or flank pain?", "key": "lower_back_pain"},
    {"id": "itchy_skin", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience itchy skin without a rash?", "key": "itchy_skin"},
    {"id": "nausea", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience frequent nausea or urge to vomit?", "key": "nausea"},
    {"id": "loss_of_appetite", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience significant loss of appetite?", "key": "loss_of_appetite"},
    {"id": "difficulty_concentrating", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience difficulty concentrating or brain fog?", "key": "difficulty_concentrating"},
    {"id": "muscle_cramps", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience muscle cramps, especially in your legs?", "key": "muscle_cramps"},
    {"id": "trouble_sleeping", "title": "CKD Assessment", "type": "symptom_input",
     "question": "Do you experience trouble falling or staying asleep?", "key": "trouble_sleeping"},

    {"id": "review", "title": "Review Answers", "type": "review"},
    {"id": "processing", "title": "Processing", "type": "processing"},
    {"id": "results", "title": "Results", "type": "results"},
]

# ==========================================
# WHY EXPLANATIONS
# ==========================================
WHY_EXPLANATIONS = {
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
