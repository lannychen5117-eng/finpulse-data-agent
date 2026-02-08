# FinPulse Data Agent - Quick Start Guide

## Prerequisites
- Python 3.12 installed at `/opt/homebrew/bin/python3.12`
- Nvidia API Key from https://build.nvidia.com/

## Setup Steps

### 1. Configure Environment Variables
Edit `.env` and set your actual API key:
```bash
NVIDIA_API_KEY=nvapi-YOUR-ACTUAL-KEY
```

### 2. Activate Virtual Environment
```bash
source .venv/bin/activate
```

### 3. Launch the Application
```bash
.venv/bin/streamlit run src/ui/app.py
```

## Configuration Options

The `.env` file contains comprehensive LLM configuration:
- **NVIDIA_MODEL_NAME**: Choose your model (default: `meta/llama3-70b-instruct`)
- **LLM_TEMPERATURE**: Control randomness (0.0-1.0, default: 0.1)
- **LLM_MAX_TOKENS**: Maximum response length (default: 1024)
- **NVIDIA_BASE_URL**: Optional custom endpoint

## Available Features

1. **Stock Analysis**: Query stock prices, history, and fundamentals
2. **Technical Indicators**: RSI, MACD, Moving Averages, Bollinger Bands
3. **News Retrieval**: Latest news for specific stocks
4. **Macro Data**: Major indices, commodities, treasury yields

## Example Queries

Try these in the Streamlit interface:
- "Analyze AAPL stock"
- "What is the latest news on Tesla?"
- "Show me the RSI for Microsoft"
- "Compare Apple and Google fundamentals"

## Troubleshooting

- **403 Forbidden**: Check that your `NVIDIA_API_KEY` is valid
- **Import Errors**: Ensure virtual environment is activated
- **SSL Warnings**: Already mitigated with `urllib3<2.0`
