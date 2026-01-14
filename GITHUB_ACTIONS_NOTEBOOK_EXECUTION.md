# Running Notebooks in GitHub Actions

This repository includes workflows to execute the Jupyter notebook in GitHub Actions.

## Available Workflows

### 1. `run-notebook-execute.yml` (Recommended)

Uses `jupyter nbconvert --execute` to run the notebook.

**Features:**
- Executes all cells sequentially
- Saves executed notebook with outputs
- Handles errors gracefully (continues on errors)
- Uploads executed notebook and outputs as artifacts

**Trigger:**
- Manual (workflow_dispatch)
- Scheduled (daily at 2 AM UTC)
- On push to main (when notebook files change)

**Usage:**
1. Go to Actions tab
2. Select "Execute MBTI Research Notebook"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

### 2. `run-notebook-papermill.yml`

Uses `papermill` for notebook execution (more advanced).

**Features:**
- Parameterized execution
- Better logging
- Can inject parameters
- More control over execution

**Trigger:**
- Manual only (workflow_dispatch)
- Can specify parameters

### 3. `run-notebook-dotenvx.yml`

Uses dotenvx for encrypted secret management (see DOTENVX_SETUP.md).

## Setup Requirements

### GitHub Secrets

Add these secrets to your repository:
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `SUPABASE_URL` or `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase URL
- `SUPABASE_ANON_KEY` or `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon key

**OR** use dotenvx (see DOTENVX_SETUP.md) - only needs `DOTENVX_KEY`

### Limitations

⚠️ **Colab-specific features won't work:**
- `google.colab.userdata` (Secrets Manager) - Falls back to environment variables
- `google.colab.files` (file downloads) - Not available
- Interactive inputs (`getpass`, `input`) - Must use environment variables

✅ **What works:**
- All Python code execution
- Data analysis and visualization
- File generation (PNG, CSV, JSON, MD)
- API calls (OpenRouter, Supabase)

## Viewing Results

After execution:
1. Go to Actions tab
2. Click on the completed workflow run
3. Scroll down to "Artifacts"
4. Download:
   - `executed-notebook` - Notebook with all outputs
   - `notebook-outputs` - Generated files (graphs, tables, etc.)

## Troubleshooting

**"ModuleNotFoundError: No module named 'google.colab'"**
- Expected - this is normal in GitHub Actions
- The notebook falls back to environment variables

**"KeyError: OPENROUTER_API_KEY"**
- Make sure secrets are set in repository settings
- Check secret names match exactly (case-sensitive)

**"Execution timeout"**
- Notebook execution is limited to 600 seconds (10 minutes)
- For longer runs, consider breaking into smaller notebooks

**"No outputs generated"**
- Check if results files exist (mbti_voice_results.csv)
- Analysis cells require results data to generate outputs

## Alternative: Use Colab Directly

For full functionality (including Colab-specific features), use Google Colab:
https://colab.research.google.com/github/InquiryInstitute/mbti-faculty-voice-research/blob/main/MBTI_Research_Colab.ipynb

