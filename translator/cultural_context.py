from config.languages import SUPPORTED_LANGUAGES, FORMALITY_DESCRIPTIONS


def get_cultural_context(language_key: str, formality_level: str) -> dict:
    """
    Returns enriched cultural context for a given language and formality level.
    This is what separates cultural localisation from plain translation.
    """
    lang = SUPPORTED_LANGUAGES.get(language_key)
    if not lang:
        raise ValueError(f"Language '{language_key}' not supported.")

    formality_desc = FORMALITY_DESCRIPTIONS.get(
        formality_level,
        FORMALITY_DESCRIPTIONS.get("colloquial", "Natural everyday speech."),
    )

    cultural_notes_str = "\n".join(
        [f"- {note}" for note in lang["cultural_notes"]]
    )

    idiom_examples_str = "\n".join(
        [f'  "{k}" → {v}' for k, v in lang["example_idioms"].items()]
    )

    return {
        "target_language": lang["name"],
        "target_language_native": lang["native_name"],
        "region": lang["region"],
        "script": lang["script"],
        "formality_level": formality_level,
        "formality_description": formality_desc,
        "cultural_notes": cultural_notes_str,
        "example_idioms": idiom_examples_str,
        "available_formality_levels": lang["formality_levels"],
    }


def get_available_languages() -> list[dict]:
    """Returns list of all supported languages with metadata."""
    return [
        {
            "key": key,
            "name": val["name"],
            "native_name": val["native_name"],
            "region": val["region"],
            "formality_levels": val["formality_levels"],
        }
        for key, val in SUPPORTED_LANGUAGES.items()
    ]


DOMAIN_HINTS = {
    "general": "General everyday communication.",
    "academic": "Academic or educational content. Use precise terminology.",
    "business": "Professional business communication. Formal, concise, respectful.",
    "casual": "Casual chat between friends. Relaxed, warm, humorous if original is humorous.",
    "technical": "Technical/engineering content. Keep technical terms in English where no native equivalent exists.",
    "emotional": "Personal or emotional content. Prioritise warmth and empathy over accuracy.",
    "motivational": "Motivational or inspirational content. Use culturally resonant uplift — proverbs, heroes, stories.",
}
