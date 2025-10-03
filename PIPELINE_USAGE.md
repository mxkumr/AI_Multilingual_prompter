# Pipeline Usage Guide

The updated pipeline now supports processing multiple prompts from a JSON file and stores results in individual folders for each prompt.

## JSON Input Format

Create a JSON file with the following structure:

```json
{
  "prompts": [
    {
      "id": "prompt_1",
      "text": "Write a function that calculates the factorial of a number."
    },
    {
      "id": "prompt_2", 
      "text": "Create a binary search tree implementation with insert and search methods."
    },
    {
      "id": "prompt_3",
      "text": "Implement quicksort algorithm with explanation of time complexity."
    }
  ]
}
```

### Required Fields:
- `id`: Unique identifier for the prompt (used for folder names)
- `text`: The actual prompt text to process

## Usage

### Process Multiple Prompts from JSON:
```bash
python pipeline.py prompts_input.json
```

### Process Single Prompt (Backward Compatibility):
```bash
python pipeline.py
```
Then enter the prompt when prompted.

## Output Structure

Each prompt gets its own folder under `data/` with the following structure:

```
data/
├── prompt_1/
│   ├── translated_prompts.json    # Translations to multiple languages
│   ├── llm_output.json           # LLM responses for each language
│   ├── llm_parsed.json           # Parsed code analysis results
│   ├── language_analysis_results.json
│   ├── language_analysis_summary.txt
│   └── *.png                     # Language distribution charts
├── prompt_2/
│   ├── translated_prompts.json
│   ├── llm_output.json
│   ├── llm_parsed.json
│   └── ...
└── prompt_3/
    └── ...
```

## Features

- **Individual Folders**: Each prompt's results are stored in separate folders
- **Progress Tracking**: Shows progress for multiple prompts (e.g., "Processing prompt 2/3")
- **Error Handling**: Continues processing other prompts if one fails
- **Backward Compatibility**: Still works with single prompt input
- **Logging**: LLM runtime logs are saved to `data/llm_runtime.log`

## Example JSON File

Create your own JSON file following the format above with your prompts for testing.

## Pipeline Steps

For each prompt, the pipeline:
1. **Translates** the prompt to multiple languages
2. **Queries** the LLM (Ollama) for each language
3. **Parses** the LLM outputs using Tree-sitter
4. **Visualizes** language distribution with charts
5. **Saves** all results in the prompt-specific folder
