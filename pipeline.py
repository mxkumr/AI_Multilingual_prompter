import os
import sys
import json
import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional


def ensure_dirs() -> str:
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    return project_root


def translate_prompt(prompt_text: str) -> Dict[str, Optional[str]]:
    # Delegate to Prompt_translation.translate_prompt (async) with TARGET_LANG_CODES
    from Prompt_translation import translate_prompt as pt_translate_prompt, TARGET_LANG_CODES

    try:
        return asyncio.run(pt_translate_prompt(prompt_text, TARGET_LANG_CODES))
    except RuntimeError:
        # Fallback if an event loop is already running
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(pt_translate_prompt(prompt_text, TARGET_LANG_CODES))


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
            start_perf = time.perf_counter()
            start_wall = time.time()
            try:
                result = query_model(prompt)
                end_wall = time.time()
                duration = time.perf_counter() - start_perf
                log_llm_duration(lang, start_wall, end_wall, duration, success=True)
                outputs[lang] = result
                print(f"Generated code for {lang}: {str(result)[:100]}...")
            except Exception as inner_e:
                end_wall = time.time()
                duration = time.perf_counter() - start_perf
                log_llm_duration(lang, start_wall, end_wall, duration, success=False, error_message=str(inner_e))
                print(f"LLM query failed for {lang}: {inner_e}")
                outputs[lang] = None
            time.sleep(1)
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


def setup_logger() -> None:
    """Configure logging to file for LLM runtimes."""
    logging.basicConfig(
        filename="data/llm_runtime.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s\t%(levelname)s\t%(message)s",
    )
    # Reduce noise from HTTP client libraries and others
    for noisy in ("httpx", "urllib3", "requests", "googletrans"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def log_llm_duration(language: str, start_ts: float, end_ts: float, seconds: float, success: bool = True, error_message: Optional[str] = None) -> None:
    """Log start time, end time, and total duration (in minutes) for an LLM run."""
    start_iso = datetime.fromtimestamp(start_ts).isoformat(timespec="seconds")
    end_iso = datetime.fromtimestamp(end_ts).isoformat(timespec="seconds")
    minutes = seconds / 60.0
    if success:
        logging.info(
            f"lang={language}\tstart={start_iso}\tend={end_iso}\tduration_min={minutes:.3f}"
        )
    else:
        logging.error(
            f"lang={language}\tstart={start_iso}\tend={end_iso}\tduration_min={minutes:.3f}\terror={error_message}"
        )


def main() -> None:
    project_root = ensure_dirs()
    data_dir = os.path.join(project_root, "data")
    setup_logger()

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


