from typing import Dict, Any

SECTOR_KEYWORDS = {
    "Information Technology": [
        "tech", "software", "cloud", "ai", "cyber", "data", "saas", "it", "systems", 
        "network", "digital", "developer", "solutions", "analytics", "platform", "app"
    ],
    "Healthcare": [
        "health", "pharma", "medical", "clinic", "hospital", "bio", "therapeutics",
        "care", "medicine", "dental", "doctor", "genomics", "patient"
    ],
    "Education": [
        "edu", "academy", "school", "university", "college", "institute", "learn", 
        "training", "tutor", "curriculum", "courses"
    ],
    "Finance": [
        "bank", "invest", "capital", "wealth", "fund", "crypto", "insurance", "credit", 
        "fintech", "financial", "equity", "accounting", "venture"
    ],
    "Manufacturing": [
        "manufactur", "factory", "industrial", "machinery", "steel", "plastics", 
        "production", "fabrication", "assembly", "automotive", "textile"
    ],
    "Retail": [
        "retail", "shop", "store", "ecommerce", "apparel", "fashion", "goods", "market", 
        "boutique", "merchandise", "groceries"
    ],
    "Real Estate": [
        "realty", "real estate", "property", "properties", "estate", "housing", 
        "apartments", "mortgage", "brokerage", "tenant"
    ]
}

class BaseSectorClassifier:
    """Abstract interface for sector classification (future RAG lead segregation agent connector)."""
    def classify(self, company_name: str, website: str = "", job_title: str = "") -> Dict[str, Any]:
        raise NotImplementedError

class RuleBasedSectorClassifier(BaseSectorClassifier):
    def classify(self, company_name: str, website: str = "", job_title: str = "") -> Dict[str, Any]:
        text_corpus = f"{company_name} {website} {job_title}".lower()
        
        matches = {}
        for sector, keywords in SECTOR_KEYWORDS.items():
            matched_words = [kw for kw in keywords if kw in text_corpus]
            if matched_words:
                matches[sector] = matched_words

        if not matches:
            return {
                "sector": "Other",
                "confidence": 0.30,
                "reason": "No sector-specific indicators detected in company metadata; flagged as Needs Review.",
                "needs_review": True
            }

        # Select sector with highest keyword hits
        best_sector = max(matches.keys(), key=lambda s: len(matches[s]))
        matched_kws = matches[best_sector]
        hit_count = len(matched_kws)
        
        # Calculate confidence
        confidence = min(0.95, 0.50 + (hit_count * 0.15))
        needs_review = confidence < 0.65

        return {
            "sector": best_sector,
            "confidence": round(confidence, 2),
            "reason": f"Matched domain keywords: {', '.join(matched_kws[:3])}",
            "needs_review": needs_review
        }

classifier_service = RuleBasedSectorClassifier()
