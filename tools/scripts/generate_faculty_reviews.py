#!/usr/bin/env python3
"""
Generate peer reviews from faculty agents and create GitHub issues.

This script:
1. Reads RESEARCH_PAPER.md and analyzes the experiment code/results
2. Generates reviews from three faculty agents (a.JohnDewey, a.AlanTuring, a.Ada Lovelace)
3. Creates GitHub issues with their reviews
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def read_research_paper() -> str:
    """Read the research paper markdown."""
    paper_path = project_root / "RESEARCH_PAPER.md"
    if not paper_path.exists():
        raise FileNotFoundError(f"Research paper not found: {paper_path}")
    return paper_path.read_text(encoding='utf-8')

def read_experiment_code() -> str:
    """Read the experiment code."""
    code_path = project_root / "mbti_voice_eval.py"
    if not code_path.exists():
        raise FileNotFoundError(f"Experiment code not found: {code_path}")
    return code_path.read_text(encoding='utf-8')

def get_experiment_summary() -> str:
    """Get a summary of the experiment results."""
    try:
        import pandas as pd
        df = pd.read_csv(project_root / "mbti_voice_results.csv")
        
        valid = df[df['voice_accuracy'] != -1]
        control = valid[valid['use_mbti'] == False]
        mbti = valid[valid['use_mbti'] == True]
        
        summary = f"""
## Experiment Summary

**Total Trials:** {len(df)}
**Valid Results:** {len(valid)}
**Control Condition:** {len(control)} trials, Mean = {control['voice_accuracy'].mean():.2f}, SD = {control['voice_accuracy'].std():.2f}
**MBTI Condition:** {len(mbti)} trials, Mean = {mbti['voice_accuracy'].mean():.2f}, SD = {mbti['voice_accuracy'].std():.2f}

**Key Findings:**
- MBTI condition shows {((mbti['voice_accuracy'].mean() - control['voice_accuracy'].mean()) / control['voice_accuracy'].mean() * 100):.1f}% improvement in voice accuracy
- Variance reduction: {((control['voice_accuracy'].std() - mbti['voice_accuracy'].std()) / control['voice_accuracy'].std() * 100):.1f}%
"""
        return summary
    except Exception as e:
        return f"Error generating summary: {e}"

def call_faculty_agent(faculty_slug: str, prompt: str) -> str:
    """Call faculty agent API to generate a review."""
    import requests
    from openai import OpenAI
    
    # Try using OpenRouter directly with faculty agent persona
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY not set, cannot call faculty agent")
        return None
    
    # Map faculty slugs to their names and system prompts
    faculty_prompts = {
        "a.john-dewey": {
            "name": "John Dewey",
            "system": """You are John Dewey, the American philosopher, psychologist, and educational reformer. You are known for your pragmatic philosophy, emphasis on experience and inquiry, and your work in progressive education. You value practical consequences, democratic participation, and learning through doing. You write in a clear, accessible style that emphasizes the connection between theory and practice."""
        },
        "a.alan-turing": {
            "name": "Alan Turing",
            "system": """You are Alan Turing, the British mathematician, logician, and computer scientist. You are known for your work on computability, the Turing machine, and code-breaking. You think with mathematical precision, value logical rigor, and are interested in the fundamental questions of computation and intelligence. You write with clarity and technical accuracy."""
        },
        "a.ada-lovelace": {
            "name": "Ada Lovelace",
            "system": """You are Ada Lovelace, the English mathematician and writer. You are known for your work on Charles Babbage's Analytical Engine and are often considered the first computer programmer. You combine mathematical rigor with imaginative vision, seeing the potential for machines to go beyond calculation. You write with elegance, precision, and visionary insight."""
        }
    }
    
    faculty_info = faculty_prompts.get(faculty_slug)
    if not faculty_info:
        print(f"⚠️  Unknown faculty slug: {faculty_slug}")
        return None
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/InquiryInstitute/mbti-faculty-voice-research",
                "X-Title": "MBTI Faculty Voice Research - Peer Review"
            }
        )
        
        messages = [
            {"role": "system", "content": faculty_info["system"]},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️  Error calling faculty agent: {e}")
        return None

def generate_review_prompt(faculty_name: str, paper_content: str, code_summary: str, results_summary: str) -> str:
    """Generate a review prompt for a faculty agent."""
    return f"""You are {faculty_name}, providing a rigorous peer review of a research paper on MBTI in prompt engineering for faculty agent accuracy.

**Your task:** Provide a thorough, critical peer review focusing STRICTLY on scientific validity, methodological rigor, and statistical soundness. Be very strict about scientific validity.

**Review both:**
1. The research paper (RESEARCH_PAPER.md)
2. The experiment code and results (mbti_voice_eval.py and results)

**Key areas to evaluate:**

1. **Experimental Design:**
   - Is the control condition properly designed?
   - Are the sample sizes adequate?
   - Is the randomization appropriate?
   - Are there confounding variables?

2. **Statistical Analysis:**
   - Is the statistical test appropriate (Welch's t-test)?
   - Are the assumptions met?
   - Is the effect size calculation correct?
   - Are p-values properly interpreted?

3. **LLM-as-Judge Methodology:**
   - Is this a valid evaluation method?
   - What are the limitations?
   - Are there biases in the judge model?
   - Should human evaluation be required?

4. **Scientific Validity:**
   - Are the claims supported by evidence?
   - Are limitations properly acknowledged?
   - Is the conclusion justified by the data?
   - Are there alternative explanations?

5. **Code and Implementation:**
   - Is the experiment code sound?
   - Are there bugs or methodological errors?
   - Is the data collection reliable?
   - Are the results reproducible?

**Research Paper Content:**
{paper_content[:8000]}

**Experiment Code Summary:**
{code_summary[:2000]}

**Results Summary:**
{results_summary}

**Your Review Should Include:**
- Summary of the work
- Critical assessment of scientific validity (be very strict)
- Methodological concerns
- Statistical concerns
- Specific recommendations for improvement
- Overall assessment

Write your review in your authentic voice as {faculty_name}, but maintain scientific rigor and critical thinking throughout."""

def create_github_issue(title: str, body: str, labels: list = None) -> Dict[str, Any]:
    """Create a GitHub issue using gh CLI."""
    repo = "InquiryInstitute/mbti-faculty-voice-research"
    
    # Prepare issue body (escape if needed)
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(body)
        temp_file = f.name
    
    try:
        # Build gh issue create command
        cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body-file", temp_file]
        
        # Only add labels if they exist (skip if they don't)
        if labels:
            # Try to create issue without labels first, then add labels if they exist
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                issue_number = issue_url.split('/')[-1]
                
                # Try to add labels (ignore errors if labels don't exist)
                for label in labels:
                    try:
                        subprocess.run(
                            ["gh", "issue", "edit", issue_number, "--repo", repo, "--add-label", label],
                            capture_output=True,
                            timeout=10
                        )
                    except:
                        pass  # Ignore label errors
                
                print(f"✅ Created issue: {issue_url}")
                return {"success": True, "url": issue_url}
            else:
                print(f"❌ Failed to create issue: {result.stderr}")
                return {"success": False, "error": result.stderr}
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                print(f"✅ Created issue: {issue_url}")
                return {"success": True, "url": issue_url}
            else:
                print(f"❌ Failed to create issue: {result.stderr}")
                return {"success": False, "error": result.stderr}
    except Exception as e:
        print(f"❌ Error creating issue: {e}")
        return {"success": False, "error": str(e)}
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass

def update_github_issue(issue_number: int, body: str) -> bool:
    """Update an existing GitHub issue with new body."""
    repo = "InquiryInstitute/mbti-faculty-voice-research"
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(body)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ["gh", "issue", "edit", str(issue_number), "--repo", repo, "--body-file", temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Updated issue #{issue_number}")
            return True
        else:
            print(f"❌ Failed to update issue #{issue_number}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error updating issue: {e}")
        return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    print("🔍 Generating faculty agent peer reviews...")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("\n⚠️  OPENROUTER_API_KEY not set in environment.")
        print("   Please set it: export OPENROUTER_API_KEY='sk-or-v1-...'")
        print("   Or it will be read from .env.local if present.")
        # Try loading from .env.local
        try:
            from dotenv import load_dotenv
            load_dotenv(project_root / ".env.local")
            if os.getenv("OPENROUTER_API_KEY"):
                print("✅ Loaded API key from .env.local")
            else:
                print("❌ No API key found. Cannot generate reviews.")
                return
        except:
            print("❌ No API key found. Cannot generate reviews.")
            return
    
    # Read materials
    print("\n📄 Reading research materials...")
    paper_content = read_research_paper()
    code_content = read_experiment_code()
    results_summary = get_experiment_summary()
    
    # Code summary (key parts)
    code_summary = f"""
The experiment code (mbti_voice_eval.py) implements:
- 10 faculty personae × 16 MBTI types × 3 prompts = 480 MBTI trials
- 10 personae × 3 prompts = 30 control trials
- Uses gpt-oss-120b for both generation and judging
- LLM-as-judge evaluates: voice_accuracy, style_marker_coverage, persona_consistency, clarity, overfitting_to_mbti
- Statistical analysis uses Welch's t-test with Cohen's d for effect size
- Results saved to mbti_voice_results.jsonl and mbti_voice_results.csv
"""
    
    # Faculty reviewers with existing issue numbers
    reviewers = [
        ("a.john-dewey", "John Dewey", "Peer Review: Scientific Validity and Pragmatic Utility (John Dewey)", 1),
        ("a.alan-turing", "Alan Turing", "Peer Review: Computational Methodology and Statistical Rigor (Alan Turing)", 2),
        ("a.ada-lovelace", "Ada Lovelace", "Peer Review: Experimental Design and Analytical Precision (Ada Lovelace)", 3),
    ]
    
    for faculty_slug, faculty_name, issue_title, issue_number in reviewers:
        print(f"\n👤 Generating review from {faculty_name}...")
        
        # Generate review prompt
        prompt = generate_review_prompt(faculty_name, paper_content, code_summary, results_summary)
        
        # Get review from faculty agent
        review = call_faculty_agent(faculty_slug, prompt)
        
        if not review:
            print(f"⚠️  Could not get review from {faculty_name}, using fallback...")
            review = f"""# Peer Review by {faculty_name}

**Note:** This is a placeholder review. The faculty agent API was unavailable.

Please review:
1. The research paper (RESEARCH_PAPER.md)
2. The experiment code (mbti_voice_eval.py)
3. The results (mbti_voice_results.csv)

Focus on scientific validity, methodological rigor, and statistical soundness.
"""
        
        # Create/update GitHub issue
        issue_body = f"""# Peer Review: {faculty_name}

**Reviewer:** {faculty_name} ({faculty_slug})
**Review Date:** {subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}

---

{review}

---

## Materials Reviewed

- **Research Paper:** RESEARCH_PAPER.md
- **Experiment Code:** mbti_voice_eval.py  
- **Results:** mbti_voice_results.csv, mbti_voice_results.jsonl
- **Notebook:** MBTI_Research_Colab.ipynb

{results_summary}
"""
        
        # Try to update existing issue first
        if update_github_issue(issue_number, issue_body):
            print(f"✅ Review from {faculty_name} updated in issue #{issue_number}")
        else:
            # If update fails, try creating a new issue
            print(f"⚠️  Could not update issue #{issue_number}, creating new issue...")
            result = create_github_issue(issue_title, issue_body, labels=None)
            if result.get("success"):
                print(f"✅ Review from {faculty_name} published as new GitHub issue")
            else:
                print(f"❌ Failed to create issue for {faculty_name}: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✅ Review generation complete!")

if __name__ == "__main__":
    main()
