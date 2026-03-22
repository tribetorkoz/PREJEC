from typing import Dict, Any, Optional


class ROICalculator:
    """
    Show every prospect exactly how much money
    they'll save and make with VoiceCore.
    Data-driven sales — closes deals faster.
    """
    
    def calculate(
        self,
        monthly_calls: int,
        current_receptionist_salary: float,
        missed_call_rate: float,
        avg_customer_value: float,
        plan_price: float
    ) -> Dict[str, Any]:
        receptionist_cost = current_receptionist_salary
        voicecore_cost = plan_price
        monthly_savings = receptionist_cost - voicecore_cost
        
        missed_calls_per_month = monthly_calls * (missed_call_rate / 100)
        calls_now_answered = missed_calls_per_month * 0.95
        
        new_customers_per_month = calls_now_answered * 0.30
        monthly_revenue_recovered = new_customers_per_month * avg_customer_value
        
        total_monthly_benefit = monthly_savings + monthly_revenue_recovered
        
        if plan_price > 0:
            monthly_roi_percent = ((total_monthly_benefit - plan_price) / plan_price) * 100
            payback_days = plan_price / (total_monthly_benefit / 30) if total_monthly_benefit > 0 else 999
        else:
            monthly_roi_percent = 0
            payback_days = 0
        
        return {
            "monthly_cost_savings": round(monthly_savings, 2),
            "monthly_revenue_recovered": round(monthly_revenue_recovered, 2),
            "total_monthly_benefit": round(total_monthly_benefit, 2),
            "annual_benefit": round(total_monthly_benefit * 12, 2),
            "roi_percent": round(monthly_roi_percent, 1),
            "payback_period_days": round(payback_days, 0),
            "summary": f"${round(total_monthly_benefit):,} benefit per month for ${plan_price} investment",
            "details": {
                "missed_calls_per_month": round(missed_calls_per_month, 1),
                "calls_answered_by_ai": round(calls_now_answered, 1),
                "new_customers_from_missed_calls": round(new_customers_per_month, 1),
                "avg_customer_value": avg_customer_value
            }
        }
    
    def calculate_by_vertical(
        self,
        vertical: str,
        monthly_calls: int,
        plan_price: float
    ) -> Dict[str, Any]:
        vertical_defaults = {
            "dental": {
                "avg_customer_value": 1500,
                "missed_call_rate": 35
            },
            "legal": {
                "avg_customer_value": 5000,
                "missed_call_rate": 42
            },
            "realty": {
                "avg_customer_value": 25000,
                "missed_call_rate": 67
            },
            "general": {
                "avg_customer_value": 1500,
                "missed_call_rate": 30
            }
        }
        
        defaults = vertical_defaults.get(vertical, vertical_defaults["general"])
        
        return self.calculate(
            monthly_calls=monthly_calls,
            current_receptionist_salary=3000,
            missed_call_rate=defaults["missed_call_rate"],
            avg_customer_value=defaults["avg_customer_value"],
            plan_price=plan_price
        )


class SalesROITools:
    """
    Tools for sales team to generate ROI reports.
    """
    
    def __init__(self, calculator: ROICalculator):
        self.calculator = calculator
    
    def generate_proposal_roi(
        self,
        prospect_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        roi = self.calculator.calculate_by_vertical(
            vertical=prospect_data.get("vertical", "general"),
            monthly_calls=prospect_data.get("monthly_calls", 500),
            plan_price=prospect_data.get("plan_price", 299)
        )
        
        return {
            "prospect_name": prospect_data.get("company_name"),
            "vertical": prospect_data.get("vertical"),
            "roi_analysis": roi,
            "recommendation": self._get_recommendation(roi)
        }
    
    def _get_recommendation(self, roi: Dict[str, Any]) -> str:
        if roi["roi_percent"] > 500:
            return "Strong value proposition - prioritize this deal"
        elif roi["roi_percent"] > 200:
            return "Good value - standard follow-up"
        elif roi["roi_percent"] > 0:
            return "Positive ROI - may need more education"
        else:
            return "Consider showing other value metrics"
