#!/usr/bin/env python3
"""
Publish RESEARCH_PAPER.md to Commonplace (Directus) as a draft.

This script:
1. Reads RESEARCH_PAPER.md
2. Extracts title and content
3. Authenticates with Directus
4. Creates or updates work in Directus
"""

import os
import sys
import json
import re
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text."""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')
    if len(slug) > 100:
        slug = slug[:100].rstrip('-')
    return slug

def read_research_paper(file_path: Path) -> tuple[str, str]:
    """Read research paper markdown and extract title and content."""
    if not file_path.exists():
        print(f"❌ Research paper not found: {file_path}")
        sys.exit(1)
    
    content = file_path.read_text(encoding='utf-8')
    
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
        title = "Investigating the Value of MBTI in Prompt Engineering for Faculty Agent Accuracy"
    
    # Extract content (skip title and author line)
    paper_content = '\n'.join(lines[content_start:])
    
    # Remove author line if present (lines starting with **)
    lines_filtered = []
    for line in paper_content.split('\n'):
        if line.strip().startswith('**') and 'Daniel' in line:
            continue  # Skip author attribution line
        if line.strip().startswith('*in voce'):
            continue  # Skip faculty voice attribution
        if line.strip() == 'Inquiry Institute':
            continue  # Skip affiliation line
        if line.strip() == '---':
            continue  # Skip separator lines at start
        lines_filtered.append(line)
    
    paper_content = '\n'.join(lines_filtered).strip()
    
    return title, paper_content

def get_directus_token() -> str:
    """Get Directus access token via email/password authentication."""
    email = os.getenv("DIRECTUS_EMAIL") or os.getenv("COMMONPLACE_AUTH_EMAIL")
    password = os.getenv("DIRECTUS_PASSWORD") or os.getenv("COMMONPLACE_AUTH_PASSWORD")
    directus_url = os.getenv("DIRECTUS_URL") or "https://commonplace-directus-652016456291.us-central1.run.app"
    
    if not email or not password:
        print("❌ DIRECTUS_EMAIL and DIRECTUS_PASSWORD (or COMMONPLACE_AUTH_EMAIL and COMMONPLACE_AUTH_PASSWORD) must be set")
        sys.exit(1)
    
    print(f"🔐 Authenticating with Directus as {email}...")
    try:
        # Directus auth endpoint
        auth_url = f"{directus_url}/auth/login"
        response = requests.post(
            auth_url,
            json={
                "email": email,
                "password": password
            },
            headers={
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("access_token", "")
            if token:
                print("✅ Authentication successful")
                return token
            else:
                print("❌ No access token in response")
                sys.exit(1)
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        sys.exit(1)

def get_or_find_author(directus_url: str, token: str) -> str | None:
    """Find author ID for William James (a-william-james)."""
    try:
        # Try to find by slug first (if persons have slugs)
        response = requests.get(
            f"{directus_url}/items/persons",
            params={
                "filter[kind][_eq]": "faculty",
                "filter[slug][_eq]": "a-william-james",
                "limit": 1
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                return data["data"][0]["id"]
        
        # Try by name
        response = requests.get(
            f"{directus_url}/items/persons",
            params={
                "filter[kind][_eq]": "faculty",
                "filter[name][_icontains]": "William James",
                "limit": 1
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                return data["data"][0]["id"]
        
        return None
    except Exception as e:
        print(f"⚠️  Could not find author: {e}")
        return None

def find_existing_work(directus_url: str, token: str, slug: str) -> str | None:
    """Find existing work by slug. Returns work ID if found, None otherwise."""
    try:
        response = requests.get(
            f"{directus_url}/items/works",
            params={
                "filter[slug][_eq]": slug,
                "limit": 1,
                "fields": "id"
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                return data["data"][0]["id"]
        return None
    except Exception as e:
        print(f"⚠️  Error checking for existing work: {e}")
        return None

def create_or_update_work(directus_url: str, token: str, title: str, content: str, slug: str, author_id: str | None):
    """Create or update work in Directus."""
    
    # Check if work exists
    existing_id = find_existing_work(directus_url, token, slug)
    
    work_data = {
        "title": title,
        "slug": slug,
        "content_md": content,
        "type": "essay",  # Research paper is an essay type
        "status": "published",  # Changed from "draft" - paper has unconditional approval
        "visibility": "public",  # Changed from "private" - paper is approved for publication
    }
    
    if author_id:
        work_data["primary_author_id"] = author_id
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if existing_id:
        # Update existing work
        print(f"📝 Updating existing work (ID: {existing_id})...")
        response = requests.patch(
            f"{directus_url}/items/works/{existing_id}",
            json=work_data,
            headers=headers,
            timeout=30
        )
        action = "updated"
        work_id = existing_id
    else:
        # Create new work
        print(f"➕ Creating new work...")
        response = requests.post(
            f"{directus_url}/items/works",
            json=work_data,
            headers=headers,
            timeout=30
        )
        action = "created"
        
        if response.status_code == 200:
            data = response.json()
            work_id = data.get("data", {}).get("id")
        else:
            work_id = None
    
    result_file = Path(__file__).parent.parent / "publish_result.txt"
    
    if response.status_code in [200, 201]:
        data = response.json() if response.content else {}
        work_data_response = data.get("data", {})
        
        print(f"✅ Work {action} successfully!")
        print(f"   Work ID: {work_id or work_data_response.get('id', 'N/A')}")
        print(f"   Slug: {slug}")
        print(f"   Status: {work_data_response.get('status', 'draft')}")
        
        # Generate URL
        url = f"https://commonplace.inquiry.institute/book?slug={slug}"
        print(f"   URL: {url}")
        
        # Write result to file
        result_file.write_text(
            f"✅ Research paper {action} in Commonplace\n"
            f"Work ID: {work_id or work_data_response.get('id', 'N/A')}\n"
            f"Status: {work_data_response.get('status', 'draft')}\n"
            f"URL: {url}\n"
        )
        return data
    else:
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        print(f"❌ Failed to {action.replace('d', '')} work: {response.status_code}")
        print(f"   Error: {json.dumps(error_data, indent=2) if isinstance(error_data, dict) else error_data}")
        
        result_file.write_text(
            f"❌ Failed to {action.replace('d', '')} research paper\n"
            f"Status Code: {response.status_code}\n"
            f"Error: {error_data}\n"
        )
        sys.exit(1)

if __name__ == "__main__":
    # Get file paths
    project_root = Path(__file__).parent.parent.parent
    paper_path = project_root / "RESEARCH_PAPER.md"
    
    # Read research paper
    title, content = read_research_paper(paper_path)
    
    # Generate slug
    slug = generate_slug(title)
    
    # Get Directus URL
    directus_url = os.getenv("DIRECTUS_URL") or "https://commonplace-directus-652016456291.us-central1.run.app"
    
    # Get authentication token
    token = get_directus_token()
    
    # Try to find author ID (optional)
    author_id = get_or_find_author(directus_url, token)
    if author_id:
        print(f"✅ Found author ID: {author_id}")
    else:
        print("⚠️  Author not found - work will be created without primary author")
    
    # Create or update work
    create_or_update_work(directus_url, token, title, content, slug, author_id)
