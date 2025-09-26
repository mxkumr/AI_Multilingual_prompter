# Translation Tool Setup Guide

This guide will help you set up the translation tool with either free or Google Cloud API options.

## Quick Start (Free Option)

1. **Run the setup script:**
   ```bash
   python setup_translation.py
   ```

2. **Test the translation:**
   ```bash
   python Prompt_translation.py
   ```

## How It Works

The tool automatically detects which translation service is available:
- **Google Cloud Translation API**: If properly configured with credentials
- **Deep Translator (Free)**: As a fallback option that works without API keys

## Google Cloud API Setup (Optional)

If you want to use Google Cloud Translation API for better quality and higher limits:

### 1. Create a Google Cloud Project
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project or select an existing one
- Note down your Project ID

### 2. Enable Translation API
- In the Google Cloud Console, go to "APIs & Services" > "Library"
- Search for "Cloud Translation API"
- Click on it and enable the API

### 3. Create Service Account
- Go to "IAM & Admin" > "Service Accounts"
- Click "Create Service Account"
- Give it a name (e.g., "translation-service")
- Grant it "Cloud Translation API User" role
- Create and download the JSON key file

### 4. Set up Credentials
- Place the downloaded JSON file in the `credentials/` directory
- Rename it to `service-account-key.json`

### 5. Set Environment Variables
```bash
# Windows (Command Prompt)
set GOOGLE_CLOUD_PROJECT=your-project-id
set GOOGLE_APPLICATION_CREDENTIALS=credentials\service-account-key.json

# Windows (PowerShell)
$env:GOOGLE_CLOUD_PROJECT="your-project-id"
$env:GOOGLE_APPLICATION_CREDENTIALS="credentials\service-account-key.json"

# Linux/Mac
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account-key.json
```

## Usage

### Basic Usage
```python
from Prompt_translation import translate_all_languages

# Translate a prompt to all 20 languages
translations = translate_all_languages("Hello, how are you?")
print(translations)
```

### Command Line Usage
```bash
python Prompt_translation.py
# Enter your prompt when prompted
```

## Supported Languages

The tool supports translation to 20 major languages:
- English (en)
- Chinese Mandarin (zh-CN)
- Hindi (hi)
- Spanish (es)
- Arabic (ar)
- Bengali (bn)
- French (fr)
- Russian (ru)
- Portuguese (pt)
- Urdu (ur)
- Indonesian (id)
- German (de)
- Japanese (ja)
- Swahili (sw)
- Turkish (tr)
- Vietnamese (vi)
- Korean (ko)
- Tamil (ta)
- Marathi (mr)
- Persian (fa)

## Troubleshooting

### Common Issues

1. **"deep-translator not available"**
   - Run: `pip install deep-translator`

2. **"Google Cloud Translate not available"**
   - Run: `pip install google-cloud-translate`

3. **"File credentials/service-account-key.json was not found"**
   - Either set up Google Cloud credentials (see above) or the tool will use the free option

4. **Rate limiting errors**
   - The free option includes delays to avoid rate limiting
   - For heavy usage, consider using Google Cloud API

### File Structure
```
your-project/
├── Prompt_translation.py          # Main translation script
├── setup_translation.py           # Setup script
├── TRANSLATION_SETUP.md          # This guide
├── credentials/                   # Google Cloud credentials (optional)
│   └── service-account-key.json
└── data/                         # Output directory
    └── translated_prompts.json
```

## Output

The tool saves translations to `data/translated_prompts.json` in the following format:
```json
{
    "en": "Hello, how are you?",
    "zh-CN": "你好，你好吗？",
    "hi": "नमस्ते, आप कैसे हैं?",
    ...
}
```
