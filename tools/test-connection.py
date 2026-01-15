#!/usr/bin/env python3
"""
Quick test script to verify OpenRouter API connection.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_connection():
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY in .env")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    # Initialize client
    if api_key.startswith("sk-or-v1-"):
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/InquiryInstitute/mbti-faculty-voice-research",
                "X-Title": "MBTI Faculty Voice Research"
            }
        )
        model = os.getenv("OPENAI_MODEL", "openai/gpt-4o")
        print(f"🔗 Using OpenRouter with model: {model}")
    else:
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        print(f"🔗 Using OpenAI with model: {model}")
    
    # Test API call
    try:
        print("\n🧪 Testing API connection...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say 'Hello' if you can read this."}
            ],
            max_tokens=10
        )
        result = response.choices[0].message.content
        print(f"✅ Connection successful!")
        print(f"📝 Response: {result}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
