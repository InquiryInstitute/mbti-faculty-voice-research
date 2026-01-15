# Remote Notebook Execution

This repository supports remote execution of the MBTI Research notebook through GitHub Actions.

## Setup

### 1. GitHub Secrets

Add the following secrets to your GitHub repository:
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anon key

To add secrets:
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret

### 2. Trigger Execution

#### Manual Execution
1. Go to the "Actions" tab in GitHub
2. Select "Execute MBTI Research Notebook" workflow
3. Click "Run workflow"
4. Select branch (usually `main`)
5. Click "Run workflow"

#### Automatic Execution
- The workflow runs automatically when:
  - Notebook files are pushed to `main` branch
  - Scheduled daily at 2 AM UTC (optional - edit workflow to enable/disable)

### 3. View Results

After execution:
1. Go to the "Actions" tab
2. Click on the completed workflow run
3. Download artifacts to see generated files (graphs, tables, etc.)

## Limitations

⚠️ **Note**: Full notebook execution in GitHub Actions has limitations:
- Colab-specific features (`google.colab.files`) won't work
- Interactive inputs (`getpass`, `input`) won't work
- The workflow focuses on analysis of existing results

For full functionality, use Google Colab:
https://colab.research.google.com/github/InquiryInstitute/mbti-faculty-voice-research/blob/main/MBTI_Research_Colab.ipynb

## Alternative: Google Cloud Run

For more advanced remote execution, you can deploy the notebook code as a Cloud Run service:

1. Convert notebook to Python script
2. Create a Dockerfile
3. Deploy to Cloud Run
4. Trigger via HTTP requests or Cloud Scheduler

See `.github/workflows/run-notebook.yml` for the GitHub Actions implementation.
