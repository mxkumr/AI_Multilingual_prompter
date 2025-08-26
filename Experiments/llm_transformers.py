import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

# Choose your multilingual model
MODEL_NAME = "qwen3:30b-a3b"  

# Load tokenizer and model
print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto")

def query_model(prompt: str, max_tokens: int = 256) -> str:
    """Query Hugging Face model with prompt and return clean code-only output"""
    formatted_prompt = f"Output ONLY valid Python code. Do not explain.\n\n{prompt}\n\n"
    
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.2,  # lower = more deterministic
        top_p=0.9
    )
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Optional cleanup: remove markdown fences if present
    text = text.replace("```python", "").replace("```", "").strip()
    return text

def main():
    # Load translated prompts
    with open("data/translated_prompts.json", "r", encoding="utf-8") as f:
        translations = json.load(f)

    output_dir = "data/generated_code"
    os.makedirs(output_dir, exist_ok=True)

    for lang, prompt in translations.items():
        if not prompt:
            continue
        print(f"Generating code for: {lang}")
        try:
            code = query_model(prompt)
            # Save directly into .py files
            file_path = os.path.join(output_dir, f"{lang}.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
            print(f"Error generating code for {lang}: {e}")

if __name__ == "__main__":
    main()
