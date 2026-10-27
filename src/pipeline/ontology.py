"""
DealPulse M&A Platform - Ontology & Standardization Module
Standardizes company entities, eliminates corporate suffixes, maps industry taxonomy,
and enforces standard investment banking ontologies.
"""
import re
from typing import Tuple
from src.config import STANDARD_SECTORS, DEAL_TYPES, BUYER_TYPES

# Suffixes to clean for entity resolution
LEGAL_SUFFIXES = [
    r"\binc(?:\.|\b)", r"\bcorp(?:\.|\b)", r"\bcorporation\b", r"\bllc\b", 
    r"\bltd(?:\.|\b)", r"\bplc\b", r"\bgmbh\b", r"\bsa\b", r"\bsas\b",
    r"\bholdings\b", r"\bgroup\b", r"\bpartners\b", r"\btechnologies\b"
]

SECTOR_KEYWORD_MAP = {
    "Cybersecurity": ["cyber", "security", "defense", "firewall", "endpoint", "soc", "siem"],
    "Enterprise Software & SaaS": ["saas", "software", "cloud", "erp", "crm", "workflow", "ai", "platform"],
    "FinTech & Payments": ["fintech", "payment", "banking", "lending", "payroll", "crypto", "trading"],
    "Digital Healthcare & MedTech": ["health", "medtech", "biotech", "clinical", "pharma", "patient", "medical"],
    "CleanTech & Energy Transition": ["energy", "solar", "wind", "cleantech", "carbon", "battery", "grid"],
    "Industrial IoT & Automation": ["industrial", "iot", "robotics", "automation", "manufacturing", "logistics"],
    "E-Commerce & Digital Consumer": ["ecommerce", "retail", "consumer", "marketplace", "d2c"],
}

def clean_company_name(raw_name: str) -> str:
    """Removes legal suffixes and trims whitespace for entity deduplication."""
    cleaned = raw_name.strip()
    for suffix_pattern in LEGAL_SUFFIXES:
        cleaned = re.sub(suffix_pattern, "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"[\s,.-]+$", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()

def generate_entity_id(name: str, country: str = "US") -> str:
    """Generates deterministic unique entity ID for dimensional modeling."""
    clean = clean_company_name(name)
    slug = re.sub(r"[^A-Za-z0-9]+", "-", clean).strip("-").upper()
    country_code = country[:3].upper() if country else "GLB"
    return f"COMP-{country_code}-{slug}"

def map_to_standard_sector(raw_text: str) -> str:
    """Maps free text, industry tags, or descriptions into standard IB sectors."""
    text_lower = raw_text.lower()
    for sector, keywords in SECTOR_KEYWORD_MAP.items():
        if any(kw in text_lower for kw in keywords):
            return sector
    return "Enterprise Software & SaaS"  # Default canonical mid-market sector
