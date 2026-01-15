# Setup Guide

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/InquiryInstitute/mbti-faculty-voice-research.git
cd mbti-faculty-voice-research
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

**Option A: Quick Setup (with provided OpenRouter key)**

```bash
./setup-env.sh
```

**Option B: Manual Setup**

Copy the example environment file:

```bash
cp env.example .env
```

Edit `.env` and add your API key:

**For OpenRouter (recommended):**
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Or for direct OpenAI:**
```bash
OPENAI_API_KEY=sk-your-key-here
```

Optionally set model preferences:

**For OpenRouter:**
```bash
OPENAI_MODEL=openai/gpt-4o
OPENAI_JUDGE_MODEL=openai/gpt-4o
```

**For direct OpenAI:**
```bash
OPENAI_MODEL=gpt-4o
OPENAI_JUDGE_MODEL=gpt-4o
```

### 5. Test Connection (Optional)

Verify your API setup works:

```bash
python test-connection.py
```

This will test the API connection and confirm everything is configured correctly.

### 6. Run the Experiment

```bash
python mbti_voice_eval.py
```

This will:
- Generate 480 trials (10 personae × 16 MBTI types × 3 prompts)
- Evaluate each response with an LLM judge
- Save results to `mbti_voice_results.csv` and `mbti_voice_results.jsonl`

**Note:** This will make 480+ API calls. Ensure you have sufficient API credits and rate limits configured.

### 7. View Results

After completion, view a summary:

```python
python -c "from mbti_voice_eval import summarize; summarize()"
```

Or analyze the CSV directly:

```python
import pandas as pd
df = pd.read_csv('mbti_voice_results.csv')
print(df.head())
```

## Customization

### Modify Test Prompts

Edit `DEFAULT_TEST_PROMPTS` in `mbti_voice_eval.py`:

```python
DEFAULT_TEST_PROMPTS = [
    "Your custom prompt here...",
    "Another prompt...",
]
```

### Adjust Personae

Modify the `PERSONAE` list in `mbti_voice_eval.py` to add or change faculty personae.

### Change Output Location

Pass custom paths to `run_experiment()`:

```python
run_experiment(
    out_jsonl="custom_results.jsonl",
    out_csv="custom_results.csv"
)
```

### Adjust Rate Limiting

Modify the `sleep_s` parameter:

```python
run_experiment(sleep_s=1.0)  # Wait 1 second between requests
```

## Troubleshooting

### API Errors

- **Rate limit exceeded:** Increase `sleep_s` in `run_experiment()`
- **Invalid API key:** Check `.env` file and ensure key is correct
- **Model not found:** Verify model name in environment variables

### JSON Parsing Errors

If the judge returns malformed JSON, the script will:
- Store the raw response in the `cues` field
- Set all scores to -1
- Continue with the next trial

Check the `rationales` field for `JUDGE_PARSE_ERROR` to identify problematic responses.

### Memory Issues

For large experiments, consider:
- Processing in batches
- Writing intermediate results
- Using a database instead of CSV/JSONL

## Next Steps

1. Review `ANALYSIS.md` for analysis guidance
2. Read `RESEARCH_PAPER.md` for theoretical context
3. Explore results in `mbti_voice_results.csv`

## Support

For questions or issues, please open an issue on GitHub or contact the Inquiry Institute.
