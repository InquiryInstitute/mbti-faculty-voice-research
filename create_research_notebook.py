#!/usr/bin/env python3
"""
Create a research notebook for faculty via Supabase Edge Function.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment from parent directory
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
    print("\nTo create notebooks, you need:")
    print("  1. Set LOVELACE_JWT_TOKEN in environment")
    print("  2. Or set LOVELACE_EMAIL and LOVELACE_PASSWORD")
    sys.exit(1)

def create_research_notebook(
    title: str,
    template: str = "mbti-research",
    research_topic: str = None,
    description: str = None,
    faculty_slug: str = "a-lovelace"
):
    """Create a research notebook via Supabase Edge Function."""
    
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not set")
        sys.exit(1)
    
    auth_token = get_auth_token()
    
    edge_function_url = f"{supabase_url}/functions/v1/create-colab-notebook"
    
    payload = {
        "title": title,
        "faculty_slug": faculty_slug,
        "template": template,
    }
    
    if research_topic:
        payload["research_topic"] = research_topic
    if description:
        payload["description"] = description
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "apikey": supabase_anon_key,
        "Content-Type": "application/json"
    }
    
    print(f"📓 Creating research notebook...")
    print(f"   Title: {title}")
    print(f"   Template: {template}")
    print(f"   Faculty: {faculty_slug}\n")
    
    try:
        response = requests.post(
            edge_function_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Notebook created successfully!")
            print(f"   Title: {result.get('metadata', {}).get('title')}")
            print(f"   Template: {result.get('metadata', {}).get('template')}")
            print(f"\n📝 Next steps:")
            print(f"   1. Copy the notebook_json from the response")
            print(f"   2. Save it as a .ipynb file")
            print(f"   3. Upload to Google Colab: File → Upload notebook")
            print(f"\n   Or use the colab_open_url if available")
            
            # Save notebook JSON to file
            notebook_file = f"{title.lower().replace(' ', '_')}.ipynb"
            with open(notebook_file, 'w', encoding='utf-8') as f:
                f.write(result.get('notebook_json', '{}'))
            
            print(f"\n💾 Notebook saved to: {notebook_file}")
            print(f"   You can now upload this to Google Colab!")
            
            return result
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ Creation failed: {response.status_code}")
            print(f"   Error: {json.dumps(error_data, indent=2)}")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create a research notebook for faculty')
    parser.add_argument('--title', required=True, help='Notebook title')
    parser.add_argument('--template', default='mbti-research', 
                       choices=['mbti-research', 'essay-generation', 'experiment', 'custom'],
                       help='Notebook template')
    parser.add_argument('--topic', help='Research topic')
    parser.add_argument('--description', help='Notebook description')
    parser.add_argument('--faculty', default='a-lovelace', help='Faculty slug')
    
    args = parser.parse_args()
    
    create_research_notebook(
        title=args.title,
        template=args.template,
        research_topic=args.topic,
        description=args.description,
        faculty_slug=args.faculty
    )
