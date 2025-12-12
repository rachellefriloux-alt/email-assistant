import logging
import os

import google.generativeai as genai

log = logging.getLogger(__name__)

_gemini_configured = False


def _configure_gemini():
    """Configure Google Generative AI with API key."""
    global _gemini_configured
    if _gemini_configured:
        return True
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        log.warning("GOOGLE_API_KEY is not set; Gemini features will be disabled.")
        return False
    
    genai.configure(api_key=api_key)
    _gemini_configured = True
    return True


async def generate_summary(email_text: str) -> str:
    """Generate a summary of an email using Gemini."""
    if not _configure_gemini():
        return "Gemini API is not configured. Please set GOOGLE_API_KEY."
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Summarize the following email concisely:\n\n{email_text}"
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as exc:
        log.error("Gemini summary failed: %s", exc)
        return "Error generating summary. Please try again later."


async def extract_action_items(email_text: str) -> str:
    """Extract action items from an email using Gemini."""
    if not _configure_gemini():
        return "Gemini API is not configured. Please set GOOGLE_API_KEY."
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Extract all action items and tasks from this email:\n\n{email_text}"
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as exc:
        log.error("Gemini action extraction failed: %s", exc)
        return "Error extracting action items. Please try again later."


async def rewrite_draft(text: str, tone: str) -> str:
    """Rewrite a draft email in a specific tone using Gemini."""
    if not _configure_gemini():
        return "Gemini API is not configured. Please set GOOGLE_API_KEY."
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Rewrite the following text in a {tone} tone:\n\n{text}"
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as exc:
        log.error("Gemini rewrite failed: %s", exc)
        return "Error rewriting text. Please try again later."
