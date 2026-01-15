#!/usr/bin/env python3
"""
Generate publication recommendation reviews from faculty agents.

This script:
1. Checks out the merged revision branch
2. Generates reviews from each reviewer assessing the revisions
3. Provides publication recommendations (approve/reject/needs revision)
4. Adds comments to existing issues
"""

import os
import sys
import subprocess
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import from create_reviews_with_gh.py
sys.path.insert(0, str(project_root / ".github" / "scripts"))
from create_reviews_with_gh import (
    read_research_paper,
    get_experiment_summary,
    call_faculty_agent
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
        issue = json.loads(result.stdout)
        return issue.get("body", "")
    return ""

def get_author_response(issue_number: int) -> str:
    """Get the author response comment from an issue."""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number),
         "--repo", "InquiryInstitute/mbti-faculty-voice-research",
         "--json", "comments"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        issue = json.loads(result.stdout)
        comments = issue.get("comments", [])
        for comment in comments:
            if "Author Response" in comment.get("body", ""):
                return comment.get("body", "")
    return ""

def generate_publication_recommendation_prompt(faculty_name: str, original_review: str, author_response: str, changes_summary: str) -> str:
    """Generate a prompt for publication recommendation review."""
    return f"""You are {faculty_name}, providing a final publication recommendation for a research paper on MBTI in prompt engineering for faculty agent accuracy.

**Context:**
You previously reviewed this paper and provided detailed feedback. The author has now made revisions based on your feedback and other reviewers' concerns.

**Your Original Review:**
{original_review[:2000]}

**Author's Response:**
{author_response[:500]}

**Summary of Revisions Made:**
{changes_summary[:1000]}

**Your Task:**
Provide a final assessment and publication recommendation. Consider:

1. **Have your concerns been adequately addressed?** 
   - Which of your original concerns have been resolved?
   - Which concerns remain unresolved?
   - Are there new issues introduced by the revisions?

2. **Quality of Revisions:**
   - Are the revisions appropriate and well-executed?
   - Do they improve the scientific rigor of the paper?
   - Have limitations been properly acknowledged?

3. **Publication Readiness:**
   - Is the paper ready for publication as-is?
   - Does it meet standards for scientific publication in your judgment?
   - What remaining concerns (if any) prevent publication?

4. **Final Recommendation:**
   Provide one of the following recommendations:
   - **APPROVE**: Paper is ready for publication
   - **MINOR REVISIONS**: Small changes needed before publication
   - **MAJOR REVISIONS**: Significant concerns remain that must be addressed
   - **REJECT**: Fundamental issues prevent publication

Write your assessment in your authentic voice as {faculty_name}, maintaining scientific rigor and providing specific, constructive feedback. Be clear and direct in your recommendation.
"""

def add_comment_to_issue(issue_number: int, comment: str) -> bool:
    """Add a comment to an issue."""
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
            print(f"✅ Publication recommendation added to issue #{issue_number}")
            return True
        else:
            print(f"❌ Failed to add comment: {result.stderr}")
            return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    print("📋 Publication Recommendation Reviews\n")
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
    
    # Checkout merged branch
    merged_branch = "revisions/merged"
    print(f"\n📂 Checking out branch: {merged_branch}")
    result = subprocess.run(["git", "checkout", merged_branch], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Could not checkout branch {merged_branch}")
        print(f"   Error: {result.stderr}")
        return
    
    # Get changes summary
    print(f"\n📝 Getting changes from main to {merged_branch}...")
    result = subprocess.run(
        ["git", "log", "main..HEAD", "--oneline"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        changes_summary = "Revisions made:\n" + result.stdout
    else:
        changes_summary = "Revisions made based on all review feedback."
    
    # Get review issues
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
    
    # Read current paper
    print("\n📄 Reading research paper from merged branch...")
    paper_content = read_research_paper()
    results_summary = get_experiment_summary()
    
    # Generate publication recommendations
    print(f"\n📝 Generating publication recommendations...")
    
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
        
        # Get original review and author response
        print("   Fetching original review and author response...")
        original_review = get_original_review(issue_num)
        author_response = get_author_response(issue_num)
        
        # Generate publication recommendation
        print(f"   Generating publication recommendation...")
        prompt = generate_publication_recommendation_prompt(
            reviewer_name, original_review, author_response, changes_summary
        )
        
        recommendation = call_faculty_agent(reviewer_name, system_prompt, prompt)
        
        if not recommendation:
            print(f"   ❌ Failed to generate recommendation")
            continue
        
        # Create comment
        comment = f"""## Publication Recommendation

**Reviewer:** {reviewer_name}  
**Review Date:** {subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}  
**Revision Branch:** `{merged_branch}`

---

{recommendation}

---

**Note:** This is a publication recommendation based on review of the revised paper.
"""
        
        # Add comment to issue
        add_comment_to_issue(issue_num, comment)
    
    print(f"\n{'='*60}")
    print(f"\n✅ Publication recommendation reviews complete!")
    print(f"\n   All reviewers have provided publication recommendations.")
    print(f"   Review the recommendations in issues #1, #2, and #3.")

if __name__ == "__main__":
    main()
