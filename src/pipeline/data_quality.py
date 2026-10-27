"""
DealPulse M&A Platform - Data Quality & Validation Engine
Enforces strict schema validation, range checks, and audit assertions.
"""
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, field_validator
from src.config import get_logger

logger = get_logger("DataQuality")

class RawDealModel(BaseModel):
    deal_id: str = Field(..., min_length=3)
    announcement_date: str
    target_company: str = Field(..., min_length=2)
    target_country: str = Field(default="United States")
    target_city: Optional[str] = None
    acquirer_company: str = Field(..., min_length=2)
    acquirer_country: str = Field(default="United States")
    sector: str
    deal_type: str
    buyer_type: str
    deal_status: str
    deal_currency: str = Field(default="USD")
    deal_value_native: float = Field(..., gt=0.0)
    target_revenue_usd: Optional[float] = None
    target_ebitda_usd: Optional[float] = None
    lead_advisor: Optional[str] = None
    source_feed: str
    source_url: Optional[str] = None

    @field_validator("deal_currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        valid_currencies = {"USD", "EUR", "GBP", "CAD", "CHF", "AUD"}
        if v.upper() not in valid_currencies:
            raise ValueError(f"Unsupported transaction currency: {v}")
        return v.upper()

def validate_deal_records(raw_records: list) -> tuple[list, list]:
    """
    Validates a batch of raw records.
    Returns: (valid_records, failed_records)
    """
    valid = []
    failed = []
    for item in raw_records:
        try:
            validated = RawDealModel(**item)
            valid.append(validated.model_dump())
        except Exception as exc:
            logger.warning(f"Data quality error on deal record {item.get('deal_id')}: {exc}")
            failed.append({"record": item, "error": str(exc)})
            
    logger.info(f"Quality Check: {len(valid)} passed, {len(failed)} rejected.")
    return valid, failed
