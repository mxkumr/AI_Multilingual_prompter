import json
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:30b-a3b"  # Change to your model name if needed


def query_model(prompt=None, model=MODEL, messages=None, tokenizer=None):
    # If chat messages and a tokenizer are provided, apply the chat template
    if messages is not None and tokenizer is not None:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False  # This is the hard switch
        )
        prompt_to_send = text
    else:
        prompt_to_send = prompt
    payload = {
        "model": model,
        "prompt": prompt_to_send,
        "system": "/no_think You are a code generator. Always respond with only the code in a Python fenced code block. No explanation. No thinking steps.",
        "stream": False,
        "enable_thinking": False,
        # Hint Ollama to use GPU where available (offload as many layers as possible)
       # "options": {
        #    "num_gpu": 999
        #}
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()["response"]


def main():
    # Load translated prompts
    with open("data/translated_prompts.json", "r", encoding="utf-8") as f:
        translations = json.load(f)

    llm_outputs = {}
    for lang, prompt in translations.items():
        if not prompt:
            llm_outputs[lang] = None
            continue
        print(f"Querying model for language: {lang}")
        try:
            llm_response = query_model(prompt)
            llm_outputs[lang] = llm_response
        except Exception as e:
            print(f"Error querying model for {lang}: {e}")
            llm_outputs[lang] = None
        time.sleep(1)  # Be nice to your LLM, avoid rate limits

    # Save LLM outputs
    with open("data/llm_output.json", "w", encoding="utf-8") as f:
        json.dump(llm_outputs, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
