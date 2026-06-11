import os
import streamlit as st


# Load from Streamlit secrets if available (for cloud deployment)
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

from translator import (
    full_translation_pipeline,
    auto_detect_formality,
    detect_domain,
    get_available_languages,
)

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dialect-aware Cultural Translator",
    page_icon="🗣️",
    layout="wide",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Hindi&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.lang-badge {
    display: inline-block;
    background: #f0f4ff;
    color: #3b4bdb;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: 500;
    margin: 2px;
}
.native-script {
    font-family: 'Tiro Devanagari Hindi', serif;
    font-size: 28px;
    color: #1a1a2e;
    line-height: 1.6;
    background: #fafafa;
    border-left: 4px solid #3b4bdb;
    padding: 16px 20px;
    border-radius: 0 8px 8px 0;
    margin: 12px 0;
}
.transliteration {
    font-style: italic;
    color: #555;
    font-size: 14px;
    margin: 4px 0 16px;
}
.adaptation-card {
    background: #fff8f0;
    border: 1px solid #ffe0b2;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 8px 0;
}
.quality-bar {
    height: 8px;
    border-radius: 4px;
    background: linear-gradient(90deg, #f44336, #ff9800, #4caf50);
}
.tip-box {
    background: #e8f5e9;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #2e7d32;
    margin-top: 8px;
}
.section-header {
    font-size: 13px;
    font-weight: 500;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 20px 0 8px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("## 🗣️ Dialect-aware Cultural Translator")
st.markdown(
    "Not just translation — **cultural localisation**. Idioms, metaphors, tone, and context adapted for each region."
)
st.divider()

# ─── Sidebar config ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        help="Free at console.groq.com → API Keys",
    )
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    st.divider()

    languages = get_available_languages()
    lang_options = {f"{l['name']} ({l['native_name']})": l["key"] for l in languages}

    selected_lang_display = st.selectbox(
        "Target Language",
        list(lang_options.keys()),
        help="Choose the target regional language",
    )
    selected_lang_key = lang_options[selected_lang_display]

    selected_lang_meta = next(l for l in languages if l["key"] == selected_lang_key)

    formality_options = selected_lang_meta["formality_levels"]
    formality_level = st.selectbox(
        "Formality / Dialect",
        formality_options,
        help="Controls vocabulary, grammar style, and slang usage",
    )

    domain = st.selectbox(
        "Domain / Context",
        ["general", "academic", "business", "casual", "technical", "emotional", "motivational"],
        help="Helps the AI choose culturally appropriate examples",
    )

    run_back_translation = st.toggle(
        "Quality check (back-translation)",
        value=True,
        help="Translates the output back to English to verify meaning was preserved",
    )

    auto_mode = st.toggle(
        "Auto-detect formality & domain",
        value=False,
        help="Let the AI analyse your text and pick the best settings",
    )

    st.divider()
    st.markdown("**Supported Languages**")
    for l in languages:
        st.markdown(
            f'<span class="lang-badge">{l["native_name"]}</span>', unsafe_allow_html=True
        )

# ─── Main UI ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="section-header">Source Text (English)</div>', unsafe_allow_html=True)
    source_text = st.text_area(
        "",
        placeholder="Paste your text here. Try something with idioms, like: 'It's raining cats and dogs, but we need to hit the ground running or we'll drop the ball on this project.'",
        height=200,
        label_visibility="collapsed",
    )

    example_texts = {
        "Motivational (idioms)": "Don't put all your eggs in one basket. Life is a marathon, not a sprint. When the going gets tough, the tough get going.",
        "Business email": "Please find attached the quarterly report. We need to circle back on the pending action items before end of day.",
        "Casual friends": "Hey! What's up? We're thinking of grabbing pizza tonight and then maybe catch a movie. You in?",
        "Academic": "The study demonstrates a statistically significant correlation between social media usage and adolescent anxiety levels.",
        "Emotional / personal": "I've been feeling really overwhelmed lately. It feels like no matter what I do, I can never catch a break.",
    }

    selected_example = st.selectbox("Or try an example:", ["— pick one —"] + list(example_texts.keys()))
    if selected_example != "— pick one —":
        source_text = example_texts[selected_example]
        st.info(source_text)

    translate_btn = st.button("🌐 Translate culturally", type="primary", use_container_width=True)

# ─── Translation Output ───────────────────────────────────────────────────────
with col2:
    st.markdown('<div class="section-header">Cultural Translation</div>', unsafe_allow_html=True)

    if translate_btn:
        if not source_text.strip():
            st.warning("Please enter some text to translate.")
        elif not os.getenv("GROQ_API_KEY"):
            st.error("Please enter your OpenAI API key in the sidebar.")
        else:
            with st.spinner("Analysing cultural context and translating..."):

                # Auto-detect if enabled
                effective_formality = formality_level
                effective_domain = domain
                if auto_mode:
                    with st.spinner("Auto-detecting formality and domain..."):
                        effective_formality = auto_detect_formality(source_text, selected_lang_key)
                        effective_domain = detect_domain(source_text)
                    st.info(f"Auto-detected → Formality: **{effective_formality}** | Domain: **{effective_domain}**")

                result = full_translation_pipeline(
                    source_text=source_text,
                    language_key=selected_lang_key,
                    formality_level=effective_formality,
                    domain=effective_domain,
                    run_back_translation=run_back_translation,
                )

            translation = result.get("translation", {})
            idioms = result.get("idiom_analysis", {})
            back = result.get("back_translation", {})

            if "error" in translation:
                st.error(f"Translation error: {translation['error']}")
            else:
                # ── Translated text ──
                translated = translation.get("translated_text", "")
                st.markdown(
                    f'<div class="native-script">{translated}</div>',
                    unsafe_allow_html=True,
                )

                roman = translation.get("transliteration", "")
                if roman:
                    st.markdown(
                        f'<div class="transliteration">🔤 {roman}</div>',
                        unsafe_allow_html=True,
                    )

                # ── Tone notes ──
                tone = translation.get("tone_notes", "")
                if tone:
                    st.markdown(f"**Tone:** {tone}")

                # ── Regional tip ──
                tip = translation.get("regional_tip", "")
                if tip:
                    st.markdown(
                        f'<div class="tip-box">💡 {tip}</div>',
                        unsafe_allow_html=True,
                    )

                st.divider()

                # ── Cultural adaptations ──
                adaptations = translation.get("cultural_adaptations", [])
                if adaptations:
                    st.markdown("**🎭 Cultural adaptations made:**")
                    for a in adaptations:
                        st.markdown(
                            f"""<div class="adaptation-card">
                            <b>Original:</b> {a.get('original', '')}<br>
                            <b>Adapted to:</b> {a.get('adapted', '')}<br>
                            <small style="color:#888">{a.get('reason', '')}</small>
                            </div>""",
                            unsafe_allow_html=True,
                        )

                # ── Idiom analysis ──
                if idioms and not idioms.get("error"):
                    with st.expander("🔍 Idiom & localisation analysis"):
                        if idioms.get("idioms"):
                            st.markdown(f"**Idioms detected:** {', '.join(idioms['idioms'])}")
                        if idioms.get("localisable_elements"):
                            st.markdown(f"**Localised:** {', '.join(idioms['localisable_elements'])}")
                        if idioms.get("cultural_references"):
                            st.markdown(f"**Western references adapted:** {', '.join(idioms['cultural_references'])}")
                        complexity = idioms.get("localisation_complexity", "")
                        colour = {"simple": "🟢", "moderate": "🟡", "complex": "🔴"}.get(complexity, "⚪")
                        st.markdown(f"**Complexity:** {colour} {complexity}")

                # ── Back-translation QA ──
                if back and not back.get("error"):
                    with st.expander("✅ Quality check (back-translation)"):
                        score = back.get("quality_score", 0)
                        st.markdown(f"**Quality score:** {score}/10")
                        st.progress(score / 10)
                        st.markdown(f"**Back-translated to English:**\n\n_{back.get('back_translation', '')}_")
                        notes = back.get("quality_notes", "")
                        if notes:
                            st.markdown(f"**Notes:** {notes}")

                # ── Difficulty indicator ──
                diff = translation.get("difficulty_for_non_native", "")
                if diff:
                    colour_map = {"easy": "🟢", "moderate": "🟡", "advanced": "🔴"}
                    st.caption(f"Native reader difficulty: {colour_map.get(diff, '⚪')} {diff}")

    else:
        st.markdown(
            """
            <div style="color:#aaa; font-size:14px; margin-top:40px; text-align:center;">
            Your translation will appear here.<br><br>
            Try the example texts on the left to see cultural adaptations in action.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─── How it works ─────────────────────────────────────────────────────────────
with st.expander("📖 How this works (3-step pipeline)"):
    st.markdown("""
**Step 1 — Idiom Detection**
LangChain analyses your input for idioms, cultural references, currencies, and localisation-sensitive content.

**Step 2 — Cultural Translation**
The LLM acts as a native speaker. It doesn't just swap words — it replaces baseball with cricket, dollars with rupees, and Western idioms with regional proverbs.

**Step 3 — Back-Translation QA**
The translated text is translated back to English to verify meaning was preserved. A quality score is generated.

**What makes this different from Google Translate?**
- Formality levels (formal vs colloquial vs regional slang)
- Domain-aware context (business vs emotional vs motivational)
- Cultural anchor injection (festivals, food, cinema references)
- Idiom → regional equivalent conversion
- Explicit adaptation notes so you can see exactly what changed and why
    """)
