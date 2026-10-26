"""
Broken UI component simulation for QA-Swarm Phase 3 testing.
Contains a rigid width constraint causing visual layout overflow,
and an unhandled exception in payment processing logic.
"""

from typing import Any, Dict


class PurchaseComponent:
    """
    Component rendering shopping cart purchase action.
    """

    def __init__(self, item_id: str, label: str = "Checkout Now"):
        self.item_id = item_id
        self.label = label
        self.style_rules = "width: 120px;"  # Line 18: Rigid width constraint

    def render(self) -> str:
        return f'<button id="btn_purchase" style="{self.style_rules}">{self.label}</button>'

    def process_order(self, order_data: Dict[str, Any]) -> float:
        # Logical flaw: No error/exception handling for missing payload keys
        amount = order_data["payment"]["total"]
        currency_multiplier = order_data["rates"]["USD"]
        return float(amount) * float(currency_multiplier)
