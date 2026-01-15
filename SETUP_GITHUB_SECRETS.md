# Setting Up GitHub Secrets

This repository uses GitHub Actions to generate PDFs and publish research papers to Commonplace (Directus). Here's how to set up the required secrets:

## Required Secrets for PDF Generation and Publishing

### 1. **DIRECTUS_URL** (required for publishing)
   - Directus instance URL
   - Default: `https://commonplace-directus-652016456291.us-central1.run.app`
   - Used to connect to the Directus API for creating/updating works

### 2. **DIRECTUS_EMAIL** (required for publishing)
   - Email address for Directus authentication
   - Must be a user account with permission to create/update works in Directus
   - Typically: `custodian@inquiry.institute` or your faculty email

### 3. **DIRECTUS_PASSWORD** (required for publishing)
   - Password for the Directus user account
   - Used to authenticate with Directus API

### Optional: Legacy Secrets (for backward compatibility)

The script also supports these environment variable names:
- `COMMONPLACE_AUTH_EMAIL` (maps to `DIRECTUS_EMAIL`)
- `COMMONPLACE_AUTH_PASSWORD` (maps to `DIRECTUS_PASSWORD`)

## Additional Secrets (for other workflows)

1. **OPENROUTER_API_KEY** (optional)
   - Your OpenRouter API key (starts with `sk-or-v1-...`)
   - Used for running experiments and generating essays

## How to Add Secrets

### Via GitHub Web UI:

1. Go to your repository: https://github.com/InquiryInstitute/mbti-faculty-voice-research
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret one by one:

   **Secret 1: DIRECTUS_URL**
   - Name: `DIRECTUS_URL`
   - Value: `https://commonplace-directus-652016456291.us-central1.run.app`
   - Click **Add secret**

   **Secret 2: DIRECTUS_EMAIL**
   - Name: `DIRECTUS_EMAIL`
   - Value: Your Directus user email (e.g., `custodian@inquiry.institute`)
   - Click **Add secret**

   **Secret 3: DIRECTUS_PASSWORD**
   - Name: `DIRECTUS_PASSWORD`
   - Value: Your Directus user password
   - Click **Add secret**

   **Secret 4: OPENROUTER_API_KEY** (optional)
   - Name: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key (starts with `sk-or-v1-...`)
   - Click **Add secret**

### Via GitHub CLI:

```bash
# Set Directus URL
gh secret set DIRECTUS_URL --repo InquiryInstitute/mbti-faculty-voice-research --body "https://commonplace-directus-652016456291.us-central1.run.app"

# Set Directus credentials
gh secret set DIRECTUS_EMAIL --repo InquiryInstitute/mbti-faculty-voice-research
gh secret set DIRECTUS_PASSWORD --repo InquiryInstitute/mbti-faculty-voice-research

# Set OpenRouter API key (optional)
gh secret set OPENROUTER_API_KEY --repo InquiryInstitute/mbti-faculty-voice-research
```

**Note:** When using `gh secret set` without `--body`, it will prompt you to enter the value securely.

## After Setting Secrets

Once secrets are configured, you can:

1. **Trigger the publish workflow manually:**
   - Go to **Actions** tab
   - Select "Generate PDF and Update Commonplace Article" workflow
   - Click **Run workflow** → **Run workflow**

2. **Or push changes to RESEARCH_PAPER.md** to trigger automatically:
   ```bash
   git add RESEARCH_PAPER.md
   git commit -m "Update research paper"
   git push origin main
   ```

3. **The workflow will:**
   - Generate a PDF from the markdown file
   - Create or update the work in Directus Commonplace
   - Output the URL to the published article

## Verify Secrets Are Set

```bash
# List secrets (names only, not values)
gh secret list --repo InquiryInstitute/mbti-faculty-voice-research
```

## Notes

- Secrets are encrypted and only accessible to GitHub Actions
- Secrets are not visible in workflow logs
- You can update secrets anytime without changing the workflow file
