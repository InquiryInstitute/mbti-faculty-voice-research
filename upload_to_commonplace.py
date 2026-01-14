#!/usr/bin/env python3
"""
Upload Ada Lovelace's essay to Commonplace via Supabase Edge Function.

This script requires authentication as a faculty user. You can either:
1. Set LOVELACE_EMAIL and LOVELACE_PASSWORD to authenticate automatically
2. Or manually authenticate and set LOVELACE_JWT_TOKEN
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment from parent directory (.env.local) and current directory
parent_env = Path(__file__).parent.parent / '.env.local'
if parent_env.exists():
    load_dotenv(parent_env)
load_dotenv('.env.local')
load_dotenv()

def read_essay(file_path: str) -> tuple[str, str]:
    """Read essay markdown and extract title and content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title (first # heading)
    lines = content.split('\n')
    title = None
    content_start = 0
    
    for i, line in enumerate(lines):
        if line.startswith('# '):
            title = line[2:].strip()
            content_start = i + 1
            break
    
    if not title:
        title = "On the Investigation of MBTI in Prompt Engineering for Faculty Agent Accuracy"
    
    # Extract content (skip frontmatter-like header)
    essay_content = '\n'.join(lines[content_start:])
    
    # Remove author/date headers if present
    essay_content = essay_content.replace('**Ada Lovelace**', '').replace('*A Commonplace Essay*', '').strip()
    essay_content = essay_content.lstrip('-').strip()
    
    return title, essay_content

def get_auth_token() -> str:
    """Get JWT token for authentication."""
    # Option 1: Use provided JWT token
    jwt_token = os.getenv("LOVELACE_JWT_TOKEN")
    if jwt_token:
        return jwt_token
    
    # Option 2: Authenticate using email/password
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
            # Use Supabase Auth REST API
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
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   {response.text}")
        except Exception as e:
            print(f"❌ Authentication error: {e}")
    
    # Option 3: No authentication available
    print("❌ No authentication method available.")
    print("\nTo upload, you need one of:")
    print("  1. Set LOVELACE_JWT_TOKEN in environment (get from browser DevTools)")
    print("  2. Set LOVELACE_EMAIL and LOVELACE_PASSWORD in environment")
    print("\nOr authenticate manually:")
    print("  1. Visit https://inquiry.institute and sign in as a.lovelace")
    print("  2. Open browser DevTools > Application > Local Storage")
    print("  3. Find 'sb-<project>-auth-token' and copy the access_token")
    print("  4. Set LOVELACE_JWT_TOKEN=<token>")
    sys.exit(1)

def upload_to_commonplace(title: str, content: str, faculty_slug: str = "a-lovelace"):
    """Upload essay to Commonplace via Supabase Edge Function."""
    
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL or NEXT_PUBLIC_SUPABASE_URL not set in environment")
        sys.exit(1)
    
    if not supabase_anon_key:
        print("❌ SUPABASE_ANON_KEY or NEXT_PUBLIC_SUPABASE_ANON_KEY not set")
        sys.exit(1)
    
    # Get authentication token
    auth_token = get_auth_token()
    
    # Edge function URL
    edge_function_url = f"{supabase_url}/functions/v1/create-commonplace"
    
    # Prepare request
    payload = {
        "title": title,
        "content": content,
        "status": "draft",  # Start as draft for review
        "faculty_slug": faculty_slug,
        "entry_type": "essay",  # Commonplace entry type
        "topics": ["mbti", "prompt-engineering", "faculty-agents", "ai-research"],
        "college": "ains",  # College of Artificial & Inquiring Systems
        "metadata": {
            "provenance_mode": "ai_generated",
            "canonical_source_url": "https://github.com/InquiryInstitute/mbti-faculty-voice-research",
            "source_refs": "Generated by Ada Lovelace faculty agent",
            "pinned": False
        }
    }
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "apikey": supabase_anon_key,
        "Content-Type": "application/json"
    }
    
    print(f"📤 Uploading essay to Commonplace...")
    print(f"   Title: {title}")
    print(f"   Faculty: {faculty_slug}")
    print(f"   Status: draft")
    print(f"   URL: {edge_function_url}\n")
    
    try:
        response = requests.post(
            edge_function_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Essay uploaded successfully!")
            print(f"   Entry ID: {result.get('entry', {}).get('id')}")
            print(f"   Permalink: {result.get('entry', {}).get('permalink', 'N/A')}")
            print(f"   Status: {result.get('entry', {}).get('status')}")
            return result
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {json.dumps(error_data, indent=2)}")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    essay_file = Path(__file__).parent / "lovelace_essay_mbti_research.md"
    
    if not essay_file.exists():
        print(f"❌ Essay file not found: {essay_file}")
        sys.exit(1)
    
    title, content = read_essay(str(essay_file))
    
    # Extract excerpt (first paragraph)
    excerpt = content.split('\n\n')[0][:200] + "..." if content else ""
    
    upload_to_commonplace(title, content, faculty_slug="a-lovelace")
