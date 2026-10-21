# -*- coding: utf-8 -*-
"""MCP Server for B2B Vendor Scorecard & On-Time In-Full (OTIF) SLA Adjudicator Skill."""
import sys
import json
import logging
from typing import Dict, Any

from .core import B2BVendorScorecardOTIFAdjudicator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLS_SCHEMA = [
    {
        "name": "compute_vendor_otif_compliance_score",
        "description": "Calculate On-Time In-Full (OTIF) percentage and supplier defect Parts-Per-Million (PPM).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "units_ordered": {
                    "type": "integer"
                },
                "units_delivered": {
                    "type": "integer"
                },
                "promised_delivery_epoch": {
                    "type": "integer"
                },
                "actual_delivery_epoch": {
                    "type": "integer"
                },
                "defect_count": {
                    "type": "integer"
                }
            },
            "required": [
                "units_ordered",
                "units_delivered",
                "promised_delivery_epoch",
                "actual_delivery_epoch"
            ]
        }
    },
    {
        "name": "adjudicate_contractual_sla_financial_penalty",
        "description": "Adjudicate SLA liquid damages penalty for PO breach under standard master purchasing agreement.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract_value_usd": {
                    "type": "number"
                },
                "otif_score_pct": {
                    "type": "number"
                },
                "defect_ppm": {
                    "type": "number"
                }
            },
            "required": [
                "contract_value_usd",
                "otif_score_pct"
            ]
        }
    }
]

def handle_rpc(line: str) -> str:
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-commerce-b2b-vendor-scorecard-sla-adjudicator-skill", "version": "1.0.0"}
            }
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": res})

        elif method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            target_func = getattr(B2BVendorScorecardOTIFAdjudicator, tool_name, None)
            if not target_func:
                return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {tool_name}"}})

            result = target_func(**args)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            })

        else:
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": req.get("id") if "req" in locals() else None, "error": {"code": -32000, "message": str(e)}})

def run_test():
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(handle_rpc(init_req))
    assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "genpark-agentic-commerce-b2b-vendor-scorecard-sla-adjudicator-skill"

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_res = json.loads(handle_rpc(list_req))
    assert len(list_res.get("result", {}).get("tools", [])) == 2
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        if run_test():
            sys.exit(0)
        sys.exit(1)

    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
