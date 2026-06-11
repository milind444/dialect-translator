# Dialect-aware Cultural Translator

A LangChain-powered cultural localisation tool that translates English into Indian regional languages — adapting idioms, metaphors, formality, and cultural references for each specific region and dialect.

## What makes this different from Google Translate?

| Feature | Google Translate | This Project |
|---|---|---|
| Word-for-word translation | ✅ | ✅ |
| Idiom → regional equivalent | ❌ | ✅ |
| Formality levels | ❌ | ✅ |
| Domain-aware context | ❌ | ✅ |
| Cultural anchor injection | ❌ | ✅ |
| Adaptation explanations | ❌ | ✅ |
| Back-translation QA | ❌ | ✅ |

## Supported Languages

- **Odia** (ଓଡ଼ିଆ) — formal, colloquial, rural
- **Tamil** (தமிழ்) — formal, colloquial, Chennai slang
- **Bengali** (বাংলা) — formal, colloquial, Kolkata street
- **Hindi** (हिन्दी) — formal, colloquial, Hinglish
- **Telugu** (తెలుగు) — formal, colloquial, Hyderabad Dakhni

## Setup

```bash
# 1. Clone / download the project
cd dialect-translator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API key
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Run the app
streamlit run app.py
```

## Project Structure

```
dialect-translator/
├── app.py                         # Streamlit UI
├── translator/
│   ├── chain.py                   # 3-step LangChain pipeline
│   ├── router.py                  # Auto-detect formality & domain
│   ├── cultural_context.py        # Cultural data injection layer
│   └── prompts.py                 # All prompt templates
├── config/
│   └── languages.py               # Language metadata + cultural notes
├── requirements.txt
└── .env.example
```

## The 3-Step Pipeline

```
English Input
      │
      ▼
[Step 1] Idiom Detector
  — finds idioms, currencies, Western references
      │
      ▼
[Step 2] Cultural Translation Chain
  — replaces baseball → cricket
  — replaces dollars → rupees
  — injects regional proverbs, festival references
  — matches formality level exactly
      │
      ▼
[Step 3] Back-Translation QA
  — translates output back to English
  — generates quality score (1-10)
  — flags any meaning loss
      │
      ▼
Output: Translated text + transliteration
        + adaptation notes + quality report
```

## Key LangChain Concepts Used

- `PromptTemplate` — structured, reusable prompts with variables
- `ChatOpenAI` — GPT-4o integration
- `LLMChain` — chaining prompts and models
- Output parsing — strict JSON extraction from LLM responses
- Sequential chains — idiom detection → translation → QA

## Example

**Input (English):**
> "It's raining cats and dogs, but we need to hit the ground running or we'll drop the ball."

**Odia colloquial output:**
> "ଆକାଶ ଫାଟି ଝଡ଼ ବର୍ଷୁଛି, କିନ୍ତୁ ଆମକୁ ତୁରନ୍ତ ଆରମ୍ଭ କରିବାକୁ ପଡ଼ିବ — ନହେଲେ ସୁଯୋଗ ହାତରୁ ଯିବ।"

**Cultural adaptations made:**
- "raining cats and dogs" → "ଆକାଶ ଫାଟି ଝଡ଼" (sky splitting with storms — the Odia expression for heavy rain)
- "drop the ball" → "ସୁଯୋଗ ହାତରୁ ଯିବ" (the opportunity slipping from hand — no ball-sport equivalent)

## Extending the Project

- Add more languages (Marathi, Gujarati, Punjabi, Malayalam)
- Add voice output using gTTS for each language
- Export translations as PDF with cultural notes
- Add a "compare dialects" mode side by side
- Fine-tune with regional literature datasets

## Resume Talking Points

- Implemented a 3-step agentic pipeline using LangChain (detection → translation → QA)
- Engineered culturally-aware prompt templates with dynamic context injection
- Built a back-translation quality assurance loop — reducing meaning loss vs naive translation
- Supports 5 Indian languages × 3 formality levels = 15 distinct translation modes
- Deployed as interactive Streamlit app with real-time cultural adaptation explanations
