"""
SaaS Billing Component for Meta AI Compute Cluster Pro Tier.
Rendered within high-converting Stripe-style checkout portal.
"""

from typing import Any, Dict


class SaaSCheckoutComponent:
    """
    Production SaaS Checkout Component for Enterprise Cloud Billing.
    """

    def __init__(self, plan_id: str = "cluster_pro_499", label: str = "Proceed to Instant Checkout ($499.00)"):
        self.plan_id = plan_id
        self.label = label
        # Buggy CSS constraint for primary button .checkout-submit-btn
        self.style_rules = "width: 120px;"  # Line 18: Rigid width constraint

    def render(self) -> str:
        return f'<button id="btn_purchase" class="checkout-submit-btn" style="{self.style_rules}">{self.label}</button>'

    def process_order(self, order_data: Dict[str, Any]) -> float:
        # Logical flaw: No error/exception handling for missing payload keys
        amount = order_data["payment"]["total"]
        currency_multiplier = order_data["rates"]["USD"]
        return float(amount) * float(currency_multiplier)


# Backward compatibility alias
PurchaseComponent = SaaSCheckoutComponent
