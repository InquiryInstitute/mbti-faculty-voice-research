#!/usr/bin/env python3
"""
Generate a commonplace essay by Ada Lovelace on MBTI in prompt engineering.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def openai_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    if api_key and api_key.startswith("sk-or-v1-"):
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/InquiryInstitute/mbti-faculty-voice-research",
                "X-Title": "MBTI Faculty Voice Research"
            }
        )
    return OpenAI(api_key=api_key)

def generate_lovelace_essay():
    client = openai_client()
    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o")
    
    prompt = """You are Ada Lovelace, writing a commonplace essay on the investigation of MBTI's value in prompt engineering for faculty agent accuracy.

Context: This research examines whether Myers-Briggs Type Indicator (MBTI) personality overlays improve voice accuracy, consistency, and interpretability in AI faculty agents. The experiment tests 10 faculty personae across 16 MBTI types with 3 test prompts each (480 trials total), using an LLM-as-judge to evaluate voice accuracy.

Your task: Write a thoughtful, elegant commonplace essay (2000-3000 words) that:
- Reflects on the relationship between symbolic systems (like MBTI) and computational mechanisms
- Considers how personality frameworks might function as "prompt compression ontologies"
- Explores the tension between psychological validity and practical utility in AI systems
- Discusses the implications for creating coherent, persistent agent identities
- Maintains your characteristic voice: elegant, analytical, visionary about computation's scope, precise but imaginative, with a "poetical science" sensibility
- Uses your signature moves: clarify mechanism vs meaning, structured explanation, poetical science sensibility
- Avoids modern dev slang, casual tone, or pretending firsthand modern tooling

Write in the style of your era (Victorian scientific culture) but addressing contemporary AI systems. Be thoughtful, precise, and allow for the imaginative possibilities while maintaining analytical rigor."""

    messages = [
        {"role": "system", "content": """You are Ada Lovelace, the first computer programmer and a visionary of computation's potential. 
Your voice is elegant, analytical, visionary about computation's scope, precise but imaginative. 
You clarify mechanism vs meaning, provide structured explanations, and maintain a 'poetical science' sensibility.
You write in the style of Victorian scientific culture, with careful distinctions and elegant prose."""},
        {"role": "user", "content": prompt}
    ]
    
    print("Generating essay by Ada Lovelace...")
    print(f"Using model: {model}\n")
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.8,
        max_tokens=4000
    )
    
    essay = response.choices[0].message.content
    
    # Save to file
    output_file = "lovelace_essay_mbti_research.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# On the Investigation of MBTI in Prompt Engineering for Faculty Agent Accuracy\n\n")
        f.write("**Ada Lovelace**\n\n")
        f.write("*A Commonplace Essay*\n\n")
        f.write("---\n\n")
        f.write(essay)
    
    print(f"\n✅ Essay saved to: {output_file}")
    print(f"\nEssay preview (first 500 chars):\n")
    print(essay[:500] + "...")
    
    return essay

if __name__ == "__main__":
    generate_lovelace_essay()
