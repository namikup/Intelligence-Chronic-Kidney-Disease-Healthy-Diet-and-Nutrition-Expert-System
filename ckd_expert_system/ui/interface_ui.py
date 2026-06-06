"""
console_ui.py — Command-line interface for the CKD Expert System.
"""


class InterfaceUI:#interface UI
    """Command-line interface for the CKD Expert System.
    Placeholder — implement run() to loop through QUESTION_ORDER,
    collect answers into a dict, pass to WorkingMemory, run the engine,
    and display results + HOW trace.
    """

    def __init__(self):
        from engine import create_expert_system
        self.kb, self.engine, self.explainer = create_expert_system()

    def collect_facts(self) -> dict:
        """TODO: loop through QUESTION_ORDER, validate and collect answers."""
        raise NotImplementedError

    def display_results(self, wm, fired_rules: list) -> None:
        """TODO: print Stage, Confidence, Risk, Recommendation, HOW trace."""
        raise NotImplementedError

    def run(self) -> None:
        """TODO: orchestrate collect_facts → engine.run → display_results."""
        raise NotImplementedError
