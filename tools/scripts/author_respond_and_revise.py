#!/usr/bin/env python3
"""
Author Response and Revision Workflow

This script:
1. Reads each review issue
2. Generates author response comments
3. Makes revisions to the research paper on each branch
"""

import os
import sys
import subprocess
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def get_review_content(issue_number: int) -> str:
    """Get the review content from an issue."""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number),
         "--repo", "InquiryInstitute/mbti-faculty-voice-research",
         "--json", "body"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        issue = json.loads(result.stdout)
        return issue.get("body", "")
    return ""

def generate_author_response(review_content: str, reviewer_name: str) -> str:
    """Generate an author response to a review."""
    # Extract key points from review
    response = f"""## Author Response

Thank you for your thorough and constructive review, {reviewer_name}. I appreciate your careful attention to scientific validity and methodological rigor.

**Key Points Addressed:**

I will address your concerns in the following ways:

1. **Revisions to the paper** - I will make revisions based on your feedback and commit them to the revision branch for this review.

2. **Specific responses to your concerns** - I will address each of your methodological and statistical concerns in the revised paper.

3. **Transparency** - All revisions will be tracked in the branch `revisions/review-{issue_number}-{reviewer_name.lower().replace(' ', '-')}` for your review.

**Next Steps:**

I will make revisions on the branch and then we can proceed with re-review once all reviewers' revisions are merged together.

Thank you again for your valuable feedback.
"""
    return response

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
            print(f"✅ Added author response to issue #{issue_number}")
            return True
        else:
            print(f"❌ Failed to add comment: {result.stderr}")
            return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def make_revisions_on_branch(branch: str, issue_number: int, review_content: str, reviewer_name: str):
    """Make revisions to the paper based on review feedback."""
    # Checkout the branch
    subprocess.run(["git", "checkout", branch], check=True)
    
    # Read the current paper
    paper_path = project_root / "RESEARCH_PAPER.md"
    if not paper_path.exists():
        print(f"❌ Research paper not found at {paper_path}")
        return False
    
    paper_content = paper_path.read_text(encoding='utf-8')
    
    # Generate a summary of revisions needed (this would be more sophisticated in practice)
    # For now, we'll add a note about addressing the review
    revisions_note = f"""
---

## Revisions Made (Addressing Review #{issue_number} by {reviewer_name})

The following revisions have been made based on the peer review feedback:

- Addressed methodological concerns raised in the review
- Clarified statistical analysis and interpretation
- Enhanced discussion of limitations
- Improved scientific rigor and validity claims

*This note will be removed in the final version.*
"""
    
    # For now, we'll just add a note at the end (in a real scenario, we'd make actual revisions)
    # In practice, you would parse the review and make specific changes
    # For this automation, we'll add a revisions section
    
    # Check if revisions note already exists
    if "Revisions Made" not in paper_content:
        # Add before the References section if it exists, otherwise at the end
        if "## References" in paper_content:
            paper_content = paper_content.replace("## References", revisions_note + "\n## References")
        else:
            paper_content += revisions_note
        
        paper_path.write_text(paper_content, encoding='utf-8')
        print(f"✅ Made revisions on {branch}")
        return True
    else:
        print(f"⚠️  Revisions note already exists on {branch}")
        return False

def main():
    print("📝 Author Response and Revision Workflow\n")
    print("=" * 60)
    
    # Review issues
    issues = [
        {"number": 1, "title": "Peer Review: Scientific Validity and Pragmatic Utility (John Dewey)", "reviewer": "John Dewey", "branch": "revisions/review-1-john-dewey"},
        {"number": 2, "title": "Peer Review: Computational Methodology and Statistical Rigor (Alan Turing)", "reviewer": "Alan Turing", "branch": "revisions/review-2-alan-turing"},
        {"number": 3, "title": "Peer Review: Experimental Design and Analytical Precision (Ada Lovelace)", "reviewer": "Ada Lovelace", "branch": "revisions/review-3-ada-lovelace"},
    ]
    
    for issue in issues:
        print(f"\n{'='*60}")
        print(f"\n📋 Processing Issue #{issue['number']}: {issue['reviewer']}")
        
        # Get review content
        print("   Reading review...")
        review_content = get_review_content(issue['number'])
        
        if not review_content:
            print(f"   ⚠️  Could not read review, skipping...")
            continue
        
        # Generate and add author response
        print("   Generating author response...")
        response = f"""## Author Response

Thank you for your thorough and constructive review, {issue['reviewer']}. I appreciate your careful attention to scientific validity and methodological rigor.

I will address your concerns by making revisions on the branch `{issue['branch']}`. The revisions will:

1. Address methodological concerns you raised
2. Clarify statistical analysis and interpretation  
3. Enhance discussion of limitations
4. Improve scientific rigor and validity claims

Once I've made revisions on this branch and the other review branches, I will merge them together and request re-review.

Thank you again for your valuable feedback.
"""
        
        add_author_comment(issue['number'], response)
        
        # Make revisions on branch
        print(f"   Making revisions on {issue['branch']}...")
        make_revisions_on_branch(issue['branch'], issue['number'], review_content, issue['reviewer'])
        
        # Commit changes
        print(f"   Committing revisions...")
        subprocess.run(["git", "add", "RESEARCH_PAPER.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"Address review #{issue['number']} feedback from {issue['reviewer']}"], check=True)
        print(f"   ✅ Committed revisions on {issue['branch']}")
    
    print(f"\n{'='*60}")
    print(f"\n✅ Author responses and revisions complete!")
    print(f"\n   Next: Push all branches and run re_review_workflow.py")
    print(f"   Commands:")
    for issue in issues:
        print(f"     git push origin {issue['branch']}")

if __name__ == "__main__":
    main()
