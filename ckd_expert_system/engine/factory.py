"""
factory.py — Factory function to instantiate the expert system.
"""

from typing import Tuple
from .knowledge_base import KnowledgeBase
from .inference import InferenceEngine
from .explanation import ExplanationEngine


def create_expert_system() -> Tuple[KnowledgeBase, InferenceEngine, ExplanationEngine]:
    """Instantiate and wire together all three components.

    Usage
    -----
    kb, engine, explainer = create_expert_system()
    wm = WorkingMemory(initial_facts={...})
    fired = engine.run(wm)
    print(explainer.how_summary(fired, wm))
    result = wm.get("Personalized_CKD_Recommendation")
    """
    kb       = KnowledgeBase()
    engine   = InferenceEngine(kb)
    explainer= ExplanationEngine(kb)
    return kb, engine, explainer
