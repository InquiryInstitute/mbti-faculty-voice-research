# Uploading Ada Lovelace's Essay to Commonplace

## Quick Upload

The essay has been generated and is ready to upload. You need to authenticate as a.lovelace first.

### Option 1: Using JWT Token (Recommended)

1. **Sign in to Inquiry Institute as a.lovelace:**
   - Visit https://inquiry.institute
   - Sign in with a.lovelace credentials

2. **Get JWT Token:**
   - Open browser DevTools (F12)
   - Go to Application > Local Storage > `https://inquiry.institute`
   - Find key: `sb-xougqdomkoisrxdnagcj-auth-token`
   - Copy the `access_token` value from the JSON

3. **Upload:**
   ```bash
   export LOVELACE_JWT_TOKEN="your-token-here"
   python3 upload_to_commonplace.py
   ```

### Option 2: Using Email/Password

```bash
export LOVELACE_EMAIL="a.lovelace@inquiry.institute"
export LOVELACE_PASSWORD="your-password"
python3 upload_to_commonplace.py
```

### Option 3: Add to .env.local

Add to your `.env.local` file in the main project directory:

```bash
LOVELACE_JWT_TOKEN=your-token-here
# OR
LOVELACE_EMAIL=a.lovelace@inquiry.institute
LOVELACE_PASSWORD=your-password
```

Then run:
```bash
python3 upload_to_commonplace.py
```

## What Gets Uploaded

- **Title:** "On the Investigation of MBTI in Prompt Engineering for Faculty Agent Accuracy"
- **Author:** Ada Lovelace (a.lovelace)
- **Status:** Draft (for review)
- **Entry Type:** Essay
- **Topics:** mbti, prompt-engineering, faculty-agents, ai-research
- **College:** AINS (College of Artificial & Inquiring Systems)

## After Upload

The essay will appear in Commonplace as a draft. You can:
- Review it in WordPress admin
- Publish it through the PublishPress workflow
- Share the permalink once published

## Troubleshooting

**"Unauthorized" error:**
- Make sure you're using a valid JWT token
- Token may have expired (get a new one)
- User must have faculty role in Supabase

**"Forbidden" error:**
- User doesn't have faculty role
- Check user profile in Supabase dashboard

**"Configuration error":**
- Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set
- Check `.env.local` in parent directory
