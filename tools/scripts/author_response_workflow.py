#!/usr/bin/env python3
"""
Author Response Workflow for Peer Review

This script helps the author:
1. Review each peer review issue
2. Create a separate branch for each review's revisions
3. After all revisions are made, merge branches together
4. Request re-review on the merged revision
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def get_review_issues() -> List[Dict]:
    """Get the list of review issues."""
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", "InquiryInstitute/mbti-faculty-voice-research", 
         "--json", "number,title,author"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        import json
        issues = json.loads(result.stdout)
        # Filter for review issues
        review_issues = [i for i in issues if "Peer Review" in i.get("title", "")]
        return review_issues
    
    # Fallback: return known issue numbers
    return [
        {"number": 1, "title": "Peer Review: Scientific Validity and Pragmatic Utility (John Dewey)"},
        {"number": 2, "title": "Peer Review: Computational Methodology and Statistical Rigor (Alan Turing)"},
        {"number": 3, "title": "Peer Review: Experimental Design and Analytical Precision (Ada Lovelace)"},
    ]

def extract_reviewer_name(title: str) -> str:
    """Extract reviewer name from issue title."""
    if "John Dewey" in title:
        return "john-dewey"
    elif "Alan Turing" in title:
        return "alan-turing"
    elif "Ada Lovelace" in title:
        return "ada-lovelace"
    else:
        # Fallback: extract from parentheses
        if "(" in title and ")" in title:
            return title.split("(")[-1].rstrip(")").lower().replace(" ", "-")
        return "reviewer"

def create_revision_branch(issue_number: int, reviewer_name: str, base_branch: str = "main") -> str:
    """Create a branch for revisions based on a review."""
    branch_name = f"revisions/review-{issue_number}-{reviewer_name}"
    
    # Ensure we're on main first
    subprocess.run(["git", "checkout", base_branch], check=True)
    subprocess.run(["git", "pull", "origin", base_branch], check=False)
    
    # Check if branch exists
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"⚠️  Branch {branch_name} already exists")
        subprocess.run(["git", "checkout", branch_name], check=True)
        return branch_name
    
    # Create and checkout branch
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    print(f"✅ Created and checked out branch: {branch_name}")
    return branch_name

def add_author_comment(issue_number: int, comment: str) -> bool:
    """Add an author response comment to an issue."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(comment)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ["gh", "issue", "comment", str(issue_number), 
             "--repo", "InquiryInstitute/mbti-faculty-voice-research",
             "--body-file", temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Added comment to issue #{issue_number}")
            return True
        else:
            print(f"❌ Failed to add comment: {result.stderr}")
            return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def merge_revision_branches(branches: List[str], target_branch: str = "revisions/merged") -> str:
    """Merge all revision branches into a single branch."""
    # Start from main
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull", "origin", "main"], check=False)
    
    # Check if target branch exists
    result = subprocess.run(
        ["git", "rev-parse", "--verify", target_branch],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        subprocess.run(["git", "checkout", target_branch], check=True)
        subprocess.run(["git", "merge", "main", "--no-edit"], check=False)
    else:
        subprocess.run(["git", "checkout", "-b", target_branch], check=True)
    
    # Merge each revision branch
    for branch in branches:
        print(f"🔄 Merging {branch}...")
        result = subprocess.run(
            ["git", "merge", branch, "--no-edit"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"⚠️  Merge conflict in {branch} - resolve manually")
            print(f"   Then run: git merge --continue")
            return None
    
    print(f"✅ All branches merged into {target_branch}")
    return target_branch

def request_re_review(issue_number: int, merged_branch: str, changes_summary: str) -> bool:
    """Request re-review after revisions are merged."""
    comment = f"""## Author Response & Revisions

Thank you for your thorough review. I have made revisions based on your feedback.

**Revision Branch:** `{merged_branch}` (merged with other reviewers' revisions)

**Summary of Changes:**
{changes_summary}

**Next Steps:**
- Please review the revisions in the branch above
- Comment on whether the revisions address your concerns
- Indicate if you approve the revisions or if further changes are needed

I look forward to your feedback on the revisions.
"""
    
    return add_author_comment(issue_number, comment)

def main():
    print("📝 Author Response Workflow for Peer Review\n")
    print("=" * 60)
    
    # Get review issues
    print("\n📋 Fetching review issues...")
    issues = get_review_issues()
    
    if not issues:
        print("❌ No review issues found")
        return
    
    print(f"\n✅ Found {len(issues)} review issue(s):")
    for issue in issues:
        reviewer = extract_reviewer_name(issue['title'])
        print(f"   #{issue['number']}: {issue['title']} → branch: revisions/review-{issue['number']}-{reviewer}")
    
    print("\n" + "=" * 60)
    print("\nOptions:")
    print("1. Create revision branch for a specific review")
    print("2. Create revision branches for all reviews")
    print("3. Merge all revision branches together")
    print("4. Request re-review on merged revision")
    print("5. Complete workflow (branches + merge + re-review)")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    # Automated workflow
    # Step 1: Create branches
    print("Step 1: Creating revision branches...")
    branches = []
    for issue in issues:
        reviewer = extract_reviewer_name(issue['title'])
        branch = create_revision_branch(issue['number'], reviewer)
        branches.append(branch)
        print(f"   ✅ {branch}")
    
    print(f"\n📝 Created {len(branches)} revision branches:")
    for i, (issue, branch) in enumerate(zip(issues, branches), 1):
        print(f"\n   {i}. Branch: {branch}")
        print(f"      Issue: #{issue['number']} - {issue['title']}")
        print(f"      Commands to make revisions:")
        print(f"        git checkout {branch}")
        print(f"        # Make your revisions based on review #{issue['number']}")
        print(f"        git add .")
        print(f"        git commit -m 'Address review #{issue['number']} feedback'")
        print(f"        git push origin {branch}")
    
    print(f"\n{'='*60}")
    print(f"\n⏸️  Waiting for revisions to be made on all {len(branches)} branches...")
    print(f"   Once you've committed and pushed revisions on all branches,")
    print(f"   run: python3 .github/scripts/re_review_workflow.py")
    print(f"   This will merge branches and request re-review automatically.")

if __name__ == "__main__":
    main()
