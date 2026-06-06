# CKD Expert System

A comprehensive forward-chaining expert system for Chronic Kidney Disease (CKD) diagnosis and dietary recommendation. The system uses 72 production rules across 15 clinical domains to evaluate CKD risk factors, determine disease stage, calculate confidence metrics, and provide personalised dietary guidance based on the patient's medical state.

## Folder Structure

```
ckd_expert_system/
│
├── engine/
│   ├── __init__.py            # Package exports
│   ├── models.py              # Rule dataclass + WorkingMemory class
│   ├── knowledge_base.py      # KnowledgeBase class (all 72 rules)
│   ├── inference.py           # InferenceEngine class (forward chaining)
│   ├── explanation.py         # ExplanationEngine class (WHY/HOW traces)
│   └── factory.py             # create_expert_system() factory function
│
├── ui/
│   ├── __init__.py
│   ├── questions.py           # QUESTION_MAP and user input configuration
│   └── interface_ui.py          # Placeholder  interface
│
├── main.py                    # Entry point
├── requirements.txt           # Dependencies (pytest)
└── README.md                  # This file
```

## Installation

1. Navigate to the project directory:

   ```bash
   cd ckd_expert_system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the CKD Expert System CLI interface:

```bash
python main.py
```

Note: The console UI is currently a placeholder. Implement `ConsoleUI.run()` to enable interactive questioning.

## Running Tests

Run all tests with verbose output:

```bash
pytest tests/ -v
```

Run only engine tests:

```bash
pytest tests/test_engine.py -v
```

Run only rule existence tests:

```bash
pytest tests/test_rules.py -v
```

## Integration Contract

Below is a minimal usage example showing how to integrate the expert system into your application:

```python
from engine import create_expert_system, WorkingMemory

# Instantiate the three components
kb, engine, explainer = create_expert_system()

# Create a working memory with patient facts
wm = WorkingMemory({
    "tiredness": "yes",
    "frequent_urination": "yes",
    "excessive_thirst": "yes",
    "constant_hunger": "yes",
    "headaches": "yes",
    "dizziness": "yes",
    "blurred_vision_bp": "yes",
    "chest_discomfort": "yes",
    "weight": 75.0,
    "height": 1.68,
    "exercise_per_week": 3,
})

# Run the inference engine
fired = engine.run(wm)

# Extract results from working memory
print("Stage:", wm.get("Stage_Determination"))            # e.g. 1
print("Confidence:", wm.get("confidence"))                # e.g. 100.0
print("Risk:", wm.get("risk"))                            # HIGH / MODERATE / LOW
print("Recommendation:", wm.get("Personalized_CKD_Recommendation"))

# Generate a human-readable HOW trace
print(explainer.how_summary(fired, wm))
```

## Rule Sections

The 72 rules are organised into 15 clinical sections:

| Section                  | Rule IDs | Purpose                                                                                                            |
| ------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------ |
| Diabetes Detection       | R1–R6    | Evaluate diabetes symptoms (tiredness, urination, thirst, hunger) and determine diabetes status                    |
| Blood Pressure Detection | R7–R12   | Evaluate hypertension symptoms (headaches, dizziness, blurred vision, chest discomfort) and determine BP status    |
| CKD Stage 1              | R13–R14  | Detect dual risk factors (diabetes + hypertension) and classify as Stage 1                                         |
| CKD Stage 2              | R15–R17  | Detect mild symptoms (swelling, fatigue) and classify as Stage 2                                                   |
| CKD Stage 3              | R18–R22  | Detect moderate symptoms (persistent fatigue, swelling, pain, itching) and classify as Stage 3                     |
| CKD Stage 4              | R23–R28  | Detect severe symptoms (nausea, appetite loss, cognitive impairment, cramps, sleep issues) and classify as Stage 4 |
| Stage Priority           | R29–R30  | Determine final CKD stage and handle no-CKD cases                                                                  |
| Confidence Calculation   | R31–R34  | Calculate confidence percentages (symptom ratio) for each stage                                                    |
| Risk Level               | R35–R37  | Classify risk as HIGH (≥75%), MODERATE (50–74%), or LOW (<50%)                                                     |
| Interpretation           | R38–R41  | Generate clinical interpretation text and finalise it                                                              |
| BMI Calculation          | R42–R46  | Calculate BMI from weight/height and classify (Underweight/Normal/Overweight)                                      |
| Activity Level           | R47–R50  | Classify activity level (Low/Moderate/High) based on weekly exercise days                                          |
| Diet Type                | R51–R53  | Determine diet type (Calorie_Deficit or Calorie_Maintenance) based on BMI + activity                               |
| Medical State            | R54–R62  | Combine stage and diet type to determine specific medical state (9 states total)                                   |
| Diet Recommendations     | R63–R72  | Provide stage-specific, diet-appropriate nutritional guidance                                                      |

## Architecture Overview

- **KnowledgeBase**: Contains all 72 production rules with condition (IF) and conclusion (THEN) logic.
- **WorkingMemory**: Dict-backed fact store that tracks all derived facts and their history.
- **InferenceEngine**: Forward-chaining agenda-driven engine that fires rules when their conditions are met.
- **ExplanationEngine**: Provides transparency via WHY (rule justification) and HOW (reasoning traces).

The engine uses pure logic with no third-party dependencies (except pytest for testing).

## Next Steps

1. **Implement ConsoleUI**: Fill in `console_ui.py` to create an interactive CLI that loops through questions, collects user input, runs the engine, and displays results.
2. **Extend UI**: Build a web UI, mobile app, or GUI frontend using the integration contract above.
3. **Integrate with Clinical Data**: Connect to EHR systems or medical databases to fetch patient facts automatically.
4. **Add Explanation Features**: Use `explainer.why_active()` to show users why questions are being asked.

## License

This CKD Expert System is provided as-is for educational and research purposes.
