# CKD Clinical Nutrition Expert System — Modern Wizard UI

A professional, intelligent medical assessment wizard for Chronic Kidney Disease (CKD) diagnosis and dietary recommendations. Powered by a 72-rule forward-chaining inference engine, this system provides a guided clinical interview experience with built-in transparency through WHY and HOW explanation facilities.

## 🚀 Key Features

- **Modern Wizard UI**: A clean, step-by-step clinical interview using `CustomTkinter`.
- **72-Rule Inference Engine**: Evaluates symptoms across 15 clinical domains to determine CKD stages (1-4).
- **Intelligent Assessment**: 
    - Automated BMI and Activity Level classification.
    - Risk Level determination (Low, Moderate, High).
    - Confidence score calculation based on symptom matching density.
- **Explanation Facility**:
    - **WHY**: Clinical justification for every question asked during the interview.
    - **HOW**: Transparent reasoning trace explaining how the final diagnosis and diet were derived.
- **Professional Dashboard**: Detailed results including clinical findings, mapping logic, and personalized nutrition plans.

## 📁 Folder Structure

```
.
├── ckd_expert_system/
│   ├── engine/                # Core Expert System Logic
│   │   ├── knowledge_base.py  # 72 Clinical Production Rules
│   │   ├── inference.py       # Forward-Chaining Engine
│   │   ├── explanation.py     # Reasoning Trace Generator
│   │   └── factory.py         # Engine Initialization
│   │
│   └── ui/                    # Modern UI Layer
│       ├── interface_ui.py    # Main CustomTkinter Wizard Engine
│       └── questions.py       # Assessment Flow & Question Metadata
│
├── main.py                    # Application Entry Point
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🛠 Installation

1. Clone the repository and navigate to the project directory.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install customtkinter
   ```

## 🏃 Running the Application

To launch the modern clinical assessment wizard:

```bash
python main.py
```

## 🔬 Clinical Logic & Stages

The system classifies CKD progression based on the following criteria:

- **Stage 1**: Requires dual markers (Positive Diabetes AND Hypertension symptoms).
- **Stage 2**: Detection of mild kidney-related fluid retention or fatigue.
- **Stage 3**: Matches patterns for moderate edema, persistent fatigue, and flank pain.
- **Stage 4**: Advanced uremic symptoms (Nausea, appetite loss, cognitive fog).
- **Dietary Selection**: Automatically chooses between **Calorie Deficit** or **Calorie Maintenance** based on BMI and activity level.

## 🧪 Testing

The system includes a suite of tests for the inference engine and knowledge base rules.

```bash
# Run all tests
pytest ckd_expert_system/tests/ -v
```

## 📜 Architecture Overview

- **Forward-Chaining**: The engine starts with user facts and applies rules iteratively to derive higher-level conclusions (Symptom Scores -> Stage -> Medical State -> Diet).
- **Modular UI**: The wizard flow is data-driven by `questions.py`, allowing for easy modification of clinical wording or assessment steps.
- **Knowledge Representation**: Rules are defined as IF-THEN production rules, making the clinical logic easy to audit and extend.

## ⚖️ Disclaimer

This system is provided for **educational and research purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider for any questions regarding a medical condition.

---

