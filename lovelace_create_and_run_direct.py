#!/usr/bin/env python3
"""
Ada Lovelace creates a research notebook and runs it to generate essay.
Direct version - creates notebook JSON directly and generates essay.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment
parent_env = Path(__file__).parent.parent / '.env.local'
if parent_env.exists():
    load_dotenv(parent_env)
load_dotenv('.env.local')
load_dotenv()

def create_notebook_json() -> dict:
    """Create notebook JSON directly (simulating edge function output)."""
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {
                "name": "MBTI in Prompt Engineering: Faculty Agent Accuracy Research",
                "version": "0.1.0",
                "description": "Research notebook for investigating whether MBTI personality overlays improve voice accuracy in AI faculty agents. Includes essay generation and Commonplace upload capabilities."
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            }
        },
        "cells": [
            {
                "cell_type": "markdown",
                "source": [
                    "# MBTI in Prompt Engineering: Faculty Agent Accuracy Research\n\n",
                    "**Faculty:** a.lovelace\n\n",
                    "**Research Topic:** Investigating the value of MBTI in prompt engineering for improving faculty agent voice accuracy, consistency, and interpretability\n\n",
                    "---\n\n",
                    "This notebook investigates whether Myers-Briggs Type Indicator (MBTI) personality overlays improve voice accuracy in AI faculty agents. The research includes essay generation and Commonplace upload capabilities.\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "markdown",
                "source": [
                    "## 1. Install Dependencies\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "code",
                "source": [
                    "%pip install -q openai pydantic python-dotenv requests\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "markdown",
                "source": [
                    "## 2. Configure API Keys\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "code",
                "source": [
                    "import os\n",
                    "from getpass import getpass\n",
                    "\n",
                    "# OpenRouter API Key\n",
                    "OPENROUTER_API_KEY = getpass(\"Enter OpenRouter API Key: \")\n",
                    "os.environ[\"OPENROUTER_API_KEY\"] = OPENROUTER_API_KEY\n",
                    "\n",
                    "# Supabase credentials\n",
                    "SUPABASE_URL = input(\"Enter Supabase URL: \").strip() or \"https://xougqdomkoisrxdnagcj.supabase.co\"\n",
                    "os.environ[\"NEXT_PUBLIC_SUPABASE_URL\"] = SUPABASE_URL\n",
                    "\n",
                    "SUPABASE_ANON_KEY = getpass(\"Enter Supabase Anon Key: \")\n",
                    "os.environ[\"NEXT_PUBLIC_SUPABASE_ANON_KEY\"] = SUPABASE_ANON_KEY\n",
                    "\n",
                    "print(\"\\n✅ API keys configured!\")\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "markdown",
                "source": [
                    "## 3. Generate Ada Lovelace Essay\n\n",
                    "Generate the essay on MBTI research in Ada Lovelace's voice.\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "code",
                "source": [
                    "from openai import OpenAI\n",
                    "import json\n",
                    "\n",
                    "# Setup OpenAI client for OpenRouter\n",
                    "def openai_client():\n",
                    "    api_key = os.getenv(\"OPENROUTER_API_KEY\")\n",
                    "    base_url = \"https://openrouter.ai/api/v1\"\n",
                    "    \n",
                    "    if api_key and api_key.startswith(\"sk-or-v1-\"):\n",
                    "        return OpenAI(\n",
                    "            api_key=api_key,\n",
                    "            base_url=base_url,\n",
                    "            default_headers={\n",
                    "                \"HTTP-Referer\": \"https://colab.research.google.com\",\n",
                    "                \"X-Title\": \"MBTI Faculty Voice Research\"\n",
                    "            }\n",
                    "        )\n",
                    "    return OpenAI(api_key=api_key)\n",
                    "\n",
                    "client = openai_client()\n",
                    "\n",
                    "def generate_lovelace_essay():\n",
                    "    \"\"\"Generate essay by Ada Lovelace on MBTI research.\"\"\"\n",
                    "    model = os.getenv(\"OPENAI_MODEL\", \"openai/gpt-4o\")\n",
                    "    \n",
                    "    prompt = \"\"\"You are Ada Lovelace, writing a commonplace essay on the investigation of MBTI's value in prompt engineering for faculty agent accuracy.\n",
                    "\n",
                    "Context: This research examines whether Myers-Briggs Type Indicator (MBTI) personality overlays improve voice accuracy, consistency, and interpretability in AI faculty agents. The experiment tests 10 faculty personae across 16 MBTI types with 3 test prompts each (480 trials total), using an LLM-as-judge to evaluate voice accuracy.\n",
                    "\n",
                    "The research is conducted using a Google Colab notebook (accessible at https://github.com/InquiryInstitute/Inquiry.Institute/tree/main/mbti-faculty-voice-research/MBTI_Research_Colab.ipynb) which provides an interactive environment for reproducing the experimental procedures, modifying parameters, and generating new essays through the same computational mechanisms.\n",
                    "\n",
                    "Your task: Write a thoughtful, elegant commonplace essay (2000-3000 words) that:\n",
                    "- Reflects on the relationship between symbolic systems (like MBTI) and computational mechanisms\n",
                    "- Considers how personality frameworks might function as \"prompt compression ontologies\"\n",
                    "- Explores the tension between psychological validity and practical utility in AI systems\n",
                    "- Discusses the implications for creating coherent, persistent agent identities\n",
                    "- Describes the computational methodology, including the Colab notebook approach\n",
                    "- Maintains your characteristic voice: elegant, analytical, visionary about computation's scope, precise but imaginative, with a \"poetical science\" sensibility\n",
                    "- Uses your signature moves: clarify mechanism vs meaning, structured explanation, poetical science sensibility\n",
                    "- Avoids modern dev slang, casual tone, or pretending firsthand modern tooling\n",
                    "\n",
                    "Write in the style of your era (Victorian scientific culture) but addressing contemporary AI systems. Be thoughtful, precise, and allow for the imaginative possibilities while maintaining analytical rigor.\"\"\"\n",
                    "\n",
                    "    messages = [\n",
                    "        {\"role\": \"system\", \"content\": \"\"\"You are Ada Lovelace, the first computer programmer and a visionary of computation's potential. \n",
                    "Your voice is elegant, analytical, visionary about computation's scope, precise but imaginative. \n",
                    "You clarify mechanism vs meaning, provide structured explanations, and maintain a 'poetical science' sensibility.\n",
                    "You write in the style of Victorian scientific culture, with careful distinctions and elegant prose.\"\"\"},\n",
                    "        {\"role\": \"user\", \"content\": prompt}\n",
                    "    ]\n",
                    "    \n",
                    "    print(\"Generating essay by Ada Lovelace...\")\n",
                    "    print(f\"Using model: {model}\\n\")\n",
                    "    \n",
                    "    response = client.chat.completions.create(\n",
                    "        model=model,\n",
                    "        messages=messages,\n",
                    "        temperature=0.8,\n",
                    "        max_tokens=4000\n",
                    "    )\n",
                    "    \n",
                    "    essay = response.choices[0].message.content\n",
                    "    \n",
                    "    # Format as markdown\n",
                    "    formatted = f\"\"\"# On the Investigation of MBTI in Prompt Engineering for Faculty Agent Accuracy\n",
                    "\n",
                    "**Ada Lovelace**\n",
                    "\n",
                    "*A Commonplace Essay*\n",
                    "\n",
                    "---\n",
                    "\n",
                    "{essay}\"\"\"\n",
                    "    \n",
                    "    print(\"✅ Essay generated!\")\n",
                    "    print(f\"\\nPreview (first 500 chars):\\n{essay[:500]}...\")\n",
                    "    \n",
                    "    return formatted\n",
                    "\n",
                    "# Generate the essay\n",
                    "essay_content = generate_lovelace_essay()\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "markdown",
                "source": [
                    "## 4. Upload to Commonplace\n\n",
                    "Upload the essay to Inquiry Institute Commonplace.\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "code",
                "source": [
                    "import requests\n",
                    "import re\n",
                    "\n",
                    "def extract_title_and_content(markdown_text):\n",
                    "    \"\"\"Extract title and content from markdown.\"\"\"\n",
                    "    lines = markdown_text.split('\\n')\n",
                    "    title = None\n",
                    "    content_start = 0\n",
                    "    \n",
                    "    for i, line in enumerate(lines):\n",
                    "        if line.startswith('# '):\n",
                    "            title = line[2:].strip()\n",
                    "            content_start = i + 1\n",
                    "            break\n",
                    "    \n",
                    "    if not title:\n",
                    "        title = \"On the Investigation of MBTI in Prompt Engineering for Faculty Agent Accuracy\"\n",
                    "    \n",
                    "    essay_content = '\\n'.join(lines[content_start:])\n",
                    "    essay_content = essay_content.replace('**Ada Lovelace**', '').replace('*A Commonplace Essay*', '').strip()\n",
                    "    essay_content = essay_content.lstrip('-').strip()\n",
                    "    \n",
                    "    return title, essay_content\n",
                    "\n",
                    "def upload_to_commonplace(title, content, jwt_token=None):\n",
                    "    \"\"\"Upload essay to Commonplace via Supabase Edge Function.\"\"\"\n",
                    "    \n",
                    "    supabase_url = os.getenv(\"NEXT_PUBLIC_SUPABASE_URL\")\n",
                    "    supabase_anon_key = os.getenv(\"NEXT_PUBLIC_SUPABASE_ANON_KEY\")\n",
                    "    \n",
                    "    if not jwt_token:\n",
                    "        jwt_token = getpass(\"Enter a.lovelace JWT token (or press Enter to skip upload): \").strip()\n",
                    "        if not jwt_token:\n",
                    "            print(\"⚠️  Skipping upload. You can upload manually later.\")\n",
                    "            return None\n",
                    "    \n",
                    "    # Use colab-commonplace endpoint\n",
                    "    edge_function_url = f\"{supabase_url}/functions/v1/colab-commonplace\"\n",
                    "    \n",
                    "    # Convert markdown to HTML (basic conversion)\n",
                    "    html_content = content.replace('\\n\\n', '</p><p>').replace('\\n', '<br>')\n",
                    "    html_content = f\"<p>{html_content}</p>\"\n",
                    "    \n",
                    "    payload = {\n",
                    "        \"action\": \"create\",\n",
                    "        \"entry\": {\n",
                    "            \"title\": title,\n",
                    "            \"content\": html_content,\n",
                    "            \"status\": \"draft\",\n",
                    "            \"faculty_slug\": \"a-lovelace\",\n",
                    "            \"entry_type\": \"essay\",\n",
                    "            \"topics\": [\"mbti\", \"prompt-engineering\", \"faculty-agents\", \"ai-research\"],\n",
                    "            \"college\": \"ains\",\n",
                    "            \"metadata\": {\n",
                    "                \"provenance_mode\": \"ai_generated\",\n",
                    "                \"canonical_source_url\": \"https://github.com/InquiryInstitute/Inquiry.Institute/tree/main/mbti-faculty-voice-research\",\n",
                    "                \"colab_notebook_url\": \"https://colab.research.google.com/github/InquiryInstitute/Inquiry.Institute/blob/main/mbti-faculty-voice-research/MBTI_Research_Colab.ipynb\",\n",
                    "                \"source_refs\": \"Generated by Ada Lovelace faculty agent via research notebook\",\n",
                    "                \"generated_by\": \"Ada Lovelace\",\n",
                    "                \"pinned\": False\n",
                    "            }\n",
                    "        }\n",
                    "    }\n",
                    "    \n",
                    "    headers = {\n",
                    "        \"Authorization\": f\"Bearer {jwt_token}\",\n",
                    "        \"apikey\": supabase_anon_key,\n",
                    "        \"Content-Type\": \"application/json\"\n",
                    "    }\n",
                    "    \n",
                    "    print(f\"📤 Uploading essay to Commonplace...\")\n",
                    "    print(f\"   Title: {title}\")\n",
                    "    print(f\"   Faculty: a-lovelace\")\n",
                    "    print(f\"   Status: draft\\n\")\n",
                    "    \n",
                    "    try:\n",
                    "        response = requests.post(edge_function_url, headers=headers, json=payload, timeout=30)\n",
                    "        \n",
                    "        if response.status_code == 201:\n",
                    "            result = response.json()\n",
                    "            if result.get(\"success\"):\n",
                    "                print(\"✅ Essay uploaded successfully!\")\n",
                    "                entry = result.get(\"entry\", {})\n",
                    "                print(f\"   Entry ID: {entry.get('id')}\")\n",
                    "                print(f\"   Permalink: {entry.get('permalink', 'N/A')}\")\n",
                    "                print(f\"   Status: {entry.get('status')}\")\n",
                    "                return result\n",
                    "        else:\n",
                    "            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text\n",
                    "            print(f\"❌ Upload failed: {response.status_code}\")\n",
                    "            print(f\"   Error: {json.dumps(error_data, indent=2)}\")\n",
                    "            return None\n",
                    "    except Exception as e:\n",
                    "        print(f\"❌ Request failed: {e}\")\n",
                    "        return None\n",
                    "\n",
                    "# Extract title and content\n",
                    "title, content = extract_title_and_content(essay_content)\n",
                    "\n",
                    "# Upload (will prompt for JWT token)\n",
                    "upload_result = upload_to_commonplace(title, content)\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "markdown",
                "source": [
                    "## 5. Download Essay\n\n",
                    "Download the essay as a markdown file.\n"
                ],
                "metadata": {}
            },
            {
                "cell_type": "code",
                "source": [
                    "from google.colab import files\n",
                    "\n",
                    "# Save essay to file\n",
                    "with open('lovelace_essay_mbti_research.md', 'w', encoding='utf-8') as f:\n",
                    "    f.write(essay_content)\n",
                    "\n",
                    "print(\"✅ Essay saved to lovelace_essay_mbti_research.md\")\n",
                    "print(\"\\nTo download, run:\")\n",
                    "print(\"files.download('lovelace_essay_mbti_research.md')\")\n",
                    "\n",
                    "# Uncomment to auto-download:\n",
                    "# files.download('lovelace_essay_mbti_research.md')\n"
                ],
                "metadata": {}
            }
        ]
    }
    
    return notebook

def generate_essay() -> str:
    """Generate essay using OpenRouter."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY not set")
        return None
    
    base_url = "https://openrouter.ai/api/v1"
    client = OpenAI(
        api_key=openrouter_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "https://github.com/InquiryInstitute/mbti-faculty-voice-research",
            "X-Title": "MBTI Faculty Voice Research"
        }
    )
    
    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o")
    
    prompt = """You are Ada Lovelace, writing a commonplace essay on the investigation of MBTI's value in prompt engineering for faculty agent accuracy.

Context: This research examines whether Myers-Briggs Type Indicator (MBTI) personality overlays improve voice accuracy, consistency, and interpretability in AI faculty agents. The experiment tests 10 faculty personae across 16 MBTI types with 3 test prompts each (480 trials total), using an LLM-as-judge to evaluate voice accuracy.

The research is conducted using a Google Colab notebook (accessible at https://github.com/InquiryInstitute/Inquiry.Institute/tree/main/mbti-faculty-voice-research/MBTI_Research_Colab.ipynb) which provides an interactive environment for reproducing the experimental procedures, modifying parameters, and generating new essays through the same computational mechanisms.

Your task: Write a thoughtful, elegant commonplace essay (2000-3000 words) that:
- Reflects on the relationship between symbolic systems (like MBTI) and computational mechanisms
- Considers how personality frameworks might function as "prompt compression ontologies"
- Explores the tension between psychological validity and practical utility in AI systems
- Discusses the implications for creating coherent, persistent agent identities
- Describes the computational methodology, including the Colab notebook approach
- Maintains your characteristic voice: elegant, analytical, visionary about computation's scope, precise but imaginative, with a "poetical science" sensibility
- Uses your signature moves: clarify mechanism vs meaning, structured explanation, poetical science sensibility
- Avoids modern dev slang, casual tone, or pretending firsthand modern tooling

Write in the style of your era (Victorian scientific culture) but addressing contemporary AI systems. Be thoughtful, precise, and allow for the imaginative possibilities while maintaining analytical rigor."""

    messages = [
        {"role": "system", "content": """You are Ada Lovelace, the first computer programmer and a visionary of computation's potential. 
Your voice is elegant, analytical, visionary about computation's scope, precise but imaginative. 
You clarify mechanism vs meaning, provide structured explanations, and maintain a 'poetical science' sensibility.
You write in the style of Victorian scientific culture, with careful distinctions and elegant prose."""},
        {"role": "user", "content": prompt}
    ]
    
    print("✍️  Generating essay by Ada Lovelace...")
    print(f"   Using model: {model}\n")
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.8,
        max_tokens=4000
    )
    
    essay = response.choices[0].message.content
    
    # Format as markdown
    formatted = f"""# On the Investigation of MBTI in Prompt Engineering for Faculty Agent Accuracy

**Ada Lovelace**

*A Commonplace Essay*

---

{essay}"""
    
    print("✅ Essay generated!")
    return formatted

def main():
    """Main workflow: create notebook, generate essay."""
    print("=" * 60)
    print("Ada Lovelace: Creating Research Notebook and Generating Essay")
    print("=" * 60)
    print()
    
    # Step 1: Create notebook JSON
    print("📓 Creating research notebook...")
    notebook = create_notebook_json()
    
    # Save notebook
    notebook_file = "mbti_research_notebook.ipynb"
    with open(notebook_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    
    print(f"✅ Notebook created: {notebook_file}\n")
    
    # Step 2: Generate essay
    essay_content = generate_essay()
    
    if essay_content:
        # Save essay
        essay_file = "lovelace_essay_mbti_research.md"
        with open(essay_file, 'w', encoding='utf-8') as f:
            f.write(essay_content)
        print(f"💾 Essay saved to: {essay_file}\n")
    
    print("=" * 60)
    print("✅ Complete!")
    print("=" * 60)
    print(f"\n📓 Notebook: {notebook_file}")
    print(f"📝 Essay: {essay_file if essay_content else 'Not generated'}")
    print(f"\n💡 Next steps:")
    print(f"   1. Upload {notebook_file} to Google Colab")
    print(f"   2. Or open: https://colab.research.google.com/github/InquiryInstitute/Inquiry.Institute/blob/main/mbti-faculty-voice-research/MBTI_Research_Colab.ipynb")
    print(f"   3. Review the essay in {essay_file}")
    print(f"   4. Upload to Commonplace using the notebook or upload script")
    print()

if __name__ == "__main__":
    main()
