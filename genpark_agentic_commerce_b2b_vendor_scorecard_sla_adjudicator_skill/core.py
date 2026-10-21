# -*- coding: utf-8 -*-
"""B2B Vendor Scorecard OTIF Adjudicator for GenPark Agentic Commerce."""
import json
from typing import Dict, Any

class B2BVendorScorecardOTIFAdjudicator:
    @staticmethod
    def compute_vendor_otif_compliance_score(units_ordered: int, units_delivered: int, promised_delivery_epoch: int, actual_delivery_epoch: int, defect_count: int = 0) -> Dict[str, Any]:
        on_time = 1.0 if actual_delivery_epoch <= promised_delivery_epoch else 0.0
        in_full_ratio = min(1.0, max(0.0, units_delivered / max(1, units_ordered)))
        
        otif_score_pct = round(on_time * in_full_ratio * 100.0, 1)
        defect_ppm = round((defect_count / max(1, units_delivered)) * 1_000_000, 1) if units_delivered > 0 else 0.0
        
        tier = "PREFERRED_VENDOR" if otif_score_pct >= 95.0 and defect_ppm < 500 else ("ACCEPTABLE_PROBATION" if otif_score_pct >= 85.0 else "BREACH_CRITICAL")
        return {
            "on_time": on_time == 1.0,
            "in_full_pct": round(in_full_ratio * 100.0, 1),
            "otif_score_pct": otif_score_pct,
            "defect_ppm": defect_ppm,
            "vendor_standing": tier
        }

    @staticmethod
    def adjudicate_contractual_sla_financial_penalty(contract_value_usd: float, otif_score_pct: float, defect_ppm: float = 0.0) -> Dict[str, Any]:
        penalty_pct = 0.0
        if otif_score_pct < 85.0:
            penalty_pct += (85.0 - otif_score_pct) * 0.2  # 0.2% per percentage point below 85%
        if defect_ppm > 1000.0:
            penalty_pct += min(5.0, (defect_ppm - 1000.0) / 1000.0 * 1.0)
            
        penalty_pct = min(15.0, round(penalty_pct, 2))
        penalty_usd = round(contract_value_usd * (penalty_pct / 100.0), 2)
        
        return {
            "contract_value_usd": contract_value_usd,
            "otif_compliance_pct": otif_score_pct,
            "contractual_penalty_pct": penalty_pct,
            "liquidated_damages_deduction_usd": penalty_usd,
            "payment_remittance_advice": f"Deduct {penalty_usd} USD from next AP disbursement invoice."
        }
