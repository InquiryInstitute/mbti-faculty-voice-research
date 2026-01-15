#!/usr/bin/env python3
"""
Final Approval Review Workflow

This script:
1. Generates final approval reviews from all reviewers
2. Checks if all reviewers approve
3. If approved, merges final revision branch to main
4. Marks issues as resolved/approved
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
try:
    from create_reviews_with_gh import (
        read_research_paper,
        get_experiment_summary,
        call_faculty_agent
    )
except ImportError:
    # Fallback implementation
    def read_research_paper() -> str:
        paper_path = project_root / "RESEARCH_PAPER.md"
        return paper_path.read_text(encoding='utf-8')
    
    def call_faculty_agent(faculty_name: str, system_prompt: str, user_prompt: str) -> str:
        """Call faculty agent using OpenRouter."""
        from openai import OpenAI
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return None
        
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/InquiryInstitute/mbti-faculty-voice-research",
                    "X-Title": "MBTI Faculty Voice Research - Final Approval"
                }
            )
            
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️  Error: {e}")
            return None

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
        
        reviewers = {
            "John Dewey": ("""You are John Dewey, the American philosopher, psychologist, and educational reformer. You are known for your pragmatic philosophy, emphasis on experience and inquiry, and your work in progressive education. You value practical consequences, democratic participation, and learning through doing. You write in a clear, accessible style that emphasizes the connection between theory and practice."""),
            "Alan Turing": ("""You are Alan Turing, the British mathematician, logician, and computer scientist. You are known for your work on computability, the Turing machine, and code-breaking. You think with mathematical precision, value logical rigor, and are interested in the fundamental questions of computation and intelligence. You write with clarity and technical accuracy."""),
            "Ada Lovelace": ("""You are Ada Lovelace, the English mathematician and writer. You are known for your work on Charles Babbage's Analytical Engine and are often considered the first computer programmer. You combine mathematical rigor with imaginative vision, seeing the potential for machines to go beyond calculation. You write with elegance, precision, and visionary insight.""")
        }
        
        for name, prompt in reviewers.items():
            if name in title:
                return name, prompt
    
    return None, None

def generate_final_approval_prompt(faculty_name: str, previous_recommendations: str, final_changes: str) -> str:
    """Generate a prompt for final approval review."""
    return f"""You are {faculty_name}, providing a final approval review for a research paper on MBTI in prompt engineering for faculty agent accuracy.

**Context:**
You previously recommended MINOR REVISIONS for this paper. The author has now made the final changes you requested and is requesting final approval for publication.

**Your Previous Recommendation:**
{previous_recommendations[:1000]}

**Final Changes Made:**
{final_changes[:1000]}

**Your Task:**
Provide a final approval assessment. Consider:

1. **Have all your requested changes been made?**
   - Are the required revisions complete?
   - Do the changes adequately address your concerns?

2. **Is the paper ready for publication?**
   - Are there any remaining issues?
   - Does the paper meet publication standards?

3. **Final Recommendation:**
   Provide one of:
   - **APPROVE** - Paper is ready for publication
   - **NEEDS MORE WORK** - Additional changes still required

Write your final assessment in your authentic voice as {faculty_name}. Be clear and direct: if the paper is ready, approve it. If not, specify what still needs to be done.
"""

def add_final_approval_comment(issue_number: int, comment: str) -> bool:
    """Add final approval comment to issue."""
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
            print(f"✅ Added final approval to issue #{issue_number}")
            return True
        else:
            print(f"❌ Failed to add comment: {result.stderr}")
            return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def close_issue(issue_number: int, comment: str = None) -> bool:
    """Close an issue with optional comment."""
    if comment:
        result = subprocess.run(
            ["gh", "issue", "close", str(issue_number),
             "--repo", "InquiryInstitute/mbti-faculty-voice-research",
             "--comment", comment],
            capture_output=True,
            text=True,
            timeout=30
        )
    else:
        result = subprocess.run(
            ["gh", "issue", "close", str(issue_number),
             "--repo", "InquiryInstitute/mbti-faculty-voice-research"],
            capture_output=True,
            text=True,
            timeout=30
        )
    
    if result.returncode == 0:
        print(f"✅ Closed issue #{issue_number}")
        return True
    else:
        print(f"⚠️  Could not close issue #{issue_number}: {result.stderr}")
        return False

def merge_to_main(branch: str) -> bool:
    """Merge final revision branch to main."""
    # Checkout main
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull", "origin", "main"], check=False)
    
    # Merge branch
    result = subprocess.run(
        ["git", "merge", branch, "--no-edit"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Push to main
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"✅ Merged {branch} to main and pushed")
        return True
    else:
        print(f"❌ Merge failed: {result.stderr}")
        return False

def main():
    print("✅ Final Approval Review Workflow\n")
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
    
    # Checkout final revision branch
    final_branch = "revisions/final"
    print(f"\n📂 Checking out branch: {final_branch}")
    result = subprocess.run(["git", "checkout", final_branch], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Could not checkout branch {final_branch}")
        print(f"   Error: {result.stderr}")
        return
    
    # Get changes summary
    print(f"\n📝 Getting changes from main to {final_branch}...")
    result = subprocess.run(
        ["git", "log", "main..HEAD", "--oneline"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        changes_summary = "Final revisions made:\n" + result.stdout
    else:
        changes_summary = "Final revisions made based on publication recommendations."
    
    # Get review issues
    print("\n📋 Fetching review issues...")
    issues = [
        {"number": 1, "title": "Peer Review: Scientific Validity and Pragmatic Utility (John Dewey)", "reviewer": "John Dewey"},
        {"number": 2, "title": "Peer Review: Computational Methodology and Statistical Rigor (Alan Turing)", "reviewer": "Alan Turing"},
        {"number": 3, "title": "Peer Review: Experimental Design and Analytical Precision (Ada Lovelace)", "reviewer": "Ada Lovelace"},
    ]
    
    # Get previous recommendations
    print("\n📋 Getting previous recommendations...")
    previous_recommendations = {}
    for issue in issues:
        result = subprocess.run(
            ["gh", "issue", "view", str(issue['number']),
             "--repo", "InquiryInstitute/mbti-faculty-voice-research",
             "--json", "comments"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            issue_data = json.loads(result.stdout)
            comments = issue_data.get("comments", [])
            for comment in reversed(comments):
                body = comment.get("body", "")
                if "Publication Recommendation" in body:
                    previous_recommendations[issue['number']] = body[:1000]
                    break
    
    # Read current paper
    print("\n📄 Reading research paper from final revision branch...")
    paper_content = read_research_paper()
    
    # Generate final approvals
    print(f"\n📝 Generating final approval reviews...")
    approvals = {}
    
    for issue in issues:
        issue_num = issue['number']
        print(f"\n{'='*60}")
        print(f"\n👤 Processing issue #{issue_num}: {issue['reviewer']}")
        
        # Get reviewer info
        reviewer_name, system_prompt = get_reviewer_from_issue(issue_num)
        if not reviewer_name:
            reviewer_name = issue['reviewer']
            # Fallback system prompts
            prompts = {
                "John Dewey": """You are John Dewey, the American philosopher, psychologist, and educational reformer. You are known for your pragmatic philosophy, emphasis on experience and inquiry, and your work in progressive education. You value practical consequences, democratic participation, and learning through doing. You write in a clear, accessible style that emphasizes the connection between theory and practice.""",
                "Alan Turing": """You are Alan Turing, the British mathematician, logician, and computer scientist. You are known for your work on computability, the Turing machine, and code-breaking. You think with mathematical precision, value logical rigor, and are interested in the fundamental questions of computation and intelligence. You write with clarity and technical accuracy.""",
                "Ada Lovelace": """You are Ada Lovelace, the English mathematician and writer. You are known for your work on Charles Babbage's Analytical Engine and are often considered the first computer programmer. You combine mathematical rigor with imaginative vision, seeing the potential for machines to go beyond calculation. You write with elegance, precision, and visionary insight."""
            }
            system_prompt = prompts.get(reviewer_name, "")
        
        print(f"   Reviewer: {reviewer_name}")
        
        # Get previous recommendation
        prev_rec = previous_recommendations.get(issue_num, "")
        
        # Generate final approval
        print(f"   Generating final approval...")
        prompt = generate_final_approval_prompt(reviewer_name, prev_rec, changes_summary)
        
        approval = call_faculty_agent(reviewer_name, system_prompt, prompt)
        
        if not approval:
            print(f"   ❌ Failed to generate approval")
            continue
        
        approvals[issue_num] = approval
        
        # Create comment
        comment = f"""## Final Approval Review

**Reviewer:** {reviewer_name}  
**Review Date:** {subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}  
**Final Revision Branch:** `{final_branch}`

---

{approval}

---

**Note:** This is the final approval review after all requested revisions have been made.
"""
        
        # Add comment to issue
        add_final_approval_comment(issue_num, comment)
        
        # Check if approved
        if "APPROVE" in approval.upper() and "NEEDS MORE WORK" not in approval.upper():
            approvals[issue_num] = "APPROVE"
        else:
            approvals[issue_num] = "NEEDS MORE WORK"
    
    print(f"\n{'='*60}")
    print(f"\n📋 Final Approval Summary:")
    for issue_num, status in approvals.items():
        reviewer = next((i['reviewer'] for i in issues if i['number'] == issue_num), "Unknown")
        print(f"   Issue #{issue_num} ({reviewer}): {status}")
    
    # Check if all approved
    all_approved = all(
        status == "APPROVE" or "APPROVE" in str(status).upper()
        for status in approvals.values()
    )
    
    if all_approved:
        print(f"\n✅ All reviewers approved!")
        
        # Merge to main
        print(f"\n🔄 Merging {final_branch} to main...")
        if merge_to_main(final_branch):
            print(f"✅ Paper published! Merged to main.")
            
            # Close issues with approval note
            print(f"\n🔒 Closing review issues...")
            for issue in issues:
                close_issue(
                    issue['number'],
                    f"✅ Paper approved and published. Final revision merged to main."
                )
            
            print(f"\n🎉 Publication complete!")
            print(f"   All review issues have been closed.")
            print(f"   Paper is now published in main branch.")
        else:
            print(f"❌ Failed to merge. Resolve conflicts manually.")
    else:
        print(f"\n⚠️  Not all reviewers approved.")
        print(f"   Review the final approval comments and make additional revisions if needed.")

if __name__ == "__main__":
    main()
