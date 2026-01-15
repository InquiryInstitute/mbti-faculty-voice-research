# Google Colab Setup Guide

## Quick Start

1. **Open the notebook in Colab:**
   - Upload `MBTI_Research_Colab.ipynb` to Google Colab
   - Or create a new notebook and copy the cells

2. **Run the cells in order:**
   - Install dependencies
   - Configure API keys
   - Generate essay
   - Upload to Commonplace (optional)

## API Keys Needed

### Required
- **OpenRouter API Key** (`sk-or-v1-...`)
  - Get from: https://openrouter.ai/keys
  - Used for: Essay generation

### Optional (for uploading)
- **Supabase URL**: `https://xougqdomkoisrxdnagcj.supabase.co`
- **Supabase Anon Key**: Get from Supabase dashboard
- **a.lovelace JWT Token**: Get from browser after signing in to inquiry.institute

## Features

The Colab notebook includes:

1. **Essay Generation**
   - Generates Ada Lovelace's essay on MBTI research
   - Uses OpenRouter API
   - Outputs formatted markdown

2. **Upload to Commonplace**
   - Uploads essay via Supabase Edge Function
   - Requires a.lovelace JWT token
   - Sets proper metadata (topics, college, entry type)

3. **Download**
   - Save essay as markdown file
   - Download to local machine

## Security Notes

- API keys are entered via `getpass()` (hidden input)
- Keys are stored in Colab session only (not saved)
- For production, consider using Colab Secrets Manager

## Troubleshooting

**"Module not found" errors:**
- Run the dependency installation cell first

**"API key invalid" errors:**
- Check that you copied the full key
- For OpenRouter, key should start with `sk-or-v1-`

**"Unauthorized" when uploading:**
- Make sure JWT token is valid and not expired
- Token must be from a.lovelace user session
- User must have faculty role in Supabase

## Next Steps

After generating the essay:
1. Review the content
2. Upload to Commonplace (or download and upload manually)
3. Publish through PublishPress workflow in WordPress
