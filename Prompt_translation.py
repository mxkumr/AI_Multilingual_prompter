from deep_translator import GoogleTranslator
import json
import re
# List of 20 languages for full run
top_20_languages = {
    "en": "English",
    "zh-CN": "Mandarin Chinese",
    "hi": "Hindi",
    "es": "Spanish",
    "ar": "Standard Arabic",
    "fr": "French",
    "bn": "Bengali",
    "pt": "Portuguese",
    "ru": "Russian",
    "id": "Indonesian",
    "ur": "Urdu",
    "de": "Standard German",
    "ja": "Japanese",
    "mr": "Marathi",
    "vi": "Vietnamese",
    "te": "Telugu",
    "ha": "Hausa",
    "tr": "Turkish"
}

SENTENCE_PUNCT = re.compile(r'([.!?])(?!\s|$)')

def normalize_text(text):
    # Ensure a single space after sentence-ending punctuation and collapse multiple spaces
    text = SENTENCE_PUNCT.sub(r'\1 ', text)
    return re.sub(r'\s{2,}', ' ', text).strip()

def translate_all_languages(prompt):
    prompt = normalize_text(prompt)
    translations = {}
    for lang in top_20_languages:
        try:
            translated = GoogleTranslator(source='auto', target=lang).translate(prompt)
            translations[lang] = translated
        except Exception as e:
            print(f"Error translating to {lang}: {e}")
            translations[lang] = None
    return translations

if __name__ == "__main__":
    prompt = input("Enter the prompt to translate: ")
    translations = translate_all_languages(prompt)
    for lang, text in translations.items():
        print(f"{lang}: {text}")

    translated = f"data/translated_prompts.json"
    with open(translated, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=4)