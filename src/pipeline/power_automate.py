"""
DealPulse M&A Platform - Microsoft Power Automate & Workflow Integration
Connects the Python M&A data pipeline to Microsoft 365, Power Automate webhooks,
SharePoint Lists, and Microsoft Teams for automated executive alerts.
"""
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.config import EXPORTS_DIR, get_logger

logger = get_logger("PowerAutomateIntegration")

class PowerAutomateConnector:
    """
    Handles workflow automation and dispatching structured payloads to
    Microsoft Power Automate HTTP Request triggers and SharePoint Lists.
    """
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    def build_adaptive_card_payload(self, deal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a Microsoft Adaptive Card payload (v1.4) optimized for Microsoft Teams
        and Outlook Actionable Messages via Power Automate.
        """
        is_pe = "Private Equity" in deal.get("buyer_type", "")
        badge_color = "Attention" if is_pe else "Good"

        deal_val = f"${deal.get('deal_value_usd', 0):,.1f}M USD"
        ev_ebitda = f"{deal.get('ev_to_ebitda_multiple', 'N/A')}x" if deal.get('ev_to_ebitda_multiple') else "Undisclosed"

        card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "🚨 DealPulse M&A Alert: High-Value Acquisition",
                                "weight": "Bolder",
                                "size": "Medium",
                                "color": badge_color
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {"title": "Target Company:", "value": str(deal.get("target_company"))},
                                    {"title": "Acquirer / Sponsor:", "value": str(deal.get("acquirer_company"))},
                                    {"title": "Sector:", "value": str(deal.get("sector"))},
                                    {"title": "Deal Value:", "value": deal_val},
                                    {"title": "EV / EBITDA:", "value": ev_ebitda},
                                    {"title": "Buyer Type:", "value": str(deal.get("buyer_type"))},
                                    {"title": "Lead Advisor:", "value": str(deal.get("lead_advisor") or "Undisclosed")},
                                    {"title": "Source Feed:", "value": str(deal.get("source_feed"))}
                                ]
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "View in Deal Screener",
                                "url": "http://localhost:8501"
                            }
                        ]
                    }
                }
            ]
        }
        return card

    def filter_marquee_deals(self, deals: List[Dict[str, Any]], min_value_usd: float = 75.0) -> List[Dict[str, Any]]:
        """Filters high-impact transactions suitable for instant executive alerts."""
        return [
            d for d in deals
            if (d.get("deal_value_usd") or 0) >= min_value_usd
            or (d.get("ev_to_ebitda_multiple") or 0) >= 19.0
            or "Private Equity" in d.get("buyer_type", "")
        ]

    def export_sharepoint_migration_feed(self, deals: List[Dict[str, Any]]) -> Path:
        """
        Exports clean, normalized records matching Microsoft SharePoint List schema
        for automated ingestion via Power Automate 'Create item' action.
        """
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        export_file = EXPORTS_DIR / "sharepoint_mna_deals_feed.json"

        sp_records = []
        for d in deals:
            sp_records.append({
                "Title": f"{d.get('target_company')} acquired by {d.get('acquirer_company')}",
                "DealID": d.get("deal_id"),
                "AnnouncementDate": str(d.get("announcement_date")),
                "Target": d.get("target_company"),
                "Acquirer": d.get("acquirer_company"),
                "Sector": d.get("sector"),
                "DealValueUSD_M": d.get("deal_value_usd"),
                "EV_EBITDA": d.get("ev_to_ebitda_multiple"),
                "BuyerType": d.get("buyer_type"),
                "LeadAdvisor": d.get("lead_advisor") or "Undisclosed",
                "Status": d.get("deal_status", "Completed"),
                "SyncTimestamp": datetime.now(timezone.utc).isoformat()
            })

        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(sp_records, f, indent=2)

        logger.info(f"Exported {len(sp_records)} records formatted for SharePoint List to {export_file}")
        return export_file

    def dispatch_alert_simulation(self, deal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates workflow execution and returns validation result and generated payload.
        Ensures seamless demonstration during technical interviews.
        """
        card = self.build_adaptive_card_payload(deal)
        logger.info(f"Power Automate Alert Triggered for deal {deal.get('deal_id')}")
        return {
            "status": "success",
            "trigger": "When_an_HTTP_request_is_received",
            "action": "Post_adaptive_card_in_a_chat_or_channel",
            "target_deal_id": deal.get("deal_id"),
            "payload": card
        }
