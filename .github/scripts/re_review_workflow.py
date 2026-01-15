#!/usr/bin/env python3
"""
Re-Review Workflow - Generate updated reviews after revisions

This script:
1. Checks out the revision branch
2. Generates updated reviews from the original reviewers
3. Adds comments to the original review issues
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import from create_reviews_with_gh.py
sys.path.insert(0, str(project_root / ".github" / "scripts"))
from create_reviews_with_gh import (
    read_research_paper,
    get_experiment_summary,
    call_faculty_agent,
    generate_review
)

def get_reviewer_from_issue(issue_number: int) -> tuple:
    """Get reviewer name and system prompt from issue."""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number), 
         "--repo", "InquiryInstitute/mbti-faculty-voice-research",
         "--json", "title"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        import json
        issue = json.loads(result.stdout)
        title = issue.get("title", "")
        
        # Map titles to reviewers
        reviewers = {
            "John Dewey": ("""You are John Dewey, the American philosopher, psychologist, and educational reformer. You are known for your pragmatic philosophy, emphasis on experience and inquiry, and your work in progressive education. You value practical consequences, democratic participation, and learning through doing. You write in a clear, accessible style that emphasizes the connection between theory and practice."""),
            "Alan Turing": ("""You are Alan Turing, the British mathematician, logician, and computer scientist. You are known for your work on computability, the Turing machine, and code-breaking. You think with mathematical precision, value logical rigor, and are interested in the fundamental questions of computation and intelligence. You write with clarity and technical accuracy."""),
            "Ada Lovelace": ("""You are Ada Lovelace, the English mathematician and writer. You are known for your work on Charles Babbage's Analytical Engine and are often considered the first computer programmer. You combine mathematical rigor with imaginative vision, seeing the potential for machines to go beyond calculation. You write with elegance, precision, and visionary insight.""")
        }
        
        for name, prompt in reviewers.items():
            if name in title:
                return name, prompt
    
    return None, None

def generate_re_review_prompt(faculty_name: str, original_review: str, changes_summary: str) -> str:
    """Generate a prompt for re-review after revisions."""
    return f"""You are {faculty_name}, providing a follow-up peer review after the author has made revisions based on your original feedback.

**Context:**
You previously reviewed a research paper on MBTI in prompt engineering for faculty agent accuracy. The author has now made revisions based on your feedback.

**Your Original Review:**
{original_review[:2000]}

**Author's Summary of Changes:**
{changes_summary[:1000]}

**Your Task:**
Review the revisions and provide a follow-up assessment:

1. **Have the revisions addressed your concerns?** Which specific concerns were addressed, and which remain?

2. **Quality of Revisions:** Are the revisions appropriate and well-executed?

3. **Remaining Issues:** Are there any new issues introduced by the revisions, or any original concerns that were not adequately addressed?

4. **Overall Assessment:** 
   - Do you approve the revisions?
   - Are further changes needed?
   - Is the paper now ready for publication (from your perspective)?

Write your re-review in your authentic voice as {faculty_name}, maintaining scientific rigor and providing constructive, specific feedback.
"""

def get_original_review(issue_number: int) -> str:
    """Get the original review from an issue."""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number),
         "--repo", "InquiryInstitute/mbti-faculty-voice-research",
         "--json", "body"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        import json
        issue = json.loads(result.stdout)
        return issue.get("body", "")
    return ""

def get_revision_branches() -> List[str]:
    """Get all revision branches."""
    result = subprocess.run(
        ["git", "branch", "-r", "--list", "origin/revisions/review-*"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        branches = [b.strip().replace("origin/", "") for b in result.stdout.strip().split("\n") if b.strip()]
        return sorted(branches)
    return []

def main():
    print("🔄 Re-Review Workflow (Automated)\n")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        try:
            from dotenv import load_dotenv
            load_dotenv(project_root / ".env.local")
        except:
            pass
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY not set. Please set it or add to .env.local")
        return
    
    # Get revision branches
    print("\n📋 Finding revision branches...")
    branches = get_revision_branches()
    
    if not branches:
        print("❌ No revision branches found. Run author_response_workflow.py first.")
        return
    
    print(f"✅ Found {len(branches)} revision branch(es):")
    for branch in branches:
        print(f"   - {branch}")
    
    # Merge branches
    merged_branch = "revisions/merged"
    print(f"\n🔄 Merging revision branches into {merged_branch}...")
    
    # Import merge function
    sys.path.insert(0, str(project_root / ".github" / "scripts"))
    from author_response_workflow import merge_revision_branches
    
    merged = merge_revision_branches(branches, merged_branch)
    if not merged:
        print("❌ Merge failed - resolve conflicts manually")
        return
    
    # Push merged branch
    print(f"\n📤 Pushing {merged_branch}...")
    subprocess.run(["git", "push", "origin", merged_branch], check=True)
    
    # Checkout the merged branch
    print(f"\n📂 Checking out branch: {merged_branch}")
    result = subprocess.run(["git", "checkout", merged_branch], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Could not checkout branch {merged_branch}")
        print(f"   Error: {result.stderr}")
        return
    
    # Get all review issues
    print("\n📋 Fetching review issues...")
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", "InquiryInstitute/mbti-faculty-voice-research", 
         "--json", "number,title"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        import json
        all_issues = json.loads(result.stdout)
        review_issues = [i for i in all_issues if "Peer Review" in i.get("title", "")]
    else:
        review_issues = [
            {"number": 1, "title": "Peer Review: Scientific Validity and Pragmatic Utility (John Dewey)"},
            {"number": 2, "title": "Peer Review: Computational Methodology and Statistical Rigor (Alan Turing)"},
            {"number": 3, "title": "Peer Review: Experimental Design and Analytical Precision (Ada Lovelace)"},
        ]
    
    print(f"✅ Found {len(review_issues)} review issue(s)")
    
    # Get changes summary
    print(f"\n📝 Getting changes from main to {branch}...")
    result = subprocess.run(
        ["git", "log", "main..HEAD", "--oneline"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        changes_summary = "Changes made:\n" + result.stdout
    else:
        changes_summary = "Revisions made based on all review feedback."
    
    # Get changes summary
    print(f"\n📝 Getting changes from main to {merged_branch}...")
    result = subprocess.run(
        ["git", "log", "main..HEAD", "--oneline"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        changes_summary = "Changes made:\n" + result.stdout
    else:
        changes_summary = "Revisions made based on all review feedback."
    
    print(f"\n📄 Generating re-reviews for all reviewers...")
    
    # Generate re-review for each reviewer
    for issue in review_issues:
        issue_num = issue['number']
        print(f"\n{'='*60}")
        print(f"\n👤 Processing issue #{issue_num}: {issue['title']}")
        
        # Get reviewer info
        reviewer_name, system_prompt = get_reviewer_from_issue(issue_num)
        if not reviewer_name:
            print(f"⚠️  Could not identify reviewer, skipping...")
            continue
        
        print(f"   Reviewer: {reviewer_name}")
        
        # Get original review
        print("   Fetching original review...")
        original_review = get_original_review(issue_num)
        
        # Read current paper (from merged revision branch)
        print("   Reading research paper from merged branch...")
        paper_content = read_research_paper()
        results_summary = get_experiment_summary()
        
        # Generate re-review
        print(f"   Generating re-review...")
        re_review_prompt = generate_re_review_prompt(reviewer_name, original_review, changes_summary)
        
        review = call_faculty_agent(reviewer_name, system_prompt, re_review_prompt)
        
        if not review:
            print(f"   ❌ Failed to generate re-review")
            continue
        
        # Create comment
        comment = f"""## Re-Review After Revisions

**Reviewer:** {reviewer_name}  
**Revision Branch:** `{branch}` (merged with other reviewers' revisions)  
**Review Date:** {subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}

---

{review}

---

**Note:** This re-review was generated after the author made revisions based on all review feedback and merged them into a single branch.
"""
        
        # Add comment to issue
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(comment)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ["gh", "issue", "comment", str(issue_num),
                 "--repo", "InquiryInstitute/mbti-faculty-voice-research",
                 "--body-file", temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"   ✅ Re-review added to issue #{issue_num}")
            else:
                print(f"   ❌ Failed to add comment: {result.stderr}")
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
    
    print(f"\n{'='*60}")
    print(f"\n✅ Re-review workflow complete!")
    print(f"\n   All reviewers have been notified to review the merged branch: {merged_branch}")
    print(f"   Once all reviewers approve, merge {merged_branch} into main:")
    print(f"     git checkout main")
    print(f"     git merge {merged_branch}")
    print(f"     git push origin main")

if __name__ == "__main__":
    main()
