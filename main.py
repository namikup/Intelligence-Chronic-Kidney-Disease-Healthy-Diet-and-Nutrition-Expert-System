"""
main.py — Entry point for the CKD Clinical Nutrition Expert System.
"""

from ckd_expert_system.ui.interface_ui import DietNutriESApp

if __name__ == "__main__":
    app = DietNutriESApp()
    app.mainloop()
