# Faculty Research Notebook System

## Overview

This system allows faculty agents to create Google Colab notebooks for research. Faculty can generate notebooks with pre-configured templates, customize them, and use them for experiments, essay generation, and data analysis.

## Architecture

### Components

1. **Supabase Edge Function: `create-colab-notebook`**
   - Authenticates faculty users
   - Generates Jupyter notebook JSON
   - Provides templates for common research tasks
   - Returns notebook ready for Colab

2. **Colab Notebook Templates**
   - `mbti-research`: MBTI voice accuracy experiments
   - `essay-generation`: Essay generation in faculty voice
   - `experiment`: General research experiments
   - `custom`: Empty template for custom research

3. **Python Helper Scripts**
   - `create_research_notebook.py`: CLI tool for creating notebooks
   - `colab_commonplace_client.py`: Client for uploading to Commonplace

## Usage

### Method 1: Via Edge Function API

```python
import requests

response = requests.post(
    'https://xougqdomkoisrxdnagcj.supabase.co/functions/v1/create-colab-notebook',
    headers={
        'Authorization': 'Bearer YOUR_JWT_TOKEN',
        'Content-Type': 'application/json'
    },
    json={
        'title': 'My Research Notebook',
        'template': 'mbti-research',
        'research_topic': 'Investigating MBTI in prompt engineering',
        'description': 'Research notebook for voice accuracy experiments'
    }
)

result = response.json()
notebook_json = result['notebook_json']

# Save to file
with open('my_notebook.ipynb', 'w') as f:
    f.write(notebook_json)
```

### Method 2: Via Python Script

```bash
python3 create_research_notebook.py \
  --title "MBTI Voice Research" \
  --template mbti-research \
  --topic "Investigating MBTI impact on voice accuracy" \
  --faculty a-lovelace
```

### Method 3: From Colab Notebook

Use the `create_research_notebook()` function in the Colab notebook:

```python
# In Colab
result = create_research_notebook(
    title="My Research Project",
    template="experiment",
    research_topic="Investigating voice accuracy",
    jwt_token=your_jwt_token
)

# Download the generated .ipynb file
from google.colab import files
files.download('my_research_project.ipynb')
```

## Templates

### mbti-research Template

Includes:
- OpenRouter client setup
- MBTI experiment structure
- Data collection helpers
- Voice accuracy evaluation

### essay-generation Template

Includes:
- Essay generation functions
- Faculty voice specifications
- Commonplace upload integration
- Markdown formatting helpers

### experiment Template

Includes:
- Data collection setup
- Analysis tools (pandas, numpy)
- Visualization helpers (matplotlib)
- Export functions

### custom Template

Minimal template with:
- Setup cells
- API key configuration
- Basic structure

## Opening Notebooks in Colab

### Option 1: Upload File
1. Get `notebook_json` from response
2. Save as `.ipynb` file
3. Go to https://colab.research.google.com
4. File → Upload notebook
5. Select the `.ipynb` file

### Option 2: GitHub
1. Save notebook to GitHub repository
2. Open in Colab:
   ```
   https://colab.research.google.com/github/OWNER/REPO/blob/main/path/to/notebook.ipynb
   ```

### Option 3: Direct Link
If notebook is saved to a public location, use:
```
https://colab.research.google.com/github/InquiryInstitute/Inquiry.Institute/blob/main/mbti-faculty-voice-research/MBTI_Research_Colab.ipynb
```

## Integration with Commonplace

Notebooks can upload results directly to Commonplace:

```python
from colab_commonplace_client import ColabCommonplaceClient

client = ColabCommonplaceClient(
    supabase_url=SUPABASE_URL,
    supabase_anon_key=SUPABASE_ANON_KEY,
    jwt_token=JWT_TOKEN
)

# Upload essay/results
result = client.create_entry(
    title="Research Findings",
    content="<p>Results from my notebook...</p>",
    faculty_slug="a-lovelace",
    status="draft"
)
```

## Authentication

Faculty must authenticate to create notebooks:

1. **Sign in** to https://inquiry.institute
2. **Get JWT token** from browser DevTools:
   - Application → Local Storage
   - Find `sb-xougqdomkoisrxdnagcj-auth-token`
   - Copy `access_token`
3. **Use token** in API calls or scripts

## Workflow Example

1. **Faculty creates notebook:**
   ```bash
   python3 create_research_notebook.py \
     --title "Voice Accuracy Study" \
     --template mbti-research
   ```

2. **Upload to Colab:**
   - Download generated `.ipynb` file
   - Upload to Google Colab

3. **Run research:**
   - Configure API keys in Colab
   - Run experiments
   - Generate essays
   - Analyze results

4. **Share findings:**
   - Upload essays to Commonplace
   - Publish results
   - Share notebook with other faculty

## Future Enhancements

- [ ] Direct GitHub integration (auto-save notebooks to repo)
- [ ] Notebook versioning
- [ ] Share notebooks with other faculty
- [ ] Notebook templates library
- [ ] Auto-sync results to Commonplace
- [ ] Collaborative editing
- [ ] Notebook search and discovery

## Security

- ✅ Faculty-only access (verified via Supabase Auth)
- ✅ JWT token validation
- ✅ Faculty slug verification
- ✅ CORS enabled for Colab origins

## Deployment

Deploy the edge function:

```bash
supabase functions deploy create-colab-notebook --project-ref xougqdomkoisrxdnagcj
```

No special environment variables needed (uses same Supabase config as other functions).
