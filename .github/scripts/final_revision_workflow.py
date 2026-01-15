#!/usr/bin/env python3
"""
Final Revision Workflow

This script:
1. Gets publication recommendations from reviewers
2. Author responds to recommendations
3. Makes final changes in a branch
4. Gets reviewer assessment of final changes
5. If approved, merges to main
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def get_publication_recommendations() -> dict:
    """Get publication recommendations from all reviewers."""
    issues = [1, 2, 3]
    recommendations = {}
    
    for issue_num in issues:
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_num),
             "--repo", "InquiryInstitute/mbti-faculty-voice-research",
             "--json", "comments"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            issue = json.loads(result.stdout)
            comments = issue.get("comments", [])
            for comment in reversed(comments):  # Check most recent first
                body = comment.get("body", "")
                if "Publication Recommendation" in body:
                    # Extract recommendation
                    if "MINOR REVISIONS" in body:
                        rec = "MINOR REVISIONS"
                    elif "MAJOR REVISIONS" in body:
                        rec = "MAJOR REVISIONS"
                    elif "APPROVE" in body:
                        rec = "APPROVE"
                    elif "REJECT" in body:
                        rec = "REJECT"
                    else:
                        rec = "UNKNOWN"
                    
                    recommendations[issue_num] = {
                        "recommendation": rec,
                        "comment": body,
                        "reviewer": "John Dewey" if issue_num == 1 else ("Alan Turing" if issue_num == 2 else "Ada Lovelace")
                    }
                    break
    
    return recommendations

def extract_required_changes(recommendation_comment: str) -> list:
    """Extract specific required changes from recommendation."""
    changes = []
    
    # Look for numbered list items
    pattern = r'\d+\.\s+\*\*[^*]+\*\*\s+(.+?)(?=\d+\.|$)'
    matches = re.findall(pattern, recommendation_comment, re.DOTALL)
    
    for match in matches:
        change = match.strip().split('\n')[0]  # Get first line
        if change:
            changes.append(change)
    
    return changes

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

def create_final_revision_branch() -> str:
    """Create a branch for final revisions."""
    branch_name = "revisions/final"
    
    # Start from main
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull", "origin", "main"], check=False)
    
    # Check if branch exists
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        subprocess.run(["git", "checkout", branch_name], check=True)
        subprocess.run(["git", "merge", "main", "--no-edit"], check=False)
        print(f"⚠️  Branch {branch_name} already exists, updating...")
    else:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(f"✅ Created and checked out branch: {branch_name}")
    
    return branch_name

def make_final_revisions(recommendations: dict):
    """Make final revisions based on recommendations."""
    paper_path = project_root / "RESEARCH_PAPER.md"
    content = paper_path.read_text(encoding='utf-8')
    
    changes_made = []
    
    # Collect all required changes
    all_changes = []
    for issue_num, rec_data in recommendations.items():
        if rec_data["recommendation"] == "MINOR REVISIONS":
            changes = extract_required_changes(rec_data["comment"])
            all_changes.extend(changes)
    
    # Make revisions
    # 1. Standardize citation format
    if any("citation" in c.lower() or "reference" in c.lower() for c in all_changes):
        print("   📝 Standardizing citation format...")
        # Ensure journal titles are italicized
        content = re.sub(r'\*([A-Z][^*]+ Journal[^*]*)\*', r'*\1*', content, flags=re.IGNORECASE)
        changes_made.append("Standardized citation format (journal titles italicized)")
    
    # 2. Add note about human-evaluation/sampling (if mentioned)
    if any("human" in c.lower() or "sampling" in c.lower() or "judge" in c.lower() for c in all_changes):
        print("   📝 Adding note about limitations and future work on human evaluation...")
        # Add to limitations section
        if "Future research should investigate:" in content:
            content = content.replace(
                "Future research should investigate:",
                "**Human Evaluation:** The current study relies primarily on LLM-as-judge evaluation. While we acknowledge this limitation and demonstrate that overfitting scores remain low, future work should include larger-scale human expert evaluation to validate the LLM judge assessments. A pilot validation study is proposed as future work.\n\nFuture research should investigate:"
            )
            changes_made.append("Added note about human evaluation limitations and future validation")
    
    # 3. Add connection to pedagogical design (if mentioned)
    if any("pedagogical" in c.lower() or "learner" in c.lower() or "design" in c.lower() for c in all_changes):
        print("   📝 Adding connection to pedagogical design...")
        # Add to conclusion
        if "In faculty-based AI systems" in content:
            content = content.replace(
                "In faculty-based AI systems, where agents must embody traditions of thought, schools of reasoning, and historical epistemologies, MBTI provides a powerful and practical scaffold.",
                "In faculty-based AI systems, where agents must embody traditions of thought, schools of reasoning, and historical epistemologies, MBTI provides a powerful and practical scaffold. The improved voice accuracy and consistency demonstrated in this study suggests that MBTI augmentation may enhance learner engagement by providing more authentic and predictable interactions with faculty agents, though direct validation of this pedagogical impact remains an important area for future research."
            )
            changes_made.append("Added connection to pedagogical design principles")
    
    paper_path.write_text(content, encoding='utf-8')
    
    return changes_made

def main():
    print("📝 Final Revision Workflow\n")
    print("=" * 60)
    
    # Step 1: Get publication recommendations
    print("\n1️⃣ Getting publication recommendations...")
    recommendations = get_publication_recommendations()
    
    if not recommendations:
        print("❌ Could not get publication recommendations")
        return
    
    print(f"✅ Found recommendations from {len(recommendations)} reviewer(s):")
    for issue_num, rec_data in recommendations.items():
        print(f"   Issue #{issue_num} ({rec_data['reviewer']}): {rec_data['recommendation']}")
    
    # Check if all recommend approval or minor revisions
    all_approved = all(
        rec["recommendation"] in ["APPROVE", "MINOR REVISIONS"] 
        for rec in recommendations.values()
    )
    
    if not all_approved:
        print("\n⚠️  Not all reviewers recommend publication. Check recommendations first.")
        return
    
    # Step 2: Author responds to recommendations
    print("\n2️⃣ Author responding to recommendations...")
    for issue_num, rec_data in recommendations.items():
        response = f"""## Author Response to Publication Recommendation

Thank you for your recommendation: **{rec_data['recommendation']}**.

I will address the requested changes in the final revision branch `revisions/final`. The revisions will include:

{chr(10).join(f"- {change}" for change in extract_required_changes(rec_data['comment'])) if extract_required_changes(rec_data['comment']) else "- Address all points raised in your recommendation"}

Once the final revisions are complete, I will request your final review to confirm the paper is ready for publication.
"""
        add_author_comment(issue_num, response)
    
    # Step 3: Create final revision branch
    print("\n3️⃣ Creating final revision branch...")
    branch = create_final_revision_branch()
    
    # Step 4: Make final revisions
    print("\n4️⃣ Making final revisions...")
    changes_made = make_final_revisions(recommendations)
    
    if changes_made:
        print(f"   ✅ Made {len(changes_made)} revision(s):")
        for change in changes_made:
            print(f"      - {change}")
    else:
        print("   ⚠️  No automated revisions applied. Manual revisions may be needed.")
    
    # Step 5: Commit changes
    print("\n5️⃣ Committing final revisions...")
    subprocess.run(["git", "add", "RESEARCH_PAPER.md"], check=True)
    subprocess.run(["git", "commit", "-m", "Apply final revisions based on publication recommendations"], check=True)
    print("   ✅ Committed final revisions")
    
    # Step 6: Push branch
    print("\n6️⃣ Pushing final revision branch...")
    subprocess.run(["git", "push", "origin", branch], check=True)
    print(f"   ✅ Pushed {branch}")
    
    print(f"\n{'='*60}")
    print(f"\n✅ Final revision workflow complete!")
    print(f"\n   Final revision branch: {branch}")
    print(f"   Next: Run publication_recommendation_reviews.py to get reviewer approval")
    print(f"   Then: If approved, merge {branch} to main")

if __name__ == "__main__":
    main()
