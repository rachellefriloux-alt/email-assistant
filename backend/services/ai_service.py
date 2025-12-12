import logging
from functools import lru_cache
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

def analyze_email(subject: str, body: str) -> dict:
    """Comprehensive AI analysis of an email with light caching."""
    category, sentiment, urgency = _analyze_cached(subject, body)
    return {"category": category, "sentiment": sentiment, "urgency": urgency}


@lru_cache(maxsize=256)
def _analyze_cached(subject: str, body: str) -> tuple[str, str, str]:
    text = f"{subject} {body}".strip()
    truncated_text = text[:1024]  # Models have token limits

    category = _categorize_rule_based(text)

    classifier = get_classifier()
    if classifier:
        try:
            categories = ["Billing", "Account Info", "Work Update", "Promotion", "Spam", "Personal"]
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
