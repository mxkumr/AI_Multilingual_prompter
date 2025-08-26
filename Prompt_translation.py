from deep_translator import GoogleTranslator
import json
# List of top 50 language codes (example, adjust as needed)
top_20_languages = {
    "en": "English",
    "zh-CN": "Chinese (Mandarin)",
    "hi": "Hindi",
    "es": "Spanish",
    "ar": "Arabic",
    "bn": "Bengali",
    "fr": "French",
    "ru": "Russian",
    "pt": "Portuguese",
    "ur": "Urdu",
    "id": "Indonesian",
    "de": "German",
    "ja": "Japanese",
    "sw": "Swahili",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "ko": "Korean",
    "ta": "Tamil",
    "mr": "Marathi",
    "fa": "Persian"
}

def translate_all_languages(prompt):
    translations = {}
    for lang in top_20_languages:
        try:
            translated = GoogleTranslator(source='en', target=lang).translate(prompt)
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

