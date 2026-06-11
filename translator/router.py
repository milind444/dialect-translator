"""
Router module: analyses source text and recommends the best
language + formality combination automatically.
"""
import os
import json
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from config.languages import SUPPORTED_LANGUAGES


def auto_detect_formality(text: str, language_key: str) -> str:
    """
    Analyses input text and recommends the most appropriate
    formality level for the target language.
    """
    lang = SUPPORTED_LANGUAGES.get(language_key, {})
    available = lang.get("formality_levels", ["formal", "colloquial"])

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    prompt = f"""Analyse this text and recommend the best formality level for translating it into {lang.get('name', language_key)}.

Text: "{text}"

Available formality levels: {available}

Consider:
- Is the text formal (official, professional)?
- Is it casual (friendly, informal)?
- Is it for rural/traditional audience?
- Does it use slang or colloquialisms?

Return ONLY valid JSON:
{{"recommended_formality": "<one of {available}>", "reason": "<one sentence explanation>"}}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        result = json.loads(response.content.strip())
        return result.get("recommended_formality", available[1])
    except Exception:
        return available[1]  # default to colloquial


def detect_domain(text: str) -> str:
    """Auto-detects the domain/context of the source text."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    domains = ["general", "academic", "business", "casual", "technical", "emotional", "motivational"]

    prompt = f"""What is the domain/context of this text?

Text: "{text}"

Choose EXACTLY one from: {domains}

Return ONLY valid JSON:
{{"domain": "<chosen domain>", "confidence": <0.0-1.0>}}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        result = json.loads(response.content.strip())
        return result.get("domain", "general")
    except Exception:
        return "general"
