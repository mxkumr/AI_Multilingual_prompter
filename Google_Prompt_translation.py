import os
import json
import re
from typing import Dict, Optional
from google.cloud import translate
# List of 20 languages for full run
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

SENTENCE_PUNCT = re.compile(r'([.!?])(?!\s|$)')

def normalize_text(text):
    # Ensure a single space after sentence-ending punctuation and collapse multiple spaces
    text = SENTENCE_PUNCT.sub(r'\1 ', text)
    return re.sub(r'\s{2,}', ' ', text).strip()

def translate_with_google_api(text: str, target_language: str, *, project_id: str, location: str = "global") -> Optional[str]:
    """Translate text with Google Cloud Translation API v3.

    Requires credentials via Application Default Credentials (e.g., GOOGLE_APPLICATION_CREDENTIALS) and
    project id via GOOGLE_CLOUD_PROJECT or provided argument.
    """
    client = translate.TranslationServiceClient()
    parent = f"projects/{project_id}/locations/{location}"
    try:
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",
                "target_language_code": target_language,
            }
        )
        if response.translations:
            return response.translations[0].translated_text
        return None
    except Exception as e:
        print(f"Error from Google Translate API for {target_language}: {e}")
        return None


def translate_all_languages(prompt: str) -> Dict[str, Optional[str]]:
    prompt = normalize_text(prompt)
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT environment variable is not set.")

    translations: Dict[str, Optional[str]] = {}
    for lang in top_20_languages:
        translated = translate_with_google_api(prompt, lang, project_id=project_id)
        translations[lang] = translated
    return translations

if __name__ == "__main__":
    prompt = input("Enter the prompt to translate: ")
    translations = translate_all_languages(prompt)
    for lang, text in translations.items():
        print(f"{lang}: {text}")

    translated = f"data/translated_prompts.json"
    with open(translated, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=4)

