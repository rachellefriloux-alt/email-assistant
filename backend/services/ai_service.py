import logging
from functools import lru_cache
from typing import Optional
from transformers import pipeline

log = logging.getLogger(__name__)

# Initialize pipelines lazily to save startup time/memory if not used
_classifier = None
_sentiment_analyzer = None

FALLBACK_KEYWORDS = {
    "Billing": ["invoice", "payment", "receipt", "bill", "subscription", "charge"],
    "Account Info": ["username", "password", "login", "account", "verify", "security"],
    "Work Update": ["meeting", "project", "deadline", "update", "standup", "report"],
    "Promotion": ["sale", "offer", "discount", "promotion", "deal", "limited time"],
    "Spam": ["lottery", "winner", "prize", "crypto", "inheritance", "urgent transfer"],
    "Personal": ["family", "friend", "party", "dinner", "weekend", "love"],
    "Travel": ["flight", "hotel", "booking", "reservation", "trip", "vacation"],
    "Shopping": ["order", "delivery", "shipping", "purchase", "cart", "product"],
    "Newsletter": ["newsletter", "subscribe", "unsubscribe", "digest", "weekly"],
    "Social": ["social media", "notification", "friend request", "comment", "like"],
}

URGENCY_KEYWORDS = ["asap", "urgent", "deadline", "immediately", "critical", "overdue", "action required"]

def get_classifier():
    global _classifier
    if _classifier is None:
        try:
            _classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        except Exception as e:
            log.error(f"Failed to load classifier model: {e}")
            return None
    return _classifier

def get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        try:
            _sentiment_analyzer = pipeline("sentiment-analysis")
        except Exception as e:
            log.error(f"Failed to load sentiment model: {e}")
            return None
    return _sentiment_analyzer

def analyze_email(subject: str, body: str, account_id: Optional[int] = None, auto_create_category: bool = True) -> dict:
    """Comprehensive AI analysis of an email with light caching and dynamic category creation."""
    category, sentiment, urgency = _analyze_cached(subject, body)
    
    # Auto-create category if enabled and using dynamic categorization
    if auto_create_category:
        from services.category_service import auto_create_category_if_needed, increment_category_count
        category = auto_create_category_if_needed(category, account_id)
        increment_category_count(category, account_id)
    
    return {"category": category, "sentiment": sentiment, "urgency": urgency}


@lru_cache(maxsize=256)
def _analyze_cached(subject: str, body: str) -> tuple[str, str, str]:
    text = f"{subject} {body}".strip()
    truncated_text = text[:1024]  # Models have token limits

    category = _categorize_rule_based(text)

    classifier = get_classifier()
    if classifier:
        try:
            # Use expanded category list for better classification
            categories = [
                "Billing", "Account Info", "Work Update", "Promotion", "Spam", "Personal",
                "Travel", "Shopping", "Newsletter", "Social", "Support", "Legal", 
                "Education", "Healthcare", "Finance"
            ]
            result = classifier(truncated_text, candidate_labels=categories)
            category = result['labels'][0]
        except Exception:
            pass  # Fallback to rule-based

    sentiment = "Neutral"
    analyzer = get_sentiment_analyzer()
    if analyzer:
        try:
            res = analyzer(truncated_text)[0]
            sentiment = res['label']
        except Exception:
            pass

    urgency = "Normal"
    if any(k in text.lower() for k in URGENCY_KEYWORDS):
        urgency = "High"

    return category, sentiment, urgency

def _categorize_rule_based(text: str) -> str:
    lowered = text.lower()
    for label, keywords in FALLBACK_KEYWORDS.items():
        if any(word in lowered for word in keywords):
            return label
    return "Unlabeled"

# Legacy wrapper for backward compatibility
def categorize_email(subject: str, body: str) -> str:
    return analyze_email(subject, body)["category"]
