# Colab Secrets Manager Setup

Google Colab has a built-in **Secrets Manager** that allows you to store API keys securely and access them automatically in your notebooks.

## Benefits

✅ **Set once, use forever** - Secrets persist across sessions  
✅ **Secure** - Encrypted storage  
✅ **No manual entry** - Automatic loading  
✅ **Easy to manage** - UI-based secret management  

## Setup Instructions

### Step 1: Open Secrets Manager

1. In your Colab notebook, look at the **left sidebar**
2. Find the **🔑 (key/lock) icon** - this is the Secrets Manager
3. Click it to open

### Step 2: Add Secrets

Click **"+ Add secret"** and add these three secrets:

**Secret 1:**
- Name: `OPENROUTER_API_KEY`
- Value: Your OpenRouter API key (starts with `sk-or-v1-...`)

**Secret 2:**
- Name: `SUPABASE_URL`
- Value: Your Supabase URL (e.g., `https://xougqdomkoisrxdnagcj.supabase.co`)

**Secret 3:**
- Name: `SUPABASE_ANON_KEY`
- Value: Your Supabase anon key

### Step 3: Run the Notebook

Once secrets are added, the notebook will automatically load them when you run cell 4!

No more manual entry needed. 🎉

## How It Works

The notebook uses this code:

```python
from google.colab import userdata

# Load secrets automatically
OPENROUTER_API_KEY = userdata.get('OPENROUTER_API_KEY')
SUPABASE_URL = userdata.get('SUPABASE_URL')
SUPABASE_ANON_KEY = userdata.get('SUPABASE_ANON_KEY')
```

If secrets aren't set, it falls back to manual input prompts.

## Managing Secrets

- **View secrets**: Click 🔑 icon → See list of saved secrets
- **Update secret**: Click 🔑 icon → Click secret name → Update value
- **Delete secret**: Click 🔑 icon → Click secret name → Delete

## Security Notes

- ✅ Secrets are encrypted and stored securely
- ✅ Only accessible in your Colab sessions
- ✅ Not visible in notebook output
- ✅ Persist across notebook sessions

## Troubleshooting

**"KeyError: OPENROUTER_API_KEY"**
- Make sure you've added the secret via the 🔑 icon
- Check the secret name matches exactly (case-sensitive)

**"ModuleNotFoundError: No module named 'google.colab'"**
- This means you're not running in Colab
- The notebook will fall back to manual input

