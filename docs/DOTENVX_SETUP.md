# Using dotenvx for Secret Management

[dotenvx](https://github.com/dotenvx/dotenvx) allows you to encrypt `.env` files and commit them to git, then decrypt them in workflows.

## Benefits

✅ **No manual GitHub Secrets management**  
✅ **Share secrets between repositories**  
✅ **Version-controlled encrypted secrets**  
✅ **Easy CI/CD integration**

## Setup

### 1. Install dotenvx

```bash
# Using Homebrew
brew install dotenvx/tap/dotenvx

# Or using npm
npm install -g @dotenvx/dotenvx
```

### 2. Create .env file (if not exists)

```bash
# Copy from parent repo or create new
cat > .env << EOL
OPENROUTER_API_KEY=your_key_here
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key_here
EOL
```

### 3. Encrypt .env file

```bash
# Encrypt .env to .env.encrypted
dotenvx encrypt

# Or specify custom output
dotenvx encrypt .env -o .env.encrypted
```

This will:
- Encrypt your `.env` file to `.env.encrypted`
- Generate a `DOTENVX_KEY` (keep this secret!)
- You can commit `.env.encrypted` to git (it's encrypted)

### 4. Add DOTENVX_KEY to GitHub Secrets

Only ONE secret needed in GitHub:

1. Go to: https://github.com/InquiryInstitute/mbti-faculty-voice-research/settings/secrets/actions
2. Click "New repository secret"
3. Name: `DOTENVX_KEY`
4. Value: The key from step 3 (starts with `dotenvx://...`)
5. Click "Add secret"

### 5. Update Workflow

The workflow `.github/workflows/run-notebook-dotenvx.yml` uses dotenvx action:

```yaml
- name: Load encrypted .env file
  uses: dotenvx/action@v4
  with:
    env_file: .env.encrypted
    dotenvx_key: ${{ secrets.DOTENVX_KEY }}
```

After this step, all environment variables from `.env.encrypted` are available!

## Usage

### Encrypt/Update Secrets

```bash
# Edit .env file
nano .env

# Re-encrypt
dotenvx encrypt

# Commit changes
git add .env.encrypted
git commit -m "Update secrets"
git push
```

### Share Secrets Between Repos

1. Copy `.env.encrypted` to another repo
2. Share the same `DOTENVX_KEY` (add to that repo's secrets)
3. Both repos can decrypt and use the same secrets

### Decrypt Locally

```bash
# Decrypt and load into environment
dotenvx decrypt .env.encrypted -o .env

# Or run command with decrypted env
dotenvx run -- python script.py
```

## Security

- ✅ `.env.encrypted` is safe to commit (it's encrypted)
- ✅ `.env` should be in `.gitignore` (never commit plain secrets!)
- ✅ Only `DOTENVX_KEY` needs to be in GitHub Secrets
- ✅ Same key can decrypt multiple `.env.encrypted` files

## Alternative: Get Keys from Parent Repo

If you want to copy keys from the parent `Inquiry.Institute` repository:

1. **Option 1: Use dotenvx in parent repo**
   - If parent repo uses dotenvx, copy `.env.encrypted` and `DOTENVX_KEY`
   
2. **Option 2: Export from parent repo**
   ```bash
   cd ../Inquiry.Institute
   # Get values (you'll need to look them up manually)
   # Then create .env in this repo
   ```

3. **Option 3: Use GitHub CLI** (limited - can't read values)
   ```bash
   # Can check what secrets exist, but can't read values
   gh secret list --repo InquiryInstitute/Inquiry.Institute
   ```

## Workflow Files

- `.github/workflows/run-notebook.yml` - Uses GitHub Secrets (manual setup)
- `.github/workflows/run-notebook-dotenvx.yml` - Uses dotenvx (automated)

Choose the workflow that fits your needs!

