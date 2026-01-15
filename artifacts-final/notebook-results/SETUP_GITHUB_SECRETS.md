# Setting Up GitHub Secrets for Automated Notebook Execution

The workflow needs API keys to run the experiment. Here's how to set them up:

## Required Secrets

1. **OPENROUTER_API_KEY** (required)
   - Your OpenRouter API key (starts with `sk-or-v1-...`)
   - Used for running the experiment and generating the essay

2. **SUPABASE_URL** (optional)
   - Your Supabase project URL
   - Only needed if uploading to Commonplace

3. **SUPABASE_ANON_KEY** (optional)
   - Your Supabase anon key
   - Only needed if uploading to Commonplace

## How to Add Secrets

### Via GitHub Web UI:

1. Go to your repository: https://github.com/InquiryInstitute/mbti-faculty-voice-research
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:
   - Name: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key
   - Click **Add secret**
5. Repeat for `SUPABASE_URL` and `SUPABASE_ANON_KEY` if needed

### Via GitHub CLI:

```bash
# Set OpenRouter API key
gh secret set OPENROUTER_API_KEY --repo InquiryInstitute/mbti-faculty-voice-research

# Set Supabase secrets (optional)
gh secret set SUPABASE_URL --repo InquiryInstitute/mbti-faculty-voice-research
gh secret set SUPABASE_ANON_KEY --repo InquiryInstitute/mbti-faculty-voice-research
```

## After Setting Secrets

Once secrets are configured, you can:

1. **Trigger workflow manually:**
   ```bash
   gh workflow run "Execute MBTI Research Notebook"
   ```

2. **Or push changes** to trigger automatically (if workflow is set to run on push)

3. **Or wait for scheduled run** (daily at 2 AM UTC)

## Verify Secrets Are Set

```bash
# List secrets (names only, not values)
gh secret list --repo InquiryInstitute/mbti-faculty-voice-research
```

## Notes

- Secrets are encrypted and only accessible to GitHub Actions
- Secrets are not visible in workflow logs
- You can update secrets anytime without changing the workflow file
