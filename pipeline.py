import os
import sys
import json
from typing import Dict, Any


def ensure_dirs() -> str:
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    return project_root


def translate_prompt(prompt_text: str) -> Dict[str, str]:
    from deep_translator import GoogleTranslator
    # Keep in sync with Prompt_translation.top_20_languages
    target_langs = [
        "en",      # English
        "zh-CN",  # Chinese (Mandarin)
        "hi",     # Hindi
        "es",     # Spanish
        "ar",     # Arabic
        "bn",     # Bengali
        "fr",     # French
        "ru",     # Russian
        "pt",     # Portuguese
        "ur",     # Urdu
        "id",     # Indonesian
        "de",     # German
        "ja",     # Japanese
        "sw",     # Swahili
        "tr",     # Turkish
        "vi",     # Vietnamese
        "ko",     # Korean
        "ta",     # Tamil
        "mr",     # Marathi
        "fa"      # Persian
    ]

    translations: Dict[str, str] = {}
    for lang in target_langs:
        try:
            translations[lang] = GoogleTranslator(source='en', target=lang).translate(prompt_text)
        except Exception as e:
            print(f"Translation failed for {lang}: {e}")
            translations[lang] = None
    return translations


def query_llm_for_translations(translations: Dict[str, str]) -> Dict[str, str]:
    # Use local Ollama via LLM.query_model
    from LLM_strip import query_model  # posts to http://localhost:11434
    outputs: Dict[str, str] = {}
    for lang, prompt in translations.items():
        if not prompt:
            outputs[lang] = None
            continue
        try:
            print(f"Querying LLM for {lang}...")
            outputs[lang] = query_model(prompt)
        except Exception as e:
            print(f"LLM query failed for {lang}: {e}")
            outputs[lang] = None
    return outputs


def parse_llm_outputs(outputs: Dict[str, str]) -> Dict[str, Any]:
    # Reuse parser.parse_code_files_with_multilang_parser
    from parser import parse_code_files_with_multilang_parser
    print("Parsing code snippets with Tree-sitter...")
    return parse_code_files_with_multilang_parser(outputs)


def visualize_language_distribution() -> None:
    # Reuse non_english.main to generate charts and summary
    import non_english
    print("Generating language charts...")
    non_english.main()


def main() -> None:
    project_root = ensure_dirs()
    data_dir = os.path.join(project_root, "data")

    # 1) Prompt input
    prompt_text = None
    if len(sys.argv) > 1:
        prompt_text = " ".join(sys.argv[1:]).strip()
    if not prompt_text:
        prompt_text = input("Enter the base prompt (in English): ").strip()
    if not prompt_text:
        print("Empty prompt; aborting.")
        return

    # Normalize prompt formatting (spaces after punctuation, collapse multiple spaces)
    try:
        from Prompt_translation import normalize_text
        prompt_text = normalize_text(prompt_text)
    except Exception:
        # Fallback to original prompt if normalization import fails
        pass

    # 2) Translate
    print("Translating prompt to multiple languages...")
    translations = translate_prompt(prompt_text)
    translated_path = os.path.join(data_dir, "translated_prompts.json")
    with open(translated_path, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    print(f"Saved translations to {translated_path}")

    # 3) Query LLM (Ollama)
    llm_outputs = query_llm_for_translations(translations)
    llm_out_path = os.path.join(data_dir, "llm_output.json")
    with open(llm_out_path, "w", encoding="utf-8") as f:
        json.dump(llm_outputs, f, ensure_ascii=False, indent=2)
    print(f"Saved LLM outputs to {llm_out_path}")

    # 4) Parse
    parsed = parse_llm_outputs(llm_outputs)
    parsed_path = os.path.join(data_dir, "llm_parsed.json")
    with open(parsed_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    print(f"Saved parsed results to {parsed_path}")

    # 5) Visualize
    visualize_language_distribution()
    print("Pipeline complete.")


if __name__ == "__main__":
    main()


