#!/usr/bin/env python3
"""
Generate peer reviews from faculty agents and create GitHub issues using gh CLI.

This script:
1. Reads RESEARCH_PAPER.md and analyzes the experiment code/results
2. Generates reviews from three faculty agents
3. Creates GitHub issues using gh CLI
"""

import os
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def read_research_paper() -> str:
    """Read the research paper markdown."""
    paper_path = project_root / "RESEARCH_PAPER.md"
    return paper_path.read_text(encoding='utf-8')

def get_experiment_summary() -> str:
    """Get a summary of the experiment results."""
    try:
        import pandas as pd
        df = pd.read_csv(project_root / "mbti_voice_results.csv")
        valid = df[df['voice_accuracy'] != -1]
        control = valid[valid['use_mbti'] == False]
        mbti = valid[valid['use_mbti'] == True]
        
        return f"""
**Total Trials:** {len(df)}
**Valid Results:** {len(valid)}
**Control Condition:** {len(control)} trials, Mean = {control['voice_accuracy'].mean():.2f}, SD = {control['voice_accuracy'].std():.2f}
**MBTI Condition:** {len(mbti)} trials, Mean = {mbti['voice_accuracy'].mean():.2f}, SD = {mbti['voice_accuracy'].std():.2f}
**Improvement:** {((mbti['voice_accuracy'].mean() - control['voice_accuracy'].mean()) / control['voice_accuracy'].mean() * 100):.1f}%
"""
    except Exception as e:
        return f"Error: {e}"

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
                "X-Title": "MBTI Faculty Voice Research - Peer Review"
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

def generate_review(faculty_name: str, system_prompt: str, paper_content: str, results_summary: str) -> str:
    """Generate a review from a faculty agent."""
    prompt = f"""You are {faculty_name}, providing a rigorous peer review of a research paper on MBTI in prompt engineering for faculty agent accuracy.

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
    
    return call_faculty_agent(faculty_name, system_prompt, prompt)

def create_issue_with_gh(title: str, body: str) -> bool:
    """Create a GitHub issue using gh CLI."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(body)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ["gh", "issue", "create", "--repo", "InquiryInstitute/mbti-faculty-voice-research", 
             "--title", title, "--body-file", temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Created: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    print("🔍 Generating faculty agent peer reviews...\n")
    
    # Load API key
    try:
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env.local")
    except:
        pass
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY not set. Please set it or add to .env.local")
        return
    
    # Read materials
    print("📄 Reading research materials...")
    paper_content = read_research_paper()
    results_summary = get_experiment_summary()
    
    # Faculty reviewers
    reviewers = [
        ("John Dewey", """You are John Dewey, the American philosopher, psychologist, and educational reformer. You are known for your pragmatic philosophy, emphasis on experience and inquiry, and your work in progressive education. You value practical consequences, democratic participation, and learning through doing. You write in a clear, accessible style that emphasizes the connection between theory and practice.""", 
         "Peer Review: Scientific Validity and Pragmatic Utility (John Dewey)"),
        ("Alan Turing", """You are Alan Turing, the British mathematician, logician, and computer scientist. You are known for your work on computability, the Turing machine, and code-breaking. You think with mathematical precision, value logical rigor, and are interested in the fundamental questions of computation and intelligence. You write with clarity and technical accuracy.""",
         "Peer Review: Computational Methodology and Statistical Rigor (Alan Turing)"),
        ("Ada Lovelace", """You are Ada Lovelace, the English mathematician and writer. You are known for your work on Charles Babbage's Analytical Engine and are often considered the first computer programmer. You combine mathematical rigor with imaginative vision, seeing the potential for machines to go beyond calculation. You write with elegance, precision, and visionary insight.""",
         "Peer Review: Experimental Design and Analytical Precision (Ada Lovelace)"),
    ]
    
    for faculty_name, system_prompt, issue_title in reviewers:
        print(f"\n👤 Generating review from {faculty_name}...")
        
        review = generate_review(faculty_name, system_prompt, paper_content, results_summary)
        
        if not review:
            print(f"⚠️  Could not generate review from {faculty_name}")
            continue
        
        issue_body = f"""# Peer Review: {faculty_name}

**Reviewer:** {faculty_name}
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
        
        print(f"📝 Creating GitHub issue...")
        create_issue_with_gh(issue_title, issue_body)
    
    print("\n✅ Review generation complete!")

if __name__ == "__main__":
    main()
