import json
import requests
import time
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1:7b"  # Change to your model name if needed

def extract_code_from_response(response_text):
    """Extract only the code from the LLM response, removing thinking process and explanations."""
    # Remove thinking process if present
    if '<think>' in response_text:
        response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
    # Look for Python code blocks
    code_block_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1).strip()
    
    # If no code block, look for any code-like content
    # Remove common explanation prefixes
    response_text = re.sub(r'^.*?(def |class |import |from |#)', r'\1', response_text, flags=re.DOTALL)
    
    # Clean up the response
    response_text = response_text.strip()
    
    return response_text


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
        "system": "You are a code generator. Only output valid code inside a single fenced code block. Do not include explanations or text outside the code.",
        "stream": False,
        "options": {"num_gpu": 10}
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    raw_text = response.json()["response"]
    cleaned_text = extract_code_from_response(raw_text)
    return cleaned_text


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
