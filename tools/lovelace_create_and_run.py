#!/usr/bin/env python3
"""
Ada Lovelace creates a research notebook and runs it to generate essay.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
parent_env = Path(__file__).parent.parent / '.env.local'
if parent_env.exists():
    load_dotenv(parent_env)
load_dotenv('.env.local')
load_dotenv()

def get_auth_token() -> str:
    """Get JWT token for authentication."""
    jwt_token = os.getenv("LOVELACE_JWT_TOKEN")
    if jwt_token:
        return jwt_token
    
    email = os.getenv("LOVELACE_EMAIL", "a.lovelace@inquiry.institute")
    password = os.getenv("LOVELACE_PASSWORD")
    
    if password:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
        supabase_anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_anon_key:
            print("❌ Supabase credentials not configured")
            sys.exit(1)
        
        print(f"🔐 Authenticating as {email}...")
        try:
            auth_url = f"{supabase_url}/auth/v1/token?grant_type=password"
            response = requests.post(
                auth_url,
                headers={
                    "apikey": supabase_anon_key,
                    "Content-Type": "application/json"
                },
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token", "")
        except Exception as e:
            print(f"❌ Authentication error: {e}")
    
    print("❌ No authentication method available.")
    print("\nSet LOVELACE_JWT_TOKEN or LOVELACE_EMAIL/LOVELACE_PASSWORD")
    sys.exit(1)

def create_notebook(jwt_token: str) -> dict:
    """Create research notebook via edge function."""
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    edge_function_url = f"{supabase_url}/functions/v1/create-colab-notebook"
    
    payload = {
        "title": "MBTI in Prompt Engineering: Faculty Agent Accuracy Research",
        "faculty_slug": "a-lovelace",
        "template": "mbti-research",
        "research_topic": "Investigating the value of MBTI in prompt engineering for improving faculty agent voice accuracy, consistency, and interpretability",
        "description": "Research notebook for investigating whether MBTI personality overlays improve voice accuracy in AI faculty agents. Includes essay generation and Commonplace upload capabilities."
    }
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "apikey": supabase_anon_key,
        "Content-Type": "application/json"
    }
    
    print("📓 Creating research notebook as Ada Lovelace...")
    print(f"   Title: {payload['title']}")
    print(f"   Template: {payload['template']}\n")
    
    try:
        response = requests.post(edge_function_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 201:
            result = response.json()
            if result.get("success"):
                print("✅ Notebook created successfully!")
                
                # Save notebook
                notebook_file = "mbti_research_notebook.ipynb"
                with open(notebook_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('notebook_json', '{}'))
                
                print(f"💾 Notebook saved to: {notebook_file}")
                return result
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ Creation failed: {response.status_code}")
            print(f"   Error: {json.dumps(error_data, indent=2)}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def generate_essay() -> str:
    """Generate essay using OpenRouter."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY not set")
        sys.exit(1)
    
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

def upload_to_commonplace(title: str, content: str, jwt_token: str) -> dict:
    """Upload essay to Commonplace."""
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    # Use colab-commonplace endpoint
    edge_function_url = f"{supabase_url}/functions/v1/colab-commonplace"
    
    # Convert markdown to HTML (basic)
    html_content = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
    html_content = f"<p>{html_content}</p>"
    
    payload = {
        "action": "create",
        "entry": {
            "title": title,
            "content": html_content,
            "status": "draft",
            "faculty_slug": "a-lovelace",
            "entry_type": "essay",
            "topics": ["mbti", "prompt-engineering", "faculty-agents", "ai-research"],
            "college": "ains",
            "metadata": {
                "provenance_mode": "ai_generated",
                "canonical_source_url": "https://github.com/InquiryInstitute/Inquiry.Institute/tree/main/mbti-faculty-voice-research",
                "colab_notebook_url": "https://colab.research.google.com/github/InquiryInstitute/Inquiry.Institute/blob/main/mbti-faculty-voice-research/MBTI_Research_Colab.ipynb",
                "source_refs": "Generated by Ada Lovelace faculty agent via research notebook",
                "generated_by": "Ada Lovelace",
                "pinned": False
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "apikey": supabase_anon_key,
        "Content-Type": "application/json"
    }
    
    print(f"📤 Uploading essay to Commonplace...")
    print(f"   Title: {title}")
    print(f"   Faculty: a-lovelace\n")
    
    try:
        response = requests.post(edge_function_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 201:
            result = response.json()
            if result.get("success"):
                print("✅ Essay uploaded successfully!")
                entry = result.get("entry", {})
                print(f"   Entry ID: {entry.get('id')}")
                print(f"   Permalink: {entry.get('permalink', 'N/A')}")
                print(f"   Status: {entry.get('status')}")
                return result
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {json.dumps(error_data, indent=2)}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    """Main workflow: create notebook, generate essay, upload."""
    print("=" * 60)
    print("Ada Lovelace: Creating Research Notebook and Generating Essay")
    print("=" * 60)
    print()
    
    # Step 1: Authenticate
    jwt_token = get_auth_token()
    print("✅ Authenticated as Ada Lovelace\n")
    
    # Step 2: Create notebook
    notebook_result = create_notebook(jwt_token)
    if not notebook_result:
        print("⚠️  Notebook creation failed, but continuing with essay generation...\n")
    
    # Step 3: Generate essay
    essay_content = generate_essay()
    
    # Save essay
    essay_file = "lovelace_essay_mbti_research.md"
    with open(essay_file, 'w', encoding='utf-8') as f:
        f.write(essay_content)
    print(f"💾 Essay saved to: {essay_file}\n")
    
    # Step 4: Extract title and upload
    lines = essay_content.split('\n')
    title = None
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    if not title:
        title = "On the Investigation of MBTI in Prompt Engineering for Faculty Agent Accuracy"
    
    # Extract content (skip header)
    content_start = 0
    for i, line in enumerate(lines):
        if line.startswith('---'):
            content_start = i + 1
            break
    
    essay_body = '\n'.join(lines[content_start:])
    essay_body = essay_body.replace('**Ada Lovelace**', '').replace('*A Commonplace Essay*', '').strip()
    essay_body = essay_body.lstrip('-').strip()
    
    # Upload to Commonplace
    upload_result = upload_to_commonplace(title, essay_body, jwt_token)
    
    print("\n" + "=" * 60)
    print("✅ Complete!")
    print("=" * 60)
    print(f"\n📓 Notebook: mbti_research_notebook.ipynb")
    print(f"📝 Essay: {essay_file}")
    if upload_result:
        print(f"🌐 Commonplace: {upload_result.get('entry', {}).get('permalink', 'N/A')}")
    print()

if __name__ == "__main__":
    main()
