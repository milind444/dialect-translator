import json
import os
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

from translator.prompts import (
    CULTURAL_TRANSLATION_PROMPT,
    IDIOM_DETECTOR_PROMPT,
    BACK_TRANSLATION_PROMPT,
)
from translator.cultural_context import get_cultural_context, DOMAIN_HINTS


def get_llm(temperature: float = 0.3) -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY"),
    )


def _safe_parse_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip().rstrip("```").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw_response": raw}


def detect_idioms(text: str) -> dict:
    """
    Step 1: Analyse source text for idioms, cultural references,
    and elements that need localisation.
    """
    llm = get_llm(temperature=0.1)
    prompt = IDIOM_DETECTOR_PROMPT.format(text=text)
    response = llm.invoke([HumanMessage(content=prompt)])
    return _safe_parse_json(response.content)


def translate_culturally(
    source_text: str,
    language_key: str,
    formality_level: str,
    domain: str = "general",
) -> dict:
    """
    Step 2: Core cultural translation chain.
    Returns translated text + cultural adaptation notes.
    """
    ctx = get_cultural_context(language_key, formality_level)
    domain_hint = DOMAIN_HINTS.get(domain, DOMAIN_HINTS["general"])

    prompt = CULTURAL_TRANSLATION_PROMPT.format(
        source_text=source_text,
        target_language=ctx["target_language"],
        target_language_native=ctx["target_language_native"],
        region=ctx["region"],
        formality_level=ctx["formality_level"],
        formality_description=ctx["formality_description"],
        cultural_notes=ctx["cultural_notes"],
        example_idioms=ctx["example_idioms"],
        domain=f"{domain} — {domain_hint}",
    )

    llm = get_llm(temperature=0.4)
    response = llm.invoke([HumanMessage(content=prompt)])
    result = _safe_parse_json(response.content)
    result["language_meta"] = ctx
    return result


def back_translate(translated_text: str, target_language: str) -> dict:
    """
    Step 3: Back-translate to English to verify meaning was preserved.
    A quality assurance step used in professional translation workflows.
    """
    llm = get_llm(temperature=0.1)
    prompt = BACK_TRANSLATION_PROMPT.format(
        translated_text=translated_text,
        source_language="English",
        target_language=target_language,
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return _safe_parse_json(response.content)


def full_translation_pipeline(
    source_text: str,
    language_key: str,
    formality_level: str,
    domain: str = "general",
    run_back_translation: bool = True,
) -> dict:
    """
    Full 3-step pipeline:
    1. Idiom detection
    2. Cultural translation
    3. Back-translation QA (optional)
    """
    # Step 1
    idiom_analysis = detect_idioms(source_text)

    # Step 2
    translation_result = translate_culturally(
        source_text, language_key, formality_level, domain
    )

    # Step 3
    back_translation = {}
    if run_back_translation and "translated_text" in translation_result:
        back_translation = back_translate(
            translation_result["translated_text"],
            translation_result["language_meta"]["target_language"],
        )

    return {
        "source_text": source_text,
        "language_key": language_key,
        "formality_level": formality_level,
        "domain": domain,
        "idiom_analysis": idiom_analysis,
        "translation": translation_result,
        "back_translation": back_translation,
    }
