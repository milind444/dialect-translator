from langchain.prompts import PromptTemplate

CULTURAL_TRANSLATION_PROMPT = PromptTemplate(
    input_variables=[
        "source_text",
        "target_language",
        "target_language_native",
        "region",
        "formality_level",
        "formality_description",
        "cultural_notes",
        "example_idioms",
        "domain",
    ],
    template="""You are a master cultural linguist and native speaker of {target_language} ({target_language_native}) from {region}.

Your task is NOT simple word-for-word translation. You must perform CULTURAL LOCALISATION — adapting the meaning, examples, idioms, tone, and emotional register so the text feels written BY a native speaker FOR a native audience.

=== SOURCE TEXT ===
{source_text}

=== TARGET LANGUAGE ===
Language: {target_language} ({target_language_native})
Region: {region}
Formality: {formality_level}
Formality guide: {formality_description}
Domain/Context: {domain}

=== CULTURAL ANCHORS (use these to adapt examples and metaphors) ===
{cultural_notes}

=== EXAMPLE IDIOM TRANSLATIONS (for reference style) ===
{example_idioms}

=== YOUR TRANSLATION RULES ===
1. Translate meaning, not words. If the source uses a baseball metaphor, replace it with cricket.
2. Adapt numbers to local context (dollars → rupees, miles → km, American cities → Indian cities).
3. Match the formality level precisely.
4. Preserve the emotional intent — humour stays humorous, urgency stays urgent.
5. Use culturally resonant examples from the region's food, festivals, cinema, or daily life.
6. If a concept has no cultural equivalent, explain it through a familiar analogy.

=== OUTPUT FORMAT (strict JSON) ===
Return ONLY valid JSON. No markdown, no backticks, no extra text.

{{
  "translated_text": "<full translation in {target_language}>",
  "transliteration": "<romanised phonetic reading for non-script readers>",
  "cultural_adaptations": [
    {{
      "original": "<what was changed>",
      "adapted": "<what it became>",
      "reason": "<why this cultural adaptation was made>"
    }}
  ],
  "tone_notes": "<brief note on how formality/emotion was handled>",
  "difficulty_for_non_native": "<easy / moderate / advanced>",
  "regional_tip": "<one interesting cultural fact about this language or region>"
}}
""",
)


IDIOM_DETECTOR_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""Analyse the following English text and identify:
1. All idioms, metaphors, and culturally-specific references
2. Numbers, currencies, or units that need localisation
3. Names of places, brands, or celebrities that may be unknown in India

Text: {text}

Return ONLY valid JSON. No markdown, no extra text.
{{
  "idioms": ["list of idioms found"],
  "localisable_elements": ["currencies, units, places to adapt"],
  "cultural_references": ["Western references that need Indian equivalents"],
  "localisation_complexity": "simple / moderate / complex"
}}
""",
)


BACK_TRANSLATION_PROMPT = PromptTemplate(
    input_variables=["translated_text", "source_language", "target_language"],
    template="""Translate the following {target_language} text back to {source_language} (English) to verify accuracy.
Do a faithful, literal back-translation — not a clean rewrite.

Text: {translated_text}

Return ONLY valid JSON. No markdown.
{{
  "back_translation": "<literal English translation>",
  "meaning_preserved": true or false,
  "quality_score": <integer 1-10>,
  "quality_notes": "<what was lost or preserved>"
}}
""",
)
