#!/bin/bash
# Quick setup script for OpenRouter API key

cat > .env << 'EOF'
# OpenRouter API Configuration
OPENROUTER_API_KEY=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

# Optional: Model Selection (OpenRouter format)
# OPENAI_MODEL=openai/gpt-4o
# OPENAI_JUDGE_MODEL=openai/gpt-4o
EOF

echo "✅ Created .env file with OpenRouter API key"
echo ""
echo "To customize models, edit .env and uncomment/modify:"
echo "  OPENAI_MODEL=openai/gpt-4o"
echo "  OPENAI_JUDGE_MODEL=openai/gpt-4o"
