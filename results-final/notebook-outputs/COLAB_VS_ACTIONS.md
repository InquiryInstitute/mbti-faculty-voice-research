# Colab vs GitHub Actions - Secret Management

## Two Different Execution Environments

This repository supports **two different ways** to run the notebook:

### 1. Google Colab (Interactive)

**For:** Interactive use, development, exploration

**Secret Management:**
- Uses `getpass()` and `input()` for secure input
- User enters API keys when running cells
- Keys are stored in Colab's runtime (session-only)
- Native Colab experience

**How it works:**
```python
# Cell 4 in notebook
OPENROUTER_API_KEY = getpass("Enter OpenRouter API Key (sk-or-v1-...): ")
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY
```

**✅ dotenvx:** NOT used in Colab (not compatible)

---

### 2. GitHub Actions (Automated)

**For:** Automated execution, CI/CD, scheduled runs

**Secret Management:**
- Uses **dotenvx** to decrypt `.env.encrypted`
- Only ONE secret needed in GitHub: `DOTENVX_KEY`
- All API keys stored in encrypted `.env.encrypted` file
- No user interaction needed

**How it works:**
```yaml
# Workflow uses dotenvx action
- name: Load encrypted .env file
  uses: dotenvx/action@v4
  with:
    env_file: .env.encrypted
    dotenvx_key: ${{ secrets.DOTENVX_KEY }}
```

**✅ dotenvx:** Used here (perfect for CI/CD)

---

## Summary

| Feature | Google Colab | GitHub Actions |
|---------|-------------|----------------|
| Secret Management | `getpass()` / `input()` | dotenvx |
| User Interaction | Required | Not needed |
| dotenvx Support | ❌ No | ✅ Yes |
| Automated | ❌ No | ✅ Yes |
| Best For | Development | Production/CI |

## Recommendation

- **Use Colab** for interactive work, testing, exploration
- **Use GitHub Actions** for automated runs, scheduled execution
- **Use dotenvx** for GitHub Actions workflows (automated secret management)

Both execution paths are independent and work well for their intended use cases!
