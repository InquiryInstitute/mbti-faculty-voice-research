# Creating Research Notebooks for Faculty

## Overview

Faculty members can create Google Colab notebooks for research through the `create-colab-notebook` Supabase Edge Function.

## Quick Start

### From Python Script

```bash
python3 create_research_notebook.py \
  --title "My Research Notebook" \
  --template mbti-research \
  --topic "Investigating MBTI in prompt engineering" \
  --faculty a-lovelace
```

### From API Call

```bash
curl -X POST 'https://xougqdomkoisrxdnagcj.supabase.co/functions/v1/create-colab-notebook' \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "MBTI Voice Research",
    "template": "mbti-research",
    "research_topic": "Investigating MBTI impact on voice accuracy"
  }'
```

## Available Templates

### mbti-research
Pre-configured for MBTI voice accuracy research:
- OpenRouter client setup
- MBTI experiment structure
- Data collection helpers

### essay-generation
Template for generating essays:
- Essay generation functions
- Voice specification helpers
- Commonplace upload integration

### experiment
General experiment template:
- Data collection setup
- Analysis tools
- Visualization helpers

### custom
Empty template - add your own cells

## Using the Notebook

After creating a notebook:

1. **Get the notebook JSON** from the response
2. **Save as .ipynb file** (the script does this automatically)
3. **Upload to Google Colab**:
   - Go to https://colab.research.google.com
   - File → Upload notebook
   - Select the .ipynb file

4. **Or open from GitHub**:
   - Save notebook to GitHub repository
   - Open: `https://colab.research.google.com/github/OWNER/REPO/blob/main/path/to/notebook.ipynb`

## Authentication

You need to authenticate as a faculty member:

**Option 1: JWT Token**
```bash
export LOVELACE_JWT_TOKEN="your-token-here"
```

**Option 2: Email/Password**
```bash
export LOVELACE_EMAIL="a.lovelace@inquiry.institute"
export LOVELACE_PASSWORD="your-password"
```

## Example Workflow

1. **Create notebook:**
   ```bash
   python3 create_research_notebook.py \
     --title "MBTI Voice Accuracy Study" \
     --template mbti-research \
     --topic "Investigating MBTI impact on faculty agent voice accuracy"
   ```

2. **Upload to Colab:**
   - Open https://colab.research.google.com
   - File → Upload notebook
   - Select the generated `.ipynb` file

3. **Start researching:**
   - Configure API keys in Colab
   - Run experiments
   - Generate essays
   - Upload results to Commonplace

## Integration with Colab

The generated notebooks include:
- ✅ Setup cells for dependencies
- ✅ API key configuration
- ✅ Template-specific code
- ✅ Helper functions
- ✅ Integration with Commonplace upload

## Next Steps

After creating a notebook, you can:
- Customize it in Colab
- Add your own research code
- Share with other faculty
- Save results to Commonplace
- Publish findings
